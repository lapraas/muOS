
from back.Dexes import Pokemon

g1 = "red-blue-yellow"
lv = "level-up"
r = "record"
m = "machine"
g1lv = lambda level: (g1, lv, level)
g1r = (g1, r, 0)
g1m = (g1, m, 0)

MISSINGNO = Pokemon(
    "missingno", 0, "Missingno",
    3.3, 1590.8,
    [], None,
    {
        "water-gun": [g1lv(1)],
        "sky-attack": [g1lv(1)],
        "pay-day": [g1lv(1)],
        "bind": [g1lv(1)],
        "mega-punch": [g1r],
        "razor-wind": [g1r],
        "swords-dance": [g1r],
        "mega-kick": [g1r],
        "toxic": [g1r],
        "take-down": [g1r],
        "double-edge": [g1r],
        "bubble-beam": [g1r],
        "ice-beam": [g1r],
        "blizzard": [g1r],
        "submission": [g1r],
        "seismic-toss": [g1r],
        "rage": [g1r],
        "thunder": [g1r],
        "earthquake": [g1r],
        "fissure": [g1r],
        "psychic": [g1r],
        "teleport": [g1r],
        "sky-attack": [g1r],
        "rest": [g1r],
        "thunder-wave": [g1r],
        "tri-attack": [g1r],
        "substitute": [g1r],
        "cut": [g1m],
        "fly": [g1m]
    },
    {
        "hp": (33, 0),
        "attack": (136, 0),
        "defense": (0, 0),
        "special-attack": (6, 0),
        "special-defense": (6, 0),
        "speed": (29, 0)
    },
    [
        "bird",
        "normal"
    ],
    [], ["missingno"], [],
    False, False, False, False,
    "barcode", "barcode", g1
)