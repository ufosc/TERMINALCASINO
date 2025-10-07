from pathlib import Path

############## UNO CARD ARTS ##############

# flipped card (face-down)
flipped_uno = """
┌─────────┐
|░░░░░░░░░|
|░░░░░░░░░|
|░░░UNO░░░|
|░░░░░░░░░|
|░░░░░░░░░|
└─────────┘
"""

# -----------------------
# Red UNO cards
# -----------------------
r0 = """
┌─────────┐
|0        |
|    0    |
|  (RED)  |
|    0    |
|        0|
└─────────┘
"""

r1 = """
┌─────────┐
|1        |
|    1    |
|  (RED)  |
|    1    |
|        1|
└─────────┘
"""

r2 = """
┌─────────┐
|2        |
|    2    |
|  (RED)  |
|    2    |
|        2|
└─────────┘
"""

r3 = """
┌─────────┐
|3        |
|    3    |
|  (RED)  |
|    3    |
|        3|
└─────────┘
"""

r4 = """
┌─────────┐
|4        |
|    4    |
|  (RED)  |
|    4    |
|        4|
└─────────┘
"""

r5 = """
┌─────────┐
|5        |
|    5    |
|  (RED)  |
|    5    |
|        5|
└─────────┘
"""

r6 = """
┌─────────┐
|6        |
|    6    |
|  (RED)  |
|    6    |
|        6|
└─────────┘
"""

r7 = """
┌─────────┐
|7        |
|    7    |
|  (RED)  |
|    7    |
|        7|
└─────────┘
"""

r8 = """
┌─────────┐
|8        |
|    8    |
|  (RED)  |
|    8    |
|        8|
└─────────┘
"""

r9 = """
┌─────────┐
|9        |
|    9    |
|  (RED)  |
|    9    |
|        9|
└─────────┘
"""

# Action cards
rskip = """
┌─────────┐
|SKIP     |
|    ⊘    |
|  (RED)  |
|    ⊘    |
|     SKIP|
└─────────┘
"""

rrev = """
┌─────────┐
|REV      |
|   ⤸⤸    |
|  (RED)  |
|   ⤸⤸    |
|      REV|
└─────────┘
"""

rplus2 = """
┌─────────┐
|+2       |
|   +2    |
|  (RED)  |
|   +2    |
|       +2|
└─────────┘
"""

# -----------------------
# Yellow UNO cards
# -----------------------
y0 = """
┌─────────┐
|0        |
|    0    |
| (YELLO) |
|    0    |
|        0|
└─────────┘
"""

y1 = """
┌─────────┐
|1        |
|    1    |
| (YELLO) |
|    1    |
|        1|
└─────────┘
"""

y2 = """
┌─────────┐
|2        |
|    2    |
| (YELLO) |
|    2    |
|        2|
└─────────┘
"""

y3 = """
┌─────────┐
|3        |
|    3    |
| (YELLO) |
|    3    |
|        3|
└─────────┘
"""

y4 = """
┌─────────┐
|4        |
|    4    |
| (YELLO) |
|    4    |
|        4|
└─────────┘
"""

y5 = """
┌─────────┐
|5        |
|    5    |
| (YELLO) |
|    5    |
|        5|
└─────────┘
"""

y6 = """
┌─────────┐
|6        |
|    6    |
| (YELLO) |
|    6    |
|        6|
└─────────┘
"""

y7 = """
┌─────────┐
|7        |
|    7    |
| (YELLO) |
|    7    |
|        7|
└─────────┘
"""

y8 = """
┌─────────┐
|8        |
|    8    |
| (YELLO) |
|    8    |
|        8|
└─────────┘
"""

y9 = """
┌─────────┐
|9        |
|    9    |
| (YELLO) |
|    9    |
|        9|
└─────────┘
"""

# Action cards
yskip = """
┌─────────┐
|SKIP     |
|    ⊘    |
| (YELLO) |
|    ⊘    |
|     SKIP|
└─────────┘
"""

yrev = """
┌─────────┐
|REV      |
|   ⤸⤸    |
| (YELLO) |
|   ⤸⤸    |
|      REV|
└─────────┘
"""

yplus2 = """
┌─────────┐
|+2       |
|   +2    |
| (YELLO) |
|   +2    |
|       +2|
└─────────┘
"""

# -----------------------
# Blue UNO cards
# -----------------------
b0 = """
┌─────────┐
|0        |
|    0    |
| (BLUE)  |
|    0    |
|        0|
└─────────┘
"""

b1 = """
┌─────────┐
|1        |
|    1    |
| (BLUE)  |
|    1    |
|        1|
└─────────┘
"""

b2 = """
┌─────────┐
|2        |
|    2    |
| (BLUE)  |
|    2    |
|        2|
└─────────┘
"""

b3 = """
┌─────────┐
|3        |
|    3    |
| (BLUE)  |
|    3    |
|        3|
└─────────┘
"""

b4 = """
┌─────────┐
|4        |
|    4    |
| (BLUE)  |
|    4    |
|        4|
└─────────┘
"""

b5 = """
┌─────────┐
|5        |
|    5    |
| (BLUE)  |
|    5    |
|        5|
└─────────┘
"""

b6 = """
┌─────────┐
|6        |
|    6    |
| (BLUE)  |
|    6    |
|        6|
└─────────┘
"""

b7 = """
┌─────────┐
|7        |
|    7    |
| (BLUE)  |
|    7    |
|        7|
└─────────┘
"""

b8 = """
┌─────────┐
|8        |
|    8    |
| (BLUE)  |
|    8    |
|        8|
└─────────┘
"""

b9 = """
┌─────────┐
|9        |
|    9    |
| (BLUE)  |
|    9    |
|        9|
└─────────┘
"""

# Action cards
bskip = """
┌─────────┐
|SKIP     |
|    ⊘    |
| (BLUE)  |
|    ⊘    |
|     SKIP|
└─────────┘
"""

brev = """
┌─────────┐
|REV      |
|   ⤸⤸    |
| (BLUE)  |
|   ⤸⤸    |
|      REV|
└─────────┘
"""

bplus2 = """
┌─────────┐
|+2       |
|   +2    |
| (BLUE)  |
|   +2    |
|       +2|
└─────────┘
"""

# -----------------------
# Green UNO cards
# -----------------------
g0 = """
┌─────────┐
|0        |
|    0    |
| (GREEN) |
|    0    |
|        0|
└─────────┘
"""

g1 = """
┌─────────┐
|1        |
|    1    |
| (GREEN) |
|    1    |
|        1|
└─────────┘
"""

g2 = """
┌─────────┐
|2        |
|    2    |
| (GREEN) |
|    2    |
|        2|
└─────────┘
"""

g3 = """
┌─────────┐
|3        |
|    3    |
| (GREEN) |
|    3    |
|        3|
└─────────┘
"""

g4 = """
┌─────────┐
|4        |
|    4    |
| (GREEN) |
|    4    |
|        4|
└─────────┘
"""

g5 = """
┌─────────┐
|5        |
|    5    |
| (GREEN) |
|    5    |
|        5|
└─────────┘
"""

g6 = """
┌─────────┐
|6        |
|    6    |
| (GREEN) |
|    6    |
|        6|
└─────────┘
"""

g7 = """
┌─────────┐
|7        |
|    7    |
| (GREEN) |
|    7    |
|        7|
└─────────┘
"""

g8 = """
┌─────────┐
|8        |
|    8    |
| (GREEN) |
|    8    |
|        8|
└─────────┘
"""

g9 = """
┌─────────┐
|9        |
|    9    |
| (GREEN) |
|    9    |
|        9|
└─────────┘
"""

# Action cards
gskip = """
┌─────────┐
|SKIP     |
|    ⊘    |
| (GREEN) |
|    ⊘    |
|     SKIP|
└─────────┘
"""

grev = """
┌─────────┐
|REV      |
|   ⤸⤸    |
| (GREEN) |
|   ⤸⤸    |
|      REV|
└─────────┘
"""

gplus2 = """
┌─────────┐
|+2       |
|   +2    |
| (GREEN) |
|   +2    |
|       +2|
└─────────┘
"""

# -----------------------
# Wild UNO cards
# -----------------------

# Standard Wild
wild = """
┌─────────┐
|WILD     |
|  WILD   |
| (ANY)   |
|  WILD   |
|     WILD|
└─────────┘
"""

# Wild +4
wildplus4 = """
┌─────────┐
|+4       |
|   +4    |
| (ANY)   |
|   +4    |
|       +4|
└─────────┘
"""

# card dictionary for UNO cards
uno_card_dict: dict[str, str] = {
    # Reds
    "r0": r0, "r1": r1, "r2": r2, "r3": r3, "r4": r4,
    "r5": r5, "r6": r6, "r7": r7, "r8": r8, "r9": r9,
    "rskip": rskip, "rrev": rrev, "r+2": rplus2,

    # Greens
    "g0": g0, "g1": g1, "g2": g2, "g3": g3, "g4": g4,
    "g5": g5, "g6": g6, "g7": g7, "g8": g8, "g9": g9,
    "gskip": gskip, "grev": grev, "g+2": gplus2,

    # Blues
    "b0": b0, "b1": b1, "b2": b2, "b3": b3, "b4": b4,
    "b5": b5, "b6": b6, "b7": b7, "b8": b8, "b9": b9,
    "bskip": bskip, "brev": brev, "b+2": bplus2,

    # Yellows
    "y0": y0, "y1": y1, "y2": y2, "y3": y3, "y4": y4,
    "y5": y5, "y6": y6, "y7": y7, "y8": y8, "y9": y9,
    "yskip": yskip, "yrev": yrev, "y+2": yplus2,

    # Wilds
    "wild": wild,
    "wild+4": wildplus4,

    # Face-down UNO card
    "flipped": flipped_uno
}

color_map = {
    "r": "red",
    "g": "green",
    "b": "blue",
    "y": "yellow",
}

action_map = {
    "skip": "skip",
    "rev": "reverse",
    "+2": "draw_2",
    "wild": "wild",
    "wild+4": "wild_draw_4",
    "flipped": "flipped"
}

def to_filename(key: str) -> str:
    """
    Converts key to file name for export()
    """

    # Handle wild cards and flipped directly
    if key in ("wild", "wild+4", "flipped"):
        return f"{action_map[key]}.txt"

    color = color_map.get(key[0], "")
    value = key[1:]

    # Translate special actions like skip/rev/+2
    if value in action_map:
        value = action_map[value]

    return f"{color}_{value}.txt"

def assign_uno_card_art(card) -> str:
    """Return UNO card art from dict."""
    _, card_id = card
    return uno_card_dict[card_id]

def export():
    for keys, card in uno_card_dict.items():
        file_name = to_filename(keys)
        card = card.lstrip("\n")

        ASSET_DIR = Path(f"./assets/cards/uno/{file_name}")

        with open(ASSET_DIR, "w", encoding="utf-8") as file:
            file.write(card)

export()