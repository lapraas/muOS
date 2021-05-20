 
from typing import Union
from back.Dexes import LearnedMove, Method, Move, Pokemon
from back.general import Cmd, EMPTY, NEWLINE, chunks, evenChunks, padItems

class COG:
    NAME = "Dex Cog"
    DESC = "A cog that provides lookup for various Pokemon resources. It includes a Pokedex, a Movedex, and an Abilitydex."

QUERY = Cmd(
    "query", "dex",
    f"""
        This is an all-purpose command that will give the user a list of Pokemon that match the entry.
    """,
    usage=[
        "porygon-z",
        "pokemon with moves trick room and tri attack",
        "legendary pokemon",
        "pokemon with types water, electric"
        "baby pokemon with ability natural cure",
    ]
)
CHECK = Cmd(
    "check",
    f"""
        This command will check whether or not a Pokemon has a list of moves.
        Specify the Pokemon's name first, then the word "for", then a comma-separated list of moves to check.
    """,
    usage=[
        "gardevoir for teleport, telekinesis, wish, life dew, future sight, protect, magical leaf, will-o-wisp, swift, shadow ball"
    ]
)

_forQuery = lambda query: f"For query `{query}`:\n"
_forExtra = lambda extra: f"For the specification `{extra}`, "
class ERR:
    # Query
    NO_MODE = lambda query, modes: f"{_forQuery(query)}If you're looking for a specific Pokemon/move/ability, you might have misspelled it.\nA mode (`{'`, `'.join(modes)}`) defining what kind of resource to look for must be provided for non-specific queries."
    BAD_MODIFIER = lambda query, bad, mode, modifiers: f"{_forQuery(query)}The modifier `{bad}` is an invalid modifier. Use one of the following modifiers for the mode {mode}: `{'`, `'.join(modifiers)}`"
    MIXING_OPS = lambda query: f"{_forQuery(query)}The combination of `and` and `or` in a single query is not implemented."
    NO_EXTRA_MODE = lambda query, extra: f"{_forQuery(query)}{_forExtra(extra)}an attribute of the target resource must be given. An attribute is something like `move`, `type`, `ability`, etc."
    # Check
    NO_FOR = f"The correct formatting for this command is `{CHECK.ref} [Pokemon] for [Moves]`, where\n  [Pokemon] is the Pokemon target, and\n  [Moves] is a comma-separated list of moves to check the target's moveset for."
    NO_PKMN = f"A target Pokemon was not specified."
    NO_MOVES = f"No moves were specified to search the target Pokemon's moveset for."
    PKMN_NOT_FOUND = lambda pkmn: f"The Pokemon `{pkmn}` was not found in the Pokedex."
    MOVE_NOT_FOUND = lambda move: f"The move `{move}` was not found in the Movedex."

class INFO:
    # Query
    NO_MATCH = lambda query: f"No results were found for the query `{query}`."
    # Check
    RESULT_HAS = lambda items: {
        "title": f"Results",
        "description": f"```{NEWLINE.join(_resultHas(items))}```"
    }

_RawEmbed = Union[tuple[str, str], tuple[str, str, bool]]
_PkmnPage = dict[str, Union[str, list[_RawEmbed]]]
def GET_PKMN_PAGES(pkmn: Pokemon):
    pages: list[_PkmnPage] = []
    base = dict(
        title=pkmn.dispName(),
        thumbnail=pkmn.getImageURL(),
        url=f"https://pokemondb.net/pokedex/{pkmn.id}"
    )
    basic = {**base, **{"fields": [
        ("Types", f"```{NEWLINE}{NEWLINE.join(pkmn.dispTypes())}```", True),
        ("Abilities", f"```{NEWLINE}{NEWLINE.join(pkmn.dispAllAbilities())}```", True),
        ("Evolution line", f"```{NEWLINE}{NEWLINE.join(pkmn.dispEvolutions())}```", False),
    ]}}
    appearance = {**base, **{f"fields": [
        ("Size", f"```Weight: {pkmn.dispWeight()}{NEWLINE}Height: {pkmn.dispHeight()}```", True),
        ("Appearance", f"```Color:      {pkmn.dispColor()}{NEWLINE}Body shape: {pkmn.dispShape()}```", True),
    ]}}
    if pkmn.hasClassifications():
        appearance["fields"].append(
            ("Other", f"```{NEWLINE}```", True)
        )
    else:
        appearance["fields"].append(
            (EMPTY, EMPTY, True)
        )
    appearance["fields"].append(
        ("Egg groups", f"```{NEWLINE}{NEWLINE.join(pkmn.dispEggGroups())}```", True)
    )
    if pkmn.hasForms():
        appearance["fields"].append(
            ("Forms", f"```{NEWLINE}{NEWLINE.join(pkmn.dispForms())}```", True)
        )

    pages.append(basic)
    pages.append(appearance)
    for fields in getMoveFields(pkmn):
        embed: _PkmnPage = {**base, "fields": []}
        for field in fields:
            embed["fields"].append(field)
        pages.append(embed)
    return pages

def getMoveFields(pkmn: Pokemon):
    fields: list[list[tuple[str, str, bool]]] = []
    addMoves(pkmn, Method.LEVEL, "Moves by level", fields)
    addMoves(pkmn, Method.TM, "Moves by TM", fields)
    addMoves(pkmn, Method.TR, "Moves by TR", fields)
    addMoves(pkmn, Method.EGG, "Moves by breeding", fields)
    addMoves(pkmn, Method.TUTOR, "Moves by tutor", fields)
    return fields

def addMoves(pkmn: Pokemon, method: str, title: str, fields: list[list[tuple[str, str, bool]]]):
    moves = pkmn.dispMovesForMethod(method)
    if not moves: return
    bodies = ["```\n" + "\n".join(chunk) + "```" for chunk in evenChunks(moves)]
    ret = [[EMPTY, bodyStr, True] for bodyStr in bodies]
    ret[0][0] = title
    fields.append(ret)

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

def GET_MOVE_PAGES(move: Move):
    move


def _resultHas(items: list[Union[LearnedMove, Move]]):
    return padItems(
        items,
        lambda move: move.dispName(),
        " ",
        lambda move: f"🟩 (via {move.dispMethods()})" if isinstance(move, LearnedMove) else f"🟥"
    )