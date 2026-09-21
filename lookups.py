"""Online identifier lookups — "ISBN function" and friends.

Each lookup takes an identifier (or a free-text query) and returns a dict
keyed by the *field names* used in the matching item type in
``type_defs.py``, ready to drop straight into an item.  Only fields the
service actually returns are included, so callers can choose to fill blanks
only and never clobber data the user already typed.

Services used (all reachable without a paid plan unless noted):

    • Books   — Open Library  (https://openlibrary.org)   free, no key
    •         — Penguin API   (https://www.penguinrandomhouse.biz/webservices/rest/)  fallback
    • Vinyl   — MusicBrainz    (https://musicbrainz.org)   free, no key
    • Games   — PriceCharting  (https://www.pricecharting.com) needs API token

Everything here uses only the Python standard library so the app keeps its
single external dependency (Pillow).
"""

from __future__ import annotations

import json
import re
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional

USER_AGENT = "CollectorCatalog/1.0 (collector catalog desktop app)"


class LookupError(Exception):
    """Raised when a lookup fails or returns nothing usable."""


def _get_json(url: str, timeout: int = 20, extra_headers: Optional[Dict[str, str]] = None) -> Any:
    hdrs = {"User-Agent": USER_AGENT}
    if extra_headers:
        hdrs.update(extra_headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise LookupError(f"HTTP {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise LookupError(f"Network error: {e.reason}") from e
    except Exception as e:  # noqa: BLE001 - surface anything as a LookupError
        raise LookupError(str(e)) from e
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise LookupError(f"Bad JSON from server: {e}") from e


# ── Books: ISBN → fields via Open Library ─────────────────────────────────────

def _clean_isbn(isbn: str) -> str:
    return re.sub(r"[^0-9Xx]", "", isbn or "").upper()


def lookup_isbn(isbn: str, try_penguin: bool = True) -> Dict[str, str]:
    """Look up a book by ISBN-10/13 via Open Library's Books API.

    Optionally tries Penguin Random House API as a fallback if Open Library
    doesn't return a result, to provide better Penguin catalog coverage.

    Returns a dict of ``book`` item fields. Raises LookupError if not found.
    """
    isbn = _clean_isbn(isbn)
    if len(isbn) not in (10, 13):
        raise LookupError("Enter a valid 10- or 13-digit ISBN first.")

    url = (
        "https://openlibrary.org/api/books?"
        + urllib.parse.urlencode({
            "bibkeys": f"ISBN:{isbn}",
            "format": "json",
            "jscmd": "data",
        })
    )
    data = _get_json(url)
    key = f"ISBN:{isbn}"

    # If Open Library has the book, use it as primary source
    if data and key in data:
        rec = data[key]
        out: Dict[str, str] = {}

        if rec.get("title"):
            title = rec["title"]
            if rec.get("subtitle"):
                title = f"{title}: {rec['subtitle']}"
            out["title"] = title

        authors = rec.get("authors") or []
        if authors:
            out["author"] = " and ".join(a.get("name", "") for a in authors if a.get("name"))

        # Open Library keeps translators (and editors, illustrators…) in a
        # separate contributors list — worth picking up for a shelf of
        # classics, where which translation you own is half the point.
        translators = [
            c.get("name", "").strip()
            for c in (rec.get("contributors") or [])
            if "translat" in str(c.get("role") or "").lower() and c.get("name")
        ]
        if translators:
            out["translator"] = " and ".join(translators)

        publishers = rec.get("publishers") or []
        if publishers:
            out["publisher"] = ", ".join(p.get("name", "") for p in publishers if p.get("name"))

        if rec.get("publish_date"):
            m = re.search(r"\d{4}", rec["publish_date"])
            out["year"] = m.group(0) if m else rec["publish_date"]

        places = rec.get("publish_places") or []
        if places:
            out["address"] = places[0].get("name", "")

        if rec.get("number_of_pages"):
            out["pages"] = str(rec["number_of_pages"])

        out["isbn"] = isbn

        if rec.get("url"):
            out["url"] = rec["url"]

        # Subjects → genre (first one) so the field isn't left blank.
        subjects = rec.get("subjects") or []
        if subjects:
            out["genre"] = subjects[0].get("name", "")

        excerpts = rec.get("excerpts") or []
        if excerpts and excerpts[0].get("text"):
            out["abstract"] = excerpts[0]["text"]

        return {k: v for k, v in out.items() if v}

    # Fallback to Penguin if enabled and Open Library fails
    if try_penguin:
        try:
            return lookup_penguin_isbn(isbn)
        except LookupError:
            pass

    # Neither source found it
    raise LookupError(f"No book found for ISBN {isbn}.")


# ── Books: ISBN → enrichment via Penguin Random House API ────────────────────

def lookup_penguin_isbn(isbn: str) -> Dict[str, str]:
    """Look up a book by ISBN via Penguin Random House API as a fallback source.

    Returns a dict of ``book`` item fields. Raises LookupError if not found.
    Can be used to fill gaps left by Open Library or verify information.
    """
    isbn = _clean_isbn(isbn)
    if len(isbn) not in (10, 13):
        raise LookupError("Enter a valid 10- or 13-digit ISBN first.")

    # Try multiple API endpoint patterns since the exact endpoint is not fully
    # documented. Penguin's public API structure may vary.
    endpoints = [
        f"https://www.penguinrandomhouse.biz/webservices/rest/v2/search?q={urllib.parse.quote(f'isbn:{isbn}')}",
        f"https://www.penguinrandomhouse.biz/webservices/rest/search?isbn={isbn}",
        f"https://www.penguinrandomhouse.biz/webservices/rest/findByIsbn?isbn={isbn}",
    ]

    data = None
    for url in endpoints:
        try:
            data = _get_json(url, timeout=10)
            if data and ("results" in data or "result" in data or "book" in data):
                break
        except (LookupError, ValueError):
            continue

    if not data:
        raise LookupError(f"No results from Penguin API for ISBN {isbn}.")

    # Handle different response structures
    result = None
    if isinstance(data, dict):
        if "results" in data and data["results"]:
            result = data["results"][0] if isinstance(data["results"], list) else data["results"]
        elif "result" in data and data["result"]:
            result = data["result"][0] if isinstance(data["result"], list) else data["result"]
        elif "book" in data:
            result = data["book"]
        else:
            # Try direct object
            result = data

    if not result or not isinstance(result, dict):
        raise LookupError("Penguin API returned unexpected format.")

    out: Dict[str, str] = {}

    # Map Penguin API fields to our book fields
    # (actual field names depend on the API version)
    if result.get("title"):
        out["title"] = result["title"]
    if result.get("author"):
        out["author"] = result["author"]
    if result.get("publisher"):
        out["publisher"] = result["publisher"]
    if result.get("isbn"):
        out["isbn"] = result["isbn"]
    if result.get("pages") or result.get("pageCount"):
        pages = result.get("pages") or result.get("pageCount")
        out["pages"] = str(pages)
    if result.get("publicationDate") or result.get("publishDate"):
        pub_date = result.get("publicationDate") or result.get("publishDate")
        if pub_date:
            m = re.search(r"\d{4}", str(pub_date))
            if m:
                out["year"] = m.group(0)
    if result.get("description"):
        out["abstract"] = result["description"]
    if result.get("language"):
        out["language"] = result["language"]
    if result.get("series"):
        out["series"] = result["series"]

    return {k: v for k, v in out.items() if v}


# ── Vinyl: artist / title / barcode → fields via MusicBrainz ──────────────────

def lookup_vinyl(*, artist: str = "", title: str = "",
                 catalog_number: str = "", barcode: str = "") -> Dict[str, str]:
    """Look up a vinyl release via MusicBrainz.

    Provide any combination of artist, album title, catalog number or
    barcode.  The most specific available query is used.  Returns a dict of
    ``vinyl`` item fields for the best-matching release.
    """
    clauses: List[str] = []
    if barcode.strip():
        clauses.append(f'barcode:{_lucene_escape(barcode.strip())}')
    if catalog_number.strip():
        clauses.append(f'catno:{_lucene_escape(catalog_number.strip())}')
    if artist.strip():
        clauses.append(f'artist:"{_lucene_escape(artist.strip())}"')
    if title.strip():
        clauses.append(f'release:"{_lucene_escape(title.strip())}"')

    if not clauses:
        raise LookupError("Enter an artist, album, catalog # or barcode first.")

    query = " AND ".join(clauses)
    url = (
        "https://musicbrainz.org/ws/2/release/?"
        + urllib.parse.urlencode({"query": query, "fmt": "json", "limit": "5"})
    )
    data = _get_json(url)
    releases = data.get("releases") or []
    if not releases:
        raise LookupError("No matching release found on MusicBrainz.")

    rel = releases[0]  # already ranked by score
    out: Dict[str, str] = {}

    if rel.get("title"):
        out["title"] = rel["title"]

    credits = rel.get("artist-credit") or []
    if credits:
        out["artist"] = "".join(
            (c.get("name") or c.get("artist", {}).get("name", "")) + (c.get("joinphrase", ""))
            for c in credits
        ).strip()

    if rel.get("date"):
        m = re.search(r"\d{4}", rel["date"])
        if m:
            out["year"] = m.group(0)

    if rel.get("country"):
        out["country"] = rel["country"]

    labels = rel.get("label-info") or []
    if labels:
        li = labels[0]
        if li.get("label", {}).get("name"):
            out["label"] = li["label"]["name"]
        if li.get("catalog-number"):
            out["catalog_number"] = li["catalog-number"]

    if rel.get("barcode"):
        out["upc"] = rel["barcode"]

    # Format (e.g. "Vinyl") from the media list.
    media = rel.get("media") or []
    if media and media[0].get("format"):
        out["format"] = media[0]["format"]

    return {k: v for k, v in out.items() if v}


def _lucene_escape(s: str) -> str:
    return re.sub(r'([+\-&|!(){}\[\]^"~*?:\\/])', r"\\\1", s)


# ── Games: UPC → fields via PriceCharting product API ─────────────────────────

def lookup_game_upc(upc: str, token: str) -> Dict[str, str]:
    """Look up a single game/console by UPC via PriceCharting's product API.

    Requires a PriceCharting API token (paid tier).  Returns a dict of
    ``videogame`` item fields, reusing the normalizer in ``pricecharting``.
    """
    upc = re.sub(r"[^0-9]", "", upc or "")
    if not upc:
        raise LookupError("Enter a UPC / barcode first.")
    if not token or not token.strip():
        raise LookupError("A PriceCharting API token is required for UPC lookup.")

    url = (
        "https://www.pricecharting.com/api/product?"
        + urllib.parse.urlencode({"t": token.strip(), "upc": upc})
    )
    data = _get_json(url)

    if isinstance(data, dict):
        status = data.get("status") or data.get("Status")
        if status and str(status).lower() not in ("success", "ok"):
            msg = data.get("error-message") or data.get("error") or status
            raise LookupError(f"PriceCharting: {msg}")
    else:
        raise LookupError("Unexpected response from PriceCharting.")

    # Reuse the row→item normalizer so prices / completeness map identically
    # to the CSV/offers importer.
    import pricecharting as pc
    item = pc._row_to_item(data)            # noqa: SLF001 - internal but stable
    fields = pc.to_catalog_fields(item)
    return {k: v for k, v in fields.items() if v}


# ── Dispatch helper ───────────────────────────────────────────────────────────

# Item types that support an auto-fill lookup, and a short button label.
# ── Music: artist / title → fields via Discogs ────────────────────────────────

def lookup_discogs(*, artist: str = "", title: str = "", token: str) -> Dict[str, str]:
    """Look up a release via the Discogs database search API.

    Requires a free Discogs Personal Access Token (create one at
    discogs.com → Settings → Developers → Generate new token).
    Returns a dict of ``music`` item fields for the best-matching release.
    If the release page is reachable a second call fetches the full tracklist.
    """
    if not token or not token.strip():
        raise LookupError("A Discogs Personal Access Token is required.")
    if not artist.strip() and not title.strip():
        raise LookupError("Enter an artist and/or album title first.")

    auth = {"Authorization": f"Discogs token={token.strip()}"}

    params: Dict[str, str] = {"type": "release", "per_page": "5"}
    if artist.strip():
        params["artist"] = artist.strip()
    if title.strip():
        params["release_title"] = title.strip()

    search_url = ("https://api.discogs.com/database/search?"
                  + urllib.parse.urlencode(params))
    data = _get_json(search_url, extra_headers=auth)
    results = data.get("results") or []
    if not results:
        raise LookupError("No matching release found on Discogs.")

    hit = results[0]
    out: Dict[str, str] = {}

    # Search result title comes as "Artist - Album Title"
    raw_title = hit.get("title", "")
    if " - " in raw_title:
        art_part, alb_part = raw_title.split(" - ", 1)
        out["title"] = alb_part.strip()
        if not artist.strip():
            out["artist"] = art_part.strip()
    elif raw_title:
        out["title"] = raw_title

    if hit.get("year"):
        out["year"] = str(hit["year"])

    genres = hit.get("genre") or []
    styles = hit.get("style") or []
    genre_val = ", ".join((genres + styles)[:3])
    if genre_val:
        out["genre"] = genre_val

    labels = hit.get("label") or []
    if labels:
        out["label"] = labels[0]

    catno = (hit.get("catno") or "").strip()
    if catno and catno.lower() != "none":
        out["catalog_number"] = catno

    if hit.get("country"):
        out["country"] = hit["country"]

    formats = hit.get("format") or []
    if formats:
        out["format"] = formats[0]

    # Second call: fetch full release page for tracklist
    resource_url = hit.get("resource_url", "")
    if resource_url:
        try:
            rel = _get_json(resource_url, extra_headers=auth)
            tracks = rel.get("tracklist") or []
            if tracks:
                lines = []
                for t in tracks:
                    pos = t.get("position", "").strip()
                    name = t.get("title", "").strip()
                    dur = t.get("duration", "").strip()
                    line = f"{pos}. {name}" if pos else name
                    if dur:
                        line += f"  ({dur})"
                    if name:
                        lines.append(line)
                if lines:
                    out["tracklist"] = "\n".join(lines)
        except LookupError:
            pass  # tracklist is a bonus; don't fail the whole lookup

    return {k: v for k, v in out.items() if v}


LOOKUP_CAPABLE = {
    "book":      "ISBN Lookup",
    "vinyl":     "MusicBrainz Lookup",
    "music":     "Discogs Lookup",
    "cd":        "Discogs Lookup",
    "cassette":  "Discogs Lookup",
    "videogame": "UPC Lookup",
}
