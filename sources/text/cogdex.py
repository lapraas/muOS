 
from typing import Union
from Dexes import Method, Move, Pokemon
from sources.general import Cmd, EMPTY, NEWLINE, chunks, evenChunks, stripLines, RawDictPaginatorPage

class COG:
    NAME = "Dex Cog"
    DESC = "A cog that provides lookup for various Pokemon resources. It includes a Pokedex, a Movedex, and an Abilitydex."

QUERY = Cmd(
    "query",
    f"""
        This is an all-purpose command that will give the user a list of Pokemon resources that match the entry.
    """,
    usage=[
        "porygon-z",
        "tri attack",
        "analytical",
        "pokemon with moves trick room and tri attack",
        "moves with type dragon",
        "legendary pokemon",
        "baby pokemon with ability natural cure"
    ]
)

_forQuery = lambda query: f"For query `{query}`:\n"
_forExtra = lambda extra: f"For the specification `{extra}`, "
class ERR:
    NO_MODE = lambda query: f"{_forQuery(query)}A type of resource to search for (pokemon, move, ability) must be provided for non-specific queries. If you're looking for a specific Pokemon/move/ability, you might have misspelled it."
    MIXING_OPS = lambda query: f"{_forQuery(query)}The combination of `and` and `or` in a single query is not implemented."
    NO_EXTRA_MODE = lambda query, extra: f"{_forQuery(query)}{_forExtra(extra)}an attribute of the target resource must be given. An attribute is something like `move`, `type`, `ability`, etc."

class INFO:
    NO_MATCH = lambda query: f"{_forQuery(query)}No results were found for this query."

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