"""Built-in reference catalog of collectible cameras and lenses.

Each entry describes a camera model or notable lens.  Selecting one
pre-fills the ``camera`` or ``lens`` item type fields.

Fields (camera): title, make, year, type, format, mount
Fields (lens):   title, make, mount, focal_length, max_aperture, lens_type, year
"""

from __future__ import annotations
from typing import List, Dict, Any

SEARCH_COLS = [
    ("title",   "Model",          230),
    ("make",    "Make",           120),
    ("year",    "Year(s)",         70),
    ("category","Category",       100),
]

DETAIL_FIELDS = [
    ("make",        "Make"),
    ("year",        "Year(s)"),
    ("type",        "Camera Type"),
    ("format",      "Format"),
    ("mount",       "Mount"),
    ("category",    "Category"),
]

CATALOG: List[Dict[str, Any]] = [

    # ── Leica Rangefinders ────────────────────────────────────────────────────
    {"title": "Leica I (Model A)",         "make": "Leica",    "year": "1925-1930", "type": "Rangefinder", "format": "35mm Film",    "mount": "Leica screw (L39)",   "category": "Camera", "notes": "First mass-produced 35mm camera. Launched modern 35mm photography."},
    {"title": "Leica II",                  "make": "Leica",    "year": "1932-1948", "type": "Rangefinder", "format": "35mm Film",    "mount": "Leica screw (L39)",   "category": "Camera", "notes": "First Leica with built-in rangefinder."},
    {"title": "Leica IIIa",                "make": "Leica",    "year": "1935-1950", "type": "Rangefinder", "format": "35mm Film",    "mount": "Leica screw (L39)",   "category": "Camera", "notes": "Added 1/1000s shutter speed. Very popular collector camera."},
    {"title": "Leica IIIf",                "make": "Leica",    "year": "1950-1957", "type": "Rangefinder", "format": "35mm Film",    "mount": "Leica screw (L39)",   "category": "Camera", "notes": "Flash sync added. Black dial version highly sought."},
    {"title": "Leica M3",                  "make": "Leica",    "year": "1954-1966", "type": "Rangefinder", "format": "35mm Film",    "mount": "Leica M",             "category": "Camera", "notes": "Introduced the M bayonet mount. Considered the finest 35mm camera ever made. Double-stroke early versions are most valuable."},
    {"title": "Leica M2",                  "make": "Leica",    "year": "1957-1968", "type": "Rangefinder", "format": "35mm Film",    "mount": "Leica M",             "category": "Camera", "notes": "Simpler/cheaper M3. Popular with photojournalists."},
    {"title": "Leica M6",                  "make": "Leica",    "year": "1984-1998", "type": "Rangefinder", "format": "35mm Film",    "mount": "Leica M",             "category": "Camera", "notes": "Built-in TTL meter. Most popular of all Leica Ms."},
    {"title": "Leica M6 TTL",              "make": "Leica",    "year": "1998-2002", "type": "Rangefinder", "format": "35mm Film",    "mount": "Leica M",             "category": "Camera", "notes": "Through-the-lens flash metering. Final M6 version."},
    {"title": "Leica MP",                  "make": "Leica",    "year": "2003-present","type": "Rangefinder","format": "35mm Film",   "mount": "Leica M",             "category": "Camera", "notes": "Modern mechanical camera with M3-style meter. No electronics save the meter."},
    {"title": "Leica M-A (Typ 127)",       "make": "Leica",    "year": "2014-present","type": "Rangefinder","format": "35mm Film",   "mount": "Leica M",             "category": "Camera", "notes": "Fully mechanical. No meter. Purist's camera."},
    {"title": "Leica M (Typ 240)",         "make": "Leica",    "year": "2012-2019", "type": "Rangefinder", "format": "Full Frame",   "mount": "Leica M",             "category": "Camera", "notes": "First M with video. 24MP CMOS sensor."},
    {"title": "Leica M11",                 "make": "Leica",    "year": "2022-present","type": "Rangefinder","format": "Full Frame",   "mount": "Leica M",             "category": "Camera", "notes": "60MP BSI CMOS. Triple resolution modes."},
    {"title": "Leica M Monochrom (Typ 246)","make": "Leica",   "year": "2015-2020", "type": "Rangefinder", "format": "Full Frame",   "mount": "Leica M",             "category": "Camera", "notes": "Black-and-white only sensor. No color filter array."},

    # ── Leica SLRs ───────────────────────────────────────────────────────────
    {"title": "Leica R3",                  "make": "Leica",    "year": "1976-1980", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Leica R",             "category": "Camera", "notes": "Co-developed with Minolta. First R-series with through-the-lens OTF metering."},
    {"title": "Leica R8",                  "make": "Leica",    "year": "1996-2002", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Leica R",             "category": "Camera", "notes": "Distinctive angular body. Matrix metering."},

    # ── Nikon ────────────────────────────────────────────────────────────────
    {"title": "Nikon SP",                  "make": "Nikon",    "year": "1957-1962", "type": "Rangefinder", "format": "35mm Film",    "mount": "Nikon S",             "category": "Camera", "notes": "Top-of-the-line Nikon rangefinder. Competitors to Leica M3 in the 1950s."},
    {"title": "Nikon F",                   "make": "Nikon",    "year": "1959-1973", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Nikon F",             "category": "Camera", "notes": "Launched the professional SLR era. Interchangeable finders and screens."},
    {"title": "Nikon F2",                  "make": "Nikon",    "year": "1971-1980", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Nikon F",             "category": "Camera", "notes": "Improved F with lighter body. Titanium shutter curtain."},
    {"title": "Nikon F2 Photomic",         "make": "Nikon",    "year": "1971",      "type": "SLR (film)",  "format": "35mm Film",    "mount": "Nikon F",             "category": "Camera", "notes": "F2 body with DP-1 metered prism finder."},
    {"title": "Nikon F3",                  "make": "Nikon",    "year": "1980-2001", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Nikon F",             "category": "Camera", "notes": "Designed by Giorgetto Giugiaro. Electronic shutter, long production run."},
    {"title": "Nikon FM2",                 "make": "Nikon",    "year": "1982-2001", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Nikon F",             "category": "Camera", "notes": "Mechanical 1/4000s shutter. Titanium honeycomb shutter curtain."},
    {"title": "Nikon FE2",                 "make": "Nikon",    "year": "1983-1987", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Nikon F",             "category": "Camera", "notes": "Aperture-priority AE with 1/4000s."},
    {"title": "Nikon F4",                  "make": "Nikon",    "year": "1988-1997", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Nikon F",             "category": "Camera", "notes": "First autofocus F-series. Modular design with interchangeable grips."},
    {"title": "Nikon F5",                  "make": "Nikon",    "year": "1996-2004", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Nikon F",             "category": "Camera", "notes": "8fps, multi-CAM 1300 AF. The professional 35mm standard in the late 1990s."},
    {"title": "Nikon D1",                  "make": "Nikon",    "year": "1999-2001", "type": "DSLR",        "format": "APS-C",        "mount": "Nikon F",             "category": "Camera", "notes": "First affordable professional digital SLR. 2.7MP."},
    {"title": "Nikon D3",                  "make": "Nikon",    "year": "2007-2009", "type": "DSLR",        "format": "35mm Full Frame","mount": "Nikon F",            "category": "Camera", "notes": "First Nikon full-frame DSLR. Exceptional ISO performance for its time."},
    {"title": "Nikon Df",                  "make": "Nikon",    "year": "2013-2020", "type": "DSLR",        "format": "35mm Full Frame","mount": "Nikon F",            "category": "Camera", "notes": "Retro design with traditional dials. Uses D4 sensor."},
    {"title": "Nikon Z6",                  "make": "Nikon",    "year": "2018-present","type": "Mirrorless", "format": "35mm Full Frame","mount": "Nikon Z",           "category": "Camera", "notes": "24MP full-frame mirrorless. Video-focused complement to Z7."},
    {"title": "Nikon Z9",                  "make": "Nikon",    "year": "2021-present","type": "Mirrorless", "format": "35mm Full Frame","mount": "Nikon Z",           "category": "Camera", "notes": "45.7MP, blackout-free. No mechanical shutter. Top-of-line Z body."},

    # ── Canon ────────────────────────────────────────────────────────────────
    {"title": "Canon F-1 (original)",      "make": "Canon",    "year": "1971-1981", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Canon FD",            "category": "Camera", "notes": "Canon's first pro SLR. Modular system."},
    {"title": "Canon F-1 New",             "make": "Canon",    "year": "1981-1992", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Canon FD",            "category": "Camera", "notes": "Redesigned for 1980 Olympics. AE Motor Drive FN."},
    {"title": "Canon AE-1",                "make": "Canon",    "year": "1976-1984", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Canon FD",            "category": "Camera", "notes": "Best-selling SLR of the 1970s-80s. Shutter-priority AE. Introduced microprocessor control."},
    {"title": "Canon AE-1 Program",        "make": "Canon",    "year": "1981-1987", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Canon FD",            "category": "Camera", "notes": "Program AE added. 'Program' became a buzzword."},
    {"title": "Canon EOS 1v",              "make": "Canon",    "year": "2000-2018", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Canon EF",            "category": "Camera", "notes": "Last Canon 35mm SLR. Professional weather-sealed body. 10fps."},
    {"title": "Canon EOS 5D Mark II",      "make": "Canon",    "year": "2008-2012", "type": "DSLR",        "format": "35mm Full Frame","mount": "Canon EF",           "category": "Camera", "notes": "First DSLR to capture 1080p video. Revolutionized video production."},
    {"title": "Canon EOS R5",              "make": "Canon",    "year": "2020-present","type": "Mirrorless", "format": "35mm Full Frame","mount": "Canon RF",           "category": "Camera", "notes": "45MP, 8K RAW video, IBIS. Flagship mirrorless."},

    # ── Minolta ───────────────────────────────────────────────────────────────
    {"title": "Minolta SR-T 101",          "make": "Minolta",  "year": "1966-1975", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Minolta MD",          "category": "Camera", "notes": "CLC metering (Contrast Light Compensator). Rugged and reliable. Very popular with students."},
    {"title": "Minolta X-700",             "make": "Minolta",  "year": "1981-2001", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Minolta MD",          "category": "Camera", "notes": "Program AE, aperture priority. EOSA Award winner."},
    {"title": "Minolta X-570",             "make": "Minolta",  "year": "1983-1988", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Minolta MD",          "category": "Camera", "notes": ""},
    {"title": "Minolta Maxxum 7000 (Alpha 7000)", "make": "Minolta", "year": "1985-1994", "type": "SLR (film)", "format": "35mm Film", "mount": "Minolta A",          "category": "Camera", "notes": "World's first autofocus SLR with integral motor. Revolutionary. Basis for the Sony A-mount."},
    {"title": "Minolta Dynax 9 (Maxxum 9)","make": "Minolta",  "year": "1998-2005", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Minolta A",           "category": "Camera", "notes": "Top-of-line Minolta AF film SLR. Titanium body."},

    # ── Olympus ──────────────────────────────────────────────────────────────
    {"title": "Olympus OM-1",              "make": "Olympus",  "year": "1972-1987", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Olympus OM",          "category": "Camera", "notes": "Designed by Yoshihisa Maitani. Compact pro SLR. Purely mechanical (OM-1n has flash sync)."},
    {"title": "Olympus OM-1n",             "make": "Olympus",  "year": "1979-1987", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Olympus OM",          "category": "Camera", "notes": "Updated OM-1 with motor drive sync and improved flash."},
    {"title": "Olympus OM-2",              "make": "Olympus",  "year": "1975-1984", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Olympus OM",          "category": "Camera", "notes": "First camera with OTF metering during exposure (off-film plane metering). Auto-exposure."},
    {"title": "Olympus XA",                "make": "Olympus",  "year": "1979-1984", "type": "Rangefinder", "format": "35mm Film",    "mount": "Fixed (Zuiko 35mm f/2.8)","category": "Camera","notes": "Ultra-compact rangefinder with clamshell. Designed by Maitani. Cult classic."},
    {"title": "Olympus Stylus Epic (mju-II)","make": "Olympus","year": "1997-2006", "type": "Point & Shoot","format": "35mm Film",   "mount": "Fixed (35mm f/2.8)",  "category": "Camera", "notes": "Extremely popular compact. Weather resistant. Film photography revival camera."},

    # ── Contax / Yashica ─────────────────────────────────────────────────────
    {"title": "Contax RTS",                "make": "Contax",   "year": "1975-1982", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Contax/Yashica",      "category": "Camera", "notes": "First Contax SLR after WWII. Porsche Design. Premium Zeiss lenses."},
    {"title": "Contax RTS III",            "make": "Contax",   "year": "1992-2003", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Contax/Yashica",      "category": "Camera", "notes": "Vacuum film plate. Highly regarded for film flatness."},
    {"title": "Contax G2",                 "make": "Contax",   "year": "1996-2005", "type": "Rangefinder", "format": "35mm Film",    "mount": "Contax G",            "category": "Camera", "notes": "Autofocus rangefinder. Titanium body. Used superb Carl Zeiss lenses."},
    {"title": "Contax T2",                 "make": "Contax",   "year": "1990-2001", "type": "Point & Shoot","format": "35mm Film",   "mount": "Fixed (Sonnar 38mm f/2.8)","category": "Camera","notes": "Titanium compact with Zeiss Sonnar lens. Celebrity favorite; prices skyrocketed in 2020s."},
    {"title": "Contax T3",                 "make": "Contax",   "year": "2001-2005", "type": "Point & Shoot","format": "35mm Film",   "mount": "Fixed (Sonnar 35mm f/2.8)","category": "Camera","notes": "Updated T2 with 35mm lens and titanium body. Very scarce."},

    # ── Rolleiflex / TLR ────────────────────────────────────────────────────
    {"title": "Rolleiflex 2.8F",           "make": "Rolleiflex","year": "1960-1981","type": "TLR",         "format": "120 Film",     "mount": "Fixed (Zeiss Planar 80mm f/2.8)","category":"Camera","notes":"Pinnacle of TLR design. Used by Diane Arbus, Vivian Maier, Richard Avedon."},
    {"title": "Rolleiflex 3.5F",           "make": "Rolleiflex","year": "1958-1980","type": "TLR",         "format": "120 Film",     "mount": "Fixed (Zeiss Planar 75mm f/3.5)","category":"Camera","notes":"More affordable than 2.8F. Excellent quality."},
    {"title": "Rolleicord Va",             "make": "Rolleiflex","year": "1957-1962","type": "TLR",         "format": "120 Film",     "mount": "Fixed (Xenar 75mm f/3.5)","category":"Camera","notes":"Budget Rolleiflex line. Simpler Xenar lens vs Zeiss/Schneider."},

    # ── Hasselblad ───────────────────────────────────────────────────────────
    {"title": "Hasselblad 500C",           "make": "Hasselblad","year": "1957-1970","type": "Medium Format","format": "120 Film",     "mount": "Hasselblad V",        "category": "Camera", "notes": "Used on the moon during Apollo missions. Interchangeable backs, finders, lenses."},
    {"title": "Hasselblad 500C/M",         "make": "Hasselblad","year": "1970-1994","type": "Medium Format","format": "120 Film",     "mount": "Hasselblad V",        "category": "Camera", "notes": "Updated 500C with interchangeable focusing screens."},
    {"title": "Hasselblad 503CW",          "make": "Hasselblad","year": "1996-2013","type": "Medium Format","format": "120 Film",     "mount": "Hasselblad V",        "category": "Camera", "notes": "Final V-system camera with film winding improvements."},
    {"title": "Hasselblad X1D II 50C",     "make": "Hasselblad","year": "2019-present","type": "Mirrorless","format": "Medium Format","mount": "Hasselblad X",        "category": "Camera", "notes": "50MP medium format mirrorless. Compact for medium format."},

    # ── Pentax / Ricoh ───────────────────────────────────────────────────────
    {"title": "Pentax K1000",              "make": "Pentax",   "year": "1976-1997", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Pentax K",            "category": "Camera", "notes": "Simple, fully mechanical SLR. No batteries needed to shoot. Popular for photography students. 20-year production run."},
    {"title": "Pentax LX",                 "make": "Pentax",   "year": "1980-2001", "type": "SLR (film)",  "format": "35mm Film",    "mount": "Pentax K",            "category": "Camera", "notes": "Professional Pentax SLR. Weather sealed. Modular finders."},
    {"title": "Pentax 67",                 "make": "Pentax",   "year": "1969-1989", "type": "Medium Format","format": "120 Film",     "mount": "Pentax 67",           "category": "Camera", "notes": "6x7cm negatives. Known as 'The Beast'. Very popular for portraits and landscapes."},
    {"title": "Pentax 67II",               "make": "Pentax",   "year": "1998-2009", "type": "Medium Format","format": "120 Film",     "mount": "Pentax 67",           "category": "Camera", "notes": "Updated 67 with improved metering and flash sync."},

    # ── Polaroid ─────────────────────────────────────────────────────────────
    {"title": "Polaroid SX-70 Alpha 1",    "make": "Polaroid", "year": "1972-1977", "type": "Instant",     "format": "Instant",      "mount": "Fixed",               "category": "Camera", "notes": "First SX-70. Folding SLR. Genuine leather cover. Andy Warhol's favorite camera."},
    {"title": "Polaroid 690 (Spectra)",    "make": "Polaroid", "year": "1986-1999", "type": "Instant",     "format": "Instant",      "mount": "Fixed",               "category": "Camera", "notes": "Higher resolution format than SX-70. Glass lens."},
    {"title": "Polaroid 600 Land Camera",  "make": "Polaroid", "year": "1981-2006", "type": "Instant",     "format": "Instant",      "mount": "Fixed",               "category": "Camera", "notes": "Most common Polaroid format. Many color variants."},

    # ── Notable Lenses ────────────────────────────────────────────────────────
    {"title": "Leica Summilux-M 35mm f/1.4 ASPH",       "make": "Leica",          "mount": "Leica M", "focal_length": "35mm",  "max_aperture": "f/1.4", "lens_type": "Prime",     "year": "1994-present",    "category": "Lens", "notes": "FLE version (2010) improved close focus. One of the most sought Leica primes."},
    {"title": "Leica Summicron-M 50mm f/2 (Rigid)",      "make": "Leica",          "mount": "Leica M", "focal_length": "50mm",  "max_aperture": "f/2",   "lens_type": "Prime",     "year": "1956-1968",       "category": "Lens", "notes": "Rigid version with distinctive look. Exceptional optical quality."},
    {"title": "Leica Noctilux-M 50mm f/0.95",            "make": "Leica",          "mount": "Leica M", "focal_length": "50mm",  "max_aperture": "f/0.95","lens_type": "Prime",     "year": "2008-present",    "category": "Lens", "notes": "Fastest production lens for decades. Unique rendering at f/0.95."},
    {"title": "Zeiss Otus 55mm f/1.4",                   "make": "Carl Zeiss",     "mount": "Nikon F / Canon EF", "focal_length": "55mm", "max_aperture": "f/1.4", "lens_type": "Prime", "year": "2013-present",  "category": "Lens", "notes": "Considered one of the sharpest 50mm-range lenses ever made. Manual focus only."},
    {"title": "Canon 50mm f/0.95 Dream Lens (TV lens)",  "make": "Canon",          "mount": "Canon 7 (L39 adapter)", "focal_length": "50mm", "max_aperture": "f/0.95", "lens_type": "Prime", "year": "1961",       "category": "Lens", "notes": "Originally for Canon 7 rangefinder. Cult lens for distinctive bokeh. Adapted to mirrorless."},
    {"title": "Voigtlander Nokton 50mm f/1.1",           "make": "Voigtlander",    "mount": "Leica M", "focal_length": "50mm",  "max_aperture": "f/1.1", "lens_type": "Prime",     "year": "2004-present",    "category": "Lens", "notes": "Fastest affordable M-mount lens. Unique rendering at wide apertures."},
    {"title": "Nikon Noct-Nikkor 58mm f/1.2",            "make": "Nikon",          "mount": "Nikon F", "focal_length": "58mm",  "max_aperture": "f/1.2", "lens_type": "Prime",     "year": "1977-1998",       "category": "Lens", "notes": "Hand-polished aspherical element. Legendary rendering. Very sought-after."},
    {"title": "Zeiss Planar T* 50mm f/0.7 (NASA)",       "make": "Carl Zeiss",     "mount": "Arriflex (adapted)", "focal_length": "50mm", "max_aperture": "f/0.7", "lens_type": "Prime", "year": "1966",          "category": "Lens", "notes": "Made for NASA (Apollo program). Stanley Kubrick bought 3 to film 'Barry Lyndon' by candlelight. Rarest collectible lens."},
    {"title": "Schneider-Kreuznach Curtagon 35mm f/1.8", "make": "Schneider",      "mount": "Exakta / M42", "focal_length": "35mm", "max_aperture": "f/1.8", "lens_type": "Wide",  "year": "1958-1965",       "category": "Lens", "notes": "Vintage radioactive lens (thorium glass). Warm rendering. Collectible."},
    {"title": "Canon FD 85mm f/1.2 L",                   "make": "Canon",          "mount": "Canon FD", "focal_length": "85mm", "max_aperture": "f/1.2", "lens_type": "Portrait",  "year": "1976-1989",       "category": "Lens", "notes": "Exotic aperture glass. Very sought for portrait rendering on adapted mirrorless."},
]

# 1980-present film & digital bodies and lenses live in a separate data
# module to keep this file manageable.
from camera_catalog_expansion import EXPANSION
CATALOG.extend(EXPANSION)


def search(query: str, category: str = "All") -> List[Dict[str, Any]]:
    q = query.strip().lower()
    results = []
    for entry in CATALOG:
        if category != "All" and entry.get("category", "") != category:
            continue
        haystack = " ".join([
            entry.get("title", ""),
            entry.get("make", ""),
            entry.get("type", ""),
            entry.get("mount", ""),
            entry.get("notes", ""),
        ]).lower()
        if not q or q in haystack:
            results.append(entry)
    return results


def to_fields(entry: Dict[str, Any]) -> Dict[str, str]:
    cat = entry.get("category", "Camera")
    if cat == "Lens":
        return {k: v for k, v in {
            "title":        entry.get("title", ""),
            "make":         entry.get("make", ""),
            "mount":        entry.get("mount", ""),
            "focal_length": entry.get("focal_length", ""),
            "max_aperture": entry.get("max_aperture", ""),
            "lens_type":    entry.get("lens_type", ""),
            "year":         entry.get("year", ""),
        }.items() if v}
    return {k: v for k, v in {
        "title":  entry.get("title", ""),
        "make":   entry.get("make", ""),
        "year":   entry.get("year", ""),
        "type":   entry.get("type", ""),
        "format": entry.get("format", ""),
        "mount":  entry.get("mount", ""),
    }.items() if v}
