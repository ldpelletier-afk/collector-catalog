"""Online identifier lookups — "ISBN function" and friends.

Each lookup takes an identifier (or a free-text query) and returns a dict
keyed by the *field names* used in the matching item type in
``type_defs.py``, ready to drop straight into an item.  Only fields the
service actually returns are included, so callers can choose to fill blanks
only and never clobber data the user already typed.

Services used (all reachable without a paid plan unless noted):

    • Books   — Open Library  (https://openlibrary.org)   free, no key
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


def _get_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
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


def lookup_isbn(isbn: str) -> Dict[str, str]:
    """Look up a book by ISBN-10/13 via Open Library's Books API.

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
    if not data or key not in data:
        raise LookupError(f"No book found for ISBN {isbn}.")

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
LOOKUP_CAPABLE = {
    "book":      "ISBN Lookup",
    "vinyl":     "MusicBrainz Lookup",
    "videogame": "UPC Lookup",
}
