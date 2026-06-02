"""Built-in reference catalog of notable vinyl records and pressings.

Covers highly collectible albums, first pressings, and landmark records.
The MusicBrainz Lookup button handles arbitrary records; this catalog
covers the most sought-after issues for quick offline entry.

Fields: title, artist, year, label, catalog_number, format, pressing,
        country, genre
"""

from __future__ import annotations
from typing import List, Dict, Any

SEARCH_COLS = [
    ("title",   "Album",          220),
    ("artist",  "Artist",         160),
    ("year",    "Year",            60),
    ("genre",   "Genre",           90),
]

DETAIL_FIELDS = [
    ("artist",         "Artist"),
    ("year",           "Year"),
    ("label",          "Label"),
    ("catalog_number", "Catalog #"),
    ("format",         "Format"),
    ("pressing",       "Pressing"),
    ("country",        "Country"),
    ("genre",          "Genre"),
]

CATALOG: List[Dict[str, Any]] = [

    # ── Rock / Classic Rock ───────────────────────────────────────────────────
    {"title": "Sgt. Pepper's Lonely Hearts Club Band",  "artist": "The Beatles",       "year": "1967", "label": "Parlophone",      "catalog_number": "PMC 7027 (mono) / PCS 7027 (stereo)", "format": "LP", "pressing": "UK First Press", "country": "UK",  "genre": "Rock",          "notes": "UK mono first press is the most valuable. Look for 'A Parlophone Production' inner ring text."},
    {"title": "Abbey Road",                             "artist": "The Beatles",       "year": "1969", "label": "Apple Records",   "catalog_number": "PCS 7088",  "format": "LP", "pressing": "UK First Press",   "country": "UK",  "genre": "Rock",          "notes": "UK first press has 'Her Majesty' unlisted on label. Apple with inner ring."},
    {"title": "The White Album (The Beatles)",          "artist": "The Beatles",       "year": "1968", "label": "Apple Records",   "catalog_number": "PCS 7067/8","format": "Double LP","pressing": "UK First Press","country": "UK","genre": "Rock",           "notes": "Low serial numbers (e.g. 0000001) are highly valuable."},
    {"title": "Revolver",                               "artist": "The Beatles",       "year": "1966", "label": "Parlophone",      "catalog_number": "PMC 7009",  "format": "LP", "pressing": "UK Mono First Press","country": "UK","genre": "Rock",           "notes": "UK mono considered superior mix. 'Taxman' opens."},
    {"title": "Led Zeppelin I",                         "artist": "Led Zeppelin",      "year": "1969", "label": "Atlantic",        "catalog_number": "588171",    "format": "LP", "pressing": "UK First Press",   "country": "UK",  "genre": "Rock",          "notes": "UK first press: plum/orange Atlantic label, red turquoise lettering. Most collectible."},
    {"title": "Led Zeppelin IV (Four Symbols)",         "artist": "Led Zeppelin",      "year": "1971", "label": "Atlantic",        "catalog_number": "2401 012",  "format": "LP", "pressing": "UK First Press",   "country": "UK",  "genre": "Rock",          "notes": "Contains Stairway to Heaven. First press has no text on cover."},
    {"title": "The Dark Side of the Moon",              "artist": "Pink Floyd",        "year": "1973", "label": "Harvest",         "catalog_number": "SHVL 804",  "format": "LP", "pressing": "UK First Press",   "country": "UK",  "genre": "Progressive Rock","notes": "UK first press: solid blue Harvest label, includes posters and stickers. Has remained on Billboard chart for over 900 weeks."},
    {"title": "Wish You Were Here",                     "artist": "Pink Floyd",        "year": "1975", "label": "Harvest",         "catalog_number": "SHVL 814",  "format": "LP", "pressing": "UK First Press",   "country": "UK",  "genre": "Progressive Rock","notes": ""},
    {"title": "Nevermind",                              "artist": "Nirvana",           "year": "1991", "label": "DGC Records",     "catalog_number": "DGC-24425", "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Grunge",         "notes": "Original pressing has 'Endless, Nameless' hidden track after 10 minutes of silence at end of side B."},
    {"title": "London Calling",                         "artist": "The Clash",         "year": "1979", "label": "CBS",             "catalog_number": "CLASH 3",   "format": "Double LP","pressing": "UK First Press","country": "UK","genre": "Punk/New Wave",  "notes": ""},
    {"title": "The Velvet Underground & Nico",          "artist": "Velvet Underground & Nico","year": "1967","label": "Verve",    "catalog_number": "V6-5008",   "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Rock",          "notes": "Andy Warhol peel-off banana cover. Torque the banana sticker. Peeled or unpeeled copies command premiums."},
    {"title": "Are You Experienced",                    "artist": "Jimi Hendrix Experience","year": "1967","label": "Track",   "catalog_number": "612 001",   "format": "LP", "pressing": "UK First Press",   "country": "UK",  "genre": "Rock",          "notes": "UK Track label first press: mono different from stereo. Very collectible."},

    # ── Blues & Soul ─────────────────────────────────────────────────────────
    {"title": "Kind of Blue",                           "artist": "Miles Davis",       "year": "1959", "label": "Columbia",        "catalog_number": "CL 1355 (mono) / CS 8163 (stereo)", "format": "LP", "pressing": "US First Press", "country": "USA", "genre": "Jazz", "notes": "Best-selling jazz album ever. Original pressing has 6-eye label. Stereo copies have pitch error on some tracks."},
    {"title": "Blue Train",                             "artist": "John Coltrane",     "year": "1957", "label": "Blue Note",       "catalog_number": "BLP 1577",  "format": "LP", "pressing": "US First Press (flat edge, deep groove)", "country": "USA", "genre": "Jazz", "notes": "Original Blue Note pressing: Lexington Ave address, flat edge, deep groove. Most valuable Coltrane LP."},
    {"title": "A Love Supreme",                         "artist": "John Coltrane",     "year": "1964", "label": "Impulse!",        "catalog_number": "A-77",      "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Jazz",          "notes": "Spiritual jazz masterwork. Orange/black Impulse label."},
    {"title": "What's Going On",                        "artist": "Marvin Gaye",       "year": "1971", "label": "Tamla",           "catalog_number": "T 310L",    "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Soul",          "notes": "Original Tamla label. Landmark soul concept album."},
    {"title": "I Never Loved a Man the Way I Love You", "artist": "Aretha Franklin",   "year": "1967", "label": "Atlantic",        "catalog_number": "8139",      "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Soul",          "notes": ""},
    {"title": "Innervisions",                           "artist": "Stevie Wonder",     "year": "1973", "label": "Tamla",           "catalog_number": "T 326V1",   "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Soul",          "notes": "Grammy Album of the Year 1974."},
    {"title": "Robert Johnson — The Complete Recordings","artist": "Robert Johnson",   "year": "1990", "label": "Columbia",        "catalog_number": "C2K 46222", "format": "Double LP","pressing": "US First Press","country": "USA","genre": "Delta Blues",   "notes": "Compiled reissue of original 1936-1937 78rpm recordings. Important historical set."},

    # ── Hip-Hop / Rap ────────────────────────────────────────────────────────
    {"title": "Illmatic",                               "artist": "Nas",               "year": "1994", "label": "Columbia",        "catalog_number": "CK 57684",  "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Hip-Hop",       "notes": "Widely considered the greatest hip-hop album. Original Columbia pressing."},
    {"title": "Ready to Die",                           "artist": "The Notorious B.I.G.","year": "1994","label": "Bad Boy",        "catalog_number": "78612-73000","format": "Double LP","pressing": "US First Press","country": "USA","genre": "Hip-Hop",      "notes": ""},
    {"title": "The Chronic",                            "artist": "Dr. Dre",           "year": "1992", "label": "Death Row / Interscope","catalog_number": "P1 57128","format": "Double LP","pressing": "US First Press","country": "USA","genre": "Hip-Hop","notes": ""},
    {"title": "Enter the Wu-Tang (36 Chambers)",        "artist": "Wu-Tang Clan",      "year": "1993", "label": "Loud",            "catalog_number": "07863 66336-1","format": "LP","pressing": "US First Press", "country": "USA", "genre": "Hip-Hop",       "notes": ""},
    {"title": "To Pimp a Butterfly",                    "artist": "Kendrick Lamar",    "year": "2015", "label": "Top Dawg / Aftermath","catalog_number": "B0022840-01","format": "Double LP","pressing": "US First Press","country": "USA","genre": "Hip-Hop","notes": "Grammy-winning. Original pressing with error label highly sought."},
    {"title": "It Takes a Nation of Millions to Hold Us Back","artist": "Public Enemy","year": "1988","label": "Def Jam",         "catalog_number": "OC 44303",  "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Hip-Hop",       "notes": ""},

    # ── Electronic ───────────────────────────────────────────────────────────
    {"title": "Autobahn",                               "artist": "Kraftwerk",         "year": "1974", "label": "Philips",         "catalog_number": "6305 231",  "format": "LP", "pressing": "German First Press","country": "Germany","genre": "Electronic",   "notes": "Pioneering electronic album. German first press on Philips."},
    {"title": "Trans-Europe Express",                   "artist": "Kraftwerk",         "year": "1977", "label": "Capitol",         "catalog_number": "SW-11603",  "format": "LP", "pressing": "German First Press","country": "Germany","genre": "Electronic",   "notes": ""},
    {"title": "Selected Ambient Works 85-92",           "artist": "Aphex Twin",        "year": "1992", "label": "Apollo",          "catalog_number": "AMB LP3922","format": "Double LP","pressing": "UK First Press","country": "UK","genre": "Ambient Electronic","notes": ""},
    {"title": "Homework",                               "artist": "Daft Punk",         "year": "1997", "label": "Virgin",          "catalog_number": "7243 8 42609 1 3","format": "Double LP","pressing": "French First Press","country": "France","genre": "Electronic","notes": ""},
    {"title": "Discovery",                              "artist": "Daft Punk",         "year": "2001", "label": "Virgin",          "catalog_number": "7243 8 10144 1 8","format": "Double LP","pressing": "French First Press","country": "France","genre": "Electronic","notes": ""},

    # ── Country / Americana ──────────────────────────────────────────────────
    {"title": "At Folsom Prison",                       "artist": "Johnny Cash",       "year": "1968", "label": "Columbia",        "catalog_number": "CS 9639",   "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Country",       "notes": "Live album recorded at Folsom Prison. Columbia 360-degree label."},
    {"title": "Red Headed Stranger",                    "artist": "Willie Nelson",     "year": "1975", "label": "Columbia",        "catalog_number": "PC 33482",  "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Country",       "notes": ""},
    {"title": "Blue",                                   "artist": "Joni Mitchell",     "year": "1971", "label": "Reprise",         "catalog_number": "MS 2038",   "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Folk/Singer-Songwriter","notes": "Widely regarded as one of the greatest albums ever made."},

    # ── Punk / New Wave ──────────────────────────────────────────────────────
    {"title": "Never Mind the Bollocks",                "artist": "Sex Pistols",       "year": "1977", "label": "Virgin",          "catalog_number": "V 2086",    "format": "LP", "pressing": "UK First Press",   "country": "UK",  "genre": "Punk",          "notes": "Banned by BBC. Original UK Virgin press."},
    {"title": "Marquee Moon",                           "artist": "Television",        "year": "1977", "label": "Elektra",         "catalog_number": "7E-1098",   "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "Punk/Art Rock",  "notes": ""},
    {"title": "Remain in Light",                        "artist": "Talking Heads",     "year": "1980", "label": "Sire",            "catalog_number": "SRK 6095",  "format": "LP", "pressing": "US First Press",   "country": "USA", "genre": "New Wave",       "notes": ""},
    {"title": "Unknown Pleasures",                      "artist": "Joy Division",      "year": "1979", "label": "Factory",         "catalog_number": "FACT 10",   "format": "LP", "pressing": "UK First Press",   "country": "UK",  "genre": "Post-Punk",     "notes": "Factory Records original. Pulsar radio wave cover. Highly collectible."},
    {"title": "Closer",                                 "artist": "Joy Division",      "year": "1980", "label": "Factory",         "catalog_number": "FACT 25",   "format": "LP", "pressing": "UK First Press",   "country": "UK",  "genre": "Post-Punk",     "notes": ""},

    # ── Classical ────────────────────────────────────────────────────────────
    {"title": "Beethoven: Symphony No. 9 (First stereo recording)", "artist": "Herbert von Karajan / BPO", "year": "1963", "label": "Deutsche Grammophon", "catalog_number": "139 001/2", "format": "Double LP", "pressing": "German First Press", "country": "Germany", "genre": "Classical", "notes": ""},
    {"title": "Glenn Gould: Goldberg Variations (1981)",            "artist": "Glenn Gould",               "year": "1982", "label": "CBS Masterworks",     "catalog_number": "IM 37779",  "format": "LP", "pressing": "US First Press", "country": "USA", "genre": "Classical", "notes": "Final studio recording by Gould; released posthumously. Different tempo from his famous 1955 debut."},
]


def search(query: str, country: str = "All") -> List[Dict[str, Any]]:
    q = query.strip().lower()
    results = []
    for entry in CATALOG:
        haystack = " ".join([
            entry.get("title", ""),
            entry.get("artist", ""),
            entry.get("label", ""),
            entry.get("genre", ""),
            entry.get("notes", ""),
        ]).lower()
        if not q or q in haystack:
            results.append(entry)
    return results


def to_fields(entry: Dict[str, Any]) -> Dict[str, str]:
    return {k: v for k, v in {
        "title":          entry.get("title", ""),
        "artist":         entry.get("artist", ""),
        "year":           entry.get("year", ""),
        "label":          entry.get("label", ""),
        "catalog_number": entry.get("catalog_number", ""),
        "format":         entry.get("format", ""),
        "pressing":       entry.get("pressing", ""),
        "country":        entry.get("country", ""),
        "genre":          entry.get("genre", ""),
    }.items() if v}
