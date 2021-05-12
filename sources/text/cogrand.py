
from copy import deepcopy
from typing import Union

from Pokemon import Evolution, LearnedMove, METHODS, Pokemon
from sources.general import BOT_PREFIX as mew, Cmd, EMPTY, chunks, evenChunks

class COG:
    NAME = "Random Cog"
    DESC = "A cog that provides various ways to randomly generate numbers among other things."

class PATH:
    TABLES = "./sources/tables.json"
    POKEDEX = "./sources/pokedex.json"

RAND = Cmd(
    "random", "rand", "r", "roll",
    f"""
        This is the base command for generating random things. See `{mew}help random` for ways to use this command.
    """
)
RAND_DICE = Cmd(
    "dice", "roll",
    f"""
        This command simulates a dice roll. Given a number of dice and a number of sides, it rolls that many die with that many sides.
    """,
    usage=[
        "4d6",
        "1d20"
    ],
    parent=RAND
)
RAND_PKMN = Cmd(
    "pokemon", "pkmn",
    f"""
        This command will fetch a random Pokemon from the Pokedex.
    """
)

DEX = Cmd(
    "dex", "search", "fetch",
    f"""
        This is the base command for getting info and lists pertaining to Pokemon and other things. See `{mew}help dex` for ways to use this command.
    """
)
DEX_PKMN = Cmd(
    "pokemon", "pkmn", "pokedex",
    f"""
        This is a subcommand which will allow you to search for information about a specific Pokemon. See `{mew}help dex pokemon` for ways to use this command.
    """,
    parent=DEX
)
DEX_PKMN_NAME = Cmd(
    "name", "named",
    f"""
        This command will search for a Pokemon with a given name.
    """,
    parent=DEX_PKMN,
    usage=[
        "Porygon",
        "porgyon2",
        "porygon z"
    ]
)
DEX_PKMN_MOVE = Cmd(
    "move", "learns", "knows",
    f"""
        This command will search for each Pokemon that can possibly learn a given move.
    """,
    parent=DEX_PKMN,
    usage=[
        "levitate",
        "Trick room",
        "tri-attack"
    ]
)
DEX_PKMN_ABILITY = Cmd(
    "ability", "has",
    f"""
        This command will search for each Pokemon that can possibly have a given ability.
    """,
    parent=DEX_PKMN,
    usage=[
        "torrent",
        "intimidate"
    ]
)
DEX_PKMN_TYPE = Cmd(
    "type", "is",
    f"""
        This command will search for each Pokemon with a given type.
    """,
    usage=[
        "dragon",
        "normal"
    ]
)

RAND_LAST = Cmd(
    "last",
    f"""
        This command will fetch a random item from the list of things you last searched.
        Try using this command after doing `{DEX_PKMN_MOVE.ref} agility`.
    """,
    parent=RAND
)

def GET_PKMN_EMBED(pkmn: Pokemon):
    return dict(
        title=pkmn.dispName(),
        imageURL=pkmn.getImage(),
        fields=[
            ("Types", "```\n" + "\n".join(
                pkmn.dispTypes()
            ) + "```", True),
            ("Abilities", "```\n" + "\n".join(
                pkmn.dispAbilities()
            ) + (f"\n{pkmn.dispHiddenAbility()} (hidden)" if pkmn.hasHiddenAbility() else "") + "```", True),
        ],
        url=f"https://pokemondb.net/pokedex/{pkmn.id}"
    )

def GET_PKMN_LIST_PAGES(title: str, pkmnList: list[Pokemon]):
    pkmnList = sorted(pkmnList, key=lambda pkmn: pkmn.dispName())
    fields = [(EMPTY, "```\n"+"\n".join(pkmn.dispName() for pkmn in chunk) + "```", True) for chunk in chunks(pkmnList, 10)]
    pages = []
    for chunk in chunks(fields, 3):
        embed = dict(
            title=title,
            description=f"{len(pkmnList)} results",
            fields=chunk
        )
        pages.append(embed)
    return pages


def GET_PKMN_PAGES(pkmn: Pokemon):
    baseEmbed = GET_PKMN_EMBED(pkmn)
    addEvolutionsField(pkmn.getEvolutions(), baseEmbed)
    fieldLists = addMovesetFields(pkmn)
    pages = []
    #for field1, field2 in zip(fields[0::1], fields[1::2]):
    #    embed = deepcopy(baseEmbed)
    #    embed["fields"].append(field1)
    #    if field2:
    #        embed["fields"].append(field2)
    #    pages.append(embed)
    for fields in fieldLists:
        embed = deepcopy(baseEmbed)
        for field in fields:
            embed["fields"].append(field)
        pages.append(embed)
    return pages

def addEvolutionsField(evolutions: list[Evolution], embed: dict[str, Union[str, list[Union[tuple[str, str], tuple[str, str, bool]]]]]):
    maxThreshLen = max(len(evo.getThresh()) for evo in evolutions)
    bodyStr = "```\n"
    for evo in evolutions:
        threshSpacing = " " * (maxThreshLen - len(evo.getThresh()))
        bodyStr += f"{evo.dispThresh()}{threshSpacing} -> {evo.dispInto()}\n"
    bodyStr += "```"
    embed["fields"].append(
        (f"Evolution Line", bodyStr)
    )

def addMovesetFields(pkmn: Pokemon):
    fields = []
    moves = pkmn.getAllMovesWithMethod(METHODS.LEVEL)
    if moves: fields.append(addMovesetField(f"Moves by level", moves))
    moves = pkmn.getAllMovesWithMethod(METHODS.TM)
    if moves: fields.append(addMovesetField(f"Moves by TM", moves))
    moves = pkmn.getAllMovesWithMethod(METHODS.TR)
    if moves: fields.append(addMovesetField(f"Moves by TR", moves))
    moves = pkmn.getAllMovesWithMethod(METHODS.EGG)
    if moves: fields.append(addMovesetField(f"Moves by breeding", moves))
    moves = pkmn.getAllMovesWithMethod(METHODS.TUTOR)
    if moves: fields.append(addMovesetField(f"Moves by tutor", moves))
    moves = pkmn.getAllMovesWithMethod(METHODS.TRANSFER)
    if moves: fields.append(addMovesetField(f"Moves by transfer", moves))
    
    return fields

def addMovesetField(title: str, moves: list[LearnedMove]):
    if moves[0].method in METHODS.HAS_NUM:
        sortedMoves = sorted(moves, key=lambda move: int(move.getFirstNum()))
    else:
        sortedMoves = sorted(moves, key=lambda move: move.getName())
    bodies = []
    for chunk in evenChunks(sortedMoves):
        bodyStr = "```\n"
        for move in chunk:
            bodyStr += f"{move.dispName()}\n"
        bodyStr += "```"
        bodies.append(bodyStr)
    ret = [[EMPTY, bodyStr, True] for bodyStr in bodies]
    ret[0][0] = title
    return ret

_not_found = lambda thing: lambda realThing: f"The {thing} `{realThing}` didn't match for any Pokemon."
class ERR:
    INVALID_SUBCOMMAND = lambda args: f"The entry `{args}` is invalid."
    BAD_DICE_FORMAT = lambda arg: f"The entry `{arg}` isn't a valid die. Format it like `4d6`, where `4` is the dice count and `6` is the number of sides on each die."
    BAD_POKEMON = lambda arg: f"The Pokemon specified, `{arg}`, wasn't found."
    NO_LAST = f"You haven't used a dex command since the bot was restarted!"
    MOVE_NOT_FOUND = _not_found("move")
    ABILITY_NOT_FOUND = _not_found("ability")
    TYPE_NOT_FOUND = _not_found("type")

_separator = ", "
_title = lambda thing: lambda realThing: f"Pokemon with the {thing} `{realThing}`"
class INFO:
    TOO_MANY_DICE = lambda entry: f"The entry `{entry}` would roll too many dice!"
    ROLL = lambda rolls: "```" + "\n\n".join([f"Rolling {arg}:\n{_separator.join(rolls[arg])}" for arg in rolls]) + "```"
    DEX_PKMN_MOVE_TITLE = _title("move")
    DEX_PKMN_ABILITY_TITLE = _title("ability")
    DEX_PKMN_TYPE_TITLE = _title("type")