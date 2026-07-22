# Collector Catalog

A desktop cataloguing app for physical collections — books, vinyl, comics,
coins, stamps, cameras, and music media. Zotero-inspired three-panel layout
(collections tree, sortable item list, detail form), BibTeX (`.bib`)
import/export so your catalog round-trips with Zotero/JabRef, and online
lookups to auto-fill item details from an ISBN, barcode, or catalog number.

## Lookup sources

- **Books** — Open Library (free, no key), Penguin Random House API (fallback)
- **Vinyl** — MusicBrainz (free, no key)
- **Games** — PriceCharting (needs a free API token)
- Discogs and PriceCharting are also used for pricing/metadata elsewhere in
  the app — see `discogs.py` / `pricecharting.py` for the (optional) tokens
  they read from the environment.

## Prerequisites

- Python 3.9+ with Tk support (`python3 -m tkinter` should open a blank
  window — on Linux this usually means installing a `python3-tk` package
  separately)

## Setup

```sh
git clone https://github.com/ldpelletier-afk/collector-catalog.git
cd collector-catalog

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
python3 main.py
```

Your catalog database lives in `~/.collector_catalog/` (created on first
run) and never touches this repo.

## Building a standalone app

```sh
./build_app.sh
```

Produces `dist/Collector Catalog.app` on macOS (or `dist/CollectorCatalog/`
elsewhere) via PyInstaller. On first launch on macOS, right-click → Open to
get past Gatekeeper (the build isn't signed/notarized).

## Notes

- Drag-and-drop image attachments require the optional `tkinterdnd2`
  package (in `requirements.txt`); without it the app runs fine, just
  without that one feature.
- `.bib` export follows Zotero/JabRef conventions (`keywords`, `groups`,
  custom entry types like `@vinyl`) so files stay usable outside this app.
