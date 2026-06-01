"""PriceCharting integration.

PriceCharting (https://www.pricecharting.com) is the standard reference
database for video-game pricing.  Members can build a "Collection"
through the site, which can then be exported as CSV — and a paid API
gives programmatic access to the same data.

This module supports both routes:

    • import_pricecharting_csv(path)
        Parse the CSV that PriceCharting hands out from
        "My Collection → Tools → Export to CSV".

    • fetch_pricecharting_offers(token)
        Fetch a member's offers/collection live via the JSON API.
        Endpoint:  https://www.pricecharting.com/api/offers?t=<token>

Both functions return a list of dicts with a uniform shape:

    {
        "type":            "videogame" | "console",
        "title":           str,
        "console":         str,         # e.g. "Super Nintendo"
        "manufacturer":    str,         # for consoles
        "completeness":    str,         # CIB / Loose / Sealed / etc.
        "condition":       str,
        "loose_price":     str,
        "cib_price":       str,
        "new_price":       str,
        "current_value":   str,
        "purchase_price":  str,
        "purchase_date":   str,
        "pricecharting_id":  str,
        "pricecharting_url": str,
        "raw":             dict,   # the original row, for debugging
    }
"""

from __future__ import annotations

import csv
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Any


# ── Column / field normalization ──────────────────────────────────────────────

# PriceCharting has tweaked its column names over the years, so we map every
# variant we've seen onto a stable internal key.
_COLUMN_ALIASES = {
    # name
    "product-name":      "title",
    "product_name":      "title",
    "name":              "title",
    "title":             "title",
    # console / platform
    "console-name":      "console",
    "console_name":      "console",
    "console":           "console",
    "platform":          "console",
    "system":            "console",
    # IDs / urls
    "id":                "pricecharting_id",
    "product-id":        "pricecharting_id",
    "product_id":        "pricecharting_id",
    "pricecharting-id":  "pricecharting_id",
    "console-id":        "console_id",
    "url":               "pricecharting_url",
    "product-url":       "pricecharting_url",
    "upc":               "upc",
    "asin":              "asin",
    "release-date":      "year",
    "release_date":      "year",
    "genre":             "genre",
    "publisher":         "publisher",
    "developer":         "developer",
    "region":            "region",
    # condition / completeness
    "condition":         "condition",
    "completeness":      "completeness",
    "box":               "_has_box",
    "manual":            "_has_manual",
    # prices — PriceCharting reports several at once
    "loose-price":       "loose_price",
    "loose_price":       "loose_price",
    "loose price":       "loose_price",
    "cib-price":         "cib_price",
    "cib_price":         "cib_price",
    "cib price":         "cib_price",
    "complete-price":    "cib_price",
    "new-price":         "new_price",
    "new_price":         "new_price",
    "new price":         "new_price",
    "sealed-price":      "new_price",
    "graded-price":      "graded_price",
    "graded_price":      "graded_price",
    "manual-price":      "manual_price",
    "box-only-price":    "box_only_price",
    # member-specific fields
    "purchase-date":     "purchase_date",
    "purchase_date":     "purchase_date",
    "purchase-price":    "purchase_price",
    "purchase_price":    "purchase_price",
    "current-value":     "current_value",
    "current_value":     "current_value",
    "notes":             "description",
    "category":          "category",
    "quantity":          "quantity",
}

# Console keywords inside the "console-name" column — if any of these match
# AND no separate "title" is present, we treat the row as a console rather
# than a game.
_CONSOLE_CATEGORY_HINTS = (
    "console", "system", "hardware", "controller",
)


# ── CSV import ────────────────────────────────────────────────────────────────

def _normalize_row(row: Dict[str, str]) -> Dict[str, str]:
    """Lower-case keys, strip whitespace, apply column aliases."""
    out: Dict[str, str] = {}
    for raw_k, v in row.items():
        if raw_k is None:
            continue
        k = raw_k.strip().lower().replace("﻿", "")
        key = _COLUMN_ALIASES.get(k, k)
        out[key] = (v or "").strip() if isinstance(v, str) else v
    return out


def _row_to_item(row: Dict[str, str]) -> Dict[str, Any]:
    """Convert one normalized CSV row into a uniform item dict."""
    norm = _normalize_row(row)
    title = norm.get("title", "")
    console = norm.get("console", "")
    category = norm.get("category", "").lower()

    # Classify game vs console.  PriceCharting marks consoles either via a
    # category of "console" or by stuffing the console name into the title.
    is_console = False
    if category and any(h in category for h in _CONSOLE_CATEGORY_HINTS):
        is_console = True
    elif not title and console:
        # e.g. row only fills console-name → it's a piece of hardware
        is_console = True
    elif title and any(h in title.lower() for h in _CONSOLE_CATEGORY_HINTS):
        # "PlayStation 2 Slim Console", "Nintendo Switch System"
        is_console = True

    completeness = norm.get("completeness", "")
    has_box = (norm.get("_has_box", "").lower() in ("yes", "y", "true", "1"))
    has_manual = (norm.get("_has_manual", "").lower() in ("yes", "y", "true", "1"))
    if not completeness:
        if has_box and has_manual:
            completeness = "CIB (Complete in Box)"
        elif has_box and not has_manual:
            completeness = "Box + Cart"
        elif has_manual and not has_box:
            completeness = "Manual + Cart"
        elif not has_box and not has_manual:
            completeness = "Cart / Disc Only (Loose)"

    # Pick a sensible "current value" if the user hasn't supplied one.
    current_value = norm.get("current_value", "")
    if not current_value:
        if "cib" in completeness.lower() or "complete" in completeness.lower():
            current_value = norm.get("cib_price", "")
        elif "sealed" in completeness.lower() or "new" in completeness.lower():
            current_value = norm.get("new_price", "")
        else:
            current_value = norm.get("loose_price", "")

    out = {
        "type": "console" if is_console else "videogame",
        "title": title or norm.get("console", ""),
        "console": console,
        "manufacturer": "",       # filled in for consoles below
        "completeness": completeness,
        "condition": norm.get("condition", ""),
        "loose_price":     norm.get("loose_price", ""),
        "cib_price":       norm.get("cib_price", ""),
        "new_price":       norm.get("new_price", ""),
        "current_value":   current_value,
        "purchase_price":  norm.get("purchase_price", ""),
        "purchase_date":   norm.get("purchase_date", ""),
        "pricecharting_id":  str(norm.get("pricecharting_id", "")),
        "pricecharting_url": norm.get("pricecharting_url", ""),
        "year":     norm.get("year", ""),
        "genre":    norm.get("genre", ""),
        "publisher":norm.get("publisher", ""),
        "developer":norm.get("developer", ""),
        "region":   norm.get("region", ""),
        "upc":      norm.get("upc", ""),
        "description": norm.get("description", ""),
        "raw": row,
    }

    if is_console:
        # For a console row the "console" column usually carries the family
        # (e.g. "PlayStation 2") and the title carries the specific model
        # ("PS2 Slim Console").  Pull the manufacturer out heuristically.
        c = (console or title).lower()
        for vendor, keys in (
            ("Nintendo", ("nintendo", "snes", "nes", "gameboy", "game boy",
                          "switch", "wii", "gamecube", "ds")),
            ("Sony",     ("playstation", "ps1", "ps2", "ps3", "ps4", "ps5",
                          "psp", "ps vita")),
            ("Microsoft",("xbox",)),
            ("Sega",     ("sega", "genesis", "dreamcast", "saturn",
                          "game gear", "master system")),
            ("Atari",    ("atari",)),
            ("SNK",      ("neo geo", "neogeo")),
        ):
            if any(k in c for k in keys):
                out["manufacturer"] = vendor
                break

    return out


def import_pricecharting_csv(path: str) -> List[Dict[str, Any]]:
    """Parse a PriceCharting collection-export CSV into a list of item dicts.

    Tolerates both delimiter conventions PriceCharting has shipped over the
    years (comma & tab) and silently ignores header-only blank rows.
    """
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
            items.append(_row_to_item(row))
    return items


# ── API import ────────────────────────────────────────────────────────────────

_API_BASE = "https://www.pricecharting.com/api"


class PriceChartingAPIError(Exception):
    """Raised when PriceCharting's API rejects or fails the request."""


def _http_get_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "CollectorCatalog/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise PriceChartingAPIError(f"HTTP {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise PriceChartingAPIError(f"Network error: {e.reason}") from e
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise PriceChartingAPIError(f"Bad JSON from PriceCharting: {e}") from e


def fetch_pricecharting_offers(token: str) -> List[Dict[str, Any]]:
    """Fetch the member's offers/collection from the PriceCharting API.

    A PriceCharting paid-tier API token is required.  See
    https://www.pricecharting.com/api-documentation for plans.
    """
    if not token or not token.strip():
        raise PriceChartingAPIError("API token is required.")

    url = f"{_API_BASE}/offers?t={urllib.parse.quote(token.strip())}"
    payload = _http_get_json(url)

    # The API can return either an envelope ({"status":"success","offers":[...]})
    # or a bare list, depending on plan.  Be lenient.
    if isinstance(payload, dict):
        status = payload.get("status") or payload.get("Status")
        if status and str(status).lower() not in ("success", "ok"):
            msg = payload.get("error-message") or payload.get("error") or status
            raise PriceChartingAPIError(f"PriceCharting: {msg}")
        rows = (payload.get("offers")
                or payload.get("products")
                or payload.get("collection")
                or [])
    elif isinstance(payload, list):
        rows = payload
    else:
        raise PriceChartingAPIError("Unexpected payload shape from PriceCharting.")

    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        # API uses hyphen keys (e.g. product-name); _row_to_item normalizes.
        out.append(_row_to_item(r))
    return out


# ── Catalog import helpers ────────────────────────────────────────────────────

def to_catalog_fields(item: Dict[str, Any]) -> Dict[str, str]:
    """Translate the uniform PriceCharting dict into the field-name set
    used by the videogame / console item types in ``type_defs.py``."""
    if item["type"] == "console":
        return {
            "title":          item["title"],
            "manufacturer":   item["manufacturer"],
            "year":           item["year"],
            "region":         item["region"],
            "completeness":   item["completeness"],
            "condition":      item["condition"],
            "purchase_date":  item["purchase_date"],
            "purchase_price": item["purchase_price"],
            "current_value":  item["current_value"],
            "pricecharting_id": item["pricecharting_id"],
            "description":    item.get("description", ""),
        }
    return {
        "title":             item["title"],
        "console":           item["console"],
        "publisher":         item["publisher"],
        "developer":         item["developer"],
        "year":              item["year"],
        "genre":             item["genre"],
        "region":            item["region"],
        "completeness":      item["completeness"],
        "condition":         item["condition"],
        "upc":               item["upc"],
        "purchase_date":     item["purchase_date"],
        "purchase_price":    item["purchase_price"],
        "loose_price":       item["loose_price"],
        "cib_price":         item["cib_price"],
        "new_price":         item["new_price"],
        "current_value":     item["current_value"],
        "pricecharting_id":  item["pricecharting_id"],
        "pricecharting_url": item["pricecharting_url"],
        "description":       item.get("description", ""),
    }
