"""Built-in reference catalog of comic series and key issues.

Each entry represents a comic series or a specific significant issue.
Selecting one pre-fills the ``comic`` item type fields.

Fields: title, writer, artist, year, publisher, notes
"""

from __future__ import annotations
from typing import List, Dict, Any

SEARCH_COLS = [
    ("title",     "Series / Issue",  240),
    ("publisher", "Publisher",       110),
    ("years",     "Year(s)",          70),
    ("genre",     "Genre",           100),
]

DETAIL_FIELDS = [
    ("writer",    "Writer"),
    ("artist",    "Artist"),
    ("years",     "Year(s)"),
    ("publisher", "Publisher"),
    ("genre",     "Genre"),
]

CATALOG: List[Dict[str, Any]] = [

    # ── Golden Age — DC ───────────────────────────────────────────────────────
    {"title": "Action Comics #1 (1st Superman)",         "writer": "Jerry Siegel",      "artist": "Joe Shuster",       "years": "1938", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First appearance of Superman. Most valuable comic ever; CGC 9.0 sold for $3.25M in 2021."},
    {"title": "Detective Comics #27 (1st Batman)",       "writer": "Bill Finger",       "artist": "Bob Kane",          "years": "1939", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First appearance of Batman. CGC 6.5 sold for $1.5M."},
    {"title": "Batman #1 (1st Joker, Catwoman)",         "writer": "Bill Finger",       "artist": "Bob Kane",          "years": "1940", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First solo Batman issue. First Joker. First Catwoman."},
    {"title": "Superman #1",                             "writer": "Jerry Siegel",      "artist": "Joe Shuster",       "years": "1939", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First solo Superman issue."},
    {"title": "Flash Comics #1 (1st Flash, Hawkman)",    "writer": "Gardner Fox",       "artist": "Harry Lampert",     "years": "1940", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First appearance of both the Flash (Jay Garrick) and Hawkman."},
    {"title": "All Star Comics #8 (1st Wonder Woman)",   "writer": "William M. Marston","artist": "H.G. Peter",        "years": "1941", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First appearance of Wonder Woman."},
    {"title": "More Fun Comics #52 (1st Spectre)",       "writer": "Jerry Siegel",      "artist": "Bernard Baily",     "years": "1940", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First appearance of The Spectre."},
    {"title": "Green Lantern #1 (Golden Age)",           "writer": "Bill Finger",       "artist": "Mart Nodell",       "years": "1941", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First solo Green Lantern (Alan Scott)."},
    {"title": "Sensation Comics #1 (1st WW solo)",       "writer": "William M. Marston","artist": "H.G. Peter",        "years": "1942", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First solo Wonder Woman issue."},

    # ── Golden Age — Timely / Marvel ──────────────────────────────────────────
    {"title": "Marvel Comics #1 (1st Namor, Torch)",     "writer": "Bill Everett",      "artist": "Carl Burgos",       "years": "1939", "publisher": "Timely Comics","genre": "Superhero", "notes": "First issue of Timely Comics (later Marvel). First Namor & Human Torch. Extremely rare in high grade."},
    {"title": "Captain America Comics #1",               "writer": "Joe Simon",         "artist": "Jack Kirby",        "years": "1941", "publisher": "Timely Comics","genre": "Superhero", "notes": "First appearance of Captain America. Cover shows Cap punching Hitler."},
    {"title": "Human Torch Comics #8 (early printing)",  "writer": "Carl Burgos",       "artist": "Carl Burgos",       "years": "1941", "publisher": "Timely Comics","genre": "Superhero", "notes": ""},

    # ── Golden Age — Other Publishers ─────────────────────────────────────────
    {"title": "Whiz Comics #2 (1st Captain Marvel)",     "writer": "Bill Parker",       "artist": "C.C. Beck",         "years": "1940", "publisher": "Fawcett",      "genre": "Superhero", "notes": "First appearance of Captain Marvel (Shazam). Was the best-selling superhero of the 1940s."},
    {"title": "Pep Comics #22 (1st Archie)",             "writer": "Vic Bloom",         "artist": "Bob Montana",       "years": "1941", "publisher": "MLJ / Archie", "genre": "Humor",     "notes": "First appearance of Archie Andrews."},

    # ── EC Comics (Horror / Sci-Fi) ───────────────────────────────────────────
    {"title": "Tales From the Crypt (EC Comics)",        "writer": "Various",           "artist": "Jack Davis / Graham Ingels", "years": "1950-1955", "publisher": "EC Comics", "genre": "Horror", "notes": "Iconic horror anthology. Led to Senate hearings and the Comics Code Authority."},
    {"title": "The Vault of Horror",                     "writer": "Various",           "artist": "Johnny Craig",      "years": "1950-1955", "publisher": "EC Comics",    "genre": "Horror", "notes": "Sister title to Tales From the Crypt. Hosted by 'The Vault Keeper'."},
    {"title": "Weird Science",                           "writer": "Various",           "artist": "Wally Wood",        "years": "1950-1953", "publisher": "EC Comics",    "genre": "Sci-Fi", "notes": "Golden Age of EC science fiction. Wally Wood's art is especially sought."},
    {"title": "Mad #1 (comic book format)",              "writer": "Harvey Kurtzman",   "artist": "Various",           "years": "1952", "publisher": "EC Comics",    "genre": "Humor",     "notes": "First issue in comic book format before becoming a magazine. Very collectible."},

    # ── Silver Age — DC ───────────────────────────────────────────────────────
    {"title": "Showcase #4 (1st Silver Age Flash)",      "writer": "Robert Kanigher",   "artist": "Carmine Infantino", "years": "1956", "publisher": "DC Comics",    "genre": "Superhero", "notes": "Marks the beginning of the Silver Age of Comics. First Barry Allen Flash."},
    {"title": "Brave and the Bold #28 (1st JLA)",        "writer": "Gardner Fox",       "artist": "Mike Sekowsky",     "years": "1960", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First appearance of the Justice League of America."},
    {"title": "Green Lantern #76 (O'Neil / Adams)",      "writer": "Denny O'Neil",      "artist": "Neal Adams",        "years": "1970", "publisher": "DC Comics",    "genre": "Superhero", "notes": "Landmark 'relevant' comics era. Green Arrow joins. Deals with racism and drugs."},
    {"title": "Superman's Pal Jimmy Olsen #134 (1st Darkseid)", "writer": "Jack Kirby", "artist": "Jack Kirby",        "years": "1970", "publisher": "DC Comics",    "genre": "Superhero", "notes": "First cameo of Darkseid (as a silhouette). Part of Kirby's Fourth World."},
    {"title": "New Gods #1",                             "writer": "Jack Kirby",        "artist": "Jack Kirby",        "years": "1971", "publisher": "DC Comics",    "genre": "Superhero", "notes": "Kirby's Fourth World saga begins. First full Darkseid."},
    {"title": "DC Special Series #27 (Batman vs Predator)", "writer": "Dave Gibbons",  "artist": "Andy Kubert",       "years": "1991", "publisher": "DC Comics",    "genre": "Superhero", "notes": ""},

    # ── Silver Age — Marvel ───────────────────────────────────────────────────
    {"title": "Fantastic Four #1",                       "writer": "Stan Lee",          "artist": "Jack Kirby",        "years": "1961", "publisher": "Marvel Comics","genre": "Superhero", "notes": "Beginning of the Marvel Age of Comics. First Fantastic Four and Mole Man."},
    {"title": "Amazing Fantasy #15 (1st Spider-Man)",    "writer": "Stan Lee",          "artist": "Steve Ditko",       "years": "1962", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First appearance of Spider-Man. CGC 9.6 sold for $3.6M in 2021."},
    {"title": "Amazing Spider-Man #1",                   "writer": "Stan Lee",          "artist": "Steve Ditko",       "years": "1963", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First solo Spider-Man title."},
    {"title": "Amazing Spider-Man #129 (1st Punisher)",  "writer": "Gerry Conway",      "artist": "Ross Andru",        "years": "1974", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First appearance of the Punisher. Major key issue."},
    {"title": "Amazing Spider-Man #300 (1st Venom)",     "writer": "David Michelinie",  "artist": "Todd McFarlane",    "years": "1988", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First full appearance of Venom (Eddie Brock). Highly sought modern key."},
    {"title": "Incredible Hulk #1",                      "writer": "Stan Lee",          "artist": "Jack Kirby",        "years": "1962", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First appearance of the Hulk. Original grey color."},
    {"title": "Incredible Hulk #181 (1st Wolverine full)","writer": "Len Wein",        "artist": "Herb Trimpe",        "years": "1974", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First full appearance of Wolverine. Most valuable Bronze Age key."},
    {"title": "X-Men #1",                                "writer": "Stan Lee",          "artist": "Jack Kirby",        "years": "1963", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First X-Men. Original team: Cyclops, Marvel Girl, Beast, Iceman, Angel."},
    {"title": "Giant-Size X-Men #1 (New X-Men team)",   "writer": "Len Wein",          "artist": "Dave Cockrum",      "years": "1975", "publisher": "Marvel Comics","genre": "Superhero", "notes": "Introduces Wolverine, Storm, Colossus, Nightcrawler to the X-Men."},
    {"title": "Uncanny X-Men #94-101 (Dark Phoenix saga begins)", "writer": "Chris Claremont", "artist": "Dave Cockrum", "years": "1975-1976", "publisher": "Marvel Comics", "genre": "Superhero", "notes": "New X-Men's first regular adventures. Foundation of the Claremont era."},
    {"title": "Uncanny X-Men #129-137 (Dark Phoenix Saga)", "writer": "Chris Claremont","artist": "John Byrne",       "years": "1980", "publisher": "Marvel Comics","genre": "Superhero", "notes": "Landmark storyline. Death of Jean Grey. Considered the peak of the Claremont era."},
    {"title": "Iron Man #128 (Demon in a Bottle)",       "writer": "David Michelinie",  "artist": "Bob Layton",        "years": "1979", "publisher": "Marvel Comics","genre": "Superhero", "notes": "Tony Stark's alcoholism storyline. Highly regarded."},
    {"title": "Avengers #1",                             "writer": "Stan Lee",          "artist": "Jack Kirby",        "years": "1963", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First Avengers. Original team: Thor, Iron Man, Ant-Man, Wasp, Hulk."},
    {"title": "Avengers #4 (1st Silver Age Captain America)", "writer": "Stan Lee",    "artist": "Jack Kirby",        "years": "1964", "publisher": "Marvel Comics","genre": "Superhero", "notes": "Captain America returns from WWII. Major Silver Age key."},
    {"title": "Thor #126",                               "writer": "Stan Lee",          "artist": "Jack Kirby",        "years": "1966", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First Thor solo title (previously Journey into Mystery)."},
    {"title": "Tales of Suspense #39 (1st Iron Man)",    "writer": "Stan Lee",          "artist": "Don Heck / Kirby",  "years": "1963", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First appearance of Iron Man (in grey armor)."},
    {"title": "Journey into Mystery #83 (1st Thor)",     "writer": "Stan Lee",          "artist": "Jack Kirby",        "years": "1962", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First appearance of Thor. Key Golden/Silver Age."},
    {"title": "Daredevil #1",                            "writer": "Stan Lee",          "artist": "Bill Everett",      "years": "1964", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First appearance of Daredevil."},
    {"title": "Silver Surfer #1",                        "writer": "Stan Lee",          "artist": "John Buscema",      "years": "1968", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First solo Silver Surfer. Oversized issue."},

    # ── Bronze Age Keys ───────────────────────────────────────────────────────
    {"title": "Hero for Hire #1 (1st Luke Cage)",        "writer": "Archie Goodwin",    "artist": "George Tuska",      "years": "1972", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First African-American superhero with own title."},
    {"title": "Special Marvel Edition #15 (1st Shang-Chi)","writer": "Steve Englehart","artist": "Jim Starlin",       "years": "1973", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First appearance of Shang-Chi, Master of Kung Fu."},
    {"title": "Avengers #57 (1st Vision)",               "writer": "Roy Thomas",        "artist": "John Buscema",      "years": "1968", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First appearance of the Vision."},
    {"title": "Ms. Marvel #1 (Carol Danvers original)",  "writer": "Gerry Conway",      "artist": "John Buscema",      "years": "1977", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First solo Carol Danvers as Ms. Marvel."},
    {"title": "New Mutants #98 (1st Deadpool)",          "writer": "Fabian Nicieza",    "artist": "Rob Liefeld",       "years": "1991", "publisher": "Marvel Comics","genre": "Superhero", "notes": "First appearance of Deadpool. Modern key issue; very sought-after."},

    # ── Landmark Storylines & Graphic Novels ─────────────────────────────────
    {"title": "Watchmen (complete 12-issue series)",     "writer": "Alan Moore",        "artist": "Dave Gibbons",      "years": "1986-1987", "publisher": "DC Comics",  "genre": "Superhero", "notes": "Deconstruction of superhero genre. Won Hugo Award. Essential reading."},
    {"title": "The Dark Knight Returns (4-issue series)","writer": "Frank Miller",      "artist": "Frank Miller",      "years": "1986",      "publisher": "DC Comics",  "genre": "Superhero", "notes": "Landmark Batman story. Aged Bruce Wayne comes out of retirement."},
    {"title": "Batman: Year One",                        "writer": "Frank Miller",      "artist": "David Mazzucchelli","years": "1987",      "publisher": "DC Comics",  "genre": "Superhero", "notes": "Definitive Batman origin story. Basis for Batman Begins."},
    {"title": "Kingdom Come",                            "writer": "Mark Waid",         "artist": "Alex Ross",         "years": "1996",      "publisher": "DC Comics",  "genre": "Superhero", "notes": "Stunning painted art by Alex Ross. Elseworlds future DC."},
    {"title": "The Amazing Spider-Man: Kraven's Last Hunt","writer": "J.M. DeMatteis", "artist": "Mike Zeck",         "years": "1987",      "publisher": "Marvel Comics","genre": "Superhero","notes": "Considered the greatest Spider-Man story. Dark tone."},
    {"title": "Maus (complete two-volume work)",         "writer": "Art Spiegelman",    "artist": "Art Spiegelman",    "years": "1980-1991", "publisher": "Pantheon Books","genre": "Historical","notes": "Pulitzer Prize winner. Holocaust memoir using anthropomorphic animals."},
    {"title": "Persepolis",                              "writer": "Marjane Satrapi",   "artist": "Marjane Satrapi",   "years": "2000-2003", "publisher": "Pantheon Books","genre": "Historical","notes": "Autobiographical account of growing up during the Iranian Revolution."},
    {"title": "V for Vendetta",                          "writer": "Alan Moore",        "artist": "David Lloyd",       "years": "1982-1988", "publisher": "Warrior / DC","genre": "Sci-Fi",    "notes": "Dystopian political thriller set in fascist Britain."},
    {"title": "Sandman (complete 75-issue run)",         "writer": "Neil Gaiman",       "artist": "Various",           "years": "1989-1996", "publisher": "DC / Vertigo","genre": "Fantasy",   "notes": "Neil Gaiman's masterwork. Won World Fantasy Award."},
    {"title": "Preacher (complete 66-issue run)",        "writer": "Garth Ennis",       "artist": "Steve Dillon",      "years": "1995-2000", "publisher": "DC / Vertigo","genre": "Horror",    "notes": "Controversial and beloved Vertigo title."},

    # ── Image / Independent ───────────────────────────────────────────────────
    {"title": "Spawn #1",                                "writer": "Todd McFarlane",    "artist": "Todd McFarlane",    "years": "1992", "publisher": "Image Comics",  "genre": "Superhero", "notes": "First issue of Image Comics' most iconic title. 1.7 million copies sold."},
    {"title": "Saga (Image Comics)",                     "writer": "Brian K. Vaughan",  "artist": "Fiona Staples",     "years": "2012-present", "publisher": "Image Comics", "genre": "Sci-Fi", "notes": "Award-winning space opera. Multiple Eisner Awards."},
    {"title": "The Walking Dead #1",                     "writer": "Robert Kirkman",    "artist": "Tony Moore",        "years": "2003", "publisher": "Image Comics",  "genre": "Horror",    "notes": "Beginning of the landmark zombie series. Basis for the TV show."},
    {"title": "Bone (complete series)",                  "writer": "Jeff Smith",        "artist": "Jeff Smith",        "years": "1991-2004", "publisher": "Cartoon Books","genre": "Fantasy",  "notes": "One of the most acclaimed independent comics. Epic fantasy-adventure."},
    {"title": "Sin City (Frank Miller, complete)",       "writer": "Frank Miller",      "artist": "Frank Miller",      "years": "1991-2000", "publisher": "Dark Horse",   "genre": "Crime",    "notes": "Neo-noir crime comics. Black and white with spot color."},
    {"title": "Hellboy",                                 "writer": "Mike Mignola",      "artist": "Mike Mignola",      "years": "1994-present","publisher": "Dark Horse",  "genre": "Horror",   "notes": "Award-winning supernatural series. Multiple spin-offs."},

    # ── Manga ─────────────────────────────────────────────────────────────────
    {"title": "Dragon Ball",                             "writer": "Akira Toriyama",    "artist": "Akira Toriyama",    "years": "1984-1995", "publisher": "Shueisha (Weekly Shonen Jump)", "genre": "Shonen", "notes": "42 volumes. One of the best-selling manga series worldwide."},
    {"title": "Naruto",                                  "writer": "Masashi Kishimoto", "artist": "Masashi Kishimoto", "years": "1999-2014", "publisher": "Shueisha",      "genre": "Shonen",    "notes": "72 volumes. Enormous influence on anime/manga culture."},
    {"title": "One Piece",                               "writer": "Eiichiro Oda",      "artist": "Eiichiro Oda",      "years": "1997-present","publisher": "Shueisha",     "genre": "Shonen",    "notes": "World's best-selling manga series. 500 million copies in print."},
    {"title": "Attack on Titan",                         "writer": "Hajime Isayama",    "artist": "Hajime Isayama",    "years": "2009-2021", "publisher": "Kodansha",       "genre": "Shonen",    "notes": "34 volumes. Critically acclaimed dark fantasy."},
    {"title": "Death Note",                              "writer": "Tsugumi Ohba",      "artist": "Takeshi Obata",     "years": "2003-2006", "publisher": "Shueisha",      "genre": "Thriller",  "notes": "12 volumes. Psychological thriller/mystery."},
    {"title": "Akira",                                   "writer": "Katsuhiro Otomo",   "artist": "Katsuhiro Otomo",   "years": "1982-1990", "publisher": "Kodansha",       "genre": "Sci-Fi",    "notes": "6 volumes. Landmark of manga and anime. Set in post-apocalyptic Neo-Tokyo."},
    {"title": "Berserk",                                 "writer": "Kentaro Miura",     "artist": "Kentaro Miura",     "years": "1989-2021", "publisher": "Hakusensha",     "genre": "Dark Fantasy","notes": "Considered one of the greatest manga of all time. Author passed 2021."},
    {"title": "Fullmetal Alchemist",                     "writer": "Hiromu Arakawa",    "artist": "Hiromu Arakawa",    "years": "2001-2010", "publisher": "Square Enix",    "genre": "Shonen",    "notes": "27 volumes. Beloved steampunk fantasy."},
    {"title": "Ghost in the Shell",                      "writer": "Masamune Shirow",   "artist": "Masamune Shirow",   "years": "1989-1990", "publisher": "Kodansha",       "genre": "Sci-Fi",    "notes": "Cyberpunk classic. Basis for the 1995 animated film."},
    {"title": "Sailor Moon",                             "writer": "Naoko Takeuchi",    "artist": "Naoko Takeuchi",    "years": "1991-1997", "publisher": "Kodansha",       "genre": "Shojo",     "notes": "18 volumes. Defining magical girl manga."},
]


def search(query: str, country: str = "All") -> List[Dict[str, Any]]:
    q = query.strip().lower()
    results = []
    for entry in CATALOG:
        haystack = " ".join([
            entry.get("title", ""),
            entry.get("writer", ""),
            entry.get("artist", ""),
            entry.get("publisher", ""),
            entry.get("genre", ""),
            entry.get("notes", ""),
        ]).lower()
        if not q or q in haystack:
            results.append(entry)
    return results


def to_fields(entry: Dict[str, Any]) -> Dict[str, str]:
    return {k: v for k, v in {
        "title":     entry.get("title", ""),
        "writer":    entry.get("writer", ""),
        "artist":    entry.get("artist", ""),
        "year":      entry.get("years", ""),
        "publisher": entry.get("publisher", ""),
    }.items() if v}
