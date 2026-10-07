"""
Museum layout model for the Grand Egyptian Museum (GEM).

IMPORTANT - what is real and what is schematic
----------------------------------------------
The *topology* follows public descriptions of the museum:
  * Hanging Obelisk (entrance) -> Grand Hall (Ramesses II colossus)
  * Grand Staircase (monumental, statues, pyramid panorama at the top)
  * At the top of the stairs: LEFT -> 12 Main Galleries (4 eras x 3 themes:
    Society / Kingship / Beliefs), RIGHT -> Tutankhamun Galleries (5 themes)
  * Khufu's Boats Museum, Children's Museum, shops/cafes, 4 basement "cave" galleries
The (x, y) coordinates are SCHEMATIC metres (each floor has its own origin) so that
walking distances are plausible. Replace them with measurements from the official
floor plan when available: edit this file (or data/zones.csv + data/edges.csv and
re-run `python scripts/build_all.py`) - everything else adapts automatically.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

FLOOR_LABELS = {
    -1: "Lower Level (Cave Galleries)",
    0: "Ground Level (Grand Hall)",
    1: "Grand Staircase - Level 1",
    2: "Grand Staircase - Level 2",
    3: "Grand Staircase - Level 3",
    4: "Galleries Level",
}

# id, name, type, floor, x, y, description
ZONES = [
    # ---- Ground level / outdoors ------------------------------------------------
    ("ENTRANCE", "Main Entrance & Hanging Obelisk", "entrance", 0, 100, 20,
     "Museum entrance plaza with the Hanging Obelisk of Ramesses II."),
    ("TICKETS", "Ticket Hall & Security", "service", 0, 100, 55,
     "Ticket checks, security screening and cloakroom for large bags."),
    ("GRAND_HALL", "Grand Hall (Ramesses II Colossus)", "gallery", 0, 100, 100,
     "Atrium dominated by the 11 m, 83-ton colossus of Ramesses II."),
    ("RESTROOM_0", "Restrooms (Ground)", "restroom", 0, 40, 90, "Restrooms near the Grand Hall."),
    ("CAFE", "Cafes & Restaurants", "food", 0, 20, 130, "Cafes and restaurants in the commercial area."),
    ("SHOP", "Museum Store", "shop", 0, 180, 130, "Gift and book shop in the commercial area."),
    ("CHILDREN", "Children's Museum", "gallery", 0, 40, 170, "Learning area for children."),
    ("GARDEN", "Exterior Gardens & Piazza", "outdoor", 0, 170, 50, "Gardens with views over the plateau."),
    ("BOATS", "Khufu's Boats Museum", "gallery", 0, 240, 120, "Dedicated building for the Solar Boats of Khufu."),
    ("ELV_W_0", "West Elevator (Ground)", "elevator", 0, 60, 110, "Step-free access to all levels."),
    ("ELV_E_0", "East Elevator (Ground)", "elevator", 0, 150, 110, "Step-free access to all levels."),
    ("STAIR_LOWER", "Stairwell to Lower Level", "stairs", 0, 120, 90, "Stairs down to the cave galleries."),
    # ---- Grand Staircase landings (statues are displayed along the stairs) -------
    ("GS_0", "Grand Staircase - Royal Image", "gallery", 0, 100, 150,
     "Foot of the Grand Staircase: royal statuary, shrines and architectural elements."),
    ("GS_1", "Grand Staircase - Divine Houses", "gallery", 1, 100, 100,
     "Shrines and architectural elements dedicated to the gods."),
    ("GS_2", "Grand Staircase - Gods & Kings", "gallery", 2, 100, 100,
     "Statues of gods and kings; Senwosret I and the king list on the side stair."),
    ("GS_3", "Grand Staircase - Journey to Eternity", "gallery", 3, 100, 100,
     "Funerary-themed monuments, the Akhenaten head and the Restoration Stela."),
    ("GS_TOP", "Grand Staircase Top & Pyramid Panorama", "junction", 4, 300, 40,
     "Panoramic window to the Giza pyramids; turn left for the Main Galleries, right for Tutankhamun."),
    # ---- Galleries level extras ------------------------------------------------
    ("ELV_W_4", "West Elevator (Galleries Level)", "elevator", 4, 270, 100, "Step-free access."),
    ("ELV_E_4", "East Elevator (Galleries Level)", "elevator", 4, 330, 100, "Step-free access."),
    ("RESTROOM_4", "Restrooms (Galleries Level)", "restroom", 4, 300, 75, "Restrooms at the top of the staircase."),
]

# id, name, era_group, theme, row (era), col (theme)
MAIN_GALLERIES = [
    ("G01", "Gallery 1 - Early Society", "Early Egypt", "Society", 0, 0),
    ("G02", "Gallery 2 - Early Kingship", "Early Egypt", "Kingship", 0, 1),
    ("G03", "Gallery 3 - Early Beliefs", "Early Egypt", "Beliefs", 0, 2),
    ("G04", "Gallery 4 - Middle Kingdom Society", "Middle Kingdom", "Society", 1, 0),
    ("G05", "Gallery 5 - Middle Kingdom Kingship", "Middle Kingdom", "Kingship", 1, 1),
    ("G06", "Gallery 6 - Middle Kingdom Beliefs", "Middle Kingdom", "Beliefs", 1, 2),
    ("G07", "Gallery 7 - New Kingdom Society", "New Kingdom", "Society", 2, 0),
    ("G08", "Gallery 8 - New Kingdom Kingship", "New Kingdom", "Kingship", 2, 1),
    ("G09", "Gallery 9 - New Kingdom Beliefs", "New Kingdom", "Beliefs", 2, 2),
    ("G10", "Gallery 10 - Late Period Society", "Late & Greco-Roman", "Society", 3, 0),
    ("G11", "Gallery 11 - Late Period Kingship", "Late & Greco-Roman", "Kingship", 3, 1),
    ("G12", "Gallery 12 - Greco-Roman Beliefs", "Late & Greco-Roman", "Beliefs", 3, 2),
]

TUT_GALLERIES = [
    ("TUT_1", "Tutankhamun - Identity of the King", "Identity", 380, 40),
    ("TUT_2", "Tutankhamun - Discovery of the Tomb", "Discovery", 440, 40),
    ("TUT_3", "Tutankhamun - Daily Life & Personal Possessions", "Daily Life", 500, 40),
    ("TUT_4", "Tutankhamun - Royal Funerary Equipment (Golden Mask)", "Burial", 500, 100),
    ("TUT_5", "Tutankhamun - Rebirth & the Afterlife", "Afterlife", 440, 100),
]

CAVES = [("CAVE_1", "Cave Gallery 1"), ("CAVE_2", "Cave Gallery 2"),
         ("CAVE_3", "Cave Gallery 3"), ("CAVE_4", "Cave Gallery 4")]


@dataclass
class Edge:
    a: str
    b: str
    kind: str        # walk | stairs | elevator | outdoor
    length: float    # metres (vertical segments get a nominal length)
    levels: int = 0


@dataclass
class Layout:
    zones: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)


def _dist(z1: dict, z2: dict) -> float:
    return math.hypot(z1["x"] - z2["x"], z1["y"] - z2["y"])


def build_layout() -> Layout:
    L = Layout()

    def add(zid, name, typ, floor, x, y, desc, era_group="", theme=""):
        L.zones[zid] = dict(id=zid, name=name, type=typ, floor=floor, x=float(x), y=float(y),
                            description=desc, era_group=era_group, theme=theme)

    for z in ZONES:
        add(*z)
    # Main Galleries: grid LEFT of the junction. G01 (col 0) is next to GS_TOP.
    for gid, name, era, theme, r, c in MAIN_GALLERIES:
        add(gid, name, "gallery", 4, 220 - c * 80, 40 + r * 60, f"{era} - {theme}", era, theme)
    for tid, name, theme, x, y in TUT_GALLERIES:
        add(tid, name, "gallery", 4, x, y, name, "Tutankhamun", theme)
    for i, (cid, name) in enumerate(CAVES):
        add(cid, name, "gallery", -1, 40 + i * 45, 120, "Small basement gallery ('cave').", "Mixed", "Special")
    add("STAIR_LOWER_-1", "Stairwell (Lower Level)", "stairs", -1, 120, 100, "Stairs up to the ground level.")
    for f in (-1, 1, 2, 3):
        for s in ("W", "E"):
            add(f"ELV_{s}_{f}", f"{'West' if s == 'W' else 'East'} Elevator (Level {f})", "elevator", f,
                60 if s == "W" else 150, 110, "Step-free access.")

    def walk(a, b, kind="walk", mult=1.0):
        L.edges.append(Edge(a, b, kind, round(max(_dist(L.zones[a], L.zones[b]), 6.0) * mult, 1)))

    # ---- Ground floor ------------------------------------------------------------
    for a, b in [("ENTRANCE", "TICKETS"), ("TICKETS", "GRAND_HALL"), ("GRAND_HALL", "RESTROOM_0"),
                 ("GRAND_HALL", "ELV_W_0"), ("GRAND_HALL", "ELV_E_0"), ("GRAND_HALL", "CAFE"),
                 ("GRAND_HALL", "SHOP"), ("GRAND_HALL", "CHILDREN"), ("GRAND_HALL", "GS_0"),
                 ("GRAND_HALL", "STAIR_LOWER"), ("CAFE", "CHILDREN")]:
        walk(a, b)
    for a, b in [("ENTRANCE", "GARDEN"), ("GARDEN", "SHOP"), ("GARDEN", "BOATS"), ("SHOP", "BOATS"),
                 ("ELV_E_0", "BOATS")]:
        walk(a, b, "outdoor", 1.3)
    # ---- Grand Staircase (stairs only; step-free users use the elevators) --------
    chain = ["GS_0", "GS_1", "GS_2", "GS_3", "GS_TOP"]
    for a, b in zip(chain, chain[1:]):
        L.edges.append(Edge(a, b, "stairs", 40.0, 1))
    # ---- Elevators ---------------------------------------------------------------
    floors = [-1, 0, 1, 2, 3, 4]
    for s in ("W", "E"):
        for f1, f2 in zip(floors, floors[1:]):
            L.edges.append(Edge(f"ELV_{s}_{f1}", f"ELV_{s}_{f2}", "elevator", 12.0, 1))
    for f, node in [(1, "GS_1"), (2, "GS_2"), (3, "GS_3")]:
        walk(f"ELV_W_{f}", node)
        walk(f"ELV_E_{f}", node)
    walk("ELV_W_4", "GS_TOP")
    walk("ELV_E_4", "GS_TOP")
    walk("RESTROOM_4", "GS_TOP")
    # ---- Lower level ---------------------------------------------------------------
    walk("ELV_W_-1", "CAVE_1")
    walk("ELV_E_-1", "CAVE_4")
    for a, b in zip(["CAVE_1", "CAVE_2", "CAVE_3"], ["CAVE_2", "CAVE_3", "CAVE_4"]):
        walk(a, b)
    walk("STAIR_LOWER_-1", "CAVE_3")
    L.edges.append(Edge("STAIR_LOWER", "STAIR_LOWER_-1", "stairs", 18.0, 1))
    # ---- Main galleries: grid neighbours + entry from the junction -----------------
    pos = {gid: (r, c) for gid, _, _, _, r, c in MAIN_GALLERIES}
    by_rc = {v: k for k, v in pos.items()}
    for gid, (r, c) in pos.items():
        for dr, dc in ((0, 1), (1, 0)):
            nb = by_rc.get((r + dr, c + dc))
            if nb:
                walk(gid, nb)
    walk("GS_TOP", "G01")
    walk("ELV_W_4", "G04")
    walk("RESTROOM_4", "G04")
    # ---- Tutankhamun galleries: a continuous one-way-friendly chain ----------------
    walk("GS_TOP", "TUT_1")
    for a, b in zip(["TUT_1", "TUT_2", "TUT_3", "TUT_4"], ["TUT_2", "TUT_3", "TUT_4", "TUT_5"]):
        walk(a, b)
    walk("ELV_E_4", "TUT_5")
    return L


def layout_as_tables():
    L = build_layout()
    zrows = [dict(z) for z in L.zones.values()]
    erows = [dict(a=e.a, b=e.b, kind=e.kind, length_m=e.length, levels=e.levels) for e in L.edges]
    return zrows, erows


if __name__ == "__main__":
    z, e = layout_as_tables()
    print(len(z), "zones", len(e), "edges")
