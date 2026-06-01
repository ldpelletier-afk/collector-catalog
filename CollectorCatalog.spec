# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Collector Catalog
#
# Build:    python3 -m PyInstaller CollectorCatalog.spec --noconfirm
# Output:   dist/Collector Catalog.app  (macOS)
#           dist/CollectorCatalog/      (Windows / Linux)

import sys
from pathlib import Path

block_cipher = None
HERE = Path(SPECPATH).resolve()

# Include the project's Python sources alongside the bundle so type_defs etc.
# are reachable at runtime.
datas = []

a = Analysis(
    ["main.py"],
    pathex=[str(HERE)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "PIL._tkinter_finder",  # ensure Pillow's tk integration ships
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # We don't need any of these — slims the bundle significantly.
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "pytest",
    ],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CollectorCatalog",
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="CollectorCatalog",
)

# macOS .app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Collector Catalog.app",
        bundle_identifier="com.dimitripelletier.collectorcatalog",
        info_plist={
            "CFBundleName":               "Collector Catalog",
            "CFBundleDisplayName":        "Collector Catalog",
            "CFBundleShortVersionString": "0.1.0",
            "CFBundleVersion":            "0.1.0",
            "NSHighResolutionCapable":    True,
            "LSMinimumSystemVersion":     "11.0",
            "NSHumanReadableCopyright":   "© 2026 Dimitri Pelletier",
        },
    )
