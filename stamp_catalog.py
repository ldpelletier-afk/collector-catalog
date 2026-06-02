"""Built-in reference catalog of US and Canadian stamps.

Each entry describes a stamp issue.  Selecting one from the Catalog dialog
pre-fills the ``stamp`` item type fields in the detail form.

Field names match the ``stamp`` type in ``type_defs.py``:
    title, country, year, denomination, catalog_number, color,
    perforation, watermark, condition, grade, gum, cancel, print_quantity
"""

from __future__ import annotations
from typing import List, Dict, Any

SEARCH_COLS = [
    ("title",          "Stamp",        260),
    ("country",        "Country",       90),
    ("years",          "Year(s)",       70),
    ("denomination",   "Denomination",  90),
]

DETAIL_FIELDS = [
    ("denomination",   "Denomination"),
    ("years",          "Year(s)"),
    ("color",          "Color"),
    ("perforation",    "Perforation"),
    ("watermark",      "Watermark"),
    ("catalog_number", "Scott #"),
    ("print_quantity", "Print Quantity"),
]

CATALOG: List[Dict[str, Any]] = [

    # ── United States — Classics (1847–1869) ─────────────────────────────────
    {"title": "1847 Benjamin Franklin 5c",     "series": "Classic US",  "country": "United States", "years": "1847", "denomination": "5 Cents",  "color": "Red Brown",     "perforation": "Imperforate", "catalog_number": "Scott #1",   "print_quantity": "~4.4 million", "notes": "First US postage stamp ever issued."},
    {"title": "1847 George Washington 10c",    "series": "Classic US",  "country": "United States", "years": "1847", "denomination": "10 Cents", "color": "Black",         "perforation": "Imperforate", "catalog_number": "Scott #2",   "print_quantity": "~865,000",     "notes": "2nd stamp ever; rarer than the 5c. Only ~550 used examples known."},
    {"title": "1851 Franklin 1c Blue",         "series": "Classic US",  "country": "United States", "years": "1851", "denomination": "1 Cent",   "color": "Blue",          "perforation": "Imperforate", "catalog_number": "Scott #5-9", "print_quantity": "Several million", "notes": "Multiple positions/types. Type I is the rarest."},
    {"title": "1857 Washington 3c",            "series": "Classic US",  "country": "United States", "years": "1857", "denomination": "3 Cents",  "color": "Dull Red",      "perforation": "Perf 15.5",   "catalog_number": "Scott #26",  "print_quantity": "Very large",  "notes": ""},
    {"title": "1869 Pictorial 1c Buff",        "series": "1869 Pictorials", "country": "United States", "years": "1869", "denomination": "1 Cent", "color": "Buff",        "perforation": "Perf 12",     "catalog_number": "Scott #112", "print_quantity": "",            "notes": "First US stamps to feature pictorial designs. Short-lived series."},
    {"title": "1869 Pictorial 15c Landing of Columbus", "series": "1869 Pictorials", "country": "United States", "years": "1869", "denomination": "15 Cents", "color": "Brown & Blue", "perforation": "Perf 12", "catalog_number": "Scott #118-119", "print_quantity": "", "notes": "Center inverts are among the most valuable US stamps."},
    {"title": "1869 Pictorial 24c Declaration", "series": "1869 Pictorials", "country": "United States", "years": "1869", "denomination": "24 Cents", "color": "Green & Violet", "perforation": "Perf 12", "catalog_number": "Scott #120", "print_quantity": "", "notes": ""},

    # ── US Bank Note Issues (1870–1893) ───────────────────────────────────────
    {"title": "1869-1880 Bank Note Series",    "series": "Bank Notes",  "country": "United States", "years": "1869-1880", "denomination": "Various", "color": "Various",    "perforation": "Perf 12",     "catalog_number": "Scott #134-218", "print_quantity": "", "notes": "Printed by National, Continental, and American Bank Note Companies. Large range of denominations."},

    # ── US Columbian Exposition (1893) ────────────────────────────────────────
    {"title": "1893 Columbian 1c Columbus in Sight of Land", "series": "Columbian Exposition", "country": "United States", "years": "1893", "denomination": "1 Cent",  "color": "Blue",          "perforation": "Perf 12", "catalog_number": "Scott #230", "print_quantity": "449 million",  "notes": "First US commemorative stamp series. Issued for the World's Columbian Exposition."},
    {"title": "1893 Columbian 2c Landing of Columbus",       "series": "Columbian Exposition", "country": "United States", "years": "1893", "denomination": "2 Cents", "color": "Brown Violet",  "perforation": "Perf 12", "catalog_number": "Scott #231", "print_quantity": "1.46 billion", "notes": "Most common of the Columbians."},
    {"title": "1893 Columbian $1 Isabella",                  "series": "Columbian Exposition", "country": "United States", "years": "1893", "denomination": "$1",       "color": "Salmon",        "perforation": "Perf 12", "catalog_number": "Scott #241", "print_quantity": "55,050",       "notes": ""},
    {"title": "1893 Columbian $2 Landing of Columbus",       "series": "Columbian Exposition", "country": "United States", "years": "1893", "denomination": "$2",       "color": "Brown Red",     "perforation": "Perf 12", "catalog_number": "Scott #242", "print_quantity": "45,550",       "notes": ""},
    {"title": "1893 Columbian $5 Columbus",                  "series": "Columbian Exposition", "country": "United States", "years": "1893", "denomination": "$5",       "color": "Black",         "perforation": "Perf 12", "catalog_number": "Scott #245", "print_quantity": "27,350",       "notes": "Rarest of the Columbians. Very high catalog value."},

    # ── US Definitives — Bureau Issues ────────────────────────────────────────
    {"title": "Pan-American Exposition 1901 Series", "series": "Pan-American", "country": "United States", "years": "1901", "denomination": "1c-10c", "color": "Various", "perforation": "Perf 12", "catalog_number": "Scott #294-299", "print_quantity": "", "notes": "Center inverts (1c, 2c, 4c) are major rarities. Bicolor designs."},
    {"title": "1901 Pan-American 1c Invert",         "series": "Pan-American", "country": "United States", "years": "1901", "denomination": "1 Cent", "color": "Green & Black", "perforation": "Perf 12", "catalog_number": "Scott #294a", "print_quantity": "~75 known",   "notes": "Major US stamp rarity. Center (steamer) printed upside down."},
    {"title": "1901 Pan-American 2c Invert",         "series": "Pan-American", "country": "United States", "years": "1901", "denomination": "2 Cents","color": "Carmine & Black","perforation": "Perf 12", "catalog_number": "Scott #295a", "print_quantity": "158 known",   "notes": "Most valuable of the Pan-American inverts."},

    # ── US Airmail ────────────────────────────────────────────────────────────
    {"title": "1918 24c Curtiss Jenny Airmail",         "series": "Airmail",     "country": "United States", "years": "1918", "denomination": "24 Cents", "color": "Carmine & Blue",  "perforation": "Perf 11",  "catalog_number": "Scott #C3",   "print_quantity": "3.4 million",   "notes": "First US airmail stamp. The inverted Jenny (plane upside down) is the world's most famous stamp error."},
    {"title": "1918 Inverted Jenny",                    "series": "Airmail",     "country": "United States", "years": "1918", "denomination": "24 Cents", "color": "Carmine & Blue",  "perforation": "Perf 11",  "catalog_number": "Scott #C3a",  "print_quantity": "100 (1 pane)", "notes": "The most famous US stamp error. Single example sold for $1.351M in 2016. One full pane of 100 known."},
    {"title": "1930 Graf Zeppelin 65c",                 "series": "Zeppelin",    "country": "United States", "years": "1930", "denomination": "65 Cents", "color": "Green",           "perforation": "Perf 11",  "catalog_number": "Scott #C13",  "print_quantity": "93,536",        "notes": ""},
    {"title": "1930 Graf Zeppelin $1.30",               "series": "Zeppelin",    "country": "United States", "years": "1930", "denomination": "$1.30",    "color": "Brown",           "perforation": "Perf 11",  "catalog_number": "Scott #C14",  "print_quantity": "72,428",        "notes": ""},
    {"title": "1930 Graf Zeppelin $2.60",               "series": "Zeppelin",    "country": "United States", "years": "1930", "denomination": "$2.60",    "color": "Blue",            "perforation": "Perf 11",  "catalog_number": "Scott #C15",  "print_quantity": "61,296",        "notes": "Rarest and most valuable of the Zeppelin trio."},

    # ── US Famous Americans / Liberty Series ──────────────────────────────────
    {"title": "1938 Presidential Series",       "series": "Prexie",      "country": "United States", "years": "1938-1954", "denomination": "0.5c-$5", "color": "Various",    "perforation": "Perf 11x10.5",  "catalog_number": "Scott #803-834+", "print_quantity": "",              "notes": "All US Presidents through Coolidge. Long-running definitive series."},
    {"title": "1954 Liberty Series",            "series": "Liberty",     "country": "United States", "years": "1954-1973", "denomination": "0.5c-$5", "color": "Various",    "perforation": "Various",        "catalog_number": "Scott #1030-1059+","print_quantity": "",             "notes": "Replaced the Prexie. Included historical figures and landmarks."},

    # ── US Modern Commemoratives ──────────────────────────────────────────────
    {"title": "1957 Alexander Hamilton 3c",     "series": "Commemorative","country": "United States", "years": "1957", "denomination": "3 Cents",  "color": "Dark Blue",     "perforation": "Perf 11x10.5",  "catalog_number": "Scott #1086", "print_quantity": "115 million",  "notes": ""},
    {"title": "1963 5c City Mail Delivery",     "series": "Commemorative","country": "United States", "years": "1963", "denomination": "5 Cents",  "color": "Gray",          "perforation": "Perf 11",        "catalog_number": "Scott #1238", "print_quantity": "128 million",  "notes": "Centennial of city mail delivery."},

    # ── US Forever Stamps ─────────────────────────────────────────────────────
    {"title": "2007 Liberty Bell Forever Stamp (first)", "series": "Forever", "country": "United States", "years": "2007", "denomination": "Forever (41c)", "color": "Multicolor", "perforation": "Perf 11.25", "catalog_number": "Scott #4125-4127", "print_quantity": "Billions", "notes": "First US Forever stamp; always valid for first-class letter regardless of future rate increases."},
    {"title": "2008 Forever Stamp - Flag",       "series": "Forever",     "country": "United States", "years": "2008", "denomination": "Forever", "color": "Multicolor",     "perforation": "Various",        "catalog_number": "Scott #4186+", "print_quantity": "Billions",    "notes": ""},

    # ── US Duck / Hunting Permit Stamps ──────────────────────────────────────
    {"title": "1934 Federal Duck Stamp RW1",    "series": "Federal Duck", "country": "United States", "years": "1934", "denomination": "$1",       "color": "Blue",          "perforation": "Perf 11",        "catalog_number": "RW1",         "print_quantity": "635,001",       "notes": "First Federal duck stamp. Mallards in flight design. Required for waterfowl hunting."},
    {"title": "1935 Federal Duck Stamp RW2",    "series": "Federal Duck", "country": "United States", "years": "1935", "denomination": "$1",       "color": "Rose Lake",     "perforation": "Perf 11",        "catalog_number": "RW2",         "print_quantity": "448,204",       "notes": "Canvasbacks taking to flight."},
    {"title": "1937 Federal Duck Stamp RW4",    "series": "Federal Duck", "country": "United States", "years": "1937", "denomination": "$1",       "color": "Light Green",   "perforation": "Perf 11",        "catalog_number": "RW4",         "print_quantity": "1,002,715",     "notes": "Scaup ducks."},

    # ── US Errors & Rarities ─────────────────────────────────────────────────
    {"title": "1915 Rotary Press Coil 2c Washington", "series": "Coil",   "country": "United States", "years": "1915", "denomination": "2 Cents",  "color": "Carmine",       "perforation": "Perf 10 Horizontally", "catalog_number": "Scott #454", "print_quantity": "~50 used known", "notes": "One of the rarest 20th-century US stamps."},
    {"title": "1868 Z Grill 1c Franklin",       "series": "Grill",        "country": "United States", "years": "1868", "denomination": "1 Cent",   "color": "Blue",          "perforation": "Perf 12",        "catalog_number": "Scott #85A",  "print_quantity": "2 known",       "notes": "Rarest standard US stamp. Swapped with a plate block of four in 2005."},

    # ── Canada — Classic Issues ───────────────────────────────────────────────
    {"title": "1851 3d Beaver (First Canadian Stamp)", "series": "Beaver", "country": "Canada",       "years": "1851", "denomination": "3 Pence",  "color": "Red",           "perforation": "Imperforate", "catalog_number": "Canada #1",   "print_quantity": "1.45 million",  "notes": "First Canadian stamp. Beaver design by Sandford Fleming. Highly prized."},
    {"title": "1851 6d Prince Albert",           "series": "Classic",      "country": "Canada",       "years": "1851", "denomination": "6 Pence",  "color": "Slate Violet",  "perforation": "Imperforate", "catalog_number": "Canada #2",   "print_quantity": "~51,000 used",  "notes": "Portrait of Prince Albert. Extremely rare used."},
    {"title": "1851 12d Queen Victoria Black",   "series": "Classic",      "country": "Canada",       "years": "1851", "denomination": "12 Pence", "color": "Black",         "perforation": "Imperforate", "catalog_number": "Canada #3",   "print_quantity": "~1,450",        "notes": "The 'Twelve Penny Black' is the rarest and most valuable Canadian stamp."},
    {"title": "1855 7.5d Victoria",              "series": "Classic",      "country": "Canada",       "years": "1855", "denomination": "7.5 Pence","color": "Green",         "perforation": "Imperforate", "catalog_number": "Canada #8",   "print_quantity": "~45,000",       "notes": ""},
    {"title": "1868 Small Queens Series",        "series": "Small Queens", "country": "Canada",       "years": "1868-1897", "denomination": "0.5c-15c", "color": "Various",  "perforation": "Various",     "catalog_number": "Canada #21-48+", "print_quantity": "",             "notes": "Long-running series. Intricate perforations and paper varieties create many collectible sub-types."},
    {"title": "1897 Jubilee Issue",              "series": "Jubilee",      "country": "Canada",       "years": "1897", "denomination": "0.5c-$5", "color": "Various",       "perforation": "Perf 12",     "catalog_number": "Canada #50-65", "print_quantity": "",              "notes": "Issued for Queen Victoria's Diamond Jubilee. The $5 is exceptionally rare."},
    {"title": "1897 Diamond Jubilee $5",         "series": "Jubilee",      "country": "Canada",       "years": "1897", "denomination": "$5",       "color": "Olive Green",   "perforation": "Perf 12",     "catalog_number": "Canada #65",  "print_quantity": "~16,000",       "notes": "Most valuable classic Canadian stamp in top grade."},

    # ── Canada — Early 20th Century ───────────────────────────────────────────
    {"title": "1898 Imperial Penny Postage (Xmas Stamp)", "series": "Imperial", "country": "Canada", "years": "1898", "denomination": "2 Cents",  "color": "Carmine & Black","perforation": "Perf 12",    "catalog_number": "Canada #85-86", "print_quantity": "~15 million",  "notes": "World's first Christmas stamp. Map of the British Empire in red."},
    {"title": "1908 Quebec Tercentenary",        "series": "Quebec",       "country": "Canada",       "years": "1908", "denomination": "0.5c-$1", "color": "Various",       "perforation": "Perf 12",     "catalog_number": "Canada #96-103", "print_quantity": "",             "notes": "Commemorates the 300th anniversary of Quebec City. Beautiful pictorials."},
    {"title": "1927 Confederation Commemoratives", "series": "Confederation","country": "Canada",      "years": "1927", "denomination": "1c-12c", "color": "Various",       "perforation": "Perf 12",     "catalog_number": "Canada #141-145", "print_quantity": "",            "notes": "60th anniversary of Confederation."},

    # ── Canada — George VI Era ────────────────────────────────────────────────
    {"title": "1942 War Issue Definitives",      "series": "War Issue",    "country": "Canada",       "years": "1942-1943", "denomination": "1c-$1", "color": "Various",    "perforation": "Perf 12",     "catalog_number": "Canada #249-262", "print_quantity": "",            "notes": "Wartime subjects including factories, munitions, and military. Very popular with collectors."},
    {"title": "1946 Peace Issue",                "series": "Peace",        "country": "Canada",       "years": "1946-1947", "denomination": "8c-14c","color": "Various",     "perforation": "Perf 12",     "catalog_number": "Canada #268-273", "print_quantity": "",            "notes": ""},

    # ── Canada — Elizabeth II (early) ────────────────────────────────────────
    {"title": "1953 Karsh Portrait Definitives", "series": "Karsh",        "country": "Canada",       "years": "1953-1954", "denomination": "1c-$1", "color": "Various",    "perforation": "Perf 12",     "catalog_number": "Canada #325-340", "print_quantity": "",            "notes": "Yousuf Karsh portrait of Queen Elizabeth II."},
    {"title": "1954 Wildlife Definitives",       "series": "Wildlife",     "country": "Canada",       "years": "1954-1963", "denomination": "1c-$1", "color": "Various",    "perforation": "Various",     "catalog_number": "Canada #337-341+","print_quantity": "",            "notes": "Iconic Canadian wildlife subjects — beaver, gannet, caribou."},
    {"title": "1967 Centennial Definitives",     "series": "Centennial",   "country": "Canada",       "years": "1967-1973", "denomination": "1c-$1", "color": "Various",    "perforation": "Various",     "catalog_number": "Canada #454-465+","print_quantity": "",            "notes": "Confederation centennial. Scenic Canada designs. Numerous varieties."},

    # ── Canada — Modern Commemoratives ───────────────────────────────────────
    {"title": "1988 Calgary Winter Olympics",    "series": "Olympics",     "country": "Canada",       "years": "1988", "denomination": "37c-74c", "color": "Multicolor",    "perforation": "Perf 12.5",   "catalog_number": "Canada #1172-1173", "print_quantity": "",          "notes": ""},
    {"title": "1992 Canada Day - Provincial Flags", "series": "Flags",    "country": "Canada",       "years": "1992", "denomination": "42 Cents","color": "Multicolor",     "perforation": "Perf 13.1",   "catalog_number": "Canada #1430-1444","print_quantity": "",           "notes": "All 12 provincial/territorial flags plus Canada flag."},
    {"title": "1994 Prehistoric Life in Canada", "series": "Prehistoric",  "country": "Canada",       "years": "1994", "denomination": "43 Cents","color": "Multicolor",     "perforation": "Perf 12.5",   "catalog_number": "Canada #1532-1535","print_quantity": "",          "notes": "Dinosaurs and prehistoric sea life."},
    {"title": "2000 Millennium Collection",      "series": "Millennium",   "country": "Canada",       "years": "2000", "denomination": "46 Cents","color": "Multicolor",     "perforation": "Perf 13.1",   "catalog_number": "Canada #1813-1822","print_quantity": "",          "notes": "17 se-tenant stamps depicting Canadian achievements."},
    {"title": "2013 Canadian Wildlife Definitives", "series": "Wildlife",  "country": "Canada",       "years": "2013-present", "denomination": "P (Permanent)", "color": "Multicolor", "perforation": "Various", "catalog_number": "Canada #2621+", "print_quantity": "",      "notes": "Replaced the Queen's portrait on some definitives. Various wildlife subjects."},
]


def search(query: str, country: str = "All") -> List[Dict[str, Any]]:
    q = query.strip().lower()
    results = []
    for entry in CATALOG:
        if country != "All" and entry.get("country", "") != country:
            continue
        haystack = " ".join([
            entry.get("title", ""),
            entry.get("series", ""),
            entry.get("denomination", ""),
            entry.get("catalog_number", ""),
            entry.get("notes", ""),
        ]).lower()
        if not q or q in haystack:
            results.append(entry)
    return results


def to_fields(entry: Dict[str, Any]) -> Dict[str, str]:
    return {k: v for k, v in {
        "title":          entry.get("title", ""),
        "country":        entry.get("country", ""),
        "year":           entry.get("years", ""),
        "denomination":   entry.get("denomination", ""),
        "catalog_number": entry.get("catalog_number", ""),
        "color":          entry.get("color", ""),
        "perforation":    entry.get("perforation", ""),
        "watermark":      entry.get("watermark", ""),
        "print_quantity": entry.get("print_quantity", ""),
    }.items() if v}
