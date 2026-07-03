#!/usr/bin/env python3
"""build_music_catalog.py — One-time script to generate music_catalog.py.

Fetches Cleveland Orchestra releases from the Discogs API, normalises the data,
deduplicates, and writes a static music_catalog.py ready to be used by the app.

Usage:
    python3 build_music_catalog.py [--token TOKEN] [--limit N] [--no-detail]

Flags:
    --token TOKEN    Discogs Personal Access Token. Falls back to DISCOGS_TOKEN
                     env var, then discogs_token in
                     ~/.collector_catalog/settings.json.
    --limit N        Only fetch detail for the first N releases (for testing).
    --no-detail      Skip the per-release detail pass (no tracklist/conductor/
                     composer/catno). Fast but thin.

Disk cache:
    Fetched release JSON is cached under .discogs_cache/{id}.json so reruns and
    crashes don't re-hit the API.

Output:
    music_catalog.py in the current directory (the app source tree).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Discogs artist id for "The Cleveland Orchestra"
# Resolved once via /database/search?type=artist&q=The+Cleveland+Orchestra.
# Hardcoded so reruns are deterministic. Verify with:
#   GET https://api.discogs.com/artists/267353
CLEVELAND_ORCHESTRA_ARTIST_ID = 267353

USER_AGENT = "CollectorCatalogBuilder/1.0 (collector catalog desktop app)"
CACHE_DIR  = Path(".discogs_cache")
OUT_FILE   = Path("music_catalog.py")

# Minimum seconds between API calls (~55 req/min, well within 60/min limit)
_MIN_INTERVAL = 1.15
_last_call_ts: float = 0.0


# ---------------------------------------------------------------------------
# Token resolution

def _resolve_token(cli_token: Optional[str]) -> str:
    if cli_token and cli_token.strip():
        return cli_token.strip()
    env = os.environ.get("DISCOGS_TOKEN", "").strip()
    if env:
        return env
    settings_path = Path.home() / ".collector_catalog" / "settings.json"
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text())
            tok = data.get("discogs_token", "").strip()
            if tok:
                return tok
        except Exception:
            pass
    print(
        "ERROR: No Discogs token found.\n"
        "  Pass --token TOKEN, set DISCOGS_TOKEN env var, or click 'Discogs Lookup'\n"
        "  once inside the app to save the token to settings.json.\n"
        "  Get a free token at: discogs.com → Settings → Developers → "
        "Generate new token",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# HTTP helpers

def _get(url: str, token: str, timeout: int = 30) -> Any:
    global _last_call_ts
    now = time.monotonic()
    gap = now - _last_call_ts
    if gap < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - gap)
    _last_call_ts = time.monotonic()

    headers = {
        "User-Agent": USER_AGENT,
        "Authorization": f"Discogs token={token}",
    }
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                remaining = resp.headers.get("X-Discogs-Ratelimit-Remaining", "60")
                if int(remaining) < 5:
                    print("  [rate-limit warning] remaining calls low, sleeping 15s…")
                    time.sleep(15)
                raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 65
                print(f"  [429 rate limited] sleeping {wait}s then retrying…")
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.reason}  url={url}") from e
        except Exception as e:
            if attempt == 3:
                raise RuntimeError(f"Request failed after 4 attempts: {e}") from e
            time.sleep(5)
    raise RuntimeError("Unreachable")


def _get_cached(release_id: int, token: str) -> dict:
    CACHE_DIR.mkdir(exist_ok=True)
    cache_path = CACHE_DIR / f"{release_id}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    data = _get(f"https://api.discogs.com/releases/{release_id}", token)
    cache_path.write_text(json.dumps(data, ensure_ascii=False))
    return data


# ---------------------------------------------------------------------------
# Enumeration: artist releases

def _enumerate_releases(token: str) -> List[dict]:
    """Page through /artists/{id}/releases and return all rows."""
    page, pages = 1, 1
    rows: List[dict] = []
    print(f"Enumerating releases for artist id {CLEVELAND_ORCHESTRA_ARTIST_ID}…")
    while page <= pages:
        url = (
            f"https://api.discogs.com/artists/{CLEVELAND_ORCHESTRA_ARTIST_ID}"
            f"/releases?per_page=100&page={page}&sort=year&sort_order=asc"
        )
        data = _get(url, token)
        pagination = data.get("pagination", {})
        pages = pagination.get("pages", 1)
        releases = data.get("releases", [])
        rows.extend(releases)
        print(f"  page {page}/{pages} — {len(releases)} rows (total so far: {len(rows)})")
        page += 1
    # Keep only proper releases where the orchestra has a main role
    kept = [
        r for r in rows
        if r.get("type") == "release"
        and r.get("role", "").lower() in ("main", "")
    ]
    print(f"  {len(rows)} total rows → {len(kept)} after filtering to releases/main role")
    return kept


# ---------------------------------------------------------------------------
# Format normalization

_FORMAT_MAP: Dict[str, str] = {
    "vinyl":          "Vinyl",
    "cd":             "CD",
    "cdr":            "CD",
    "cassette":       "Cassette",
    "sacd":           "SACD",
    "dvd-audio":      "DVD-Audio",
    "dvd":            "DVD-Audio",
    "blu-ray":        "Blu-ray Audio",
    "reel-to-reel":   "Reel-to-Reel",
    "8-track cartridge": "8-Track",
    "8-track":        "8-Track",
    "minidisc":       "MiniDisc",
    "file":           "Digital / Streaming",
    "digital":        "Digital / Streaming",
    "shellac":        "Vinyl",
    "laserdisc":      "DVD-Audio",
}

_RELEASE_TYPE_DESCRIPTIONS = {
    "album", "compilation", "ep", "single", "live", "soundtrack",
    "box set", "bootleg", "demo", "mixtape", "promo",
}


def _normalize_format(fmt_list: Any) -> str:
    """Convert a Discogs formats list to a single primary media type string."""
    if not fmt_list:
        return ""
    first = fmt_list[0] if isinstance(fmt_list, list) else fmt_list
    # Detail endpoint: list of dicts with "name" and optional "descriptions"
    if isinstance(first, dict):
        name = first.get("name", "").strip()
        descs = [d.strip().lower() for d in (first.get("descriptions") or [])]
        # SACD is a description, not a media name
        if "sacd" in descs:
            return "SACD"
        if "dvd-audio" in descs:
            return "DVD-Audio"
        if "blu-ray audio" in descs:
            return "Blu-ray Audio"
        key = name.lower()
        if key in _FORMAT_MAP:
            return _FORMAT_MAP[key]
        return name  # verbatim fallback

    # Search endpoint: flat list of strings
    if isinstance(first, str):
        for item in fmt_list:
            key = item.strip().lower()
            if key in _FORMAT_MAP:
                return _FORMAT_MAP[key]
        return fmt_list[0]  # verbatim fallback

    return ""


def _derive_release_type(fmt_list: Any) -> str:
    """Extract release type from Discogs format descriptions (Album, Compilation…)."""
    if not fmt_list or not isinstance(fmt_list, list):
        return ""
    descs: List[str] = []
    for item in fmt_list:
        if isinstance(item, dict):
            descs.extend(item.get("descriptions") or [])
    type_map = {
        "album":       "Album",
        "compilation": "Compilation",
        "ep":          "EP",
        "single":      "Single",
        "live":        "Live Album",
        "soundtrack":  "Soundtrack",
        "box set":     "Box Set",
        "bootleg":     "Bootleg",
        "demo":        "Demo",
        "mixtape":     "Mixtape",
        "promo":       "Album",
    }
    for d in descs:
        key = d.strip().lower()
        if key in type_map:
            return type_map[key]
    return "Album"


# ---------------------------------------------------------------------------
# Credit extraction

def _extract_credits(release_detail: dict):
    """Return (conductor, composer) strings from release extraartists."""
    conductor_names: List[str] = []
    composer_names: List[str] = []

    def _scan(credits: List[dict]):
        for c in credits:
            role = c.get("role", "").lower()
            name = c.get("name", c.get("anv", "")).strip()
            if not name:
                continue
            if "conductor" in role:
                conductor_names.append(name)
            if any(r in role for r in ("composed by", "composer", "music by",
                                        "written-by", "written by")):
                composer_names.append(name)

    _scan(release_detail.get("extraartists") or [])
    # Also check tracklist-level extraartists for conductors/composers
    for track in (release_detail.get("tracklist") or []):
        _scan(track.get("extraartists") or [])

    # Fallback: try to parse composer from title ("Beethoven: Symphony No. 5")
    if not composer_names:
        title = release_detail.get("title", "")
        m = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*[:\-–]', title)
        # Only treat as composer if it's not an orchestra/common word
        skip = {"the", "volume", "symphony", "concerto", "complete"}
        if m and m.group(1).split()[0].lower() not in skip:
            composer_names.append(m.group(1))

    conductor = ", ".join(dict.fromkeys(conductor_names))  # deduplicated, ordered
    composer  = ", ".join(dict.fromkeys(composer_names))
    return conductor, composer


def _build_tracklist(release_detail: dict) -> str:
    tracks = release_detail.get("tracklist") or []
    lines: List[str] = []
    for t in tracks:
        pos   = t.get("position", "").strip()
        name  = t.get("title", "").strip()
        dur   = t.get("duration", "").strip()
        if not name:
            continue
        line = f"{pos}. {name}" if pos else name
        if dur:
            line += f"  ({dur})"
        lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Build full entry from detail

def _build_entry(row: dict, detail: Optional[dict]) -> dict:
    """Merge artist-releases row + optional release detail into a catalog entry."""
    entry: dict = {
        "title":          "",
        "artist":         "The Cleveland Orchestra",
        "year":           "",
        "release_type":   "",
        "genre":          "Classical",
        "label":          "",
        "catalog_number": "",
        "country":        "",
        "format":         "",
        "tracklist":      "",
        "conductor":      "",
        "composer":       "",
    }

    # Title: row title often "Artist - Album"; strip the artist prefix
    raw_title = (row.get("title") or "").strip()
    if " - " in raw_title:
        _art, alb = raw_title.split(" - ", 1)
        entry["title"] = alb.strip()
    else:
        entry["title"] = raw_title

    year = row.get("year") or ""
    entry["year"] = str(year) if year else ""

    if detail is None:
        # Thin entry (--no-detail)
        fmt_list = row.get("format", [])
        if isinstance(fmt_list, str):
            fmt_list = [fmt_list]
        entry["format"] = _normalize_format(fmt_list)
        label_list = row.get("label") or []
        if isinstance(label_list, list) and label_list:
            entry["label"] = label_list[0]
        return {k: v for k, v in entry.items() if v != ""}

    # --- Full detail ---
    # Title from detail is more reliable
    detail_title = (detail.get("title") or "").strip()
    if detail_title:
        entry["title"] = detail_title

    if detail.get("year"):
        entry["year"] = str(detail["year"])

    # Format
    fmt_list = detail.get("formats") or []
    entry["format"]       = _normalize_format(fmt_list)
    entry["release_type"] = _derive_release_type(fmt_list)

    # Label + catno
    labels = detail.get("labels") or []
    if labels:
        entry["label"]          = labels[0].get("name", "")
        entry["catalog_number"] = labels[0].get("catno", "")
        if entry["catalog_number"].lower() == "none":
            entry["catalog_number"] = ""

    entry["country"] = detail.get("country", "")

    # Genres / styles
    genres = (detail.get("genres") or []) + (detail.get("styles") or [])
    if genres:
        entry["genre"] = ", ".join(genres[:2])

    # Credits
    entry["conductor"], entry["composer"] = _extract_credits(detail)

    # Tracklist
    entry["tracklist"] = _build_tracklist(detail)

    return {k: v for k, v in entry.items() if v != ""}


# ---------------------------------------------------------------------------
# Dedup

def _dedup(entries: List[dict]) -> List[dict]:
    seen: set = set()
    out: List[dict] = []
    for e in entries:
        key = (
            e.get("title", "").strip().lower(),
            e.get("format", "").strip().lower(),
            e.get("year", "").strip(),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


# ---------------------------------------------------------------------------
# Emit

_INTERFACE = '''
# ── Search / lookup interface ─────────────────────────────────────────────────

def search(query: str, media: str = "All"):
    """Return entries matching *query* and optional *media* filter.

    The kwarg is named ``media`` (not ``format``) to avoid shadowing the
    built-in and to match the REGISTRY filter_field key in catalogs.py.
    """
    q = query.strip().lower()
    results = []
    for entry in CATALOG:
        if media != "All" and entry.get("format", "") != media:
            continue
        haystack = " ".join([
            entry.get("title", ""),
            entry.get("artist", ""),
            entry.get("conductor", ""),
            entry.get("composer", ""),
            entry.get("label", ""),
            entry.get("catalog_number", ""),
            entry.get("genre", ""),
        ]).lower()
        if not q or q in haystack:
            results.append(entry)
    return results


def to_music_fields(entry):
    """Map a CATALOG entry to music item-type fields."""
    return {k: v for k, v in {
        "title":          entry.get("title", ""),
        "artist":         entry.get("artist", ""),
        "conductor":      entry.get("conductor", ""),
        "composer":       entry.get("composer", ""),
        "year":           entry.get("year", ""),
        "release_type":   entry.get("release_type", ""),
        "genre":          entry.get("genre", "") or "Classical",
        "label":          entry.get("label", ""),
        "catalog_number": entry.get("catalog_number", ""),
        "country":        entry.get("country", ""),
        "format":         entry.get("format", ""),
        "tracklist":      entry.get("tracklist", ""),
    }.items() if v}


# Required alias
to_fields = to_music_fields

SEARCH_COLS = [
    ("title",     "Album / Release", 260),
    ("conductor", "Conductor",       150),
    ("year",      "Year",             60),
    ("format",    "Media",            90),
]

DETAIL_FIELDS = [
    ("artist",         "Artist"),
    ("conductor",      "Conductor"),
    ("composer",       "Composer"),
    ("year",           "Year"),
    ("format",         "Media"),
    ("label",          "Record Label"),
    ("catalog_number", "Catalog #"),
    ("country",        "Country"),
    ("genre",          "Genre"),
]
'''


def _emit(entries: List[dict], out_path: Path):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: List[str] = [
        '"""Cleveland Orchestra reference catalog for Collector Catalog.',
        "",
        f"Auto-generated by build_music_catalog.py on {now}.",
        "Source: Discogs API (https://www.discogs.com).",
        "",
        "DO NOT edit by hand — re-run build_music_catalog.py to regenerate.",
        '"""',
        "",
        "from __future__ import annotations",
        "from typing import List, Dict, Any",
        "",
        "",
        "# ── Data ─────────────────────────────────────────────────────────────────────",
        "",
        "CATALOG: List[Dict[str, Any]] = [",
    ]

    # Sort: year (numeric, blank last) then title
    def _sort_key(e):
        yr = e.get("year", "")
        try:
            y = int(re.search(r"\d{4}", yr).group())
        except Exception:
            y = 9999
        return (y, e.get("title", "").lower())

    entries.sort(key=_sort_key)

    for e in entries:
        lines.append("    " + repr(e) + ",")

    lines += ["]", ""]
    lines.append(_INTERFACE)

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {len(entries)} entries to {out_path}")


# ---------------------------------------------------------------------------
# Main

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--token",     help="Discogs Personal Access Token")
    parser.add_argument("--limit",     type=int, default=0,
                        help="Only process first N releases (0 = all)")
    parser.add_argument("--no-detail", action="store_true",
                        help="Skip per-release detail fetch (fast but thin)")
    args = parser.parse_args()

    token = _resolve_token(args.token)

    # Enumerate
    rows = _enumerate_releases(token)
    if args.limit:
        rows = rows[: args.limit]
        print(f"  --limit {args.limit}: processing {len(rows)} releases")

    # Detail pass
    entries: List[dict] = []
    total = len(rows)
    for i, row in enumerate(rows, 1):
        rid = row.get("id")
        if not rid:
            continue
        if args.no_detail:
            entry = _build_entry(row, detail=None)
        else:
            print(f"[{i:4d}/{total}] release {rid}  {row.get('title','')[:60]}")
            try:
                detail = _get_cached(rid, token)
            except Exception as exc:
                print(f"  WARNING: could not fetch release {rid}: {exc}")
                entry = _build_entry(row, detail=None)
            else:
                entry = _build_entry(row, detail=detail)
        if entry.get("title"):
            entries.append(entry)

    print(f"\nFetched {len(entries)} entries before dedup")
    entries = _dedup(entries)
    print(f"After dedup: {len(entries)} entries")

    _emit(entries, OUT_FILE)
    print("Done. Run the app rebuild script to include the new catalog.")


if __name__ == "__main__":
    main()
