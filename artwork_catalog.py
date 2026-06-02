"""Built-in reference catalog of artworks and artists.

Each entry represents either a specific famous work or an artist's body of
work.  Selecting one pre-fills the ``artwork`` item type fields.

Fields: title, artist, year, medium, period, school, subject, location
"""

from __future__ import annotations
from typing import List, Dict, Any

SEARCH_COLS = [
    ("title",   "Title / Work",   250),
    ("artist",  "Artist",         160),
    ("year",    "Year",            70),
    ("period",  "Period / Style", 120),
]

DETAIL_FIELDS = [
    ("artist",  "Artist"),
    ("year",    "Year / Date"),
    ("medium",  "Medium"),
    ("period",  "Period / Style"),
    ("school",  "School"),
    ("subject", "Subject"),
    ("location","Current Location"),
]

CATALOG: List[Dict[str, Any]] = [

    # ── Italian Renaissance ───────────────────────────────────────────────────
    {"title": "Mona Lisa",                     "artist": "Leonardo da Vinci",     "year": "c.1503-1519", "medium": "Oil on panel",          "period": "High Renaissance", "school": "Italian / Florentine", "subject": "Portrait",   "location": "Louvre, Paris"},
    {"title": "The Last Supper",               "artist": "Leonardo da Vinci",     "year": "1495-1498",   "medium": "Tempera on plaster",    "period": "High Renaissance", "school": "Italian",              "subject": "Religious",  "location": "Santa Maria delle Grazie, Milan"},
    {"title": "Vitruvian Man",                 "artist": "Leonardo da Vinci",     "year": "c.1490",      "medium": "Pen, ink, watercolor",  "period": "High Renaissance", "school": "Italian / Florentine", "subject": "Figure",     "location": "Gallerie dell'Accademia, Venice"},
    {"title": "The Creation of Adam",          "artist": "Michelangelo",           "year": "1508-1512",   "medium": "Fresco",                "period": "High Renaissance", "school": "Italian / Roman",      "subject": "Religious",  "location": "Sistine Chapel, Vatican"},
    {"title": "David",                         "artist": "Michelangelo",           "year": "1501-1504",   "medium": "Marble",                "period": "High Renaissance", "school": "Italian / Florentine", "subject": "Historical", "location": "Galleria dell'Accademia, Florence"},
    {"title": "The School of Athens",          "artist": "Raphael",                "year": "1509-1511",   "medium": "Fresco",                "period": "High Renaissance", "school": "Italian",              "subject": "Mythological","location": "Apostolic Palace, Vatican"},
    {"title": "Sistine Madonna",               "artist": "Raphael",                "year": "1512",        "medium": "Oil on canvas",         "period": "High Renaissance", "school": "Italian",              "subject": "Religious",  "location": "Gemaldegalerie Alte Meister, Dresden"},
    {"title": "Birth of Venus",                "artist": "Sandro Botticelli",      "year": "c.1484-1486", "medium": "Tempera on canvas",     "period": "Early Renaissance","school": "Italian / Florentine", "subject": "Mythological","location": "Uffizi, Florence"},
    {"title": "Primavera",                     "artist": "Sandro Botticelli",      "year": "c.1477-1482", "medium": "Tempera on panel",      "period": "Early Renaissance","school": "Italian / Florentine", "subject": "Mythological","location": "Uffizi, Florence"},
    {"title": "Man in a Red Turban",           "artist": "Jan van Eyck",           "year": "1433",        "medium": "Oil on oak panel",      "period": "Early Renaissance","school": "Flemish",               "subject": "Portrait",   "location": "National Gallery, London"},
    {"title": "Arnolfini Portrait",            "artist": "Jan van Eyck",           "year": "1434",        "medium": "Oil on oak panel",      "period": "Early Renaissance","school": "Flemish",               "subject": "Genre Scene","location": "National Gallery, London"},

    # ── Baroque ───────────────────────────────────────────────────────────────
    {"title": "Girl with a Pearl Earring",     "artist": "Johannes Vermeer",       "year": "c.1665",      "medium": "Oil on canvas",         "period": "Baroque",          "school": "Dutch",                "subject": "Portrait",   "location": "Mauritshuis, The Hague"},
    {"title": "The Milkmaid",                  "artist": "Johannes Vermeer",       "year": "c.1657-1658", "medium": "Oil on canvas",         "period": "Baroque",          "school": "Dutch",                "subject": "Genre Scene","location": "Rijksmuseum, Amsterdam"},
    {"title": "The Night Watch",               "artist": "Rembrandt van Rijn",     "year": "1642",        "medium": "Oil on canvas",         "period": "Baroque",          "school": "Dutch",                "subject": "Genre Scene","location": "Rijksmuseum, Amsterdam"},
    {"title": "Self-Portrait with Two Circles","artist": "Rembrandt van Rijn",     "year": "c.1665-1669", "medium": "Oil on canvas",         "period": "Baroque",          "school": "Dutch",                "subject": "Portrait",   "location": "Kenwood House, London"},
    {"title": "Las Meninas",                   "artist": "Diego Velazquez",         "year": "1656",        "medium": "Oil on canvas",         "period": "Baroque",          "school": "Spanish",              "subject": "Genre Scene","location": "Prado, Madrid"},
    {"title": "The Anatomy Lesson",            "artist": "Rembrandt van Rijn",     "year": "1632",        "medium": "Oil on canvas",         "period": "Baroque",          "school": "Dutch",                "subject": "Genre Scene","location": "Mauritshuis, The Hague"},
    {"title": "Judith Slaying Holofernes",     "artist": "Artemisia Gentileschi",  "year": "c.1614-1620", "medium": "Oil on canvas",         "period": "Baroque",          "school": "Italian",              "subject": "Historical", "location": "Uffizi, Florence"},
    {"title": "The Calling of Saint Matthew",  "artist": "Caravaggio",             "year": "1599-1600",   "medium": "Oil on canvas",         "period": "Baroque",          "school": "Italian",              "subject": "Religious",  "location": "San Luigi dei Francesi, Rome"},
    {"title": "Rubens — Descent from the Cross","artist": "Peter Paul Rubens",     "year": "1612-1614",   "medium": "Oil on panel",          "period": "Baroque",          "school": "Flemish",              "subject": "Religious",  "location": "Cathedral of Our Lady, Antwerp"},

    # ── Rococo ────────────────────────────────────────────────────────────────
    {"title": "The Swing",                     "artist": "Jean-Honore Fragonard",  "year": "1767",        "medium": "Oil on canvas",         "period": "Rococo",           "school": "French",               "subject": "Genre Scene","location": "Wallace Collection, London"},
    {"title": "Portrait of Madame de Pompadour","artist": "Francois Boucher",      "year": "1756",        "medium": "Oil on canvas",         "period": "Rococo",           "school": "French",               "subject": "Portrait",   "location": "Alte Pinakothek, Munich"},

    # ── Neoclassicism & Romanticism ───────────────────────────────────────────
    {"title": "Oath of the Horatii",           "artist": "Jacques-Louis David",    "year": "1784",        "medium": "Oil on canvas",         "period": "Neoclassicism",    "school": "French",               "subject": "Historical", "location": "Louvre, Paris"},
    {"title": "Napoleon Crossing the Alps",    "artist": "Jacques-Louis David",    "year": "1801-1805",   "medium": "Oil on canvas",         "period": "Neoclassicism",    "school": "French",               "subject": "Historical", "location": "Chateau de Malmaison"},
    {"title": "Liberty Leading the People",    "artist": "Eugene Delacroix",       "year": "1830",        "medium": "Oil on canvas",         "period": "Romanticism",      "school": "French",               "subject": "Historical", "location": "Louvre, Paris"},
    {"title": "The Raft of the Medusa",        "artist": "Theodore Gericault",     "year": "1818-1819",   "medium": "Oil on canvas",         "period": "Romanticism",      "school": "French",               "subject": "Historical", "location": "Louvre, Paris"},
    {"title": "The Fighting Temeraire",        "artist": "J.M.W. Turner",          "year": "1839",        "medium": "Oil on canvas",         "period": "Romanticism",      "school": "English / British",    "subject": "Seascape",   "location": "National Gallery, London"},
    {"title": "Rain, Steam, and Speed",        "artist": "J.M.W. Turner",          "year": "1844",        "medium": "Oil on canvas",         "period": "Romanticism",      "school": "English / British",    "subject": "Landscape",  "location": "National Gallery, London"},
    {"title": "Wanderer above the Sea of Fog", "artist": "Caspar David Friedrich", "year": "c.1817",      "medium": "Oil on canvas",         "period": "Romanticism",      "school": "German",               "subject": "Landscape",  "location": "Kunsthalle Hamburg"},

    # ── Realism ───────────────────────────────────────────────────────────────
    {"title": "The Stone Breakers",            "artist": "Gustave Courbet",        "year": "1849",        "medium": "Oil on canvas",         "period": "Realism",          "school": "French",               "subject": "Genre Scene","location": "Destroyed (WWII)"},
    {"title": "Olympia",                       "artist": "Edouard Manet",          "year": "1863",        "medium": "Oil on canvas",         "period": "Realism",          "school": "French",               "subject": "Nude",       "location": "Musee d'Orsay, Paris"},
    {"title": "Le Dejeuner sur l'herbe",       "artist": "Edouard Manet",          "year": "1863",        "medium": "Oil on canvas",         "period": "Realism",          "school": "French",               "subject": "Genre Scene","location": "Musee d'Orsay, Paris"},

    # ── Impressionism ─────────────────────────────────────────────────────────
    {"title": "Impression, Sunrise",           "artist": "Claude Monet",           "year": "1872",        "medium": "Oil on canvas",         "period": "Impressionism",    "school": "French",               "subject": "Seascape",   "location": "Musee Marmottan, Paris"},
    {"title": "Water Lilies (Nympheas)",       "artist": "Claude Monet",           "year": "1896-1926",   "medium": "Oil on canvas",         "period": "Impressionism",    "school": "French",               "subject": "Landscape",  "location": "Various (series)"},
    {"title": "Haystacks",                     "artist": "Claude Monet",           "year": "1890-1891",   "medium": "Oil on canvas",         "period": "Impressionism",    "school": "French",               "subject": "Landscape",  "location": "Various (series)"},
    {"title": "A Sunday on La Grande Jatte",   "artist": "Georges Seurat",         "year": "1884-1886",   "medium": "Oil on canvas",         "period": "Pointillism",      "school": "French",               "subject": "Genre Scene","location": "Art Institute of Chicago"},
    {"title": "The Dance Class",               "artist": "Edgar Degas",            "year": "1874",        "medium": "Oil on canvas",         "period": "Impressionism",    "school": "French",               "subject": "Genre Scene","location": "Metropolitan Museum, New York"},
    {"title": "At the Moulin Rouge",           "artist": "Edgar Degas",            "year": "c.1892",      "medium": "Oil on canvas",         "period": "Impressionism",    "school": "French",               "subject": "Genre Scene","location": "Art Institute of Chicago"},
    {"title": "Bal du moulin de la Galette",   "artist": "Pierre-Auguste Renoir",  "year": "1876",        "medium": "Oil on canvas",         "period": "Impressionism",    "school": "French",               "subject": "Genre Scene","location": "Musee d'Orsay, Paris"},
    {"title": "Two Sisters (On the Terrace)",  "artist": "Pierre-Auguste Renoir",  "year": "1881",        "medium": "Oil on canvas",         "period": "Impressionism",    "school": "French",               "subject": "Genre Scene","location": "Art Institute of Chicago"},
    {"title": "The Card Players",              "artist": "Paul Cezanne",           "year": "1890-1895",   "medium": "Oil on canvas",         "period": "Post-Impressionism","school": "French",              "subject": "Genre Scene","location": "Various (5 versions)"},
    {"title": "Mont Sainte-Victoire",          "artist": "Paul Cezanne",           "year": "1885-1906",   "medium": "Oil on canvas",         "period": "Post-Impressionism","school": "French",              "subject": "Landscape",  "location": "Various (series)"},

    # ── Post-Impressionism ───────────────────────────────────────────────────
    {"title": "The Starry Night",              "artist": "Vincent van Gogh",       "year": "1889",        "medium": "Oil on canvas",         "period": "Post-Impressionism","school": "Dutch",               "subject": "Landscape",  "location": "MoMA, New York"},
    {"title": "Sunflowers",                    "artist": "Vincent van Gogh",       "year": "1888",        "medium": "Oil on canvas",         "period": "Post-Impressionism","school": "Dutch",               "subject": "Floral",     "location": "Various (series)"},
    {"title": "Bedroom in Arles",              "artist": "Vincent van Gogh",       "year": "1888",        "medium": "Oil on canvas",         "period": "Post-Impressionism","school": "Dutch",               "subject": "Interior",   "location": "Various (3 versions)"},
    {"title": "Where Do We Come From?",        "artist": "Paul Gauguin",           "year": "1897-1898",   "medium": "Oil on canvas",         "period": "Post-Impressionism","school": "French",              "subject": "Allegorical","location": "MFA Boston"},
    {"title": "Vision After the Sermon",       "artist": "Paul Gauguin",           "year": "1888",        "medium": "Oil on canvas",         "period": "Post-Impressionism","school": "French",              "subject": "Religious",  "location": "National Galleries of Scotland"},
    {"title": "The Scream",                    "artist": "Edvard Munch",           "year": "1893",        "medium": "Oil, tempera, pastel",   "period": "Expressionism",    "school": "Norwegian",            "subject": "Abstract",   "location": "National Museum, Oslo"},

    # ── Symbolism & Art Nouveau ───────────────────────────────────────────────
    {"title": "The Kiss",                      "artist": "Gustav Klimt",           "year": "1907-1908",   "medium": "Oil and gold leaf on canvas", "period": "Art Nouveau",  "school": "Austrian",             "subject": "Genre Scene","location": "Belvedere, Vienna"},
    {"title": "Portrait of Adele Bloch-Bauer I","artist": "Gustav Klimt",         "year": "1907",        "medium": "Oil and gold leaf on canvas", "period": "Art Nouveau",  "school": "Austrian",             "subject": "Portrait",   "location": "Neue Galerie, New York"},

    # ── Expressionism ────────────────────────────────────────────────────────
    {"title": "Der Sturm — Rider on Horseback","artist": "Wassily Kandinsky",      "year": "1903",        "medium": "Oil on canvas",         "period": "Expressionism",    "school": "German",               "subject": "Genre Scene","location": "Lenbach house, Munich"},
    {"title": "Composition VIII",              "artist": "Wassily Kandinsky",      "year": "1923",        "medium": "Oil on canvas",         "period": "Abstract Expressionism","school": "German / Bauhaus",  "subject": "Abstract",   "location": "Guggenheim, New York"},

    # ── Cubism & Dada ────────────────────────────────────────────────────────
    {"title": "Les Demoiselles d'Avignon",     "artist": "Pablo Picasso",          "year": "1907",        "medium": "Oil on canvas",         "period": "Cubism",           "school": "Spanish",              "subject": "Nude",       "location": "MoMA, New York"},
    {"title": "Guernica",                      "artist": "Pablo Picasso",          "year": "1937",        "medium": "Oil on canvas",         "period": "Cubism",           "school": "Spanish",              "subject": "Historical", "location": "Museo Reina Sofia, Madrid"},
    {"title": "Three Musicians",               "artist": "Pablo Picasso",          "year": "1921",        "medium": "Oil on canvas",         "period": "Cubism",           "school": "Spanish",              "subject": "Genre Scene","location": "MoMA, New York"},
    {"title": "Nude Descending a Staircase No.2","artist": "Marcel Duchamp",       "year": "1912",        "medium": "Oil on canvas",         "period": "Cubism",           "school": "French",               "subject": "Nude",       "location": "Philadelphia Museum of Art"},

    # ── Surrealism ───────────────────────────────────────────────────────────
    {"title": "The Persistence of Memory",     "artist": "Salvador Dali",          "year": "1931",        "medium": "Oil on canvas",         "period": "Surrealism",       "school": "Spanish",              "subject": "Abstract",   "location": "MoMA, New York"},
    {"title": "The Son of Man",                "artist": "Rene Magritte",          "year": "1964",        "medium": "Oil on canvas",         "period": "Surrealism",       "school": "Belgian",              "subject": "Portrait",   "location": "Private Collection"},
    {"title": "The Treachery of Images",       "artist": "Rene Magritte",          "year": "1929",        "medium": "Oil on canvas",         "period": "Surrealism",       "school": "Belgian",              "subject": "Abstract",   "location": "LACMA, Los Angeles"},
    {"title": "The Two Fridas",                "artist": "Frida Kahlo",            "year": "1939",        "medium": "Oil on canvas",         "period": "Surrealism",       "school": "Mexican",              "subject": "Portrait",   "location": "Museo de Arte Moderno, Mexico City"},
    {"title": "Self-Portrait with Thorn Necklace","artist": "Frida Kahlo",         "year": "1940",        "medium": "Oil on canvas",         "period": "Surrealism",       "school": "Mexican",              "subject": "Portrait",   "location": "Harry Ransom Center, Austin"},

    # ── Abstract Expressionism ────────────────────────────────────────────────
    {"title": "Number 31",                     "artist": "Jackson Pollock",        "year": "1950",        "medium": "Oil, enamel on canvas",  "period": "Abstract Expressionism","school": "American",         "subject": "Abstract",   "location": "MoMA, New York"},
    {"title": "Lavender Mist (Number 1)",      "artist": "Jackson Pollock",        "year": "1950",        "medium": "Oil, enamel, aluminum",  "period": "Abstract Expressionism","school": "American",         "subject": "Abstract",   "location": "National Gallery of Art, Washington D.C."},
    {"title": "Woman I",                       "artist": "Willem de Kooning",      "year": "1950-1952",   "medium": "Oil on canvas",          "period": "Abstract Expressionism","school": "American",         "subject": "Figure",     "location": "MoMA, New York"},
    {"title": "Orange, Red, Yellow",           "artist": "Mark Rothko",            "year": "1961",        "medium": "Oil on canvas",          "period": "Abstract Expressionism","school": "American",         "subject": "Abstract",   "location": "Christie's auction 2012 ($86.9M)"},
    {"title": "Elegy to the Spanish Republic", "artist": "Robert Motherwell",      "year": "1948-1967",   "medium": "Oil on canvas",          "period": "Abstract Expressionism","school": "American",         "subject": "Abstract",   "location": "Various (series)"},

    # ── Pop Art ──────────────────────────────────────────────────────────────
    {"title": "Campbell's Soup Cans",          "artist": "Andy Warhol",            "year": "1962",        "medium": "Synthetic polymer on canvas","period": "Pop Art",       "school": "American",             "subject": "Still Life", "location": "MoMA, New York"},
    {"title": "Marilyn Diptych",               "artist": "Andy Warhol",            "year": "1962",        "medium": "Acrylic on canvas",      "period": "Pop Art",          "school": "American",             "subject": "Portrait",   "location": "Tate Modern, London"},
    {"title": "Shot Marilyns",                 "artist": "Andy Warhol",            "year": "1964",        "medium": "Acrylic on canvas",      "period": "Pop Art",          "school": "American",             "subject": "Portrait",   "location": "Various private collections"},
    {"title": "Whaam!",                        "artist": "Roy Lichtenstein",       "year": "1963",        "medium": "Acrylic on canvas",      "period": "Pop Art",          "school": "American",             "subject": "Genre Scene","location": "Tate Modern, London"},
    {"title": "Drowning Girl",                 "artist": "Roy Lichtenstein",       "year": "1963",        "medium": "Oil and synthetic polymer","period": "Pop Art",         "school": "American",             "subject": "Genre Scene","location": "MoMA, New York"},

    # ── American Art ─────────────────────────────────────────────────────────
    {"title": "American Gothic",               "artist": "Grant Wood",             "year": "1930",        "medium": "Oil on beaver board",    "period": "Realism",          "school": "American",             "subject": "Genre Scene","location": "Art Institute of Chicago"},
    {"title": "Christina's World",             "artist": "Andrew Wyeth",           "year": "1948",        "medium": "Tempera on gessoed panel","period": "Realism",         "school": "American",             "subject": "Landscape",  "location": "MoMA, New York"},
    {"title": "Nighthawks",                    "artist": "Edward Hopper",          "year": "1942",        "medium": "Oil on canvas",          "period": "Realism",          "school": "American",             "subject": "Genre Scene","location": "Art Institute of Chicago"},
    {"title": "Watson and the Shark",          "artist": "John Singleton Copley",  "year": "1778",        "medium": "Oil on canvas",          "period": "Neoclassicism",    "school": "American",             "subject": "Historical", "location": "National Gallery of Art, Washington D.C."},
    {"title": "Washington Crossing the Delaware","artist": "Emanuel Leutze",       "year": "1851",        "medium": "Oil on canvas",          "period": "Romanticism",      "school": "American",             "subject": "Historical", "location": "Metropolitan Museum, New York"},

    # ── Ancient & Medieval ────────────────────────────────────────────────────
    {"title": "Winged Victory of Samothrace",  "artist": "Unknown (Greek)",        "year": "c.200-190 BC","medium": "Marble",                "period": "Ancient",          "school": "Greek (Hellenistic)",  "subject": "Figure",     "location": "Louvre, Paris"},
    {"title": "Venus de Milo",                 "artist": "Unknown (Greek)",        "year": "c.130-100 BC","medium": "Marble",                "period": "Ancient",          "school": "Greek (Hellenistic)",  "subject": "Figure",     "location": "Louvre, Paris"},
    {"title": "Laocoön and His Sons",          "artist": "Agesander et al.",       "year": "c.42-20 BC",  "medium": "Marble",                "period": "Ancient",          "school": "Greek",                "subject": "Mythological","location": "Vatican Museums"},

    # ── Modern / Contemporary ────────────────────────────────────────────────
    {"title": "No. 5, 1948",                   "artist": "Jackson Pollock",        "year": "1948",        "medium": "Oil on fibreboard",      "period": "Abstract Expressionism","school": "American",         "subject": "Abstract",   "location": "Private Collection (sold $140M 2006)"},
    {"title": "Balloon Dog (Orange)",          "artist": "Jeff Koons",             "year": "1994-2000",   "medium": "Mirror-polished stainless steel with transparent color coating", "period": "Contemporary", "school": "American", "subject": "Abstract",  "location": "Various (edition of 5)"},
    {"title": "For the Love of God",           "artist": "Damien Hirst",           "year": "2007",        "medium": "Platinum, diamonds",     "period": "Contemporary",     "school": "English / British",    "subject": "Abstract",   "location": "Private Collection"},
    {"title": "Three Studies of Lucian Freud", "artist": "Francis Bacon",         "year": "1969",        "medium": "Oil on canvas (triptych)","period": "Contemporary",     "school": "English / British",    "subject": "Portrait",   "location": "Private Collection (sold $142M 2013)"},
]


def search(query: str, country: str = "All") -> List[Dict[str, Any]]:
    q = query.strip().lower()
    results = []
    for entry in CATALOG:
        haystack = " ".join([
            entry.get("title", ""),
            entry.get("artist", ""),
            entry.get("period", ""),
            entry.get("school", ""),
            entry.get("medium", ""),
        ]).lower()
        if not q or q in haystack:
            results.append(entry)
    return results


def to_fields(entry: Dict[str, Any]) -> Dict[str, str]:
    return {k: v for k, v in {
        "title":    entry.get("title", ""),
        "artist":   entry.get("artist", ""),
        "year":     entry.get("year", ""),
        "medium":   entry.get("medium", ""),
        "period":   entry.get("period", ""),
        "school":   entry.get("school", ""),
        "subject":  entry.get("subject", ""),
        "location": entry.get("location", ""),
    }.items() if v}
