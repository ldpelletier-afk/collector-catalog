"""BibTeX (.bib) import and export for Collector Catalog.

Supports standard BibTeX entry types for books/articles plus custom entry
types (@artwork, @vinyl, etc.) for collector items.

Conventions used so .bib files round-trip cleanly between this app and
other tools (Zotero / JabRef / Better-BibTeX):

    keywords = {tag1, tag2}                Zotero / JabRef compatible tags
    groups   = {Parent > Child > Leaf}     JabRef-style folder path. Multiple
                                           paths may be separated by ``;``.
    _images  = {path1; path2}              Local image attachments.

`@comment{ccatalog-meta: ...}` blocks are emitted alongside so the file
remains self-describing even outside this app.
"""

import json
import re

SCHEMA_VERSION = 1
SCHEMA_TAG = "ccatalog-schema:"


# Path / tag separators we accept on import
_PATH_SEP_RE = re.compile(r"\s*(?:>>|>|/)\s*")
_GROUP_SPLIT_RE = re.compile(r"\s*;\s*")
_TAG_SPLIT_RE = re.compile(r"\s*[,;]\s*")


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_bib_string(text):
    """Back-compat: return a list of entry dicts (no schemas)."""
    return parse_bib_string_full(text)["entries"]


def parse_bib_string_full(text):
    """Parse a .bib string. Returns:
        {
            "entries": [ {bib_key, cite_key, fields}, ... ],
            "schemas": [ <schema dict>, ... ],  # from @comment{ccatalog-schema: ...}
        }
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    entries = []
    schemas = []
    i = 0
    # Match the start of each entry: @type{ or @type(
    entry_re = re.compile(r"@(\w+)\s*[{(]", re.MULTILINE)

    while i < len(text):
        m = entry_re.search(text, i)
        if not m:
            break
        entry_type = m.group(1).lower()
        open_ch = m.group(0)[-1]

        # Walk forward to find matching closing delimiter
        depth = 1
        j = m.end()
        while j < len(text) and depth > 0:
            if text[j] == "{" or text[j] == "(":
                depth += 1
            elif text[j] == "}" or text[j] == ")":
                depth -= 1
            j += 1
        body = text[m.end(): j - 1]
        i = j

        if entry_type == "comment":
            # Look for embedded type-schema blocks
            stripped = body.strip()
            if stripped.startswith(SCHEMA_TAG):
                payload = stripped[len(SCHEMA_TAG):].strip()
                try:
                    obj = json.loads(payload)
                    schemas.append(obj)
                except Exception:
                    pass
            continue
        if entry_type in ("string", "preamble"):
            continue

        comma = body.find(",")
        if comma == -1:
            continue
        cite_key = body[:comma].strip()
        fields_text = body[comma + 1:]
        fields = _parse_fields(fields_text)

        entries.append(
            {"bib_key": entry_type, "cite_key": cite_key, "fields": fields}
        )

    return {"entries": entries, "schemas": schemas}


def _parse_fields(text):
    """Parse ``field = value`` pairs from the body of a BibTeX entry."""
    fields = {}
    pos = 0
    text = text.strip()

    while pos < len(text):
        # Skip whitespace and commas
        while pos < len(text) and text[pos] in " \t\n\r,":
            pos += 1
        if pos >= len(text):
            break

        # Field name
        nm = re.match(r"([a-zA-Z_][a-zA-Z0-9_:.-]*)\s*=\s*", text[pos:])
        if not nm:
            # Can't parse here; skip to next comma
            nxt = text.find(",", pos)
            pos = nxt + 1 if nxt != -1 else len(text)
            continue

        field_name = nm.group(1).lower()
        pos += nm.end()

        if pos >= len(text):
            break

        value, pos = _read_value(text, pos)
        fields[field_name] = _clean_braces(value)

    return fields


def _read_value(text, pos):
    """Read one BibTeX value starting at *pos*; return (value, new_pos)."""
    # Skip leading whitespace
    while pos < len(text) and text[pos] in " \t\n\r":
        pos += 1
    if pos >= len(text):
        return "", pos

    ch = text[pos]

    if ch == "{":
        depth = 0
        start = pos + 1
        for k in range(pos, len(text)):
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
                if depth == 0:
                    return text[start:k], k + 1
        return text[start:], len(text)

    elif ch == '"':
        start = pos + 1
        depth = 0
        for k in range(start, len(text)):
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
            elif text[k] == '"' and depth == 0:
                return text[start:k], k + 1
        return text[start:], len(text)

    else:
        # Bare value (number / macro)
        end = pos
        while end < len(text) and text[end] not in ",}\n":
            end += 1
        return text[pos:end].strip(), end


def _clean_braces(value):
    """Remove outer BibTeX brace groups used just for case-protection."""
    value = value.strip()
    # Collapse runs of whitespace
    value = re.sub(r"\s+", " ", value)
    return value


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_groups_field(text):
    """Parse a ``groups`` field into a list of path segment lists.

    ``"Books > Fiction; Wishlist"`` → ``[["Books", "Fiction"], ["Wishlist"]]``
    """
    if not text:
        return []
    paths = []
    for raw in _GROUP_SPLIT_RE.split(text):
        parts = [p for p in _PATH_SEP_RE.split(raw.strip()) if p]
        if parts:
            paths.append(parts)
    return paths


def parse_tags_field(text):
    """Parse a ``keywords`` / ``tags`` field into a list of tag names."""
    if not text:
        return []
    return [t.strip() for t in _TAG_SPLIT_RE.split(text) if t.strip()]


def format_groups(paths):
    """``[["Books","Fiction"], ["Wishlist"]]`` → ``"Books > Fiction; Wishlist"``."""
    return "; ".join(" > ".join(p) for p in paths if p)


# ── Exporter ──────────────────────────────────────────────────────────────────

# Field names that are reserved for catalog metadata and should never appear
# twice in an output entry.
_META_FIELDS = ("_images", "groups", "keywords", "tags")


def export_bib_string(items, type_schemas=None):
    """Return a BibTeX string for a list of item dicts.

    Each item may include:
      - bib_key, cite_key, fields (dict), images (list)
      - collection_path: list of parent→child collection names
      - tags: list of tag names

    ``type_schemas`` is an optional list of dicts (one per item type used
    in the export) of the form
        {bib_key, display_name, icon, fields: [{name, label, type, options, ...}]}
    They are written into a self-describing ``@comment{ccatalog-schema: ...}``
    block at the top of the file, so any tool that understands them can
    reconstruct the full data model exactly.  Tools that don't understand
    the block ignore it (it's a standard BibTeX comment).
    """
    parts = ["% Collector Catalog — universal collectables catalog",
             "% This .bib is self-describing: the @comment{ccatalog-schema}",
             "% block below carries the full definition of every entry",
             "% type used in this file (fields, labels, preset options).",
             "% Folders are preserved in `groups`, tags in `keywords`.",
             ""]

    if type_schemas:
        payload = {
            "version": SCHEMA_VERSION,
            "app":     "collector-catalog",
            "types":   type_schemas,
        }
        schema_json = json.dumps(payload, indent=2, ensure_ascii=False)
        parts.append("@comment{" + SCHEMA_TAG + "\n" + schema_json + "\n}\n")

    for item in items:
        bib_key = item.get("bib_key", "misc")
        cite_key = item.get("cite_key", "item")
        fields = dict(item.get("fields", {}))  # copy
        images = item.get("images", [])
        coll_path = item.get("collection_path") or []
        tags = item.get("tags") or []

        # Strip any pre-existing metadata fields we're about to set ourselves
        for k in _META_FIELDS:
            fields.pop(k, None)

        lines = [f"@{bib_key}{{{cite_key},"]
        for k, v in fields.items():
            if v is None or not str(v).strip():
                continue
            safe = _escape_value(str(v))
            lines.append(f"  {k:<20} = {{{safe}}},")

        if coll_path:
            lines.append(
                f"  {'groups':<20} = {{{format_groups([coll_path])}}},"
            )
        if tags:
            safe_tags = ", ".join(_escape_value(t) for t in tags)
            lines.append(f"  {'keywords':<20} = {{{safe_tags}}},")
        if images:
            safe_imgs = "; ".join(_escape_value(p) for p in images)
            lines.append(f"  {'_images':<20} = {{{safe_imgs}}},")
        lines.append("}\n")
        parts.append("\n".join(lines))

    return "\n".join(parts)


def _escape_value(s):
    """Make a string safe inside BibTeX ``{...}`` braces."""
    # Escape backslashes; balance stray braces by replacing them.
    s = s.replace("\\", "\\\\")
    s = s.replace("{", "(").replace("}", ")")
    return s


def import_bib_file(path):
    """Parse a .bib file and return a list of entry dicts."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return parse_bib_string(fh.read())


def export_bib_file(items, path):
    """Write items to *path* as a .bib file."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(export_bib_string(items))
