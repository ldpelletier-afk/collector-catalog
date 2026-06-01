"""SQLite data store for Collector Catalog."""

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / ".collector_catalog"
DB_PATH = DATA_DIR / "catalog.db"
IMAGES_DIR = DATA_DIR / "images"
SETTINGS_PATH = DATA_DIR / "settings.json"


def _ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)


# ── Lightweight key/value settings (API tokens, prefs) ────────────────────────

def get_setting(key, default=None):
    """Read a value from the JSON settings file. Returns *default* if absent."""
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh).get(key, default)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def set_setting(key, value):
    """Persist a value to the JSON settings file (merging with existing keys)."""
    _ensure_dirs()
    data = {}
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        data = {}
    data[key] = value
    with open(SETTINGS_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def get_connection():
    _ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    _ensure_dirs()
    conn = get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS item_types (
                id           INTEGER PRIMARY KEY,
                bib_key      TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                icon         TEXT DEFAULT '',
                fields_json  TEXT NOT NULL DEFAULT '[]',
                is_builtin   INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS collections (
                id         INTEGER PRIMARY KEY,
                name       TEXT NOT NULL,
                parent_id  INTEGER REFERENCES collections(id) ON DELETE SET NULL,
                color      TEXT DEFAULT '#4A90D9',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS items (
                id            INTEGER PRIMARY KEY,
                type_id       INTEGER NOT NULL REFERENCES item_types(id),
                cite_key      TEXT UNIQUE NOT NULL,
                title         TEXT DEFAULT '',
                creator       TEXT DEFAULT '',
                year          TEXT DEFAULT '',
                fields_json   TEXT NOT NULL DEFAULT '{}',
                images_json   TEXT NOT NULL DEFAULT '[]',
                collection_id INTEGER REFERENCES collections(id) ON DELETE SET NULL,
                notes         TEXT DEFAULT '',
                date_added    TEXT DEFAULT CURRENT_TIMESTAMP,
                date_modified TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tags (
                id    INTEGER PRIMARY KEY,
                name  TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#e0e0e0'
            );

            CREATE TABLE IF NOT EXISTS item_tags (
                item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                tag_id  INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
                PRIMARY KEY (item_id, tag_id)
            );

            CREATE INDEX IF NOT EXISTS idx_items_type       ON items(type_id);
            CREATE INDEX IF NOT EXISTS idx_items_collection ON items(collection_id);
            CREATE INDEX IF NOT EXISTS idx_items_title      ON items(title COLLATE NOCASE);
        """)
    conn.close()
    _seed_builtin_types()


def _seed_builtin_types():
    """Insert missing built-in types and keep existing ones in sync with code.

    Built-in types are authoritative from ``type_defs.BUILTIN_TYPES`` (the UI
    forbids editing them), so on every launch we refresh their field
    definitions / icons from code.  This lets shipped updates — new fields,
    new dropdown options, the universal Era field — reach databases that were
    created by an earlier version.  User-created (custom) types are never
    touched.
    """
    from type_defs import BUILTIN_TYPES
    conn = get_connection()
    with conn:
        for t in BUILTIN_TYPES:
            fields_json = json.dumps(t["fields"])
            row = conn.execute(
                "SELECT id, fields_json, display_name, icon, is_builtin "
                "FROM item_types WHERE bib_key = ?",
                (t["bib_key"],),
            ).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO item_types (bib_key, display_name, icon, fields_json, is_builtin) "
                    "VALUES (?,?,?,?,1)",
                    (t["bib_key"], t["display_name"], t["icon"], fields_json),
                )
            elif row["is_builtin"]:
                # Refresh definition if anything drifted from the code spec.
                if (row["fields_json"] != fields_json
                        or row["display_name"] != t["display_name"]
                        or row["icon"] != t["icon"]):
                    conn.execute(
                        "UPDATE item_types SET display_name=?, icon=?, fields_json=? "
                        "WHERE id=?",
                        (t["display_name"], t["icon"], fields_json, row["id"]),
                    )
    conn.close()


# ── Item Types ────────────────────────────────────────────────────────────────

def get_all_types():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM item_types ORDER BY is_builtin DESC, display_name"
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["fields"] = json.loads(d["fields_json"])
        result.append(d)
    return result


def get_type_by_id(type_id):
    conn = get_connection()
    r = conn.execute("SELECT * FROM item_types WHERE id=?", (type_id,)).fetchone()
    conn.close()
    if r:
        d = dict(r)
        d["fields"] = json.loads(d["fields_json"])
        return d
    return None


def get_type_by_bib_key(bib_key):
    conn = get_connection()
    r = conn.execute(
        "SELECT * FROM item_types WHERE LOWER(bib_key)=LOWER(?)", (bib_key,)
    ).fetchone()
    conn.close()
    if r:
        d = dict(r)
        d["fields"] = json.loads(d["fields_json"])
        return d
    return None


def create_type(bib_key, display_name, icon, fields):
    conn = get_connection()
    with conn:
        c = conn.execute(
            "INSERT INTO item_types (bib_key, display_name, icon, fields_json, is_builtin) "
            "VALUES (?,?,?,?,0)",
            (bib_key, display_name, icon, json.dumps(fields)),
        )
        new_id = c.lastrowid
    conn.close()
    return new_id


def update_type(type_id, display_name, icon, fields):
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE item_types SET display_name=?, icon=?, fields_json=? WHERE id=?",
            (display_name, icon, json.dumps(fields), type_id),
        )
    conn.close()


def delete_type(type_id):
    conn = get_connection()
    with conn:
        misc = conn.execute(
            "SELECT id FROM item_types WHERE bib_key='misc'"
        ).fetchone()
        if misc:
            conn.execute(
                "UPDATE items SET type_id=? WHERE type_id=?", (misc["id"], type_id)
            )
        conn.execute(
            "DELETE FROM item_types WHERE id=? AND is_builtin=0", (type_id,)
        )
    conn.close()


# ── Collections ───────────────────────────────────────────────────────────────

def get_collections():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM collections ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_collection(name, parent_id=None, color="#4A90D9"):
    conn = get_connection()
    with conn:
        c = conn.execute(
            "INSERT INTO collections (name, parent_id, color) VALUES (?,?,?)",
            (name, parent_id, color),
        )
        new_id = c.lastrowid
    conn.close()
    return new_id


def get_collection(coll_id):
    """Return one collection row as a dict, or None."""
    if not coll_id:
        return None
    conn = get_connection()
    r = conn.execute("SELECT * FROM collections WHERE id=?", (coll_id,)).fetchone()
    conn.close()
    return dict(r) if r else None


def get_or_create_collection_path(path_parts, parent_id=None):
    """Walk/create a collection hierarchy. ``path_parts`` is a list of names
    (parent-first).  Returns the id of the deepest collection.

    Existing collections at each level (matched by name + parent) are
    reused so that re-importing a .bib doesn't duplicate folders."""
    if not path_parts:
        return parent_id
    conn = get_connection()
    cur_parent = parent_id
    try:
        for name in path_parts:
            name = name.strip()
            if not name:
                continue
            if cur_parent is None:
                row = conn.execute(
                    "SELECT id FROM collections WHERE name=? AND parent_id IS NULL",
                    (name,),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT id FROM collections WHERE name=? AND parent_id=?",
                    (name, cur_parent),
                ).fetchone()
            if row:
                cur_parent = row["id"]
            else:
                with conn:
                    c = conn.execute(
                        "INSERT INTO collections (name, parent_id) VALUES (?,?)",
                        (name, cur_parent),
                    )
                    cur_parent = c.lastrowid
    finally:
        conn.close()
    return cur_parent


def get_collection_path(coll_id):
    """Return the ancestor chain (root-first) as a list of names."""
    if not coll_id:
        return []
    conn = get_connection()
    path = []
    try:
        cur = coll_id
        seen = set()
        while cur and cur not in seen:
            seen.add(cur)
            row = conn.execute(
                "SELECT name, parent_id FROM collections WHERE id=?", (cur,),
            ).fetchone()
            if not row:
                break
            path.append(row["name"])
            cur = row["parent_id"]
    finally:
        conn.close()
    return list(reversed(path))


def move_collection(coll_id, new_parent_id):
    """Reparent a collection. ``new_parent_id`` may be ``None`` (top-level).
    Rejects moves that would create a cycle.  Returns True on success.
    """
    if coll_id == new_parent_id:
        return False
    if new_parent_id is not None:
        # Walk up from new_parent_id; if we hit coll_id, refuse.
        conn = get_connection()
        try:
            cur = new_parent_id
            seen = set()
            while cur is not None and cur not in seen:
                if cur == coll_id:
                    conn.close()
                    return False
                seen.add(cur)
                row = conn.execute(
                    "SELECT parent_id FROM collections WHERE id=?", (cur,)
                ).fetchone()
                cur = row["parent_id"] if row else None
        finally:
            conn.close()
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE collections SET parent_id=? WHERE id=?",
            (new_parent_id, coll_id),
        )
    conn.close()
    return True


def update_collection(coll_id, name=None, color=None):
    conn = get_connection()
    with conn:
        if name is not None:
            conn.execute("UPDATE collections SET name=? WHERE id=?", (name, coll_id))
        if color is not None:
            conn.execute("UPDATE collections SET color=? WHERE id=?", (color, coll_id))
    conn.close()


def delete_collection(coll_id):
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE items SET collection_id=NULL WHERE collection_id=?", (coll_id,)
        )
        conn.execute(
            "UPDATE collections SET parent_id=NULL WHERE parent_id=?", (coll_id,)
        )
        conn.execute("DELETE FROM collections WHERE id=?", (coll_id,))
    conn.close()


# ── Items ─────────────────────────────────────────────────────────────────────

def _make_cite_key(title, creator, year, conn):
    creator_part = ""
    if creator:
        last = creator.split(",")[0].strip().split()[-1] if creator.strip() else ""
        creator_part = re.sub(r"[^a-zA-Z]", "", last).lower()[:12]
    title_part = ""
    if title:
        words = re.findall(r"[a-zA-Z]+", title)
        title_part = "".join(w[:4].lower() for w in words[:2])
    year_part = re.sub(r"[^0-9]", "", str(year))[:4] if year else ""
    base = (creator_part + title_part + year_part) or "item"
    key = base
    n = 1
    while conn.execute("SELECT id FROM items WHERE cite_key=?", (key,)).fetchone():
        key = f"{base}{chr(96 + n)}"
        n += 1
    return key


def get_items(collection_id=None, query=None, type_id=None, tag_id=None):
    conn = get_connection()
    sql = """
        SELECT i.*, it.display_name AS type_name, it.icon AS type_icon, it.bib_key
        FROM items i
        JOIN item_types it ON i.type_id = it.id
        WHERE 1=1
    """
    params = []
    if collection_id is not None and collection_id != -1:
        sql += " AND i.collection_id = ?"
        params.append(collection_id)
    if type_id is not None:
        sql += " AND i.type_id = ?"
        params.append(type_id)
    if tag_id is not None:
        sql += " AND i.id IN (SELECT item_id FROM item_tags WHERE tag_id=?)"
        params.append(tag_id)
    if query:
        q = f"%{query}%"
        sql += (
            " AND (i.title LIKE ? OR i.creator LIKE ? OR i.year LIKE ?"
            " OR i.cite_key LIKE ? OR i.fields_json LIKE ?)"
        )
        params.extend([q, q, q, q, q])
    sql += " ORDER BY i.title COLLATE NOCASE"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["fields"] = json.loads(d["fields_json"])
        d["images"] = json.loads(d["images_json"])
        result.append(d)
    return result


def get_item(item_id):
    conn = get_connection()
    r = conn.execute(
        """SELECT i.*, it.display_name AS type_name, it.icon AS type_icon,
                  it.bib_key, it.fields_json AS type_fields_json
           FROM items i JOIN item_types it ON i.type_id = it.id
           WHERE i.id = ?""",
        (item_id,),
    ).fetchone()
    conn.close()
    if r:
        d = dict(r)
        d["fields"] = json.loads(d["fields_json"])
        d["images"] = json.loads(d["images_json"])
        d["type_fields"] = json.loads(d["type_fields_json"])
        return d
    return None


def create_item(type_id, fields_dict, collection_id=None, notes="", images=None):
    from type_defs import get_field_attr
    t = get_type_by_id(type_id)
    if not t:
        return None
    tf = t["fields"]
    title = fields_dict.get(get_field_attr(tf, "is_title", "title"), "")
    creator = fields_dict.get(get_field_attr(tf, "is_creator", "creator"), "")
    year = fields_dict.get(get_field_attr(tf, "is_year", "year"), "")
    conn = get_connection()
    cite_key = _make_cite_key(title, creator, year, conn)
    with conn:
        c = conn.execute(
            "INSERT INTO items "
            "(type_id, cite_key, title, creator, year, fields_json, images_json, collection_id, notes) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                type_id, cite_key, title, creator, year,
                json.dumps(fields_dict),
                json.dumps(images or []),
                collection_id, notes,
            ),
        )
        new_id = c.lastrowid
    conn.close()
    return new_id


def update_item(item_id, fields_dict=None, collection_id=-2, notes=None,
                images=None, cite_key=None):
    from type_defs import get_field_attr
    item = get_item(item_id)
    if not item:
        return
    sets, vals = [], []
    if fields_dict is not None:
        tf = item["type_fields"]
        sets += ["title=?", "creator=?", "year=?", "fields_json=?"]
        vals += [
            fields_dict.get(get_field_attr(tf, "is_title", "title"), ""),
            fields_dict.get(get_field_attr(tf, "is_creator", "creator"), ""),
            fields_dict.get(get_field_attr(tf, "is_year", "year"), ""),
            json.dumps(fields_dict),
        ]
    if collection_id != -2:
        sets.append("collection_id=?")
        vals.append(None if collection_id == -1 else collection_id)
    if notes is not None:
        sets.append("notes=?")
        vals.append(notes)
    if images is not None:
        sets.append("images_json=?")
        vals.append(json.dumps(images))
    if cite_key is not None:
        sets.append("cite_key=?")
        vals.append(cite_key)
    if not sets:
        return
    sets.append("date_modified=?")
    vals.append(datetime.now().isoformat())
    vals.append(item_id)
    conn = get_connection()
    with conn:
        conn.execute(
            f"UPDATE items SET {', '.join(sets)} WHERE id=?", vals
        )
    conn.close()


def delete_items(item_ids):
    if not item_ids:
        return
    conn = get_connection()
    with conn:
        placeholders = ",".join("?" * len(item_ids))
        conn.execute(f"DELETE FROM items WHERE id IN ({placeholders})", item_ids)
    conn.close()


def duplicate_item(item_id):
    item = get_item(item_id)
    if not item:
        return None
    return create_item(
        item["type_id"],
        dict(item["fields"]),
        item["collection_id"],
        item["notes"],
        list(item["images"]),
    )


def get_item_count(collection_id=None, tag_id=None):
    conn = get_connection()
    sql = "SELECT COUNT(*) FROM items WHERE 1=1"
    params = []
    if collection_id is not None and collection_id != -1:
        sql += " AND collection_id=?"
        params.append(collection_id)
    if tag_id is not None:
        sql += " AND id IN (SELECT item_id FROM item_tags WHERE tag_id=?)"
        params.append(tag_id)
    r = conn.execute(sql, params).fetchone()
    conn.close()
    return r[0] if r else 0


# ── Tags ──────────────────────────────────────────────────────────────────────

def get_all_tags():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tags ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_or_create_tag(name):
    name = name.strip()
    conn = get_connection()
    r = conn.execute(
        "SELECT * FROM tags WHERE LOWER(name)=LOWER(?)", (name,)
    ).fetchone()
    if r:
        conn.close()
        return dict(r)
    with conn:
        c = conn.execute("INSERT INTO tags (name) VALUES (?)", (name,))
        tag_id = c.lastrowid
    r = conn.execute("SELECT * FROM tags WHERE id=?", (tag_id,)).fetchone()
    conn.close()
    return dict(r)


def delete_tag(tag_id):
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM tags WHERE id=?", (tag_id,))
    conn.close()


def get_item_tags(item_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.* FROM tags t
           JOIN item_tags it ON t.id = it.tag_id
           WHERE it.item_id=? ORDER BY t.name""",
        (item_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_item_tags(item_id, tag_names):
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM item_tags WHERE item_id=?", (item_id,))
    conn.close()
    for name in tag_names:
        if name.strip():
            add_item_tag(item_id, name.strip())


def add_item_tag(item_id, tag_name):
    tag = get_or_create_tag(tag_name)
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO item_tags (item_id, tag_id) VALUES (?,?)",
            (item_id, tag["id"]),
        )
    conn.close()


def remove_item_tag(item_id, tag_id):
    conn = get_connection()
    with conn:
        conn.execute(
            "DELETE FROM item_tags WHERE item_id=? AND tag_id=?", (item_id, tag_id)
        )
    conn.close()
