"""Collector Catalog — main application window.

Zotero-inspired three-panel layout:
  Left   – collections tree + tags
  Center – sortable item list
  Right  – item detail form (Info / Notes / Tags / Images tabs)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path

import database as db
import bib_io
from type_defs import get_field_attr

try:
    from PIL import Image, ImageTk, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def _open_oriented(path):
    """Open an image and apply its EXIF orientation so portrait photos
    (e.g. from phones) display upright instead of sideways.

    Cameras and phones often store pixels in a fixed sensor orientation and
    record the intended rotation in the EXIF Orientation tag.  PIL ignores
    that tag unless asked, which is why vertical shots came in horizontal.
    ``ImageOps.exif_transpose`` bakes the rotation into the pixels and
    removes the now-redundant tag.
    """
    img = Image.open(path)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass  # malformed/absent EXIF — fall back to the raw image
    return img


_IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"}


def migrate_image_orientations():
    """One-time pass that rewrites already-imported images upright on disk.

    Newly added images are baked upright at import time, but images added
    before that fix still carry a raw EXIF Orientation tag.  This walks the
    images directory once (guarded by a settings flag) and re-saves any file
    whose orientation tag isn't normal, so older imports become permanently
    upright too — for Finder, exports, and any external viewer.

    Returns the number of files rewritten.
    """
    if not PIL_AVAILABLE:
        return 0
    if db.get_setting("images_orientation_baked"):
        return 0

    rewritten = 0
    images_dir = db.IMAGES_DIR
    if images_dir.exists():
        for path in images_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _IMG_EXTS:
                continue
            try:
                with Image.open(path) as probe:
                    orientation = probe.getexif().get(274)  # 274 = Orientation
                    if orientation in (None, 1):
                        continue  # already upright — don't re-encode
                    fmt = probe.format
                img = _open_oriented(path)
                save_kwargs = {}
                eff_fmt = (fmt or path.suffix.lstrip(".")).upper()
                if eff_fmt in ("JPG", "JPEG"):
                    save_kwargs = {"quality": 95, "subsampling": 0}
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                img.save(str(path), **save_kwargs)
                rewritten += 1
            except Exception:
                continue  # skip unreadable/odd files; never block startup

    db.set_setting("images_orientation_baked", True)
    return rewritten

# ── Palette / fonts ───────────────────────────────────────────────────────────

C = {
    "sidebar":     "#e4e9ef",   # cool gray, distinct from main
    "main":        "#ffffff",
    "toolbar":     "#eef2f6",
    "header_row":  "#d8dee6",   # darker for clear separation
    "border":      "#a8b2bd",   # bolder
    "border_soft": "#cdd5dd",
    "sel_bg":      "#1d4ed8",   # deeper, more readable blue
    "sel_fg":      "#ffffff",
    "text":        "#0f172a",
    "subtext":     "#475569",   # darker subtext, better contrast
    "tag_pill":    "#dbeafe",
    "tag_text":    "#1e3a8a",
    "btn_bg":      "#ffffff",
    "btn_border":  "#94a3b8",
    "btn_hover":   "#dde4ec",
    "red":         "#b91c1c",
    "red_hover":   "#991b1b",
    "primary":     "#1d4ed8",
    "primary_hov": "#1e40af",
    "section_lbl": "#64748b",
    "stripe":      "#f5f7fa",
}

THUMB_SIZE = (90, 90)


def _font(size=11, bold=False, mono=False):
    if sys.platform == "darwin":
        family = "Menlo" if mono else "SF Pro Text"
    elif sys.platform == "win32":
        family = "Consolas" if mono else "Segoe UI"
    else:
        family = "Monospace" if mono else "Sans"
    weight = "bold" if bold else "normal"
    return (family, size, weight)


def setup_styles():
    """Force a cross-platform ttk theme and bind it to the palette.
    Without this, macOS aqua bleeds dark mode colors into ttk widgets."""
    s = ttk.Style()
    try:
        s.theme_use("clam")
    except tk.TclError:
        pass

    s.configure(".", background=C["main"], foreground=C["text"],
                font=_font(11), borderwidth=0)
    s.configure("TFrame",      background=C["main"])
    s.configure("TLabel",      background=C["main"], foreground=C["text"])
    s.configure("TPanedwindow", background=C["border"])
    s.configure("Sash", sashthickness=4, gripcount=0)

    # Notebook (detail tabs)
    s.configure("TNotebook", background=C["toolbar"],
                borderwidth=0, tabmargins=(2, 4, 2, 0))
    s.configure("TNotebook.Tab",
                background=C["toolbar"], foreground=C["subtext"],
                padding=(16, 7), borderwidth=0, font=_font(10, bold=True))
    s.map("TNotebook.Tab",
          background=[("selected", C["main"]), ("active", C["btn_hover"])],
          foreground=[("selected", C["primary"]), ("active", C["text"])])

    # Scrollbars
    s.configure("Vertical.TScrollbar",
                background=C["sidebar"], troughcolor=C["main"],
                borderwidth=0, arrowcolor=C["subtext"], gripcount=0)
    s.configure("Horizontal.TScrollbar",
                background=C["sidebar"], troughcolor=C["main"],
                borderwidth=0, arrowcolor=C["subtext"], gripcount=0)

    # Treeview – default + ItemList
    s.configure("Treeview",
                background=C["main"], foreground=C["text"],
                fieldbackground=C["main"], borderwidth=0,
                rowheight=26, font=_font(11))
    s.map("Treeview",
          background=[("selected", C["sel_bg"])],
          foreground=[("selected", C["sel_fg"])])
    s.configure("Treeview.Heading",
                background=C["header_row"], foreground=C["text"],
                relief="flat", borderwidth=0, font=_font(10, bold=True),
                padding=(8, 6))
    s.map("Treeview.Heading",
          background=[("active", C["header_row"])])

    # Combobox (used for fields with preset options)
    s.configure("TCombobox",
                fieldbackground=C["main"], background=C["main"],
                foreground=C["text"], arrowcolor=C["subtext"],
                bordercolor=C["btn_border"], lightcolor=C["btn_border"],
                darkcolor=C["btn_border"], borderwidth=1, padding=4)
    s.map("TCombobox",
          fieldbackground=[("readonly", C["main"]), ("disabled", C["toolbar"])],
          bordercolor=[("focus", C["sel_bg"])],
          lightcolor=[("focus", C["sel_bg"])],
          darkcolor=[("focus", C["sel_bg"])])

    # Sidebar treeview override (use the sidebar bg)
    s.configure("Sidebar.Treeview",
                background=C["sidebar"], fieldbackground=C["sidebar"],
                foreground=C["text"], borderwidth=0,
                rowheight=28, font=_font(11))
    s.map("Sidebar.Treeview",
          background=[("selected", C["sel_bg"])],
          foreground=[("selected", C["sel_fg"])])


class FlatButton(tk.Frame):
    """A genuinely flat button — macOS doesn't honour bg= on tk.Button."""

    KIND = {
        "default": dict(bg=C["btn_bg"],  fg=C["text"],   border=C["btn_border"],
                        hover=C["btn_hover"], bold=False),
        "primary": dict(bg=C["primary"], fg="#ffffff",   border=C["primary"],
                        hover=C["primary_hov"], bold=True),
        "danger":  dict(bg=C["btn_bg"],  fg=C["red"],    border=C["btn_border"],
                        hover="#fee2e2", bold=False),
        "ghost":   dict(bg=C["toolbar"], fg=C["text"],   border=None,
                        hover=C["btn_hover"], bold=False),
    }

    def __init__(self, parent, text, command=None, kind="default",
                 padx=12, pady=4, **kw):
        style = self.KIND.get(kind, self.KIND["default"])
        self._style = style
        self._cmd = command
        self._enabled = True
        bd = 1 if style["border"] else 0
        super().__init__(
            parent, bg=style["bg"], highlightthickness=bd,
            highlightbackground=style["border"] or style["bg"],
            highlightcolor=style["border"] or style["bg"], **kw,
        )
        self.lbl = tk.Label(
            self, text=text, bg=style["bg"], fg=style["fg"],
            font=_font(11, bold=style["bold"]),
            padx=padx, pady=pady, cursor="hand2",
        )
        self.lbl.pack()
        for w in (self, self.lbl):
            w.bind("<Button-1>", self._on_click)
            w.bind("<Enter>",    self._on_enter)
            w.bind("<Leave>",    self._on_leave)

    def _on_click(self, _e):
        if self._enabled and self._cmd:
            self._cmd()

    def _on_enter(self, _e):
        if self._enabled:
            self.configure(bg=self._style["hover"])
            self.lbl.configure(bg=self._style["hover"])

    def _on_leave(self, _e):
        self.configure(bg=self._style["bg"])
        self.lbl.configure(bg=self._style["bg"])

    def set_enabled(self, enabled):
        self._enabled = bool(enabled)
        if enabled:
            self.lbl.configure(fg=self._style["fg"], cursor="hand2")
        else:
            self.lbl.configure(fg=C["section_lbl"], cursor="arrow")

    def configure_text(self, text):
        self.lbl.configure(text=text)


# ── Scrollable frame helper ───────────────────────────────────────────────────

def _route_scroll(e):
    """Route a mousewheel/trackpad event to the nearest ScrollFrame ancestor."""
    w = e.widget
    while w is not None:
        if isinstance(w, ScrollFrame):
            if getattr(e, "num", None) == 4:
                step = -1
            elif getattr(e, "num", None) == 5:
                step = 1
            else:
                d = e.delta
                # macOS trackpads report small per-line deltas (±1..±10);
                # Windows wheels report multiples of 120.
                if abs(d) >= 120:
                    d = d / 120
                step = -1 if d > 0 else 1
                step *= max(1, min(4, int(abs(d))))
            w.canvas.yview_scroll(step, "units")
            return "break"
        w = getattr(w, "master", None)


class ScrollFrame(ttk.Frame):
    """A ttk.Frame with a vertical scrollbar; put children in self.inner."""

    def __init__(self, parent, bg=None, **kw):
        super().__init__(parent, **kw)
        self._bg = bg or C["main"]
        self.canvas = tk.Canvas(
            self, highlightthickness=0, bg=self._bg, borderwidth=0
        )
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.inner = tk.Frame(self.canvas, bg=self._bg)
        self._win_id = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        # All instances register the same global handler so later creations
        # don't silently overwrite earlier ones via bind_all replacement.
        self.canvas.bind_all("<MouseWheel>", _route_scroll)
        self.canvas.bind_all("<Button-4>",   _route_scroll)
        self.canvas.bind_all("<Button-5>",   _route_scroll)

    def _on_inner_configure(self, _e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.canvas.itemconfig(self._win_id, width=e.width)

    def scroll_to_top(self):
        self.canvas.yview_moveto(0)


# ── Sidebar ───────────────────────────────────────────────────────────────────

class Sidebar(tk.Frame):
    """Left panel: My Library, collections tree, tags."""

    LIBRARY_ID = "__library__"
    TAG_PREFIX  = "__tag__"

    def __init__(self, parent, app, **kw):
        super().__init__(parent, bg=C["sidebar"], **kw)
        self.app = app
        self._build()

    def _build(self):
        # ── Collections section ──────────────────────────────────────────────
        hdr = tk.Frame(self, bg=C["sidebar"])
        hdr.pack(fill="x", padx=10, pady=(12, 4))
        tk.Label(
            hdr, text="LIBRARIES", bg=C["sidebar"],
            fg=C["section_lbl"], font=_font(9, bold=True),
        ).pack(side="left")
        # Right-aligned, right-most button shown last (pack side=right reverses).
        FlatButton(
            hdr, "Delete", command=self._delete_selected_library, kind="ghost",
            padx=8, pady=1,
        ).pack(side="right")
        FlatButton(
            hdr, "+ Folder", command=self._new_subfolder, kind="ghost",
            padx=8, pady=1,
        ).pack(side="right", padx=(0, 4))
        FlatButton(
            hdr, "+ Library", command=self._new_library, kind="ghost",
            padx=8, pady=1,
        ).pack(side="right", padx=(0, 4))

        tree_wrap = tk.Frame(self, bg=C["sidebar"])
        tree_wrap.pack(fill="both", expand=True, padx=6)
        self.tree = ttk.Treeview(
            tree_wrap, selectmode="browse", show="tree",
            style="Sidebar.Treeview",
        )
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("drop_target", background=C["tag_pill"])

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Button-3>", self._on_right_click)
        self.tree.bind("<Double-1>", self._on_double_click)
        # Delete key removes the selected library/folder.
        self.tree.bind("<Delete>",    self._on_delete_key)
        self.tree.bind("<BackSpace>", self._on_delete_key)
        # Drag-and-drop to reorganize the library tree
        self._drag_src = None
        self._drag_started = False
        self._drag_press_xy = (0, 0)
        self._drop_target = None
        self.tree.bind("<ButtonPress-1>",   self._on_drag_press)
        self.tree.bind("<B1-Motion>",       self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_release)

        # ── Tags section ─────────────────────────────────────────────────────
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", pady=4)
        hdr2 = tk.Frame(self, bg=C["sidebar"])
        hdr2.pack(fill="x", padx=8, pady=(0, 2))
        tk.Label(
            hdr2, text="TAGS", bg=C["sidebar"],
            fg=C["section_lbl"], font=_font(9, bold=True),
        ).pack(side="left")

        self.tag_list = tk.Listbox(
            self, bg=C["sidebar"], fg=C["text"], relief="flat", borderwidth=0,
            selectbackground=C["sel_bg"], selectforeground=C["sel_fg"],
            font=_font(11), highlightthickness=0, height=6,
        )
        self.tag_list.pack(fill="x", padx=10, pady=(0, 10))
        self.tag_list.bind("<<ListboxSelect>>", self._on_tag_select)

    def refresh(self):
        # Remember what was selected so a rebuild doesn't bounce the user back
        # to "My Library".  Tags clear the tree selection on purpose, so an
        # empty selection while a tag filter is active is preserved too.
        prev = self.tree.selection()
        prev_iid = prev[0] if prev else None
        tag_active = getattr(self.app, "_current_tag", None) is not None

        self.tree.delete(*self.tree.get_children())
        # "My Library" is the implicit catch-all: shows every item across
        # every library.  Always present.
        count = db.get_item_count()
        self.tree.insert(
            "", "end", iid=self.LIBRARY_ID,
            text=f"  My Library  ({count})", open=True,
        )
        collections = db.get_collections()
        coll_map = {c["id"]: c for c in collections}
        inserted = set()

        def insert_coll(c):
            if c["id"] in inserted:
                return
            # My Library is the umbrella: everything nests under it.  Depth is
            # conveyed by the tree's own indentation rather than an icon.
            if not c["parent_id"]:
                parent_iid = self.LIBRARY_ID
            else:
                if c["parent_id"] in coll_map:
                    insert_coll(coll_map[c["parent_id"]])
                parent_iid = f"coll_{c['parent_id']}"
            n = db.get_item_count(collection_id=c["id"])
            self.tree.insert(
                parent_iid, "end", iid=f"coll_{c['id']}",
                text=f"  {c['name']}  ({n})", open=True,
            )
            inserted.add(c["id"])

        for c in collections:
            insert_coll(c)

        # Restore the prior selection if it still exists; only fall back to
        # "My Library" on first build (no prior selection and no active tag).
        if prev_iid and self.tree.exists(prev_iid):
            self.tree.selection_set(prev_iid)
        elif not prev_iid and not tag_active:
            self.tree.selection_set(self.LIBRARY_ID)

        # Tags
        self.tag_list.delete(0, "end")
        for t in db.get_all_tags():
            n = db.get_item_count(tag_id=t["id"])
            self.tag_list.insert("end", f"  {t['name']}  ({n})")
        self._tags = db.get_all_tags()

    def _selected_collection_id(self):
        sel = self.tree.selection()
        if not sel:
            return -1
        iid = sel[0]
        if iid == self.LIBRARY_ID:
            return -1
        if iid.startswith("coll_"):
            return int(iid[5:])
        return -1

    def _on_select(self, _e):
        # An empty selection means the tree was cleared programmatically — e.g.
        # the user just picked a tag, which deselects the tree on purpose.
        # Don't reload by collection here or we'd clobber the tag filter.
        if not self.tree.selection():
            return
        self.tag_list.selection_clear(0, "end")
        cid = self._selected_collection_id()
        # Ignore a re-selection of the collection that's already on screen.
        # Rebuilding the tree (e.g. after adding an item) re-fires this event
        # for the same node; reloading the list there would drop the user's
        # current item selection.  A genuine navigation always changes either
        # the collection or clears an active tag, so this only skips no-ops.
        if (cid == getattr(self.app, "_current_collection", None)
                and getattr(self.app, "_current_tag", None) is None):
            return
        self.app.load_items(collection_id=cid, tag_id=None)

    def _on_tag_select(self, _e):
        self.tree.selection_remove(self.tree.selection())
        idx = self.tag_list.curselection()
        if not idx or not hasattr(self, "_tags"):
            return
        tag = self._tags[idx[0]]
        self.app.load_items(collection_id=None, tag_id=tag["id"])

    def _on_right_click(self, e):
        iid = self.tree.identify_row(e.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        menu = tk.Menu(self, tearoff=0)
        if iid == self.LIBRARY_ID:
            menu.add_command(label="New Library",
                             command=self._new_library)
        else:
            cid = int(iid[5:])
            menu.add_command(label="New Library (top-level)",
                             command=self._new_library)
            menu.add_command(label="New Folder Inside",
                             command=lambda: self._new_collection(parent_id=cid))
            menu.add_separator()
            menu.add_command(label="Rename",
                             command=lambda: self._rename_collection(cid))
            menu.add_command(label="Delete",
                             command=lambda: self._delete_collection(cid))
        menu.tk_popup(e.x_root, e.y_root)

    def _on_double_click(self, e):
        iid = self.tree.identify_row(e.y)
        if iid and iid.startswith("coll_"):
            self._rename_collection(int(iid[5:]))

    # ── Drag-and-drop reorganization ─────────────────────────────────────────
    DRAG_THRESHOLD = 6  # pixels before a click becomes a drag

    def _on_drag_press(self, e):
        iid = self.tree.identify_row(e.y)
        # Only collections are draggable — "My Library" and tags can't be moved.
        if iid and iid.startswith("coll_"):
            self._drag_src = iid
        else:
            self._drag_src = None
        self._drag_started = False
        self._drag_press_xy = (e.x, e.y)
        self._clear_drop_target()

    def _on_drag_motion(self, e):
        if not self._drag_src:
            return
        if not self._drag_started:
            dx = abs(e.x - self._drag_press_xy[0])
            dy = abs(e.y - self._drag_press_xy[1])
            if dx + dy < self.DRAG_THRESHOLD:
                return
            self._drag_started = True
            self.tree.configure(cursor="hand2")

        target = self.tree.identify_row(e.y)
        # Don't show a drop indicator on yourself.
        if target == self._drag_src:
            target = None
        self._set_drop_target(target)

    def _on_drag_release(self, e):
        try:
            if not self._drag_started or not self._drag_src:
                return  # treat as a normal click — selection handler runs

            src_id = int(self._drag_src[5:])
            tgt = self._drop_target

            # Resolve drop target → new parent id
            if tgt is None or tgt == self.LIBRARY_ID:
                new_parent = None  # become a top-level library
            elif tgt.startswith("coll_"):
                tgt_id = int(tgt[5:])
                if tgt_id == src_id:
                    return
                new_parent = tgt_id
            else:
                return

            ok = db.move_collection(src_id, new_parent)
            if not ok:
                messagebox.showinfo(
                    "Can't move there",
                    "A library can't be made a child of itself or one of its own folders.",
                    parent=self,
                )
                return
            self.refresh()
            # Re-select the moved item so the user keeps context
            new_iid = f"coll_{src_id}"
            if self.tree.exists(new_iid):
                self.tree.selection_set(new_iid)
                self.tree.see(new_iid)
        finally:
            self._clear_drop_target()
            self._drag_src = None
            self._drag_started = False
            self.tree.configure(cursor="")

    def _set_drop_target(self, iid):
        if iid == self._drop_target:
            return
        self._clear_drop_target()
        if iid:
            current_tags = list(self.tree.item(iid, "tags") or ())
            if "drop_target" not in current_tags:
                self.tree.item(iid, tags=current_tags + ["drop_target"])
            self._drop_target = iid

    def _clear_drop_target(self):
        if not self._drop_target:
            return
        if self.tree.exists(self._drop_target):
            tags = [t for t in (self.tree.item(self._drop_target, "tags") or ())
                    if t != "drop_target"]
            self.tree.item(self._drop_target, tags=tags)
        self._drop_target = None

    def _new_collection(self, parent_id=None):
        """Generic — kept for the app menu / external callers."""
        prompt = "Folder name:" if parent_id else "Library name:"
        title  = "New Folder"   if parent_id else "New Library"
        name = simpledialog.askstring(title, prompt, parent=self)
        if name and name.strip():
            db.create_collection(name.strip(), parent_id=parent_id)
            self.refresh()

    def _new_library(self):
        """Create a new library as a sibling of the currently selected node.

        - Nothing selected, or 'My Library' selected → new top-level library.
        - A library/folder selected → new library is created next to it,
          sharing the same parent.  This matches how most file managers
          treat ``New …`` actions.
        """
        cid = self._selected_collection_id()
        parent_id = None
        if cid != -1:
            coll = db.get_collection(cid)
            if coll:
                parent_id = coll.get("parent_id")
        self._new_collection(parent_id=parent_id)

    def _new_subfolder(self):
        """Create a folder under the currently-selected library or folder.

        If 'My Library' (or nothing) is selected there's no real parent —
        fall through to creating a new top-level library instead, so the
        button never feels broken."""
        cid = self._selected_collection_id()
        if cid == -1:
            self._new_library()
        else:
            self._new_collection(parent_id=cid)

    def _rename_collection(self, cid):
        colls = {c["id"]: c for c in db.get_collections()}
        old = colls.get(cid, {}).get("name", "")
        name = simpledialog.askstring(
            "Rename Collection", "New name:", initialvalue=old, parent=self
        )
        if name and name.strip():
            db.update_collection(cid, name=name.strip())
            self.refresh()

    def _on_delete_key(self, _event=None):
        """Delete the currently selected library/folder via keyboard."""
        self._delete_selected_library()
        return "break"

    def _delete_selected_library(self):
        cid = self._selected_collection_id()
        if cid == -1:
            messagebox.showinfo(
                "Delete Library",
                "Select a library or folder in the sidebar first. "
                "'My Library' is the umbrella container and can't be removed.",
                parent=self,
            )
            return
        self._delete_collection(cid)

    def _delete_collection(self, cid):
        if messagebox.askyesno(
            "Delete Collection",
            "Delete this collection? Items will remain in the library.",
            parent=self,
        ):
            db.delete_collection(cid)
            self.refresh()
            self.app.load_items(collection_id=-1, tag_id=None)

    def get_current_collection_id(self):
        return self._selected_collection_id()


# ── Item List ─────────────────────────────────────────────────────────────────

class ItemList(tk.Frame):
    """Center panel: sortable table of items."""

    COLS = [
        ("title",   "Title",   300),
        ("creator", "Creator", 160),
        ("year",    "Year",     60),
        ("type",    "Type",    100),
    ]

    def __init__(self, parent, app, **kw):
        super().__init__(parent, bg=C["main"], **kw)
        self.app = app
        self._sort_col = "title"
        self._sort_asc = True
        self._items = []
        self._build()

    def _build(self):
        col_ids = [c[0] for c in self.COLS]
        self.tree = ttk.Treeview(
            self, columns=col_ids, show="headings",
            selectmode="extended", style="Items.Treeview",
        )
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for cid, label, width in self.COLS:
            self.tree.heading(
                cid, text=label,
                command=lambda c=cid: self._sort_by(c),
            )
            self.tree.column(cid, width=width, minwidth=50, stretch=(cid == "title"))

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tree.tag_configure("odd",  background=C["stripe"])
        self.tree.tag_configure("even", background=C["main"])

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Button-3>", self._on_right_click)
        self.tree.bind("<Delete>",   lambda _e: self.app.delete_selected())
        self.tree.bind("<BackSpace>", lambda _e: self.app.delete_selected())

        s = ttk.Style()
        s.configure("Items.Treeview",
                    background=C["main"], fieldbackground=C["main"],
                    foreground=C["text"], rowheight=26, font=_font(11),
                    borderwidth=0)
        s.map("Items.Treeview",
              background=[("selected", C["sel_bg"])],
              foreground=[("selected", C["sel_fg"])])

    def load(self, items):
        self._items = items
        self._render()

    def _render(self):
        self.tree.delete(*self.tree.get_children())
        items = list(self._items)
        rev = not self._sort_asc
        if self._sort_col == "title":
            items.sort(key=lambda x: x["title"].lower(), reverse=rev)
        elif self._sort_col == "creator":
            items.sort(key=lambda x: x["creator"].lower(), reverse=rev)
        elif self._sort_col == "year":
            items.sort(key=lambda x: x["year"] or "", reverse=rev)
        elif self._sort_col == "type":
            items.sort(key=lambda x: x["type_name"].lower(), reverse=rev)

        for i, item in enumerate(items):
            tag = "even" if i % 2 == 0 else "odd"
            type_label = item["type_name"]
            self.tree.insert(
                "", "end",
                iid=str(item["id"]),
                values=(
                    item["title"] or "(no title)",
                    item["creator"],
                    item["year"],
                    type_label,
                ),
                tags=(tag,),
            )

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        # Update heading arrows
        for cid, label, _ in self.COLS:
            arrow = ""
            if cid == self._sort_col:
                arrow = "  ↑" if self._sort_asc else "  ↓"
            self.tree.heading(cid, text=label + arrow)
        self._render()

    def _on_select(self, _e):
        ids = self.get_selected_ids()
        if ids:
            self.app.on_item_selected(ids[-1])
        else:
            self.app.on_item_selected(None)

    def _on_right_click(self, e):
        iid = self.tree.identify_row(e.y)
        if not iid:
            return
        if iid not in self.tree.selection():
            self.tree.selection_set(iid)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Duplicate",
                         command=lambda: self.app.duplicate_selected())
        menu.add_separator()
        # Move to collection sub-menu
        colls = db.get_collections()
        if colls:
            sub = tk.Menu(menu, tearoff=0)
            sub.add_command(label="(No Collection)",
                            command=lambda: self.app.move_to_collection(None))
            for c in colls:
                sub.add_command(
                    label=c["name"],
                    command=lambda cid=c["id"]: self.app.move_to_collection(cid),
                )
            menu.add_cascade(label="Move to Collection", menu=sub)
        menu.add_separator()
        menu.add_command(label="Delete", command=self.app.delete_selected)
        menu.tk_popup(e.x_root, e.y_root)

    def get_selected_ids(self):
        return [int(iid) for iid in self.tree.selection()]

    def select_item(self, item_id):
        iid = str(item_id)
        if self.tree.exists(iid):
            self.tree.selection_set(iid)
            self.tree.see(iid)

    def refresh_row(self, item):
        iid = str(item["id"])
        if self.tree.exists(iid):
            type_label = item["type_name"]
            self.tree.item(
                iid,
                values=(
                    item["title"] or "(no title)",
                    item["creator"],
                    item["year"],
                    type_label,
                ),
            )


# ── Detail Panel ──────────────────────────────────────────────────────────────

class DetailPanel(tk.Frame):
    """Right panel: tabbed item detail form."""

    def __init__(self, parent, app, **kw):
        super().__init__(parent, bg=C["main"], **kw)
        self.app = app
        self._item_id = None
        self._field_vars = {}        # field_name → StringVar / Text widget
        self._image_paths = []
        self._thumb_refs = []        # keep PIL refs alive
        self._dirty = False
        # Reference suggestion panel state
        self._sugg_tree    = None
        self._sugg_entries = []
        self._sugg_bib_key = None
        self._sugg_after   = None   # pending debounce after-id
        self._auto_fill_after       = None
        self._auto_fill_bib_key     = None
        self._auto_fill_title_field = "title"
        self._suppress_auto_fill    = False
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        # Header row
        self._header = tk.Frame(self, bg=C["toolbar"], relief="flat")
        self._header.pack(fill="x")
        tk.Frame(self._header, bg=C["border"], height=1).pack(fill="x", side="bottom")

        self._lbl_type = tk.Label(
            self._header, text="", bg=C["toolbar"], fg=C["subtext"], font=_font(10),
        )
        self._lbl_type.pack(side="left", padx=(12, 4), pady=6)

        self._lbl_key = tk.Label(
            self._header, text="", bg=C["toolbar"], fg=C["text"],
            font=_font(10, mono=True),
        )
        self._lbl_key.pack(side="left", padx=0, pady=6)

        self._btn_save = FlatButton(
            self._header, "Save Changes", command=self._save, kind="primary",
            padx=10, pady=2,
        )
        self._btn_save.pack(side="right", padx=10, pady=6)
        self._btn_save.set_enabled(False)

        # Web auto-fill button — only shown for lookup-capable types
        # (book → ISBN, vinyl → MusicBrainz, video game → UPC).
        self._btn_lookup = FlatButton(
            self._header, "Lookup", command=self._do_lookup,
            kind="default", padx=10, pady=2,
        )
        self._lookup_bib_key = None  # set per-item in load_item()

        # Reference catalog button — shown for any type that has a catalog
        self._btn_catalog = FlatButton(
            self._header, "Reference Catalog", command=self._open_catalog,
            kind="default", padx=10, pady=2,
        )

        # Import Artist button — shown for music / cd / cassette types
        self._btn_import_artist = FlatButton(
            self._header, "Import Artist", command=self._import_artist,
            kind="default", padx=10, pady=2,
        )

        # Edit Sections button — always available when an item is loaded
        self._btn_edit_sections = FlatButton(
            self._header, "Edit Sections", command=self._edit_sections,
            kind="default", padx=10, pady=2,
        )

        # Notebook container — give it an explicit white bg so the ttk
        # client area never shows through dark.
        nb_frame = tk.Frame(self, bg=C["main"])
        nb_frame.pack(fill="both", expand=True)

        self._nb = ttk.Notebook(nb_frame)
        self._nb.pack(fill="both", expand=True, padx=1, pady=1)

        self._info_sf  = ScrollFrame(self._nb, bg=C["main"])
        self._notes_f  = tk.Frame(self._nb, bg=C["main"])
        self._tags_f   = tk.Frame(self._nb, bg=C["main"])
        self._images_f = ScrollFrame(self._nb, bg=C["main"])

        self._nb.add(self._info_sf,  text="  Info  ")
        self._nb.add(self._notes_f,  text="  Notes  ")
        self._nb.add(self._tags_f,   text="  Tags  ")
        self._nb.add(self._images_f, text="  Images  ")

        self._build_notes_tab()
        self._build_tags_tab()
        self._build_images_tab()

    # ── Info tab ──────────────────────────────────────────────────────────────

    def _build_info_fields(self, type_fields, type_id=None, bib_key=None):
        inner = self._info_sf.inner
        for w in inner.winfo_children():
            w.destroy()
        self._field_vars.clear()
        self._first_field_widget = None   # first editable input, for focus
        self._current_type_id = type_id

        # Apply custom section layout from settings if one exists
        layout = db.get_section_layout(bib_key) if bib_key else None
        if layout:
            field_by_name = {f["name"]: f for f in type_fields if f.get("name")}
            new_fields = []
            seen: set = set()
            for entry in layout:
                if isinstance(entry, dict) and "section" in entry:
                    new_fields.append({"type": "section", "label": entry["section"]})
                elif isinstance(entry, str) and entry in field_by_name:
                    new_fields.append(field_by_name[entry])
                    seen.add(entry)
            # Append any fields not mentioned in the layout (no orphans)
            for f in type_fields:
                if f.get("name") and f["name"] not in seen:
                    new_fields.append(f)
            type_fields = new_fields

        # Pre-load catalog values for every field so each Combobox is pre-populated
        import catalogs as _cat
        catalog_vals: dict = {}
        if bib_key and _cat.has_catalog(bib_key):
            for f in type_fields:
                if f.get("type") not in ("multiline", "section"):
                    vals = _cat.get_field_values(bib_key, f["name"])
                    if vals:
                        catalog_vals[f["name"]] = vals

        inner.grid_columnconfigure(1, weight=1)

        row = 0
        # Cite key row
        tk.Label(
            inner, text="Cite Key", bg=C["main"], fg=C["subtext"],
            font=_font(10), anchor="e", width=14,
        ).grid(row=row, column=0, sticky="e", padx=(12, 6), pady=3)
        self._cite_key_var = tk.StringVar()
        ck_entry = tk.Entry(
            inner, textvariable=self._cite_key_var,
            bg=C["main"], fg=C["text"], relief="flat", bd=0, font=_font(10, mono=True),
            highlightthickness=1, highlightbackground=C["btn_border"],
            highlightcolor=C["sel_bg"],
        )
        ck_entry.grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=3)
        self._cite_key_var.trace_add("write", lambda *_: self._mark_dirty())
        row += 1

        # Separator
        tk.Frame(inner, bg=C["border"], height=1).grid(
            row=row, column=0, columnspan=2, sticky="ew",
            padx=12, pady=(2, 6)
        )
        row += 1

        for field in type_fields:
            if field.get("type") == "section":
                hdr = tk.Frame(inner, bg=C["main"])
                hdr.grid(row=row, column=0, columnspan=2, sticky="ew",
                         padx=12, pady=(10, 0))
                tk.Frame(hdr, bg=C["border"], height=1).pack(fill="x", side="top", pady=(0, 3))
                tk.Label(
                    hdr, text=field["label"].upper(),
                    bg=C["main"], fg=C["section_lbl"], font=_font(9, bold=True), anchor="w",
                ).pack(side="left")
                row += 1
                continue

            lbl = tk.Label(
                inner, text=field["label"], bg=C["main"], fg=C["text"],
                font=_font(10, bold=True), anchor="e", width=14,
            )
            lbl.grid(row=row, column=0, sticky="ne" if field["type"] == "multiline" else "e",
                     padx=(12, 6), pady=3)

            if field["type"] == "multiline":
                txt = tk.Text(
                    inner, height=4, wrap="word",
                    bg=C["main"], fg=C["text"], relief="flat",
                    bd=0, font=_font(10), highlightbackground=C["btn_border"],
                    highlightthickness=1, highlightcolor=C["sel_bg"],
                )
                txt.grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=3)
                txt.bind("<<Modified>>", lambda e, w=txt: self._on_text_modified(w))
                for _ev in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                    txt.bind(_ev, _route_scroll)
                self._field_vars[field["name"]] = txt
                if self._first_field_widget is None:
                    self._first_field_widget = txt
            else:
                var = tk.StringVar()
                # 1. Preset options from type definition
                preset = list(field.get("options") or [])
                # 2. Values the user has already entered (learned)
                learned = (db.get_field_values(type_id, field["name"])
                           if type_id else [])
                # 3. Catalog reference values for this field
                cat_vals = catalog_vals.get(field["name"], [])
                # Merge, preserving order: presets → learned → catalog (no dupes)
                seen_lower: set = set()
                combined: list = []
                for v in preset + learned + cat_vals:
                    key = v.lower()
                    if key not in seen_lower:
                        seen_lower.add(key)
                        combined.append(v)

                widget = ttk.Combobox(
                    inner, textvariable=var, values=combined,
                    font=_font(11), state="normal",
                )
                widget.grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=3)
                var.trace_add("write", lambda *_: self._mark_dirty())
                self._field_vars[field["name"]] = var
                if self._first_field_widget is None:
                    self._first_field_widget = widget
            row += 1

        self._info_sf.scroll_to_top()

        # Wire up catalog auto-fill on the title field for types that have a catalog
        import catalogs as _cat
        self._auto_fill_bib_key = bib_key if (bib_key and _cat.has_catalog(bib_key)) else None
        self._auto_fill_title_field = get_field_attr(type_fields, "is_title", "title")
        title_var = self._field_vars.get(self._auto_fill_title_field)
        if self._auto_fill_bib_key and isinstance(title_var, tk.StringVar):
            title_var.trace_add("write", lambda *_: self._schedule_auto_fill())

    def focus_first_field(self):
        """Put the cursor in the first editable field, ready for typing.

        Used right after a new item is created so the user can start filling
        in details immediately, the way other cataloguing apps behave.
        """
        w = getattr(self, "_first_field_widget", None)
        if w is not None:
            try:
                self._nb.select(self._info_sf)   # ensure the Info tab is shown
                w.focus_set()
            except Exception:
                pass

    def _on_text_modified(self, widget):
        if widget.edit_modified():
            self._mark_dirty()
            widget.edit_modified(False)

    # ── Reference suggestions ──────────────────────────────────────────────────

    def _schedule_suggestion_update(self):
        """Debounce: run _update_suggestions 180ms after the last keystroke."""
        if self._sugg_tree is None:
            return
        if self._sugg_after:
            try:
                self.after_cancel(self._sugg_after)
            except Exception:
                pass
        self._sugg_after = self.after(180, self._update_suggestions)

    def _update_suggestions(self):
        """Refresh the suggestion panel based on current field values."""
        if self._sugg_tree is None or not self._sugg_bib_key:
            return
        import catalogs as _cat

        # Build a query from whatever the user has typed so far
        parts = []
        for name, widget in self._field_vars.items():
            v = (widget.get("1.0", "end") if isinstance(widget, tk.Text)
                 else widget.get()).strip()
            if v:
                parts.append(v)
        query = " ".join(parts[:2])   # first two non-empty fields

        results = _cat.search(self._sugg_bib_key, query)[:10]
        self._sugg_entries = results

        self._sugg_tree.delete(*self._sugg_tree.get_children())
        col_ids = [c[0] for c in _cat.get_search_cols(self._sugg_bib_key)]
        for i, e in enumerate(results):
            tag = "even" if i % 2 == 0 else "odd"
            self._sugg_tree.insert(
                "", "end", iid=str(i),
                values=tuple(str(e.get(c, "")) for c in col_ids),
                tags=(tag,),
            )
        n = len(results)
        if hasattr(self, "_sugg_count_lbl"):
            self._sugg_count_lbl.configure(
                text=f"Reference Suggestions  ({n} match{'es' if n != 1 else ''})"
            )

    def _use_suggestion(self):
        """Fill form fields from the selected suggestion row."""
        if self._sugg_tree is None or not self._sugg_entries:
            return
        sel = self._sugg_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if not (0 <= idx < len(self._sugg_entries)):
            return
        import catalogs as _cat
        fields = _cat.to_fields(self._sugg_bib_key, self._sugg_entries[idx])
        for k, v in fields.items():
            if k in self._field_vars:
                self._set_field_value(k, v)
        self._mark_dirty()

    # ── Catalog auto-fill (title → physical fields) ───────────────────────────

    def _schedule_auto_fill(self):
        if self._suppress_auto_fill or not self._auto_fill_bib_key:
            return
        if self._auto_fill_after:
            try:
                self.after_cancel(self._auto_fill_after)
            except Exception:
                pass
        self._auto_fill_after = self.after(600, self._do_auto_fill)

    def _do_auto_fill(self):
        self._auto_fill_after = None
        bib_key = self._auto_fill_bib_key
        if not bib_key:
            return
        import catalogs as _cat
        title_val = self._field_value(self._auto_fill_title_field).strip()
        if len(title_val) < 3:
            return
        results = _cat.search(bib_key, title_val)
        exact = [e for e in results
                 if e.get("title", "").strip().lower() == title_val.lower()]
        if len(exact) != 1:
            return
        fields = _cat.to_fields(bib_key, exact[0])
        changed = False
        for k, v in fields.items():
            if k == self._auto_fill_title_field:
                continue
            if v and not self._field_value(k):
                self._suppress_auto_fill = True
                self._set_field_value(k, v)
                self._suppress_auto_fill = False
                changed = True
        if changed:
            self._mark_dirty()

    # ── Notes tab ─────────────────────────────────────────────────────────────

    def _build_notes_tab(self):
        f = self._notes_f
        tk.Label(f, text="Notes", bg=C["main"], fg=C["subtext"],
                 font=_font(10)).pack(anchor="w", padx=12, pady=(10, 4))
        self._notes_txt = tk.Text(
            f, wrap="word", bg=C["main"], fg=C["text"],
            relief="solid", bd=1, font=_font(11), padx=8, pady=8,
            highlightthickness=1, highlightcolor=C["sel_bg"],
        )
        self._notes_txt.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._notes_txt.bind("<<Modified>>", self._on_notes_modified)

    def _on_notes_modified(self, _e):
        if self._notes_txt.edit_modified():
            self._mark_dirty()
            self._notes_txt.edit_modified(False)

    # ── Tags tab ──────────────────────────────────────────────────────────────

    def _build_tags_tab(self):
        f = self._tags_f
        f.grid_columnconfigure(0, weight=1)
        tk.Label(f, text="Tags", bg=C["main"], fg=C["subtext"],
                 font=_font(10)).pack(anchor="w", padx=12, pady=(10, 4))

        self._tags_container = tk.Frame(f, bg=C["main"])
        self._tags_container.pack(fill="x", padx=12)

        add_row = tk.Frame(f, bg=C["main"])
        add_row.pack(fill="x", padx=12, pady=8)
        self._tag_entry_var = tk.StringVar()
        tk.Entry(
            add_row, textvariable=self._tag_entry_var,
            bg=C["main"], fg=C["text"], relief="solid", bd=1, font=_font(11),
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Button(
            add_row, text="Add Tag", relief="flat", bg=C["sel_bg"], fg="white",
            font=_font(10), padx=8, cursor="hand2",
            command=self._add_tag,
        ).pack(side="left")

    def _refresh_tags_display(self):
        for w in self._tags_container.winfo_children():
            w.destroy()
        if self._item_id is None:
            return
        tags = db.get_item_tags(self._item_id)
        for tag in tags:
            pill = tk.Frame(self._tags_container, bg=C["tag_pill"])
            pill.pack(side="left", padx=(0, 4), pady=2)
            tk.Label(
                pill, text=tag["name"], bg=C["tag_pill"], fg=C["tag_text"],
                font=_font(10), padx=6, pady=2,
            ).pack(side="left")
            tk.Button(
                pill, text="×", bg=C["tag_pill"], fg=C["tag_text"],
                relief="flat", font=_font(9), padx=2, pady=0, cursor="hand2",
                command=lambda tid=tag["id"]: self._remove_tag(tid),
            ).pack(side="left")

    def _add_tag(self):
        name = self._tag_entry_var.get().strip()
        if not name or self._item_id is None:
            return
        db.add_item_tag(self._item_id, name)
        self._tag_entry_var.set("")
        self._refresh_tags_display()
        self.app.sidebar.refresh()

    def _remove_tag(self, tag_id):
        if self._item_id is None:
            return
        db.remove_item_tag(self._item_id, tag_id)
        self._refresh_tags_display()
        self.app.sidebar.refresh()

    # ── Images tab ────────────────────────────────────────────────────────────

    def _build_images_tab(self):
        f = self._images_f.inner
        btn_row = tk.Frame(f, bg=C["main"])
        btn_row.pack(fill="x", padx=12, pady=8)
        tk.Button(
            btn_row, text="+ Add Image", relief="flat", bg=C["sel_bg"],
            fg="white", font=_font(10), padx=8, cursor="hand2",
            command=self._add_image,
        ).pack(side="left")
        if not PIL_AVAILABLE:
            tk.Label(
                btn_row, text="(Install Pillow for thumbnails)",
                bg=C["main"], fg=C["subtext"], font=_font(9),
            ).pack(side="left", padx=8)
        self._img_grid = tk.Frame(f, bg=C["main"])
        self._img_grid.pack(fill="both", padx=12)

    def _refresh_images_display(self):
        self._thumb_refs.clear()
        for w in self._img_grid.winfo_children():
            w.destroy()
        col, max_col = 0, 3
        for path in self._image_paths:
            abs_path = db.DATA_DIR / path if not Path(path).is_absolute() else Path(path)
            cell = tk.Frame(self._img_grid, bg=C["main"], padx=4, pady=4)
            cell.grid(row=col // max_col, column=col % max_col, sticky="nw")
            if PIL_AVAILABLE and abs_path.exists():
                try:
                    img = _open_oriented(abs_path)
                    img.thumbnail(THUMB_SIZE, Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self._thumb_refs.append(photo)
                    btn = tk.Button(
                        cell, image=photo, relief="solid", bd=1,
                        cursor="hand2",
                        command=lambda p=str(abs_path): self._view_image(p),
                    )
                    btn.pack()
                except Exception:
                    tk.Label(
                        cell, text="(image error)", bg=C["main"],
                        fg=C["subtext"], font=_font(9),
                    ).pack()
            else:
                tk.Label(
                    cell, text="(no preview)", bg=C["main"], fg=C["subtext"],
                    font=_font(10),
                ).pack()
            fname = Path(path).name
            if len(fname) > 14:
                fname = fname[:12] + "…"
            tk.Label(
                cell, text=fname, bg=C["main"], fg=C["subtext"],
                font=_font(8), wraplength=90,
            ).pack()
            tk.Button(
                cell, text="Remove", relief="flat", bg=C["main"],
                fg=C["red"], font=_font(8), cursor="hand2",
                command=lambda p=path: self._remove_image(p),
            ).pack()
            col += 1

    def _add_image(self):
        if self._item_id is None:
            return
        paths = filedialog.askopenfilenames(
            title="Add Images",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("All files", "*.*"),
            ],
            parent=self,
        )
        for src in paths:
            src = Path(src)
            dest_dir = db.IMAGES_DIR / str(self._item_id)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name
            if str(src) != str(dest):
                # Bake EXIF orientation into the saved pixels so the stored
                # copy is permanently upright (and looks right in Finder,
                # exports, etc.).  Fall back to a raw copy if PIL can't read it.
                saved = False
                if PIL_AVAILABLE:
                    try:
                        img = _open_oriented(src)
                        save_kwargs = {}
                        fmt = (img.format or src.suffix.lstrip(".")).upper()
                        if fmt in ("JPG", "JPEG"):
                            save_kwargs = {"quality": 95, "subsampling": 0}
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                        img.save(str(dest), **save_kwargs)
                        saved = True
                    except Exception:
                        saved = False
                if not saved:
                    shutil.copy2(str(src), str(dest))
            rel = str(dest.relative_to(db.DATA_DIR))
            if rel not in self._image_paths:
                self._image_paths.append(rel)
        db.update_item(self._item_id, images=self._image_paths)
        self._refresh_images_display()

    def _remove_image(self, path):
        if path in self._image_paths:
            self._image_paths.remove(path)
        db.update_item(self._item_id, images=self._image_paths)
        self._refresh_images_display()

    def _view_image(self, path):
        if not Path(path).exists():
            return
        win = tk.Toplevel(self)
        win.title(Path(path).name)
        win.configure(bg=C["main"])
        if PIL_AVAILABLE:
            img = _open_oriented(path)
            max_w, max_h = 900, 700
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(win, image=photo, bg=C["main"])
            lbl.image = photo
            lbl.pack(padx=12, pady=12)
        else:
            tk.Label(win, text=path, bg=C["main"], font=_font(11)).pack(padx=20, pady=20)

    # ── Load / Save ───────────────────────────────────────────────────────────

    def load_item(self, item_id):
        self._item_id = item_id
        self._dirty = False
        self._btn_save.set_enabled(False)
        if item_id is None:
            self._clear()
            return

        item = db.get_item(item_id)
        if not item:
            self._clear()
            return

        type_fields = item["type_fields"]
        bib_key = item.get("bib_key")
        self._lookup_bib_key = bib_key
        self._build_info_fields(type_fields, type_id=item["type_id"], bib_key=bib_key)

        # Populate Info fields
        self._cite_key_var.set(item["cite_key"])
        self._lbl_type.configure(text=item["type_name"])
        self._lbl_key.configure(text=item["cite_key"])

        # Toggle the web-lookup button for this item's type.
        import lookups
        label = lookups.LOOKUP_CAPABLE.get(bib_key)
        if label:
            self._btn_lookup.configure_text(label)
            if not self._btn_lookup.winfo_ismapped():
                self._btn_lookup.pack(side="right", padx=(0, 4), pady=6)
        else:
            self._btn_lookup.pack_forget()

        # Reference catalog button — shown for any type that has a built-in catalog
        import catalogs
        if catalogs.has_catalog(bib_key):
            label = catalogs.get_dialog_title(bib_key)
            self._btn_catalog.configure_text(label)
            if not self._btn_catalog.winfo_ismapped():
                self._btn_catalog.pack(side="right", padx=(0, 4), pady=6)
        else:
            self._btn_catalog.pack_forget()

        # Import Artist button — music / cd / cassette
        if bib_key in ("music", "cd", "cassette"):
            if not self._btn_import_artist.winfo_ismapped():
                self._btn_import_artist.pack(side="right", padx=(0, 4), pady=6)
        else:
            self._btn_import_artist.pack_forget()

        # Edit Sections — always visible when an item is loaded
        if not self._btn_edit_sections.winfo_ismapped():
            self._btn_edit_sections.pack(side="right", padx=(0, 4), pady=6)

        self._suppress_auto_fill = True
        for field in type_fields:
            if field.get("type") == "section":
                continue
            name = field["name"]
            val = item["fields"].get(name, "")
            widget = self._field_vars.get(name)
            if widget is None:
                continue
            if isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
                if val:
                    widget.insert("1.0", val)
                widget.edit_modified(False)
            else:
                widget.set(val)
        self._suppress_auto_fill = False

        # Notes
        self._notes_txt.delete("1.0", "end")
        if item.get("notes"):
            self._notes_txt.insert("1.0", item["notes"])
        self._notes_txt.edit_modified(False)

        # Tags
        self._refresh_tags_display()

        # Images
        self._image_paths = list(item.get("images", []))
        self._refresh_images_display()

        self._dirty = False
        self._btn_save.set_enabled(False)

    def _clear(self):
        self._lbl_type.configure(text="")
        self._lbl_key.configure(text="")
        self._lookup_bib_key = None
        self._first_field_widget = None
        self._sugg_tree    = None
        self._sugg_entries = []
        self._sugg_bib_key = None
        if self._sugg_after:
            try:
                self.after_cancel(self._sugg_after)
            except Exception:
                pass
            self._sugg_after = None
        if self._auto_fill_after:
            try:
                self.after_cancel(self._auto_fill_after)
            except Exception:
                pass
            self._auto_fill_after = None
        self._auto_fill_bib_key = None
        self._suppress_auto_fill = False
        self._btn_lookup.pack_forget()
        self._btn_catalog.pack_forget()
        self._btn_import_artist.pack_forget()
        self._btn_edit_sections.pack_forget()
        self._field_vars.clear()
        for w in self._info_sf.inner.winfo_children():
            w.destroy()
        self._notes_txt.delete("1.0", "end")
        for w in self._tags_container.winfo_children():
            w.destroy()
        self._image_paths = []
        self._thumb_refs.clear()
        for w in self._img_grid.winfo_children():
            w.destroy()

    def _mark_dirty(self):
        self._dirty = True
        self._btn_save.set_enabled(True)
        self._schedule_suggestion_update()

    # ── Web auto-fill (ISBN / MusicBrainz / UPC) ──────────────────────────────

    def _field_value(self, name):
        w = self._field_vars.get(name)
        if w is None:
            return ""
        if isinstance(w, tk.Text):
            return w.get("1.0", "end").strip()
        return w.get().strip()

    def _set_field_value(self, name, value):
        w = self._field_vars.get(name)
        if w is None:
            return False
        if isinstance(w, tk.Text):
            w.delete("1.0", "end")
            w.insert("1.0", value)
        else:
            w.set(value)
        return True

    def _do_lookup(self):
        if self._item_id is None or not self._lookup_bib_key:
            return
        import lookups
        bib = self._lookup_bib_key

        self.config(cursor="watch")
        self.update_idletasks()
        try:
            if bib == "book":
                isbn = self._field_value("isbn")
                if not isbn:
                    messagebox.showinfo(
                        "ISBN Lookup",
                        "Type an ISBN into the ISBN field first, then click Lookup.",
                        parent=self)
                    return
                results = lookups.lookup_isbn(isbn)

            elif bib == "vinyl":
                results = lookups.lookup_vinyl(
                    artist=self._field_value("artist"),
                    title=self._field_value("title"),
                    catalog_number=self._field_value("catalog_number"),
                    barcode=self._field_value("upc"),
                )

            elif bib in ("music", "cd", "cassette"):
                token = _get_discogs_token(self)
                if not token:
                    return
                barcode = self._field_value("barcode") if bib == "cd" else ""
                results = lookups.lookup_discogs(
                    artist=self._field_value("artist"),
                    title=self._field_value("title"),
                    token=token,
                )

            elif bib == "videogame":
                upc = self._field_value("upc")
                if not upc:
                    messagebox.showinfo(
                        "UPC Lookup",
                        "Type a UPC / barcode into the UPC field first.",
                        parent=self)
                    return
                token = db.get_setting("pricecharting_token", "")
                if not token:
                    token = simpledialog.askstring(
                        "PriceCharting API Token",
                        "UPC lookup uses the PriceCharting API (paid plan).\n"
                        "Paste your API token (saved for next time):",
                        parent=self, show="•")
                    if not token or not token.strip():
                        return
                    db.set_setting("pricecharting_token", token.strip())
                    token = token.strip()
                results = lookups.lookup_game_upc(upc, token)
            else:
                return

        except lookups.LookupError as exc:
            messagebox.showerror("Lookup failed", str(exc), parent=self)
            return
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(
                "Lookup failed", f"Unexpected error:\n{exc}", parent=self)
            return
        finally:
            self.config(cursor="")

        if not results:
            messagebox.showinfo(
                "Lookup", "Nothing was returned for that identifier.", parent=self)
            return

        # Split results into blanks (auto-fill) vs conflicts (ask first).
        applicable = {k: v for k, v in results.items() if k in self._field_vars}
        conflicts = {
            k: v for k, v in applicable.items()
            if self._field_value(k) and self._field_value(k) != v
        }
        overwrite = False
        if conflicts:
            overwrite = messagebox.askyesno(
                "Lookup",
                f"Found {len(applicable)} matching field(s).\n\n"
                f"{len(conflicts)} already contain different values.\n"
                "Overwrite those too? (No = fill only empty fields)",
                parent=self)

        filled = 0
        for k, v in applicable.items():
            cur = self._field_value(k)
            if not cur or (overwrite and cur != v):
                if self._set_field_value(k, v):
                    filled += 1

        if filled:
            self._mark_dirty()
        messagebox.showinfo(
            "Lookup complete",
            f"Filled {filled} field(s). Review the results and click "
            "“Save Changes” to keep them.",
            parent=self)

    def _save(self):
        if self._item_id is None:
            return
        item = db.get_item(self._item_id)
        if not item:
            return
        fields_dict = {}
        for name, widget in self._field_vars.items():
            if isinstance(widget, tk.Text):
                fields_dict[name] = widget.get("1.0", "end").rstrip("\n")
            else:
                fields_dict[name] = widget.get()

        new_key = re.sub(r"[^\x21-\x7e]", "", self._cite_key_var.get())
        notes = self._notes_txt.get("1.0", "end").rstrip("\n")
        try:
            db.update_item(
                self._item_id,
                fields_dict=fields_dict,
                notes=notes,
                cite_key=new_key or None,
            )
        except sqlite3.IntegrityError:
            # Cite key already used by another item — make it unique and retry.
            base, n = new_key or "item", 2
            while True:
                new_key = f"{base}{n}"
                try:
                    db.update_item(
                        self._item_id, fields_dict=fields_dict,
                        notes=notes, cite_key=new_key,
                    )
                    self._cite_key_var.set(new_key)
                    break
                except sqlite3.IntegrityError:
                    n += 1
        except Exception as exc:  # noqa: BLE001 — never fail a save silently
            messagebox.showerror(
                "Save failed",
                f"The item could not be saved:\n{exc}", parent=self)
            return
        self._dirty = False
        self._btn_save.set_enabled(False)
        self._lbl_key.configure(text=new_key)
        updated = db.get_item(self._item_id)
        if updated:
            self.app.item_list.refresh_row(updated)
        self.app.sidebar.refresh()

    def save_if_dirty(self):
        if self._dirty:
            self._save()

    # ── Reference catalog (fill fields from built-in data) ───────────────────

    def _open_catalog(self):
        if self._item_id is None:
            return
        bib_key = self._lookup_bib_key
        import catalogs
        if not catalogs.has_catalog(bib_key):
            return
        dlg = CatalogDialog(self, bib_key)
        self.wait_window(dlg)
        if not dlg.result:
            return
        # Fill empty fields; ask before overwriting ones the user already typed
        filled, conflicts = 0, []
        for k, v in dlg.result.items():
            if k not in self._field_vars:
                continue
            cur = self._field_value(k)
            if not cur:
                self._set_field_value(k, v)
                filled += 1
            elif cur != v:
                conflicts.append((k, v))
        if conflicts:
            ow = messagebox.askyesno(
                "Reference Catalog",
                f"{filled} empty field(s) filled.\n\n"
                f"{len(conflicts)} field(s) already have different values.\n"
                "Overwrite those too?",
                parent=self,
            )
            if ow:
                for k, v in conflicts:
                    if k in self._field_vars:
                        self._set_field_value(k, v)
        if filled or conflicts:
            self._mark_dirty()

    def _edit_sections(self):
        if self._item_id is None or not self._lookup_bib_key:
            return
        item = db.get_item(self._item_id)
        if not item:
            return
        dlg = SectionEditorDialog(self, self._lookup_bib_key,
                                  item["type_fields"], item["type_name"])
        self.wait_window(dlg)
        if dlg.applied:
            # Rebuild the Info tab with the new layout
            self._build_info_fields(item["type_fields"],
                                    type_id=item["type_id"],
                                    bib_key=self._lookup_bib_key)
            # Re-populate field values
            self._suppress_auto_fill = True
            for field in item["type_fields"]:
                if field.get("type") == "section":
                    continue
                name = field["name"]
                val = item["fields"].get(name, "")
                w = self._field_vars.get(name)
                if w is None:
                    continue
                if isinstance(w, tk.Text):
                    w.delete("1.0", "end")
                    if val:
                        w.insert("1.0", val)
                    w.edit_modified(False)
                else:
                    w.set(val)
            self._suppress_auto_fill = False

    def _import_artist(self):
        token = _get_discogs_token(self)
        if not token:
            return
        dlg = ImportArtistDialog(self, token)
        self.wait_window(dlg)
        # After import, refresh the suggestion panel so new entries appear
        self._schedule_suggestion_update()

    @property
    def current_item_id(self):
        return self._item_id


# ── Shared Discogs token helper ───────────────────────────────────────────────

def _get_discogs_token(parent) -> str:
    """Return the stored Discogs token, prompting the user if not yet saved."""
    token = db.get_setting("discogs_token", "")
    if not token:
        token = simpledialog.askstring(
            "Discogs API Token",
            "Discogs requires a free Personal Access Token.\n"
            "Get one at: discogs.com → Settings → Developers → Generate new token\n\n"
            "Paste your token (saved for next time):",
            parent=parent, show="•")
        if not token or not token.strip():
            return ""
        db.set_setting("discogs_token", token.strip())
    return token.strip()


# ── Section Editor Dialog ─────────────────────────────────────────────────────

class SectionEditorDialog(tk.Toplevel):
    """Edit the section headers (groupings) on the Info tab for a given item type.

    Text format:
        - A line starting with four or more dashes is a section header.
          Everything between the dashes and the trailing "/" (optional) is
          the section name.  Examples:
              ---- Physical /
              ----Grading/
              ---- My Custom Section
        - All other non-empty lines are field labels and define the order
          fields appear in.
        - Empty lines are ignored.

    Changes are stored in settings.json and apply immediately — the base type
    definition is never modified, so built-in types are unaffected on relaunch.
    """

    _SECTION_RE = re.compile(r'^-{2,}\s*(.*?)\s*/?$')

    def __init__(self, parent, bib_key: str, type_fields: list, type_name: str):
        super().__init__(parent, bg=C["main"])
        self.title(f"Edit Sections — {type_name}")
        self.resizable(True, True)
        self.applied = False
        self._bib_key     = bib_key
        self._type_fields = type_fields
        self._label_to_name = {
            f["label"]: f["name"]
            for f in type_fields if f.get("name")
        }
        self._build()
        self._populate()
        self.transient(parent)
        self.grab_set()
        self.after(50, self._center)

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_width()
        ph = self.master.winfo_height()
        px = self.master.winfo_rootx()
        py = self.master.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{px+(pw-w)//2}+{py+(ph-h)//2}")

    def _build(self):
        # Instructions
        instr = tk.Frame(self, bg=C["toolbar"])
        instr.pack(fill="x")
        tk.Frame(instr, bg=C["border"], height=1).pack(fill="x", side="bottom")
        tk.Label(
            instr,
            text=(
                "Lines starting with  ----  create section dividers.\n"
                "Drag lines up/down in the text to reorder fields. "
                "Delete a  ----  line to remove that section."
            ),
            bg=C["toolbar"], fg=C["subtext"], font=_font(9),
            justify="left", anchor="w", padx=12, pady=6,
        ).pack(fill="x")

        # Text editor
        txt_frame = tk.Frame(self, bg=C["main"],
                             highlightthickness=1,
                             highlightbackground=C["btn_border"])
        txt_frame.pack(fill="both", expand=True, padx=12, pady=(10, 6))
        vsb = ttk.Scrollbar(txt_frame, orient="vertical")
        vsb.pack(side="right", fill="y")
        self._txt = tk.Text(
            txt_frame, wrap="none", font=_font(11, mono=True),
            bg=C["main"], fg=C["text"], relief="flat", bd=0,
            width=42, height=22,
            highlightthickness=0,
            yscrollcommand=vsb.set,
        )
        self._txt.pack(fill="both", expand=True, padx=4, pady=4)
        vsb.configure(command=self._txt.yview)

        # Buttons
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", padx=12)
        btn_row = tk.Frame(self, bg=C["main"])
        btn_row.pack(fill="x", padx=12, pady=8)

        FlatButton(btn_row, "Reset to Default",
                   command=self._reset, kind="default", padx=10).pack(side="left")
        FlatButton(btn_row, "Cancel",
                   command=self.destroy, kind="default", padx=10).pack(side="right", padx=(4,0))
        FlatButton(btn_row, "Apply",
                   command=self._apply, kind="primary", padx=10).pack(side="right")

    def _populate(self):
        """Fill the text widget from the current (possibly custom) field list."""
        lines = []
        for f in self._type_fields:
            if f.get("type") == "section":
                lines.append(f"---- {f['label']} /")
            elif f.get("label"):
                lines.append(f["label"])
        self._txt.delete("1.0", "end")
        self._txt.insert("1.0", "\n".join(lines))

    def _apply(self):
        raw = self._txt.get("1.0", "end")
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]

        layout = []
        for line in lines:
            m = self._SECTION_RE.match(line)
            if line.startswith("--") and m:
                name = m.group(1).strip().rstrip("/").strip()
                if name:
                    layout.append({"section": name})
            elif line in self._label_to_name:
                layout.append(self._label_to_name[line])
            # Unknown labels silently ignored

        db.set_section_layout(self._bib_key, layout)
        self.applied = True
        self.destroy()

    def _reset(self):
        if messagebox.askyesno(
            "Reset Sections",
            "Remove your custom section layout and revert to the type default?",
            parent=self,
        ):
            db.clear_section_layout(self._bib_key)
            self.applied = True
            self.destroy()


# ── Import Artist Dialog ──────────────────────────────────────────────────────

class ImportArtistDialog(tk.Toplevel):
    """Fetch all physical releases for an artist from Discogs and save them
    to the local music catalog so they appear in the Music Reference dialog."""

    _PHYS_SKIP = {"file", "digital", ""}
    _FORMAT_NORM = {
        "vinyl": "Vinyl", "shellac": "Vinyl", "lathe cut": "Vinyl",
        "cd": "CD", "cdr": "CD",
        "cassette": "Cassette",
        "sacd": "SACD",
        "dvd-audio": "DVD-Audio", "dvd": "DVD-Audio",
        "blu-ray audio": "Blu-ray Audio", "blu-ray": "Blu-ray Audio",
        "8-track cartridge": "8-Track", "8-track": "8-Track",
        "minidisc": "MiniDisc",
        "reel-to-reel": "Reel-to-Reel",
    }

    def __init__(self, parent, token: str):
        super().__init__(parent, bg=C["main"])
        self.title("Import Artist from Discogs")
        self.resizable(False, False)
        self._token    = token
        self._entries  = []
        self._stop     = __import__("threading").Event()
        self._thread   = None
        self._build()
        self.transient(parent)
        self.grab_set()
        self.after(100, self._center)

    def _center(self):
        self.update_idletasks()
        pw, ph = self.master.winfo_width(), self.master.winfo_height()
        px, py = self.master.winfo_rootx(), self.master.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw-w)//2}+{py + (ph-h)//2}")

    def _build(self):
        pad = dict(padx=14, pady=6)

        # ── Search row ──
        top = tk.Frame(self, bg=C["main"])
        top.pack(fill="x", **pad)
        tk.Label(top, text="Artist:", bg=C["main"], fg=C["text"],
                 font=_font(11)).pack(side="left")
        self._artist_var = tk.StringVar()
        entry = tk.Entry(top, textvariable=self._artist_var,
                         bg=C["main"], fg=C["text"], relief="flat", bd=0,
                         font=_font(11), width=32,
                         highlightthickness=1, highlightbackground=C["btn_border"],
                         highlightcolor=C["sel_bg"])
        entry.pack(side="left", padx=(6, 8))
        entry.bind("<Return>", lambda _: self._search())
        entry.focus_set()
        self._btn_search = FlatButton(top, "Search", command=self._search,
                                      kind="primary", padx=10)
        self._btn_search.pack(side="left")

        # ── Progress bar + status ──
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", padx=14)
        prog_frame = tk.Frame(self, bg=C["main"])
        prog_frame.pack(fill="x", padx=14, pady=(6, 2))
        import tkinter.ttk as _ttk
        self._progress = _ttk.Progressbar(prog_frame, mode="indeterminate", length=420)
        self._progress.pack(side="left")
        self._status_var = tk.StringVar(value="Enter an artist name and click Search.")
        tk.Label(prog_frame, textvariable=self._status_var,
                 bg=C["main"], fg=C["subtext"], font=_font(9),
                 anchor="w", wraplength=420).pack(side="left", padx=(8, 0))

        # ── Results tree ──
        tree_frame = tk.Frame(self, bg=C["main"])
        tree_frame.pack(fill="both", expand=True, padx=14, pady=6)
        cols = ("title", "year", "format", "label")
        self._tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                  height=14, selectmode="browse")
        for col, lbl, w in [("title","Album / Release",280),
                             ("year","Year",50), ("format","Media",75),
                             ("label","Label",160)]:
            self._tree.heading(col, text=lbl)
            self._tree.column(col, width=w, minwidth=40)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        # ── Bottom buttons ──
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", padx=14)
        btn_row = tk.Frame(self, bg=C["main"])
        btn_row.pack(fill="x", padx=14, pady=8)
        self._count_lbl = tk.Label(btn_row, text="", bg=C["main"],
                                   fg=C["subtext"], font=_font(10))
        self._count_lbl.pack(side="left")
        FlatButton(btn_row, "Cancel", command=self._cancel,
                   kind="default", padx=10).pack(side="right", padx=(4, 0))
        self._btn_import = FlatButton(btn_row, "Import", command=self._import,
                                      kind="primary", padx=10)
        self._btn_import.set_enabled(False)
        self._btn_import.pack(side="right")

    def _search(self):
        if self._thread and self._thread.is_alive():
            return
        artist = self._artist_var.get().strip()
        if not artist:
            return
        self._entries = []
        self._tree.delete(*self._tree.get_children())
        self._btn_import.set_enabled(False)
        self._count_lbl.configure(text="")
        self._btn_search.set_enabled(False)
        self._progress.start(12)
        self._stop.clear()
        import threading
        self._thread = threading.Thread(target=self._fetch, args=(artist,), daemon=True)
        self._thread.start()

    def _fetch(self, artist_name: str):
        import urllib.parse, time
        try:
            auth = {"Authorization": f"Discogs token={self._token}"}
            import lookups as _lu

            # 1. Resolve artist
            self.after(0, self._set_status, f'Searching for "{artist_name}"…')
            url = ("https://api.discogs.com/database/search?"
                   + urllib.parse.urlencode({"type": "artist", "q": artist_name,
                                             "per_page": "5"}))
            data = _lu._get_json(url, extra_headers=auth)
            hits = data.get("results") or []
            if not hits:
                self.after(0, self._set_status, f'No artist found for "{artist_name}".')
                self.after(0, self._done, False)
                return

            artist = hits[0]
            artist_id   = artist["id"]
            artist_resolved = artist.get("title", artist_name)

            # 2. Page through releases
            page, pages = 1, 1
            entries = []
            while page <= pages and not self._stop.is_set():
                url = (f"https://api.discogs.com/artists/{artist_id}/releases"
                       f"?per_page=100&page={page}&sort=year&sort_order=asc")
                data = _lu._get_json(url, extra_headers=auth)
                pages = data.get("pagination", {}).get("pages", 1)
                for r in (data.get("releases") or []):
                    if r.get("type") != "release":
                        continue
                    fmt_raw = (r.get("format") or "").strip()
                    if fmt_raw.lower() in self._PHYS_SKIP:
                        continue
                    fmt = self._FORMAT_NORM.get(fmt_raw.lower(), fmt_raw)
                    raw_title = (r.get("title") or "").strip()
                    title = raw_title.split(" - ", 1)[1].strip() \
                        if " - " in raw_title else raw_title
                    catno = (r.get("catno") or "")
                    if catno.lower() == "none":
                        catno = ""
                    e = {k: v for k, v in {
                        "title":          title,
                        "artist":         artist_resolved,
                        "year":           str(r["year"]) if r.get("year") else "",
                        "format":         fmt,
                        "label":          r.get("label", ""),
                        "catalog_number": catno,
                        "country":        r.get("country", ""),
                    }.items() if v}
                    if e.get("title"):
                        entries.append(e)

                self.after(0, self._set_status,
                           f'{artist_resolved} — {len(entries)} physical releases'
                           f' (page {page}/{pages})')
                self.after(0, self._append_rows,
                           [(e.get("title",""), e.get("year",""),
                             e.get("format",""), e.get("label",""))
                            for e in entries[len(self._entries):]])
                page += 1
                if page <= pages:
                    time.sleep(1.15)

            # Dedup: same (title, format, year)
            seen: set = set()
            deduped = []
            for e in entries:
                key = (e.get("title","").lower(),
                       e.get("format","").lower(),
                       e.get("year",""))
                if key not in seen:
                    seen.add(key)
                    deduped.append(e)

            self.after(0, self._on_results, deduped, artist_resolved)

        except Exception as exc:
            self.after(0, self._set_status, f"Error: {exc}")
            self.after(0, self._done, False)

    def _append_rows(self, rows):
        for row in rows:
            tag = "even" if len(self._tree.get_children()) % 2 == 0 else "odd"
            self._tree.insert("", "end", values=row, tags=(tag,))
        self._tree.tag_configure("even", background=C["main"])
        self._tree.tag_configure("odd",  background=C["toolbar"])

    def _on_results(self, entries, artist_name):
        self._entries = entries
        self._tree.delete(*self._tree.get_children())
        for e in entries:
            tag = "even" if len(self._tree.get_children()) % 2 == 0 else "odd"
            self._tree.insert("", "end",
                              values=(e.get("title",""), e.get("year",""),
                                      e.get("format",""), e.get("label","")),
                              tags=(tag,))
        self._tree.tag_configure("even", background=C["main"])
        self._tree.tag_configure("odd",  background=C["toolbar"])
        n = len(entries)
        self._count_lbl.configure(text=f"{n} physical release{'s' if n!=1 else ''}")
        self._btn_import.configure_text(
            f"Import All  ({n})" if n else "Import All")
        self._btn_import.set_enabled(n > 0)
        self._set_status(f'Found {n} physical releases for "{artist_name}".')
        self._done(True)

    def _set_status(self, msg: str):
        self._status_var.set(msg)

    def _done(self, success: bool):
        self._progress.stop()
        self._btn_search.set_enabled(True)

    def _import(self):
        if not self._entries:
            return
        import music_catalog as _mc
        _mc.save_entries(self._entries)
        n = len(self._entries)
        messagebox.showinfo(
            "Import complete",
            f"Imported {n} release{'s' if n!=1 else ''} into the Music Reference catalog.\n\n"
            "They will appear when you click 'Music Reference'.",
            parent=self,
        )
        self.destroy()

    def _cancel(self):
        self._stop.set()
        self.destroy()


# ── ISBN Lookup Dialog (Book creation flow) ───────────────────────────────────

class ISBNDialog(tk.Toplevel):
    """Small dialog shown when creating a new Book.

    The user types (or scans) an ISBN.  Clicking Fetch queries Open Library
    and shows a preview.  "Add to Collection" returns the pre-filled fields;
    "Enter Manually" returns an empty dict so the form opens blank; Cancel
    sets ``cancelled=True``.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.result: dict = {}        # filled fields, empty if manual entry
        self.cancelled: bool = False

        self.title("Add Book")
        self.configure(bg=C["main"])
        self.geometry("480x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._build()
        self._centre(parent)
        self.after(60, self._isbn_entry.focus_set)

    def _centre(self, parent):
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2
        self.geometry(f"+{px - self.winfo_width()//2}+{py - self.winfo_height()//2}")

    def _build(self):
        # ── ISBN entry row ────────────────────────────────────────────────────
        top = tk.Frame(self, bg=C["toolbar"], pady=14)
        top.pack(fill="x")
        tk.Frame(top, bg=C["border"], height=1).pack(fill="x", side="bottom")

        tk.Label(top, text="ISBN", bg=C["toolbar"], fg=C["subtext"],
                 font=_font(10)).pack(side="left", padx=(16, 6))
        self._isbn_var = tk.StringVar()
        self._isbn_entry = tk.Entry(top, textvariable=self._isbn_var,
                                    font=_font(14), relief="solid", bd=1,
                                    width=22)
        self._isbn_entry.pack(side="left", padx=(0, 8))
        self._isbn_entry.bind("<Return>", lambda _e: self._fetch())

        self._fetch_btn = FlatButton(top, "Fetch", command=self._fetch,
                                     kind="primary", padx=10)
        self._fetch_btn.pack(side="left")

        # ── Preview area ──────────────────────────────────────────────────────
        self._preview_frame = tk.Frame(self, bg=C["main"], pady=0)
        self._preview_frame.pack(fill="both", expand=True, padx=20, pady=(14, 0))

        self._status_lbl = tk.Label(
            self._preview_frame,
            text="Enter a 10- or 13-digit ISBN and click Fetch.",
            bg=C["main"], fg=C["subtext"], font=_font(10),
            wraplength=420, justify="left",
        )
        self._status_lbl.pack(anchor="w")
        self._preview_inner = tk.Frame(self._preview_frame, bg=C["main"])
        self._preview_inner.pack(fill="x", pady=(8, 0))

        # ── Footer ────────────────────────────────────────────────────────────
        foot = tk.Frame(self, bg=C["toolbar"], pady=10)
        foot.pack(fill="x", side="bottom")
        tk.Frame(foot, bg=C["border"], height=1).pack(fill="x", side="top")

        FlatButton(foot, "Cancel", command=self._cancel,
                   kind="default", padx=10).pack(side="right", padx=8)
        self._add_btn = FlatButton(foot, "Add to Collection",
                                   command=self._add, kind="primary", padx=10)
        self._add_btn.pack(side="right", padx=(0, 4))
        self._add_btn.set_enabled(False)
        FlatButton(foot, "Enter Manually", command=self.destroy,
                   kind="default", padx=10).pack(side="left", padx=12)

    def _fetch(self):
        isbn = self._isbn_var.get().strip()
        if not isbn:
            return
        import lookups
        self.config(cursor="watch")
        self._fetch_btn.set_enabled(False)
        self.update_idletasks()
        try:
            fields = lookups.lookup_isbn(isbn)
        except lookups.LookupError as exc:
            self._set_status(f"Not found: {exc}", error=True)
            return
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Error: {exc}", error=True)
            return
        finally:
            self.config(cursor="")
            self._fetch_btn.set_enabled(True)

        if not fields:
            self._set_status("No data returned for that ISBN.", error=True)
            return

        self._result_fields = fields
        self._show_preview(fields)
        self._add_btn.set_enabled(True)

    def _set_status(self, msg, error=False):
        self._status_lbl.configure(
            text=msg, fg=C["red"] if error else C["subtext"])
        for w in self._preview_inner.winfo_children():
            w.destroy()

    def _show_preview(self, fields):
        self._status_lbl.configure(text="Book found:", fg=C["subtext"])
        inner = self._preview_inner
        for w in inner.winfo_children():
            w.destroy()

        title = fields.get("title", "")
        author = fields.get("author", "")
        year = fields.get("year", "")
        publisher = fields.get("publisher", "")

        tk.Label(inner, text=title, bg=C["main"], fg=C["text"],
                 font=_font(12, bold=True),
                 wraplength=420, justify="left").pack(anchor="w")
        sub_parts = [p for p in [author, year, publisher] if p]
        if sub_parts:
            tk.Label(inner, text="  |  ".join(sub_parts),
                     bg=C["main"], fg=C["subtext"], font=_font(10),
                     wraplength=420, justify="left").pack(anchor="w", pady=(2, 0))
        n = len(fields)
        tk.Label(inner, text=f"{n} fields ready to fill.",
                 bg=C["main"], fg=C["section_lbl"], font=_font(9)).pack(
            anchor="w", pady=(6, 0))

    def _add(self):
        self.result = getattr(self, "_result_fields", {})
        self.destroy()

    def _cancel(self):
        self.cancelled = True
        self.destroy()


# ── Generic Reference Catalog Dialog ─────────────────────────────────────────

class CatalogDialog(tk.Toplevel):
    """Searchable reference catalog for any item type that has a catalog.

    Used in two modes:
      standalone=True  — opened *before* an item is created (from _new_item).
                         Shows "Add to Collection", "Create Blank", and "Cancel".
      standalone=False — opened from the detail panel of an existing item to
                         fill fields.  Shows "Fill Fields" and "Cancel".

    ``result``  is set to a fields-dict when the user picks an entry.
    ``skipped`` is True when the user chooses "Create Blank" (standalone mode).
    """

    def __init__(self, parent, bib_key: str, standalone: bool = False):
        super().__init__(parent)
        import catalogs as _cat
        self._bib_key   = bib_key
        self._standalone = standalone
        self._catalogs  = _cat
        self.result  = None
        self.skipped = False
        self._entries: list = []

        self.title(_cat.get_dialog_title(bib_key))
        self.configure(bg=C["main"])
        self.geometry("680x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self._build()
        self._centre(parent)
        # Load after the window is drawn so the geometry is stable
        self.after(10, self._load_all)

    def _centre(self, parent):
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2
        self.geometry(f"+{px - self.winfo_width()//2}+{py - self.winfo_height()//2}")

    def _build(self):
        import catalogs as _cat

        # ── Blank entry at top ────────────────────────────────────────────────
        top = tk.Frame(self, bg=C["toolbar"], pady=10)
        top.pack(fill="x")
        tk.Frame(top, bg=C["border"], height=1).pack(fill="x", side="bottom")

        entry_row = tk.Frame(top, bg=C["toolbar"])
        entry_row.pack(fill="x", padx=14, pady=(0, 6))
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())
        search_entry = tk.Entry(entry_row, textvariable=self._search_var,
                                font=_font(14), relief="solid", bd=1)
        search_entry.pack(fill="x", expand=True)
        self.after(60, search_entry.focus_set)

        # Optional filter + count row below entry
        sub_row = tk.Frame(top, bg=C["toolbar"])
        sub_row.pack(fill="x", padx=14)

        self._filter_var = None
        filter_field, filter_opts = _cat.get_filter_spec(self._bib_key)
        if filter_field and filter_opts:
            tk.Label(sub_row, text=filter_field.title() + ":", bg=C["toolbar"],
                     fg=C["subtext"], font=_font(10)).pack(side="left", padx=(0, 4))
            self._filter_var = tk.StringVar(value=filter_opts[0])
            cb = ttk.Combobox(sub_row, textvariable=self._filter_var,
                              values=filter_opts, state="readonly",
                              width=18, font=_font(10))
            cb.pack(side="left")
            self._filter_var.trace_add("write", lambda *_: self._filter())

        self._count_lbl = tk.Label(sub_row, text="", bg=C["toolbar"],
                                   fg=C["subtext"], font=_font(9))
        self._count_lbl.pack(side="right")

        # ── Full-width options list ───────────────────────────────────────────
        list_frame = tk.Frame(self, bg=C["main"])
        list_frame.pack(fill="both", expand=True)

        search_cols = _cat.get_search_cols(self._bib_key)
        col_ids = [c[0] for c in search_cols]
        self._tree = ttk.Treeview(list_frame, columns=col_ids, show="headings",
                                  selectmode="browse", style="Items.Treeview")
        for cid, lbl, w in search_cols:
            self._tree.heading(cid, text=lbl)
            self._tree.column(cid, width=w, minwidth=50,
                               stretch=(cid == search_cols[0][0]))
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tree.pack(side="left", fill="both", expand=True)
        self._tree.tag_configure("odd",  background="#fafafa")
        self._tree.tag_configure("even", background=C["main"])
        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>",          lambda _e: self._use_selected())
        self._tree.bind("<Return>",            lambda _e: self._use_selected())

        # ── Detail strip below list ───────────────────────────────────────────
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")
        detail_outer = tk.Frame(self, bg=C["toolbar"], pady=8)
        detail_outer.pack(fill="x")
        self._detail_inner = tk.Frame(detail_outer, bg=C["toolbar"])
        self._detail_inner.pack(fill="x", padx=14)

        # ── Footer ───────────────────────────────────────────────────────────
        foot = tk.Frame(self, bg=C["toolbar"], pady=8)
        foot.pack(fill="x", side="bottom")
        tk.Frame(foot, bg=C["border"], height=1).pack(fill="x", side="top")

        FlatButton(foot, "Cancel", command=self.destroy,
                   kind="default", padx=12).pack(side="right", padx=8)

        if self._standalone:
            FlatButton(foot, "Add to Collection", command=self._use_selected,
                       kind="primary", padx=12).pack(side="right", padx=(0, 4))
            FlatButton(foot, "Create Blank Instead", command=self._skip,
                       kind="default", padx=12).pack(side="left", padx=12)
        else:
            FlatButton(foot, "Fill Fields", command=self._use_selected,
                       kind="primary", padx=12).pack(side="right", padx=(0, 4))

    def _load_all(self):
        self._filter()

    def _filter(self):
        import catalogs as _cat
        q = self._search_var.get().strip() if hasattr(self, "_search_var") else ""
        fv = self._filter_var.get() if self._filter_var else "All"
        results = _cat.search(self._bib_key, q, fv)
        self._entries = results

        self._tree.delete(*self._tree.get_children())
        search_cols = _cat.get_search_cols(self._bib_key)
        col_ids = [c[0] for c in search_cols]

        for i, e in enumerate(results):
            tag = "even" if i % 2 == 0 else "odd"
            values = tuple(str(e.get(cid, "")) for cid in col_ids)
            self._tree.insert("", "end", iid=str(i), values=values, tags=(tag,))

        n = len(results)
        self._count_lbl.configure(text=f"{n} result{'s' if n != 1 else ''}")

        children = self._tree.get_children()
        if children:
            self._tree.selection_set(children[0])
            self._show_detail(self._entries[0])

    def _on_select(self, _e):
        sel = self._tree.selection()
        if sel and self._entries:
            idx = int(sel[0])
            if 0 <= idx < len(self._entries):
                self._show_detail(self._entries[idx])

    def _show_detail(self, entry):
        import catalogs as _cat
        inner = self._detail_inner
        for w in inner.winfo_children():
            w.destroy()

        title = entry.get("title") or entry.get("name") or ""
        tk.Label(inner, text=title, bg=C["toolbar"], fg=C["text"],
                 font=_font(11, bold=True), anchor="w").pack(side="left", padx=(0, 12))

        # Build a compact summary from the first few populated detail fields
        detail_fields = _cat.get_detail_fields(self._bib_key)
        parts = []
        for field_name, field_label in detail_fields[:6]:
            v = str(entry.get(field_name, "")).strip()
            if v and v != title:
                parts.append(f"{field_label}: {v}")
        if parts:
            tk.Label(inner, text="  |  ".join(parts), bg=C["toolbar"],
                     fg=C["subtext"], font=_font(10), anchor="w",
                     wraplength=520, justify="left").pack(side="left")

    def _use_selected(self):
        import catalogs as _cat
        sel = self._tree.selection()
        if not sel or not self._entries:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self._entries):
            self.result = _cat.to_fields(self._bib_key, self._entries[idx])
        self.destroy()

    def _skip(self):
        """User chose to create a blank item instead of using the catalog."""
        self.skipped = True
        self.destroy()


# ── New Item Dialog ───────────────────────────────────────────────────────────

class ImportBibDialog(tk.Toplevel):
    """Options dialog shown before a .bib import."""

    def __init__(self, parent, *, total, n_groups, n_tags, current_coll):
        super().__init__(parent)
        self.result = None
        self.title("Import BibTeX")
        self.configure(bg=C["main"])
        self.resizable(False, False)
        self._current_coll = current_coll
        self._build(total, n_groups, n_tags)
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2
        self.geometry(f"+{px - self.winfo_width() // 2}"
                      f"+{py - self.winfo_height() // 2}")

    def _build(self, total, n_groups, n_tags):
        wrap = tk.Frame(self, bg=C["main"], padx=24, pady=20)
        wrap.pack(fill="both", expand=True)

        tk.Label(
            wrap, text="Import options", bg=C["main"], fg=C["text"],
            font=_font(13, bold=True),
        ).pack(anchor="w", pady=(0, 4))
        tk.Label(
            wrap,
            text=f"Found {total} entr{'ies' if total != 1 else 'y'}.  "
                 f"{n_groups} carry folder paths, {n_tags} carry tags.",
            bg=C["main"], fg=C["subtext"], font=_font(10),
            wraplength=380, justify="left",
        ).pack(anchor="w", pady=(0, 14))

        # Checkboxes
        self._v_folders = tk.BooleanVar(value=True)
        self._v_tags    = tk.BooleanVar(value=True)
        for var, lbl, help_ in [
            (self._v_folders, "Preserve folder structure",
             "Recreate folders from the `groups` field (Parent > Child > Leaf)."),
            (self._v_tags, "Import tags",
             "Attach tags from `keywords` (or `tags`) on each entry."),
        ]:
            tk.Checkbutton(
                wrap, text=lbl, variable=var, bg=C["main"], fg=C["text"],
                activebackground=C["main"], font=_font(11, bold=True),
            ).pack(anchor="w")
            tk.Label(
                wrap, text=help_, bg=C["main"], fg=C["section_lbl"],
                font=_font(9), wraplength=380, justify="left",
            ).pack(anchor="w", padx=24, pady=(0, 8))

        # Fallback destination
        tk.Label(
            wrap, text="For entries with no folder path:",
            bg=C["main"], fg=C["text"], font=_font(11, bold=True),
        ).pack(anchor="w", pady=(6, 4))

        self._v_fallback = tk.StringVar(value="library")
        choices = [("library", "Place in the library root")]
        if self._current_coll and self._current_coll != -1:
            choices.append(("current", "Place in the currently selected collection"))
        choices.append(("named", "Place in a new collection named:"))
        for val, lbl in choices:
            tk.Radiobutton(
                wrap, text=lbl, variable=self._v_fallback, value=val,
                bg=C["main"], fg=C["text"], activebackground=C["main"],
                font=_font(10),
            ).pack(anchor="w", padx=4)

        self._v_name = tk.StringVar(value="Imported")
        row = tk.Frame(wrap, bg=C["main"])
        row.pack(anchor="w", padx=24, pady=(2, 0))
        self._name_entry = tk.Entry(
            row, textvariable=self._v_name, bg=C["main"], fg=C["text"],
            relief="flat", bd=0, font=_font(11), width=24,
            highlightthickness=1, highlightbackground=C["btn_border"],
            highlightcolor=C["sel_bg"],
        )
        self._name_entry.pack()

        # Buttons
        btns = tk.Frame(wrap, bg=C["main"])
        btns.pack(fill="x", pady=(18, 0))
        FlatButton(btns, "Cancel", command=self.destroy)\
            .pack(side="right", padx=(8, 0))
        FlatButton(btns, "Import", command=self._ok, kind="primary")\
            .pack(side="right")

    def _ok(self):
        self.result = {
            "preserve_folders": self._v_folders.get(),
            "import_tags":      self._v_tags.get(),
            "fallback":         self._v_fallback.get(),
            "fallback_name":    self._v_name.get().strip() or "Imported",
        }
        self.destroy()


class NewItemDialog(tk.Toplevel):
    """Pick an item type to create."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.result = None
        self.title("New Item — Choose Type")
        self.configure(bg=C["main"])
        self.resizable(False, False)
        self._build()
        self.transient(parent)
        self.grab_set()
        self._centre(parent)

    def _centre(self, parent):
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2
        x = px - self.winfo_width() // 2
        y = py - self.winfo_height() // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        tk.Label(
            self, text="Select item type", bg=C["main"],
            fg=C["text"], font=_font(13, bold=True),
        ).pack(padx=24, pady=(20, 4))
        tk.Label(
            self, text="Click a category to create a new entry.  "
                       "Custom categories show a × to remove them.",
            bg=C["main"], fg=C["subtext"], font=_font(10),
        ).pack(padx=24, pady=(0, 12))

        self._grid_holder = tk.Frame(self, bg=C["main"])
        self._grid_holder.pack(padx=20, pady=(0, 12))
        self._render_grid()

        footer = tk.Frame(self, bg=C["main"])
        footer.pack(fill="x", padx=20, pady=(0, 16))
        FlatButton(footer, "Manage Categories…",
                   command=self._manage, kind="ghost")\
            .pack(side="left")
        FlatButton(footer, "Cancel", command=self.destroy, kind="default")\
            .pack(side="right")

    def _render_grid(self):
        for w in self._grid_holder.winfo_children():
            w.destroy()

        types = db.get_all_types()
        cols = 4
        for i, t in enumerate(types):
            tile = self._make_tile(self._grid_holder, t)
            tile.grid(row=i // cols, column=i % cols, padx=6, pady=6, sticky="nsew")

        # Trailing "+ New Type" tile
        add_tile = tk.Frame(
            self._grid_holder, bg=C["main"], width=120, height=92,
            highlightthickness=2, highlightbackground=C["btn_border"],
        )
        add_tile.grid_propagate(False)
        add_tile.grid(row=len(types) // cols, column=len(types) % cols,
                      padx=6, pady=6, sticky="nsew")
        lbl = tk.Label(
            add_tile, text="+\nNew Category",
            bg=C["main"], fg=C["primary"], cursor="hand2",
            font=_font(10, bold=True), justify="center",
        )
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        for w in (add_tile, lbl):
            w.bind("<Button-1>", lambda _e: self._new_type())
            w.bind("<Enter>", lambda _e, t=add_tile, l=lbl:
                   (t.configure(bg=C["btn_hover"], highlightbackground=C["primary"]),
                    l.configure(bg=C["btn_hover"])))
            w.bind("<Leave>", lambda _e, t=add_tile, l=lbl:
                   (t.configure(bg=C["main"], highlightbackground=C["btn_border"]),
                    l.configure(bg=C["main"])))

    def _make_tile(self, parent, t):
        is_builtin = bool(t.get("is_builtin"))
        tile = tk.Frame(
            parent, bg=C["toolbar"], width=120, height=92,
            highlightthickness=1, highlightbackground=C["btn_border"],
        )
        tile.grid_propagate(False)

        # delete button in corner — only for non-builtin types
        if not is_builtin:
            x = tk.Label(
                tile, text="x", bg=C["toolbar"], fg=C["red"],
                font=_font(11, bold=True), cursor="hand2", padx=4,
            )
            x.place(relx=1.0, y=2, anchor="ne")
            x.bind("<Button-1>",
                   lambda _e, tid=t["id"], name=t["display_name"]:
                       self._delete_type(tid, name))
            x.bind("<Enter>", lambda _e, w=x: w.configure(fg=C["red_hover"]))
            x.bind("<Leave>", lambda _e, w=x: w.configure(fg=C["red"]))

        body = tk.Label(
            tile,
            text=t["display_name"],
            bg=C["toolbar"], fg=C["text"], cursor="hand2",
            font=_font(10, bold=True), justify="center",
        )
        body.place(relx=0.5, rely=0.5, anchor="center")

        def _on_click(_e):
            self._pick(t["id"], t["bib_key"])

        def _on_enter(_e):
            tile.configure(bg=C["sel_bg"], highlightbackground=C["sel_bg"])
            body.configure(bg=C["sel_bg"], fg=C["sel_fg"])

        def _on_leave(_e):
            tile.configure(bg=C["toolbar"], highlightbackground=C["btn_border"])
            body.configure(bg=C["toolbar"], fg=C["text"])

        for w in (tile, body):
            w.bind("<Button-1>", _on_click)
            w.bind("<Enter>", _on_enter)
            w.bind("<Leave>", _on_leave)

        # Right-click → edit type (works for built-in or custom)
        for w in (tile, body):
            w.bind("<Button-3>",
                   lambda _e, tid=t["id"]: self._edit_type(tid))

        return tile

    def _delete_type(self, type_id, name):
        if not messagebox.askyesno(
            "Delete Category",
            f"Delete the category “{name}”?\n\n"
            "Any items currently using it will move to Miscellaneous.",
            parent=self,
        ):
            return
        db.delete_type(type_id)
        self._render_grid()
        self.app.sidebar.refresh()
        self.app._refresh()

    def _new_type(self):
        d = TypeEditorDialog(self, self.app)
        self.wait_window(d)
        if d.result:
            self._render_grid()
            self.app.sidebar.refresh()

    def _edit_type(self, type_id):
        d = TypeEditorDialog(self, self.app, type_id=type_id)
        self.wait_window(d)
        if d.result:
            self._render_grid()
            self.app.sidebar.refresh()

    def _manage(self):
        self.destroy()
        self.app._manage_types()

    def _pick(self, type_id, bib_key):
        self.result = (type_id, bib_key)
        self.destroy()


# ── Type Editor Dialog ────────────────────────────────────────────────────────

class TypeEditorDialog(tk.Toplevel):
    """Create or edit a custom item type."""

    def __init__(self, parent, app, type_id=None):
        super().__init__(parent)
        self.app = app
        self._type_id = type_id
        self._fields = []
        self.result = None
        title = "Edit Item Type" if type_id else "New Item Type"
        self.title(title)
        self.configure(bg=C["main"])
        self.resizable(True, True)
        self.geometry("540x620")
        self._build()
        if type_id:
            self._load_type(type_id)
        self.transient(parent)
        self.grab_set()
        self._centre(parent)

    def _centre(self, parent):
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2
        x = px - self.winfo_width() // 2
        y = py - self.winfo_height() // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        top = tk.Frame(self, bg=C["main"], padx=20, pady=16)
        top.pack(fill="x")
        top.grid_columnconfigure(1, weight=1)

        # Icon kept in the data model for .bib compatibility but no longer
        # surfaced in the UI — new types simply carry an empty icon.
        self._icon_var = tk.StringVar()
        for row, (lbl, attr) in enumerate([
            ("Display Name", "_name_var"),
            ("BibTeX Key",   "_bib_var"),
        ]):
            tk.Label(top, text=lbl, bg=C["main"], fg=C["subtext"],
                     font=_font(10), anchor="e", width=14).grid(
                row=row, column=0, sticky="e", pady=4, padx=(0, 8)
            )
            var = tk.StringVar()
            setattr(self, attr, var)
            tk.Entry(
                top, textvariable=var, bg=C["main"], fg=C["text"],
                relief="solid", bd=1, font=_font(11),
            ).grid(row=row, column=1, sticky="ew", pady=4)

        # Fields list
        tk.Label(
            self, text="Fields", bg=C["main"], fg=C["subtext"],
            font=_font(10, bold=True),
        ).pack(anchor="w", padx=20, pady=(8, 4))

        list_frame = tk.Frame(self, bg=C["main"])
        list_frame.pack(fill="both", expand=True, padx=20)
        list_frame.grid_columnconfigure(0, weight=1)

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        self._fields_lb = tk.Listbox(
            list_frame, bg=C["main"], fg=C["text"], relief="flat", bd=0, font=_font(11),
            highlightthickness=1, highlightbackground=C["btn_border"], selectbackground=C["sel_bg"],
            selectforeground=C["sel_fg"], yscrollcommand=vsb.set,
        )
        vsb.configure(command=self._fields_lb.yview)
        self._fields_lb.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        list_frame.grid_rowconfigure(0, weight=1)

        btns = tk.Frame(self, bg=C["main"], padx=20, pady=8)
        btns.pack(fill="x")
        for lbl, cmd in [
            ("Add Field",    self._add_field),
            ("Edit Field",   self._edit_field),
            ("Remove Field", self._remove_field),
            ("Move Up",      self._move_up),
            ("Move Down",    self._move_down),
        ]:
            tk.Button(
                btns, text=lbl, relief="flat", bg=C["toolbar"],
                fg=C["text"], font=_font(10), padx=8, cursor="hand2",
                command=cmd,
            ).pack(side="left", padx=(0, 4))

        footer = tk.Frame(self, bg=C["main"], padx=20, pady=12)
        footer.pack(fill="x")
        tk.Button(
            footer, text="Cancel", relief="flat", bg=C["toolbar"],
            fg=C["text"], font=_font(10), padx=12, cursor="hand2",
            command=self.destroy,
        ).pack(side="right", padx=(4, 0))
        tk.Button(
            footer, text="Save Type", relief="flat", bg=C["sel_bg"],
            fg="white", font=_font(10, bold=True), padx=12, cursor="hand2",
            command=self._save,
        ).pack(side="right")

    def _load_type(self, type_id):
        t = db.get_type_by_id(type_id)
        if not t:
            return
        self._name_var.set(t["display_name"])
        self._bib_var.set(t["bib_key"])
        self._icon_var.set(t["icon"])
        self._fields = list(t["fields"])
        self._refresh_list()

    def _refresh_list(self):
        self._fields_lb.delete(0, "end")
        for f in self._fields:
            mtype = " (multiline)" if f.get("type") == "multiline" else ""
            req = " *" if f.get("required") else ""
            self._fields_lb.insert("end", f"  {f['label']}  [{f['name']}]{mtype}{req}")

    def _add_field(self):
        d = FieldDialog(self)
        self.wait_window(d)
        if d.result:
            self._fields.append(d.result)
            self._refresh_list()

    def _edit_field(self):
        idx = self._fields_lb.curselection()
        if not idx:
            return
        d = FieldDialog(self, field=self._fields[idx[0]])
        self.wait_window(d)
        if d.result:
            self._fields[idx[0]] = d.result
            self._refresh_list()

    def _remove_field(self):
        idx = self._fields_lb.curselection()
        if idx:
            self._fields.pop(idx[0])
            self._refresh_list()

    def _move_up(self):
        idx = self._fields_lb.curselection()
        if idx and idx[0] > 0:
            i = idx[0]
            self._fields[i-1], self._fields[i] = self._fields[i], self._fields[i-1]
            self._refresh_list()
            self._fields_lb.selection_set(i-1)

    def _move_down(self):
        idx = self._fields_lb.curselection()
        if idx and idx[0] < len(self._fields) - 1:
            i = idx[0]
            self._fields[i], self._fields[i+1] = self._fields[i+1], self._fields[i]
            self._refresh_list()
            self._fields_lb.selection_set(i+1)

    def _save(self):
        name = self._name_var.get().strip()
        bib  = self._bib_var.get().strip().lower().replace(" ", "_")
        icon = self._icon_var.get().strip()
        if not name or not bib:
            messagebox.showerror("Error", "Name and BibTeX Key are required.", parent=self)
            return
        if self._type_id:
            db.update_type(self._type_id, name, icon, self._fields)
        else:
            self._type_id = db.create_type(bib, name, icon, self._fields)
        self.result = self._type_id
        self.destroy()


class FieldDialog(tk.Toplevel):
    """Add / edit a single field definition."""

    def __init__(self, parent, field=None):
        super().__init__(parent)
        self.result = None
        self.title("Field")
        self.configure(bg=C["main"])
        self.resizable(False, False)
        self._build(field or {})
        self.transient(parent)
        self.grab_set()

    def _build(self, field):
        f = tk.Frame(self, bg=C["main"], padx=20, pady=16)
        f.pack(fill="both", expand=True)
        f.grid_columnconfigure(1, weight=1)

        self._vars = {}
        rows = [
            ("name",     "Field Key (snake_case)"),
            ("label",    "Display Label"),
        ]
        for r, (key, lbl) in enumerate(rows):
            tk.Label(f, text=lbl, bg=C["main"], fg=C["subtext"],
                     font=_font(10), anchor="e", width=18).grid(
                row=r, column=0, sticky="e", pady=4, padx=(0, 8)
            )
            var = tk.StringVar(value=field.get(key, ""))
            self._vars[key] = var
            tk.Entry(f, textvariable=var, bg=C["main"], fg=C["text"],
                     relief="solid", bd=1, font=_font(11)).grid(
                row=r, column=1, sticky="ew", pady=4
            )

        # Type radio
        tk.Label(f, text="Field Type", bg=C["main"], fg=C["subtext"],
                 font=_font(10), anchor="e", width=18).grid(
            row=2, column=0, sticky="ne", pady=4, padx=(0, 8)
        )
        self._type_var = tk.StringVar(value=field.get("type", "text"))
        radio_f = tk.Frame(f, bg=C["main"])
        radio_f.grid(row=2, column=1, sticky="w", pady=4)
        for val, lbl in [("text", "Text (single line)"), ("multiline", "Text (multiline)")]:
            tk.Radiobutton(
                radio_f, text=lbl, variable=self._type_var, value=val,
                bg=C["main"], fg=C["text"], font=_font(10), activebackground=C["main"],
            ).pack(anchor="w")

        # Checkboxes
        self._req_var   = tk.BooleanVar(value=field.get("required", False))
        self._title_var = tk.BooleanVar(value=field.get("is_title", False))
        self._creator_var = tk.BooleanVar(value=field.get("is_creator", False))
        self._year_var  = tk.BooleanVar(value=field.get("is_year", False))

        for r_off, (var, lbl) in enumerate([
            (self._req_var,     "Required"),
            (self._title_var,   "Use as Title in list"),
            (self._creator_var, "Use as Creator in list"),
            (self._year_var,    "Use as Year in list"),
        ], start=3):
            tk.Checkbutton(
                f, text=lbl, variable=var,
                bg=C["main"], fg=C["text"], font=_font(10),
                activebackground=C["main"],
            ).grid(row=r_off, column=1, sticky="w", pady=2)

        # Options (one per line) – turns the field into a dropdown
        tk.Label(f, text="Preset Options", bg=C["main"], fg=C["subtext"],
                 font=_font(10), anchor="ne", width=18).grid(
            row=7, column=0, sticky="ne", pady=(8, 4), padx=(0, 8)
        )
        opt_wrap = tk.Frame(f, bg=C["main"], highlightthickness=1,
                            highlightbackground=C["btn_border"])
        opt_wrap.grid(row=7, column=1, sticky="ew", pady=(8, 4))
        self._options_txt = tk.Text(
            opt_wrap, height=5, width=32, wrap="word",
            bg=C["main"], fg=C["text"], relief="flat", bd=0,
            font=_font(10), highlightthickness=0,
        )
        self._options_txt.pack(fill="both", expand=True)
        existing_opts = field.get("options") or []
        if existing_opts:
            self._options_txt.insert("1.0", "\n".join(existing_opts))
        tk.Label(
            f, text="One per line. Leave empty for a free-text field.",
            bg=C["main"], fg=C["section_lbl"], font=_font(9),
        ).grid(row=8, column=1, sticky="w", pady=(0, 4))

        btn_row = tk.Frame(f, bg=C["main"])
        btn_row.grid(row=9, column=0, columnspan=2, pady=(16, 0))
        tk.Button(
            btn_row, text="Cancel", relief="flat", bg=C["toolbar"],
            fg=C["text"], font=_font(10), padx=12, cursor="hand2",
            command=self.destroy,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btn_row, text="OK", relief="flat", bg=C["sel_bg"],
            fg="white", font=_font(10, bold=True), padx=12, cursor="hand2",
            command=self._ok,
        ).pack(side="left")

    def _ok(self):
        name  = self._vars["name"].get().strip().lower().replace(" ", "_")
        label = self._vars["label"].get().strip()
        if not name or not label:
            messagebox.showerror("Error", "Key and Label are required.", parent=self)
            return
        opts_raw = self._options_txt.get("1.0", "end").strip()
        opts = [ln.strip() for ln in opts_raw.splitlines() if ln.strip()]
        self.result = {
            "name":       name,
            "label":      label,
            "type":       self._type_var.get(),
            "required":   self._req_var.get(),
            "is_title":   self._title_var.get(),
            "is_creator": self._creator_var.get(),
            "is_year":    self._year_var.get(),
            "options":    opts,
        }
        self.destroy()


# ── PriceCharting Import Dialog ───────────────────────────────────────────────

class PriceChartingImportDialog(tk.Toplevel):
    """Two-tab dialog: import a video-game collection from PriceCharting.

    Tab 1 — CSV: pick a CSV the user downloaded from
            PriceCharting → My Collection → Tools → Export.
    Tab 2 — API: paste a PriceCharting API token; the dialog fetches
            the member's offers live over HTTPS.

    On success ``self.result`` is set to ::

        {"rows": [<pricecharting row>, ...],
         "collection_id": <int or None>}
    """

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.result = None
        self.title("Import from PriceCharting")
        self.configure(bg=C["main"])
        self.resizable(False, False)
        self._build()
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2
        self.geometry(f"+{px - self.winfo_width() // 2}"
                      f"+{py - self.winfo_height() // 2}")

    def _build(self):
        wrap = tk.Frame(self, bg=C["main"], padx=24, pady=18)
        wrap.pack(fill="both", expand=True)

        tk.Label(
            wrap, text="Import a PriceCharting collection",
            bg=C["main"], fg=C["text"], font=_font(13, bold=True),
        ).pack(anchor="w", pady=(0, 4))
        tk.Label(
            wrap,
            text="Pulls games & consoles in, with prices, completeness "
                 "and condition pre-filled.  Two ways to get the data:",
            bg=C["main"], fg=C["subtext"], font=_font(10),
            wraplength=460, justify="left",
        ).pack(anchor="w", pady=(0, 12))

        nb = ttk.Notebook(wrap)
        nb.pack(fill="x")

        # ── CSV tab ──────────────────────────────────────────────────────────
        csv_tab = tk.Frame(nb, bg=C["main"], padx=12, pady=12)
        nb.add(csv_tab, text="  From CSV  ")
        tk.Label(
            csv_tab,
            text="On pricecharting.com, open My Collection → Tools → "
                 "Export to CSV, save the file, then pick it here.",
            bg=C["main"], fg=C["subtext"], font=_font(10),
            wraplength=440, justify="left",
        ).pack(anchor="w", pady=(0, 8))
        self._csv_path = tk.StringVar()
        row = tk.Frame(csv_tab, bg=C["main"])
        row.pack(fill="x")
        tk.Entry(
            row, textvariable=self._csv_path, bg=C["main"], fg=C["text"],
            relief="flat", bd=0, font=_font(10),
            highlightthickness=1, highlightbackground=C["btn_border"],
            highlightcolor=C["sel_bg"],
        ).pack(side="left", fill="x", expand=True, ipady=4)
        FlatButton(row, "Browse…", command=self._pick_csv)\
            .pack(side="left", padx=(6, 0))

        # ── API tab ──────────────────────────────────────────────────────────
        api_tab = tk.Frame(nb, bg=C["main"], padx=12, pady=12)
        nb.add(api_tab, text="  Via API token  ")
        tk.Label(
            api_tab,
            text="Paste your PriceCharting API token (found at "
                 "pricecharting.com → Account → API).  Requires a paid plan.",
            bg=C["main"], fg=C["subtext"], font=_font(10),
            wraplength=440, justify="left",
        ).pack(anchor="w", pady=(0, 8))
        self._api_token = tk.StringVar()
        tk.Entry(
            api_tab, textvariable=self._api_token, bg=C["main"], fg=C["text"],
            relief="flat", bd=0, font=_font(10, mono=True), show="•",
            highlightthickness=1, highlightbackground=C["btn_border"],
            highlightcolor=C["sel_bg"],
        ).pack(fill="x", ipady=4)

        self._nb = nb

        # ── Destination ──────────────────────────────────────────────────────
        tk.Label(
            wrap, text="Place imported items in:",
            bg=C["main"], fg=C["text"], font=_font(11, bold=True),
        ).pack(anchor="w", pady=(14, 4))

        current_coll = self.app.sidebar.get_current_collection_id()
        self._dest = tk.StringVar(value="new")
        choices = []
        if current_coll and current_coll != -1:
            choices.append(("current", "The currently selected library/folder"))
        choices.append(("new", "A new library named:"))
        choices.append(("none", "No library (top of catalog)"))
        for val, lbl in choices:
            tk.Radiobutton(
                wrap, text=lbl, variable=self._dest, value=val,
                bg=C["main"], fg=C["text"], activebackground=C["main"],
                font=_font(10),
            ).pack(anchor="w")
        self._dest_name = tk.StringVar(value="Video Games")
        tk.Entry(
            wrap, textvariable=self._dest_name, bg=C["main"], fg=C["text"],
            relief="flat", bd=0, font=_font(10), width=24,
            highlightthickness=1, highlightbackground=C["btn_border"],
            highlightcolor=C["sel_bg"],
        ).pack(anchor="w", padx=24, pady=(2, 0), ipady=2)

        # ── Buttons ──────────────────────────────────────────────────────────
        btns = tk.Frame(wrap, bg=C["main"])
        btns.pack(fill="x", pady=(18, 0))
        FlatButton(btns, "Cancel", command=self.destroy)\
            .pack(side="right", padx=(8, 0))
        FlatButton(btns, "Import", command=self._ok, kind="primary")\
            .pack(side="right")

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _pick_csv(self):
        path = filedialog.askopenfilename(
            title="Choose PriceCharting CSV",
            filetypes=[("CSV files", "*.csv *.tsv *.txt"), ("All files", "*.*")],
            parent=self,
        )
        if path:
            self._csv_path.set(path)
            # auto-switch to the CSV tab in case they tabbed away
            self._nb.select(0)

    def _resolve_collection(self):
        mode = self._dest.get()
        if mode == "none":
            return None
        if mode == "current":
            cid = self.app.sidebar.get_current_collection_id()
            return None if cid == -1 else cid
        # mode == "new"
        name = self._dest_name.get().strip() or "Video Games"
        return db.create_collection(name)

    def _ok(self):
        import pricecharting as pc

        tab_idx = self._nb.index(self._nb.select())
        try:
            if tab_idx == 0:
                path = self._csv_path.get().strip()
                if not path:
                    messagebox.showerror(
                        "PriceCharting", "Please choose a CSV file.",
                        parent=self,
                    )
                    return
                rows = pc.import_pricecharting_csv(path)
            else:
                token = self._api_token.get().strip()
                if not token:
                    messagebox.showerror(
                        "PriceCharting", "Please paste your API token.",
                        parent=self,
                    )
                    return
                self.config(cursor="watch")
                self.update_idletasks()
                try:
                    rows = pc.fetch_pricecharting_offers(token)
                finally:
                    self.config(cursor="")
        except pc.PriceChartingAPIError as exc:
            messagebox.showerror("PriceCharting", str(exc), parent=self)
            return
        except Exception as exc:
            messagebox.showerror(
                "PriceCharting",
                f"Couldn't read that source:\n{exc}",
                parent=self,
            )
            return

        coll_id = self._resolve_collection()
        self.result = {"rows": rows, "collection_id": coll_id}
        self.destroy()


# ── Discogs Import Dialog ─────────────────────────────────────────────────────

class DiscogsImportDialog(tk.Toplevel):
    """Import a Discogs collection CSV into the app.

    Export at: discogs.com → Profile → Collection → Export Collection (CSV).

    On success ``self.result`` is set to::

        {"rows": [<discogs item dict>, ...],
         "collection_id": <int or None>,
         "use_folders": <bool>}
    """

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app    = app
        self.result = None
        self.title("Import from Discogs")
        self.configure(bg=C["main"])
        self.resizable(False, False)
        self._build()
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2
        self.geometry(f"+{px - self.winfo_width() // 2}"
                      f"+{py - self.winfo_height() // 2}")

    def _build(self):
        wrap = tk.Frame(self, bg=C["main"], padx=24, pady=18)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="Import a Discogs collection",
                 bg=C["main"], fg=C["text"], font=_font(13, bold=True),
                 ).pack(anchor="w", pady=(0, 4))
        tk.Label(
            wrap,
            text="Imports your Discogs collection into Vinyl, CD, Cassette, "
                 "and Music items with metadata, condition, and notes pre-filled.\n"
                 "On Discogs: Profile → Collection → Export Collection  (choose CSV).",
            bg=C["main"], fg=C["subtext"], font=_font(10),
            wraplength=460, justify="left",
        ).pack(anchor="w", pady=(0, 12))

        # ── CSV file picker ───────────────────────────────────────────────────
        tk.Label(wrap, text="Discogs collection CSV:",
                 bg=C["main"], fg=C["text"], font=_font(11, bold=True),
                 ).pack(anchor="w", pady=(0, 4))
        self._csv_path = tk.StringVar()
        row = tk.Frame(wrap, bg=C["main"])
        row.pack(fill="x", pady=(0, 10))
        tk.Entry(
            row, textvariable=self._csv_path, bg=C["main"], fg=C["text"],
            relief="flat", bd=0, font=_font(10),
            highlightthickness=1, highlightbackground=C["btn_border"],
            highlightcolor=C["sel_bg"],
        ).pack(side="left", fill="x", expand=True, ipady=4)
        FlatButton(row, "Browse…", command=self._pick_csv)\
            .pack(side="left", padx=(6, 0))

        # ── Options ───────────────────────────────────────────────────────────
        tk.Frame(wrap, bg=C["border"], height=1).pack(fill="x", pady=(0, 10))
        self._use_folders = tk.BooleanVar(value=True)
        tk.Checkbutton(
            wrap,
            text="Create sub-collections from Discogs folder names",
            variable=self._use_folders,
            bg=C["main"], fg=C["text"], activebackground=C["main"],
            font=_font(10),
        ).pack(anchor="w")

        # ── Destination ───────────────────────────────────────────────────────
        tk.Label(wrap, text="Place imported items in:",
                 bg=C["main"], fg=C["text"], font=_font(11, bold=True),
                 ).pack(anchor="w", pady=(12, 4))

        current_coll = self.app.sidebar.get_current_collection_id()
        self._dest = tk.StringVar(value="new")
        choices = []
        if current_coll and current_coll != -1:
            choices.append(("current", "The currently selected library/folder"))
        choices.append(("new", "A new library named:"))
        choices.append(("none", "No library (top of catalog)"))
        for val, lbl in choices:
            tk.Radiobutton(
                wrap, text=lbl, variable=self._dest, value=val,
                bg=C["main"], fg=C["text"], activebackground=C["main"],
                font=_font(10),
            ).pack(anchor="w")
        self._dest_name = tk.StringVar(value="Discogs Collection")
        tk.Entry(
            wrap, textvariable=self._dest_name, bg=C["main"], fg=C["text"],
            relief="flat", bd=0, font=_font(10), width=28,
            highlightthickness=1, highlightbackground=C["btn_border"],
            highlightcolor=C["sel_bg"],
        ).pack(anchor="w", padx=24, pady=(2, 0), ipady=2)

        # ── Buttons ───────────────────────────────────────────────────────────
        btns = tk.Frame(wrap, bg=C["main"])
        btns.pack(fill="x", pady=(18, 0))
        FlatButton(btns, "Cancel", command=self.destroy)\
            .pack(side="right", padx=(8, 0))
        FlatButton(btns, "Import", command=self._ok, kind="primary")\
            .pack(side="right")

    def _pick_csv(self):
        path = filedialog.askopenfilename(
            title="Choose Discogs CSV",
            filetypes=[("CSV files", "*.csv *.tsv *.txt"), ("All files", "*.*")],
            parent=self,
        )
        if path:
            self._csv_path.set(path)

    def _resolve_collection(self):
        mode = self._dest.get()
        if mode == "none":
            return None
        if mode == "current":
            cid = self.app.sidebar.get_current_collection_id()
            return None if cid == -1 else cid
        name = self._dest_name.get().strip() or "Discogs Collection"
        return db.create_collection(name)

    def _ok(self):
        import discogs as dg
        path = self._csv_path.get().strip()
        if not path:
            messagebox.showerror("Discogs", "Please choose a CSV file.", parent=self)
            return
        try:
            rows = dg.import_discogs_csv(path)
        except Exception as exc:
            messagebox.showerror("Discogs", f"Couldn't read CSV:\n{exc}", parent=self)
            return
        if not rows:
            messagebox.showinfo("Discogs",
                                "No items found in that CSV. "
                                "Make sure it's a Discogs collection export.",
                                parent=self)
            return
        coll_id = self._resolve_collection()
        self.result = {
            "rows":        rows,
            "collection_id": coll_id,
            "use_folders": self._use_folders.get(),
        }
        self.destroy()


# ── Main Application Window ───────────────────────────────────────────────────

class CollectorCatalogApp:
    """Root application controller."""

    def __init__(self, root):
        self.root = root
        self.root.title("Collector Catalog")
        self.root.geometry("1200x740")
        self.root.configure(bg=C["main"])
        if sys.platform == "darwin":
            self.root.createcommand("tk::mac::Quit", self.on_quit)

        db.init_db()
        migrate_image_orientations()   # one-time: bake older imports upright
        setup_styles()
        self.root.report_callback_exception = self._on_callback_exception

        # Scrolling over a closed Combobox must not cycle its value; let the
        # event fall through to the page-level scroll handler instead.
        for ev in ("<MouseWheel>", "<Shift-MouseWheel>",
                   "<Button-4>", "<Button-5>",
                   "<ButtonPress-4>", "<ButtonPress-5>"):
            try:
                self.root.unbind_class("TCombobox", ev)
            except tk.TclError:
                pass
        self._current_collection = -1
        self._current_tag = None
        self._search_query = ""

        self._build_menu()
        self._build_toolbar()
        self._build_main()
        self._build_status()

        self.sidebar.refresh()
        self.load_items(collection_id=-1, tag_id=None)

        self.root.bind("<Control-n>", lambda _e: self._new_item())
        self.root.bind("<Control-s>", lambda _e: self.detail.save_if_dirty())
        self.root.bind("<Control-f>", lambda _e: self._focus_search())
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)

    def _on_callback_exception(self, exc_type, exc, tb):
        """Log UI callback errors and show them, instead of failing silently.

        In the packaged .app stderr goes nowhere, so an uncaught exception in
        a button handler looks like a freeze.  Write the traceback to
        ~/.collector_catalog/error.log and tell the user what happened.
        """
        import traceback
        from datetime import datetime as _dt
        text = "".join(traceback.format_exception(exc_type, exc, tb))
        try:
            log = Path.home() / ".collector_catalog" / "error.log"
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(f"\n[{_dt.now().isoformat()}]\n{text}")
        except Exception:
            pass
        try:
            messagebox.showerror(
                "Unexpected error",
                f"{exc_type.__name__}: {exc}\n\n"
                "Details were written to ~/.collector_catalog/error.log",
                parent=self.root)
        except Exception:
            pass

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_menu(self):
        mb = tk.Menu(self.root)
        self.root.configure(menu=mb)

        # File
        fm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label="File", menu=fm)
        fm.add_command(label="New Item\t⌘N", command=self._new_item)
        fm.add_command(label="New Collection", command=self._new_collection)
        fm.add_separator()
        fm.add_command(label="Import .bib…", command=self._import_bib)
        fm.add_command(label="Export .bib…", command=self._export_bib)
        fm.add_separator()
        fm.add_command(label="Import PriceCharting…", command=self._import_pricecharting)
        fm.add_command(label="Import Discogs…",       command=self._import_discogs)
        fm.add_separator()
        fm.add_command(label="Quit\t⌘Q", command=self.on_quit)

        # Edit
        em = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label="Edit", menu=em)
        em.add_command(label="Delete Selected\tDel", command=self.delete_selected)
        em.add_command(label="Duplicate Selected", command=self.duplicate_selected)
        em.add_separator()
        em.add_command(label="Find\t⌘F", command=self._focus_search)

        # Types
        tm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label="Item Types", menu=tm)
        tm.add_command(label="New Custom Type…", command=self._new_type)
        tm.add_command(label="Manage Types…",    command=self._manage_types)

    def _build_toolbar(self):
        tb = tk.Frame(self.root, bg=C["toolbar"], pady=8)
        tb.pack(fill="x", side="top")
        tk.Frame(tb, bg=C["border"], height=1).pack(fill="x", side="bottom")

        FlatButton(tb, "+ New Item", command=self._new_item, kind="primary")\
            .pack(side="left", padx=(12, 4))
        FlatButton(tb, "Delete", command=self.delete_selected, kind="danger")\
            .pack(side="left", padx=4)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", padx=10, pady=4)

        FlatButton(tb, "Import .bib", command=self._import_bib)\
            .pack(side="left", padx=2)
        FlatButton(tb, "Export .bib", command=self._export_bib)\
            .pack(side="left", padx=2)
        FlatButton(tb, "PriceCharting…",
                   command=self._import_pricecharting)\
            .pack(side="left", padx=2)
        FlatButton(tb, "Discogs…",
                   command=self._import_discogs)\
            .pack(side="left", padx=2)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", padx=10, pady=4)

        FlatButton(tb, "New Type…", command=self._new_type)\
            .pack(side="left", padx=2)

        # Search bar
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._on_search())
        sf = tk.Frame(tb, bg=C["main"], highlightthickness=1,
                      highlightbackground=C["btn_border"],
                      highlightcolor=C["primary"])
        sf.pack(side="right", padx=14)
        self._search_entry = tk.Entry(
            sf, textvariable=self._search_var,
            bg=C["main"], fg=C["text"], relief="flat",
            font=_font(11), width=24, borderwidth=0,
            highlightthickness=0, insertbackground=C["text"],
        )
        self._search_entry.pack(side="left", padx=(8, 8), pady=4)
        self._search_entry.insert(0, "Search…")
        self._search_entry.configure(fg=C["subtext"])
        self._search_entry.bind("<FocusIn>",  self._search_focus_in)
        self._search_entry.bind("<FocusOut>", self._search_focus_out)
        self._search_entry.bind("<Escape>",   self._search_clear)

    def _build_main(self):
        pane = ttk.PanedWindow(self.root, orient="horizontal")
        pane.pack(fill="both", expand=True)

        self.sidebar = Sidebar(pane, self, width=220)
        self.item_list = ItemList(pane, self, width=480)
        self.detail = DetailPanel(pane, self, width=380)

        pane.add(self.sidebar,   weight=0)
        pane.add(self.item_list, weight=1)
        pane.add(self.detail,    weight=0)

    def _build_status(self):
        self._status_var = tk.StringVar(value="Ready")
        sb = tk.Frame(self.root, bg=C["toolbar"])
        sb.pack(fill="x", side="bottom")
        tk.Frame(sb, bg=C["border"], height=1).pack(fill="x", side="top")
        tk.Label(
            sb, textvariable=self._status_var,
            bg=C["toolbar"], fg=C["subtext"], font=_font(9),
        ).pack(side="left", padx=12, pady=3)

    # ── Data loading ──────────────────────────────────────────────────────────

    def load_items(self, collection_id=-1, tag_id=None):
        self._current_collection = collection_id
        self._current_tag = tag_id
        query = self._search_query or None
        items = db.get_items(
            collection_id=collection_id,
            query=query,
            tag_id=tag_id,
        )
        self.item_list.load(items)
        n = len(items)
        self._status_var.set(f"{n} item{'s' if n != 1 else ''}")

    def _refresh(self):
        self.detail.save_if_dirty()
        self.load_items(
            collection_id=self._current_collection,
            tag_id=self._current_tag,
        )
        self.sidebar.refresh()

    # ── Item selection ────────────────────────────────────────────────────────

    def on_item_selected(self, item_id):
        self.detail.save_if_dirty()
        self.detail.load_item(item_id)

    # ── New item ──────────────────────────────────────────────────────────────

    def _new_item(self):
        # Step 1: pick the item type
        dlg = NewItemDialog(self.root, self)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        type_id, bib_key = dlg.result

        # Step 2: for books, show ISBN lookup dialog to optionally pre-fill.
        prefilled = {}
        if bib_key == "book":
            isbn_dlg = ISBNDialog(self.root)
            self.root.wait_window(isbn_dlg)
            if isbn_dlg.cancelled:
                return
            prefilled = isbn_dlg.result   # empty dict = user chose "Enter Manually"

        # Step 3: create the item (blank or pre-filled) and open it for editing.
        cid = self.sidebar.get_current_collection_id()
        coll_id = None if cid == -1 else cid
        item_id = db.create_item(type_id, prefilled, collection_id=coll_id)
        if item_id:
            self._refresh()
            self.item_list.select_item(item_id)
            self.detail.load_item(item_id)
            self.detail.focus_first_field()

    # ── Delete / duplicate ────────────────────────────────────────────────────

    def delete_selected(self):
        ids = self.item_list.get_selected_ids()
        if not ids:
            return
        noun = f"{len(ids)} item{'s' if len(ids) > 1 else ''}"
        if not messagebox.askyesno(
            "Delete", f"Permanently delete {noun}?", parent=self.root
        ):
            return
        if self.detail.current_item_id in ids:
            self.detail.load_item(None)
        db.delete_items(ids)
        self._refresh()

    def duplicate_selected(self):
        ids = self.item_list.get_selected_ids()
        if not ids:
            return
        new_id = db.duplicate_item(ids[-1])
        if new_id:
            self._refresh()
            self.item_list.select_item(new_id)
            self.detail.load_item(new_id)

    def move_to_collection(self, coll_id):
        ids = self.item_list.get_selected_ids()
        for iid in ids:
            db.update_item(iid, collection_id=coll_id if coll_id else -1)
        self._refresh()

    # ── Import / Export ───────────────────────────────────────────────────────

    def _import_bib(self):
        path = filedialog.askopenfilename(
            title="Import BibTeX",
            filetypes=[("BibTeX files", "*.bib"), ("All files", "*.*")],
            parent=self.root,
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                parsed = bib_io.parse_bib_string_full(fh.read())
            entries = parsed["entries"]
            schemas = parsed["schemas"]
        except Exception as exc:
            messagebox.showerror("Import Error", str(exc), parent=self.root)
            return

        if not entries:
            messagebox.showinfo(
                "Import", "No entries found in that .bib file.",
                parent=self.root,
            )
            return

        # Apply embedded schemas FIRST so unknown types come in with the
        # right fields/labels/options instead of bare auto-generated stubs.
        schema_types_created = 0
        for schema in schemas:
            for tdef in schema.get("types", []):
                bk = tdef.get("bib_key")
                if not bk:
                    continue
                existing = db.get_type_by_bib_key(bk)
                if existing:
                    continue  # never overwrite user's existing types
                try:
                    db.create_type(
                        bk,
                        tdef.get("display_name", bk.title()),
                        tdef.get("icon", ""),
                        tdef.get("fields", []),
                    )
                    schema_types_created += 1
                except Exception:
                    pass

        # Quick scan to show the user what's coming
        n_with_groups = sum(1 for e in entries if e["fields"].get("groups"))
        n_with_tags   = sum(1 for e in entries
                            if e["fields"].get("keywords")
                            or e["fields"].get("tags"))

        dlg = ImportBibDialog(self.root, total=len(entries),
                              n_groups=n_with_groups, n_tags=n_with_tags,
                              current_coll=self.sidebar.get_current_collection_id())
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        opts = dlg.result

        # Resolve the fallback target collection
        if opts["fallback"] == "current":
            cur = self.sidebar.get_current_collection_id()
            fallback_coll = None if cur == -1 else cur
        elif opts["fallback"] == "named":
            fallback_coll = db.get_or_create_collection_path([opts["fallback_name"]])
        else:  # "library"
            fallback_coll = None

        imported, skipped = 0, 0
        created_colls = set()

        for e in entries:
            bib_key = e["bib_key"]
            raw_fields = dict(e["fields"])

            # Pull out catalog metadata before passing to create_item
            images_raw = raw_fields.pop("_images", "")
            images = [p.strip() for p in images_raw.split(";") if p.strip()]

            tags_raw = raw_fields.pop("keywords", "") or raw_fields.pop("tags", "")
            tag_names = bib_io.parse_tags_field(tags_raw) if opts["import_tags"] else []

            groups_raw = raw_fields.pop("groups", "")
            group_paths = bib_io.parse_groups_field(groups_raw) \
                if opts["preserve_folders"] else []

            # Pick the target collection: first parsed path, else fallback
            target_coll = fallback_coll
            if group_paths:
                target_coll = db.get_or_create_collection_path(group_paths[0])
                if target_coll:
                    created_colls.add(target_coll)

            # Find or create the item type
            t = db.get_type_by_bib_key(bib_key)
            if not t:
                fields = [
                    {"name": k, "label": k.replace("_", " ").title(),
                     "type": "text", "is_title": (k == "title"),
                     "is_creator": (k in ("author", "artist", "creator")),
                     "is_year": (k in ("year", "date"))}
                    for k in raw_fields
                ]
                new_tid = db.create_type(bib_key, bib_key.title(), "", fields)
                t = db.get_type_by_id(new_tid)

            item_id = db.create_item(
                t["id"], raw_fields, target_coll, images=images
            )
            if item_id and e.get("cite_key"):
                try:
                    db.update_item(item_id, cite_key=e["cite_key"])
                except Exception:
                    pass

            # Apply tags
            if item_id and tag_names:
                for name in tag_names:
                    try:
                        db.add_item_tag(item_id, name)
                    except Exception:
                        pass

            if item_id:
                imported += 1
            else:
                skipped += 1

        self._refresh()
        parts = [f"Imported {imported} item{'s' if imported != 1 else ''}."]
        if schema_types_created:
            parts.append(f"Created {schema_types_created} item type"
                         f"{'s' if schema_types_created != 1 else ''} "
                         "from embedded schema.")
        if created_colls:
            parts.append(f"Touched {len(created_colls)} collection"
                         f"{'s' if len(created_colls) != 1 else ''}.")
        if skipped:
            parts.append(f"{skipped} skipped.")
        messagebox.showinfo("Import Complete", " ".join(parts), parent=self.root)

    def _export_bib(self):
        ids = self.item_list.get_selected_ids()
        if not ids:
            # Export all visible items
            all_items = db.get_items(
                collection_id=self._current_collection,
                tag_id=self._current_tag,
            )
            ids = [it["id"] for it in all_items]

        if not ids:
            messagebox.showinfo("Export", "No items to export.", parent=self.root)
            return

        path = filedialog.asksaveasfilename(
            title="Export BibTeX",
            defaultextension=".bib",
            filetypes=[("BibTeX files", "*.bib"), ("All files", "*.*")],
            parent=self.root,
        )
        if not path:
            return

        export_items = []
        used_type_ids = set()
        for iid in ids:
            item = db.get_item(iid)
            if not item:
                continue
            item["collection_path"] = db.get_collection_path(
                item.get("collection_id")
            )
            item["tags"] = [t["name"] for t in db.get_item_tags(iid)]
            export_items.append(item)
            if item.get("type_id"):
                used_type_ids.add(item["type_id"])

        # Build the self-describing schema header — one entry per type
        # actually referenced in this export.
        type_schemas = []
        for tid in used_type_ids:
            t = db.get_type_by_id(tid)
            if not t:
                continue
            type_schemas.append({
                "bib_key":      t["bib_key"],
                "display_name": t["display_name"],
                "icon":         t.get("icon", ""),
                "is_builtin":   bool(t.get("is_builtin")),
                "fields":       t["fields"],
            })

        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(bib_io.export_bib_string(export_items, type_schemas))
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc), parent=self.root)
            return
        messagebox.showinfo(
            "Export Complete",
            f"Exported {len(export_items)} item{'s' if len(export_items) != 1 else ''} to:\n{path}",
            parent=self.root,
        )

    # ── PriceCharting ─────────────────────────────────────────────────────────

    def _import_pricecharting(self):
        """Open the PriceCharting import dialog and apply the result."""
        dlg = PriceChartingImportDialog(self.root, self)
        self.root.wait_window(dlg)
        if not dlg.result:
            return

        rows = dlg.result["rows"]
        target_collection_id = dlg.result["collection_id"]
        if not rows:
            messagebox.showinfo(
                "PriceCharting Import",
                "No items found in that source.",
                parent=self.root,
            )
            return

        import pricecharting as pc

        vg_type = db.get_type_by_bib_key("videogame")
        cs_type = db.get_type_by_bib_key("console")
        if not vg_type or not cs_type:
            messagebox.showerror(
                "PriceCharting Import",
                "Built-in 'Video Game' and 'Video Game Console' types are missing. "
                "Try restarting the app to re-seed the database.",
                parent=self.root,
            )
            return

        imported = {"videogame": 0, "console": 0}
        for row in rows:
            t = cs_type if row["type"] == "console" else vg_type
            fields = pc.to_catalog_fields(row)
            item_id = db.create_item(
                t["id"], fields,
                collection_id=target_collection_id,
            )
            if item_id:
                imported[row["type"]] += 1

        self._refresh()
        messagebox.showinfo(
            "PriceCharting Import",
            f"Imported {imported['videogame']} games "
            f"and {imported['console']} consoles.",
            parent=self.root,
        )

    # ── Discogs ───────────────────────────────────────────────────────────────

    def _import_discogs(self):
        """Open the Discogs import dialog and apply the result."""
        dlg = DiscogsImportDialog(self.root, self)
        self.root.wait_window(dlg)
        if not dlg.result:
            return

        rows         = dlg.result["rows"]
        base_coll_id = dlg.result["collection_id"]
        use_folders  = dlg.result["use_folders"]

        if not rows:
            messagebox.showinfo("Discogs Import", "No items found in that CSV.",
                                parent=self.root)
            return

        import discogs as dg

        # Pre-load the four music-adjacent types we route into
        type_map = {}
        for bk in ("vinyl", "cd", "cassette", "music"):
            t = db.get_type_by_bib_key(bk)
            if t:
                type_map[bk] = t

        if not type_map:
            messagebox.showerror(
                "Discogs Import",
                "Could not find Vinyl, CD, Cassette, or Music item types. "
                "Restart the app to re-seed the database.",
                parent=self.root,
            )
            return

        counts: dict = {bk: 0 for bk in type_map}
        folder_colls: dict = {}   # folder_name → collection_id

        for row in rows:
            bk = row.get("type", "music")
            t  = type_map.get(bk) or type_map.get("music")
            if not t:
                continue

            # Resolve collection: folder sub-collection or base
            coll_id = base_coll_id
            if use_folders and base_coll_id is not None:
                folder = (row.get("discogs_folder") or "").strip()
                if folder and folder.lower() not in ("all", "uncategorized"):
                    if folder not in folder_colls:
                        folder_colls[folder] = db.get_or_create_collection_path(
                            [folder], parent_id=base_coll_id
                        )
                    coll_id = folder_colls[folder]

            fields = dg.to_item_fields(row)
            notes  = row.get("notes", "")

            item_id = db.create_item(t["id"], fields,
                                     collection_id=coll_id,
                                     notes=notes)
            if item_id:
                counts[bk] = counts.get(bk, 0) + 1

        self._refresh()

        total = sum(counts.values())
        parts = [f"Imported {total} item{'s' if total != 1 else ''}."]
        detail = ", ".join(
            f"{v} {k}" for k, v in sorted(counts.items()) if v
        )
        if detail:
            parts.append(f"({detail})")
        if folder_colls:
            parts.append(
                f"{len(folder_colls)} Discogs folder"
                f"{'s' if len(folder_colls) != 1 else ''} "
                "created as sub-collections."
            )
        messagebox.showinfo("Discogs Import", " ".join(parts), parent=self.root)

    # ── Types ─────────────────────────────────────────────────────────────────

    def _new_type(self):
        dlg = TypeEditorDialog(self.root, self)
        self.root.wait_window(dlg)
        if dlg.result:
            self._refresh()

    def _manage_types(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Item Types")
        win.configure(bg=C["main"])
        win.geometry("500x500")
        win.transient(self.root)

        tk.Label(
            win, text="Item Types", bg=C["main"], fg=C["text"],
            font=_font(13, bold=True),
        ).pack(padx=20, pady=(16, 8))

        vsb = ttk.Scrollbar(win, orient="vertical")
        lb = tk.Listbox(
            win, bg=C["main"], fg=C["text"], relief="solid", bd=1,
            font=_font(11), selectbackground=C["sel_bg"], selectforeground=C["sel_fg"],
            yscrollcommand=vsb.set, height=16,
        )
        vsb.configure(command=lb.yview)
        lb.pack(fill="both", expand=True, padx=20, side="left")
        vsb.pack(fill="y", side="left", pady=0, padx=(0, 20))

        all_types = db.get_all_types()
        for t in all_types:
            builtin = " (built-in)" if t["is_builtin"] else ""
            lb.insert("end", f"  {t['display_name']}  [{t['bib_key']}]{builtin}")

        btn_frame = tk.Frame(win, bg=C["main"])
        btn_frame.pack(fill="x", padx=20, pady=12)

        def on_edit():
            idx = lb.curselection()
            if not idx:
                return
            t = all_types[idx[0]]
            if t["is_builtin"]:
                messagebox.showinfo("Built-in Type",
                                    "Built-in types cannot be edited.", parent=win)
                return
            dlg = TypeEditorDialog(win, self, type_id=t["id"])
            win.wait_window(dlg)
            win.destroy()
            self._manage_types()

        def on_delete():
            idx = lb.curselection()
            if not idx:
                return
            t = all_types[idx[0]]
            if t["is_builtin"]:
                messagebox.showinfo("Built-in Type",
                                    "Built-in types cannot be deleted.", parent=win)
                return
            if messagebox.askyesno(
                "Delete Type",
                f"Delete type '{t['display_name']}'? Items of this type will become Miscellaneous.",
                parent=win,
            ):
                db.delete_type(t["id"])
                win.destroy()
                self._refresh()

        tk.Button(
            btn_frame, text="New Type", relief="flat", bg=C["sel_bg"],
            fg="white", font=_font(10), padx=10, cursor="hand2",
            command=lambda: [win.destroy(), self._new_type()],
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            btn_frame, text="Edit", relief="flat", bg=C["toolbar"],
            fg=C["text"], font=_font(10), padx=10, cursor="hand2",
            command=on_edit,
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            btn_frame, text="Delete", relief="flat", bg=C["toolbar"],
            fg=C["red"], font=_font(10), padx=10, cursor="hand2",
            command=on_delete,
        ).pack(side="left")

    # ── Search ────────────────────────────────────────────────────────────────

    def _on_search(self):
        if not hasattr(self, "item_list"):
            return
        raw = self._search_var.get()
        if raw == "Search…":
            self._search_query = ""
        else:
            self._search_query = raw
        self.load_items(
            collection_id=self._current_collection,
            tag_id=self._current_tag,
        )

    def _focus_search(self):
        self._search_entry.focus_set()
        self._search_entry.select_range(0, "end")

    def _search_focus_in(self, _e):
        if self._search_entry.get() == "Search…":
            self._search_entry.delete(0, "end")
            self._search_entry.configure(fg=C["text"])

    def _search_focus_out(self, _e):
        if not self._search_entry.get():
            self._search_entry.insert(0, "Search…")
            self._search_entry.configure(fg=C["subtext"])

    def _search_clear(self, _e):
        self._search_var.set("")
        self._search_entry.delete(0, "end")
        self._search_entry.insert(0, "Search…")
        self._search_entry.configure(fg=C["subtext"])
        self._search_query = ""
        self.load_items(
            collection_id=self._current_collection,
            tag_id=self._current_tag,
        )

    # ── Misc helpers ──────────────────────────────────────────────────────────

    def _new_collection(self):
        self.sidebar._new_collection()

    def on_quit(self):
        self.detail.save_if_dirty()
        self.root.destroy()
