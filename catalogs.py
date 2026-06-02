"""Central registry for all built-in reference catalogs.

Each catalog module exposes:
    CATALOG      : List[dict]
    SEARCH_COLS  : [(field, label, width), ...]
    DETAIL_FIELDS: [(field, label), ...]
    search(query, **filters) -> List[dict]
    to_fields(entry) -> Dict[str, str]

This module maps item-type bib_keys to the appropriate catalog module
and provides a single entry point used by the CatalogDialog in app.py.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any, Tuple
import importlib

# bib_key -> (module_name, dialog_title, filter_field, filter_options)
# filter_field/options: an extra combobox filter shown in the dialog toolbar
# (e.g. Country filter for coins; Category filter for cameras).
# Set to (None, None) when no extra filter is needed.
REGISTRY: Dict[str, Tuple[str, str, Optional[str], Optional[List[str]]]] = {
    "coin":       ("coin_catalog",    "Coin Reference",       "country",  ["All", "United States", "Canada"]),
    "stamp":      ("stamp_catalog",   "Stamp Reference",      "country",  ["All", "United States", "Canada"]),
    "artwork":    ("artwork_catalog", "Artwork Reference",    None,       None),
    "comic":      ("comic_catalog",   "Comic Reference",      None,       None),
    "vinyl":      ("vinyl_catalog",   "Vinyl Reference",      None,       None),
    "camera":     ("camera_catalog",  "Camera Reference",     "category", ["All", "Camera", "Lens"]),
    "lens":       ("camera_catalog",  "Camera / Lens Reference","category",["All", "Camera", "Lens"]),
}


def has_catalog(bib_key: str) -> bool:
    return bib_key in REGISTRY


def get_module(bib_key: str):
    """Import and return the catalog module for *bib_key*, or None."""
    if bib_key not in REGISTRY:
        return None
    module_name = REGISTRY[bib_key][0]
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def get_dialog_title(bib_key: str) -> str:
    return REGISTRY.get(bib_key, ("", "Reference Catalog", None, None))[1]


def get_filter_spec(bib_key: str) -> Tuple[Optional[str], Optional[List[str]]]:
    """Return (filter_field_name, filter_options) or (None, None)."""
    entry = REGISTRY.get(bib_key)
    if not entry:
        return None, None
    return entry[2], entry[3]


def search(bib_key: str, query: str, filter_value: str = "All") -> List[Dict[str, Any]]:
    mod = get_module(bib_key)
    if not mod:
        return []
    field, _ = get_filter_spec(bib_key)
    if field:
        return mod.search(query, **{field: filter_value})
    return mod.search(query)


def to_fields(bib_key: str, entry: Dict[str, Any]) -> Dict[str, str]:
    mod = get_module(bib_key)
    if not mod:
        return {}
    return mod.to_fields(entry)


def get_search_cols(bib_key: str) -> List[Tuple[str, str, int]]:
    mod = get_module(bib_key)
    if mod and hasattr(mod, "SEARCH_COLS"):
        return mod.SEARCH_COLS
    return [("title", "Title", 300)]


def get_detail_fields(bib_key: str) -> List[Tuple[str, str]]:
    mod = get_module(bib_key)
    if mod and hasattr(mod, "DETAIL_FIELDS"):
        return mod.DETAIL_FIELDS
    return []
