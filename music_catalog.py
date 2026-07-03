"""Music reference catalog for Collector Catalog.

Data lives in ~/.collector_catalog/music_catalog.json and is populated
in-app via the "Import Artist" button (fetches from Discogs).  This module
reloads the file on every search call so newly imported artists appear
immediately without restarting the app.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

_DATA_PATH = Path.home() / ".collector_catalog" / "music_catalog.json"

# Normalise Discogs raw format strings → music type's format options
_FORMAT_NORM: Dict[str, str] = {
    "vinyl":             "Vinyl",
    "shellac":           "Vinyl",
    "lathe cut":         "Vinyl",
    "cd":                "CD",
    "cdr":               "CD",
    "cassette":          "Cassette",
    "sacd":              "SACD",
    "dvd-audio":         "DVD-Audio",
    "blu-ray audio":     "Blu-ray Audio",
    "8-track cartridge": "8-Track",
    "8-track":           "8-Track",
    "minidisc":          "MiniDisc",
    "reel-to-reel":      "Reel-to-Reel",
    "file":              "Digital / Streaming",
    "digital":           "Digital / Streaming",
}

# Format strings that are NOT physical media — excluded from import
_DIGITAL_FORMATS = {"file", "digital", ""}


def normalise_format(raw: str) -> str:
    """Map a Discogs format string to the app's format option values."""
    return _FORMAT_NORM.get(raw.strip().lower(), raw.strip())


def is_physical(raw: str) -> bool:
    return raw.strip().lower() not in _DIGITAL_FORMATS


def _load() -> List[Dict[str, Any]]:
    if not _DATA_PATH.exists():
        return []
    try:
        return json.loads(_DATA_PATH.read_text("utf-8"))
    except Exception:
        return []


def save_entries(entries: List[Dict[str, Any]]) -> None:
    """Append *entries* to the catalog, replacing any existing rows for the
    same artist (case-insensitive) so re-imports refresh cleanly."""
    existing = _load()
    new_artists = {e.get("artist", "").lower() for e in entries}
    kept = [e for e in existing if e.get("artist", "").lower() not in new_artists]
    merged = kept + entries
    _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DATA_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), "utf-8")


def search(query: str, media: str = "All") -> List[Dict[str, Any]]:
    """Return entries matching *query* text, filtered by *media* type.

    The kwarg is ``media`` (not ``format``) to avoid shadowing the built-in
    and to match the ``filter_field`` key in the catalogs.py REGISTRY.
    """
    entries = _load()
    q = query.strip().lower()
    results = []
    for e in entries:
        if media != "All" and e.get("format", "") != media:
            continue
        haystack = " ".join([
            e.get("title", ""),
            e.get("artist", ""),
            e.get("label", ""),
            e.get("catalog_number", ""),
            e.get("genre", ""),
            e.get("year", ""),
        ]).lower()
        if not q or q in haystack:
            results.append(e)
    return results


def to_music_fields(entry: Dict[str, Any]) -> Dict[str, str]:
    """Map a catalog entry to item field names (works for music, cd, cassette)."""
    return {k: v for k, v in {
        "title":          entry.get("title", ""),
        "artist":         entry.get("artist", ""),
        "year":           str(entry.get("year", "")),
        "release_type":   entry.get("release_type", ""),
        "genre":          entry.get("genre", ""),
        "label":          entry.get("label", ""),
        "catalog_number": entry.get("catalog_number", ""),
        "country":        entry.get("country", ""),
        "format":         entry.get("format", ""),
        "tracklist":      entry.get("tracklist", ""),
        # CD-specific
        "edition":        entry.get("edition", ""),
        # Cassette-specific
        "tape_type":      entry.get("tape_type", ""),
    }.items() if v}


# Required alias
to_fields = to_music_fields

SEARCH_COLS = [
    ("title",  "Album / Release", 240),
    ("artist", "Artist",          150),
    ("year",   "Year",             55),
    ("format", "Media",            75),
]

DETAIL_FIELDS = [
    ("artist",         "Artist"),
    ("year",           "Year"),
    ("format",         "Media"),
    ("release_type",   "Release Type"),
    ("genre",          "Genre"),
    ("label",          "Record Label"),
    ("catalog_number", "Catalog #"),
    ("country",        "Country"),
]
