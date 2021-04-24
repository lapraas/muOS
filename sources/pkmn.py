
from Pokemon import Evolution, Pokemon, LearnedMove, METHODS

MISSINGNO = Pokemon("missingno", None)
MISSINGNO.id = "0"
MISSINGNO.image = "https://cdn2.bulbagarden.net/upload/4/47/RBGlitchMissingno._b.png"
MISSINGNO.types = ["Bird", "Normal", "999"]
MISSINGNO.height = "0"
MISSINGNO.weight = "0"
MISSINGNO.abilities = []
MISSINGNO.hiddenAbility = "NONE"
MISSINGNO.evolutions = [
    Evolution("224", "missingno")
]
MISSINGNO.moves = [
    LearnedMove("water gun", "1", METHODS.LEVEL, "1"),
    LearnedMove("water gun", "1", METHODS.LEVEL, "1"),
    LearnedMove("sky attack", "1", METHODS.LEVEL, "1"),
    LearnedMove("pay day", "1", METHODS.LEVEL, "1"),
    LearnedMove("bind", "1", METHODS.LEVEL, "1"),
    LearnedMove("mega punch", "1", METHODS.TR, "1"),
    LearnedMove("razor wind", "1", METHODS.TR, "2"),
    LearnedMove("swords dance", "1", METHODS.TR, "3"),
    LearnedMove("mega kick", "1", METHODS.TR, "5"),
    LearnedMove("toxic", "1", METHODS.TR, "6"),
    LearnedMove("take down", "1", METHODS.TR, "9"),
    LearnedMove("double-edge", "1", METHODS.TR, "10"),
    LearnedMove("bubblebeam", "1", METHODS.TR, "11"),
    LearnedMove("ice beam", "1", METHODS.TR, "13"),
    LearnedMove("blizzard", "1", METHODS.TR, "14"),
    LearnedMove("submission", "1", METHODS.TR, "17"),
    LearnedMove("seismic toss", "1", METHODS.TR, "19"),
    LearnedMove("rage", "1", METHODS.TR, "20"),
    LearnedMove("thunder", "1", METHODS.TR, "25"),
    LearnedMove("earthquake", "1", METHODS.TR, "26"),
    LearnedMove("fissure", "1", METHODS.TR, "27"),
    LearnedMove("psychic", "1", METHODS.TR, "29"),
    LearnedMove("teleport", "1", METHODS.TR, "30"),
    LearnedMove("sky attack", "1", METHODS.TR, "43"),
    LearnedMove("rest", "1", METHODS.TR, "44"),
    LearnedMove("thunder wave", "1", METHODS.TR, "45"),
    LearnedMove("tri attack", "1", METHODS.TR, "49"),
    LearnedMove("substitute", "1", METHODS.TR, "50"),
    LearnedMove("cut", "1", METHODS.TM, "1"),
    LearnedMove("fly", "1", METHODS.TM, "2")
]