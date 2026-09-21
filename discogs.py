"""Discogs collection CSV import.

Export your Discogs collection at:
    discogs.com → Profile → Collection → Export Collection  (CSV, all formats)

The downloaded file typically has these columns (Discogs may vary):
    Catalog#, Artist, Title, Label, Format, Rating, Released,
    release_id, CollectionFolder, Date Added,
    Collection Media Condition, Collection Sleeve Condition,
    Collection Notes

``import_discogs_csv(path)`` returns a list of uniform dicts, one per row,
with the shape described in ``_row_to_item``.  The ``type`` key indicates
which app item type to create: ``vinyl``, ``cd``, ``cassette``, or ``music``.
"""

from __future__ import annotations

import csv
import re
from typing import Any, Dict, List, Tuple

# ── Column-name normalisation ─────────────────────────────────────────────────

_COLUMN_ALIASES: Dict[str, str] = {
    # catalog number — Discogs uses a "#" suffix
    "catalog#":                   "catalog_number",
    "catalog":                    "catalog_number",
    "catno":                      "catalog_number",
    # core fields
    "artist":                     "artist",
    "title":                      "title",
    "label":                      "label",
    "format":                     "format_raw",
    "rating":                     "rating",
    "released":                   "released",
    "release_id":                 "release_id",
    # collection-specific
    "collectionfolder":           "folder",
    "collection folder":          "folder",
    "date added":                 "date_added",
    "collection media condition": "condition",
    "media condition":            "condition",
    "collection sleeve condition":"sleeve_condition",
    "sleeve condition":           "sleeve_condition",
    "collection notes":           "notes",
    "notes":                      "notes",
}


def _normalize_row(row: Dict[str, str]) -> Dict[str, str]:
    """Lower-case, strip, and alias every key in a raw CSV row."""
    out: Dict[str, str] = {}
    for raw_k, v in row.items():
        if raw_k is None:
            continue
        k = raw_k.strip().lower().replace("﻿", "").replace("​", "")
        key = _COLUMN_ALIASES.get(k, k)
        out[key] = (v or "").strip()
    return out


# ── Format classification ─────────────────────────────────────────────────────

# Discogs vinyl sub-format strings → vinyl type's "format" field options
_VINYL_SUBFORMAT: Dict[str, str] = {
    '7"':        '7" Single',
    "7 inch":    '7" Single',
    '10"':       '10"',
    "10 inch":   '10"',
    '12"':       '12" Single',
    "12 inch":   '12" Single',
    "ep":        "EP",
    "double lp": "Double LP",
    "2xlp":      "Double LP",
    "picture disc":    "Picture Disc",
    "coloured vinyl":  "Coloured Vinyl",
    "colored vinyl":   "Coloured Vinyl",
    "box set":         "Box Set",
    "test pressing":   "Test Pressing",
    "promo":           "Promo",
    "78 rpm":          "78 RPM",
    "45 rpm":          "45 RPM",
    "33 1/3":          "33 1/3 RPM",
    "33 rpm":          "33 1/3 RPM",
}

# Format-description parts → release_type field options
_RELEASE_TYPE_MAP: Dict[str, str] = {
    "album":       "Album",
    "ep":          "EP",
    "single":      "Single",
    "compilation": "Compilation",
    "live":        "Live Album",
    "soundtrack":  "Soundtrack",
    "mixtape":     "Mixtape",
    "bootleg":     "Bootleg",
    "demo":        "Demo",
    "box set":     "Box Set",
}


def _extract_year(released: str) -> str:
    m = re.search(r'\b(1[89]\d{2}|20\d{2})\b', released or "")
    return m.group(1) if m else ""


def _release_type_from_format(parts_lower: List[str]) -> str:
    for part in parts_lower:
        rt = _RELEASE_TYPE_MAP.get(part.strip())
        if rt:
            return rt
    return ""


def _classify_format(format_raw: str) -> Tuple[str, Dict[str, str]]:
    """Return ``(bib_key, extra_fields)`` from the Discogs Format column.

    ``extra_fields`` contains type-specific pre-fills (vinyl sub-format,
    CD edition, cassette tape type, etc.) that are NOT already in the
    base item dict.
    """
    parts = [p.strip() for p in format_raw.split(",")]
    parts_lower = [p.lower() for p in parts]
    primary = parts_lower[0] if parts_lower else ""
    fmt_lower = format_raw.lower()

    release_type = _release_type_from_format(parts_lower)

    # ── Vinyl ──
    if primary == "vinyl":
        sub = "LP"  # default
        for token, val in _VINYL_SUBFORMAT.items():
            if token in fmt_lower:
                sub = val
                break
        return "vinyl", {k: v for k, v in {
            "format":       sub,
            "release_type": release_type,
        }.items() if v}

    # ── CD / CDr ──
    if primary in ("cd", "cdr"):
        edition = ""
        if "deluxe"      in fmt_lower: edition = "Deluxe Edition"
        elif "limited"   in fmt_lower: edition = "Limited Edition"
        elif "remaster"  in fmt_lower: edition = "Remaster"
        elif "anniversary" in fmt_lower: edition = "Anniversary Edition"
        elif "special"   in fmt_lower: edition = "Special Edition"
        elif "collector" in fmt_lower: edition = "Collector's Edition"
        elif "promo"     in fmt_lower: edition = "Promo"
        return "cd", {k: v for k, v in {
            "edition":      edition,
            "release_type": release_type,
        }.items() if v}

    # ── Cassette ──
    if primary == "cassette":
        tape_type = ""
        if "chrome"  in fmt_lower or "cro2"   in fmt_lower \
                or "cr02" in fmt_lower or "type ii" in fmt_lower:
            tape_type = "Type II (Chrome / CrO2)"
        elif "metal" in fmt_lower or "type iv" in fmt_lower:
            tape_type = "Type IV (Metal)"
        elif "type i" in fmt_lower or "ferric" in fmt_lower \
                or "normal" in fmt_lower:
            tape_type = "Type I (Normal / Ferric)"

        noise = ""
        if   "dolby b"  in fmt_lower: noise = "Dolby B"
        elif "dolby c"  in fmt_lower: noise = "Dolby C"
        elif "dolby s"  in fmt_lower: noise = "Dolby S"
        elif "dolby hx" in fmt_lower: noise = "Dolby HX Pro"
        elif "dbx"      in fmt_lower: noise = "dbx"

        tape_len = ""
        for code in ("c120", "c90", "c60", "c46"):
            if code in fmt_lower:
                tape_len = code.upper()
                break

        return "cassette", {k: v for k, v in {
            "tape_type":      tape_type,
            "noise_reduction": noise,
            "tape_length":    tape_len,
            "release_type":   release_type,
        }.items() if v}

    # ── Other physical formats → music type ──
    if primary == "sacd":
        return "music", {"format": "SACD",              "release_type": release_type}
    if primary == "minidisc":
        return "music", {"format": "MiniDisc",          "release_type": release_type}
    if "dvd-audio" in fmt_lower or primary in ("dvd", "dvd-audio"):
        return "music", {"format": "DVD-Audio",         "release_type": release_type}
    if "8-track" in fmt_lower or "8 track" in fmt_lower:
        return "music", {"format": "8-Track",           "release_type": release_type}
    if primary in ("file", "digital"):
        return "music", {"format": "Digital / Streaming","release_type": release_type}
    if "reel-to-reel" in fmt_lower or "reel to reel" in fmt_lower:
        return "music", {"format": "Reel-to-Reel",      "release_type": release_type}
    if "shellac" in fmt_lower or "lathe" in fmt_lower:
        return "vinyl", {"format": "LP",                "release_type": release_type}

    # Unknown — fall back to music with raw primary as format
    fallback = parts[0].strip() if parts else ""
    return "music", {k: v for k, v in {
        "format": fallback, "release_type": release_type
    }.items() if v}


# ── Row → item dict ───────────────────────────────────────────────────────────

def _row_to_item(row: Dict[str, str]) -> Dict[str, Any]:
    """Convert one raw CSV row into a uniform item dict."""
    norm = _normalize_row(row)
    bib_key, extra = _classify_format(norm.get("format_raw", ""))

    base: Dict[str, Any] = {
        "type":           bib_key,
        "title":          norm.get("title", ""),
        "artist":         norm.get("artist", ""),
        "label":          norm.get("label", ""),
        "catalog_number": norm.get("catalog_number", ""),
        "year":           _extract_year(norm.get("released", "")),
        "condition":      norm.get("condition", ""),
        "notes":          norm.get("notes", ""),
        # kept for folder→collection routing in the dialog
        "discogs_folder": norm.get("folder", ""),
        "release_id":     norm.get("release_id", ""),
    }
    base.update(extra)
    return base


def import_discogs_csv(path: str) -> List[Dict[str, Any]]:
    """Parse a Discogs collection-export CSV and return a list of item dicts."""
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as fh:
        head = fh.read(4096)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(head, delimiters=",\t;")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(fh, dialect=dialect)
        items: List[Dict[str, Any]] = []
        for row in reader:
            if not row:
                continue
            if not any((v or "").strip() for v in row.values()):
                continue
            norm = _normalize_row(row)
            if norm.get("title") or norm.get("artist"):
                items.append(_row_to_item(row))
    return items


def to_item_fields(item: Dict[str, Any]) -> Dict[str, str]:
    """Return the subset of *item* that maps directly to item-type field names."""
    skip = {"type", "discogs_folder", "release_id", "notes"}
    return {k: v for k, v in item.items()
            if k not in skip and isinstance(v, str) and v}
