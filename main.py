#!/usr/bin/env python3
"""Collector Catalog — entry point."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from app import CollectorCatalogApp


def main():
    root = tk.Tk()

    # macOS: bring window to front
    if sys.platform == "darwin":
        try:
            root.tk.call("::tk::unsupported::MacWindowStyle", "style",
                         root._w, "document", "closeBox collapseBox resizable")
        except Exception:
            pass

    app = CollectorCatalogApp(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
