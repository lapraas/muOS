
import json
from typing import Callable, Union
from bs4 import BeautifulSoup
import re
import requests

NamedResource = dict[str, str]

spacePat = r"[^\w]"
apostrophePat = r"\'"

####
# Pokemon
####

def getPokemon(rawPkmn: dict):
    rawSpcs = json.loads(requests.get(rawPkmn["species"]["url"]).text)

    pkmn = {}

    pkmn["id"] = rawPkmn["id"]
    pkmn["name"] = getDispName(rawSpcs["names"])
    pkmn["height"] = rawPkmn["height"]
    pkmn["weight"] = rawPkmn["weight"]
    pkmn["abilities"], pkmn["hiddenAbility"] = getAbilities(rawPkmn["abilities"])
    pkmn["forms"] = getForms(rawSpcs["varieties"])
    pkmn["moves"] = getMoves(rawPkmn["moves"])
    addMissedMoves(rawPkmn["id"], pkmn["moves"])
    pkmn["stats"] = getStats(rawPkmn["stats"])
    pkmn["types"] = getTypes(rawPkmn["types"])
    pkmn["evolutions"] = getEvolutions(rawSpcs["evolution_chain"])
    pkmn["baby"] = rawSpcs["is_baby"]
    pkmn["legendary"] = rawSpcs["is_legendary"]
    pkmn["mythical"] = rawSpcs["is_mythical"]
    pkmn["groups"] = getEggGroups(rawSpcs["egg_groups"])
    pkmn["color"] = getName(rawSpcs["color"])
    pkmn["shape"] = getName(rawSpcs["shape"])
    pkmn["gen"] = getName(rawSpcs["generation"])

    return pkmn

def getName(raw: NamedResource):
    return raw["name"]

def getDispName(raw: list[dict[str, Union[NamedResource, str]]]):
    for lang in raw:
        if getName(lang["language"]) == "en":
            return lang["name"]

def getAbilities(raw: list[dict[str, Union[NamedResource, bool]]]):
    abilities = []
    hidden = None
    for ability in raw:
        if not ability["is_hidden"]:
            abilities.append(getName(ability["ability"]))
        else:
            hidden = getName(ability["ability"])
    return abilities, hidden

def getForms(raw: list[dict[str, Union[NamedResource, bool]]]):
    forms = []
    for form in raw:
        forms.append(getName(form["pokemon"]))
    return forms

def getMoves(raw: list[dict[str, Union[NamedResource, list[dict[str, Union[NamedResource, int]]]]]]):
    moves: list[Union[str, tuple[str, str, str]]] = []
    for rawMove in raw:
        move = [getName(rawMove["move"])]
        for rawVersion in rawMove["version_group_details"]:
            version = getName(rawVersion["version_group"])
            if version in ["ultra-sun-ultra-moon"]:
                method = getName(rawVersion["move_learn_method"])
                level = rawVersion["level_learned_at"]
                move.append((version, method, level))
        if len(move) == 1:
            continue
        moves.append(move)
    return moves

def _addMovesFromPDB(moveSoup: BeautifulSoup, versionText: str, checkText: str, dexText: str, moves: dict[str, list[tuple[str, str, str]]], *, includeNumber: bool=False):
    p = moveSoup.find(string=checkText)
    if not p:
        return
    elem = p.find_next("table", class_="data-table")

    for number, tr in enumerate(elem.findAll("tr")):
        if (tr.find("th")): continue
        moveName = tr.find("a", class_="ent-name").getText().lower()
        if not moveName in moves:
            moves[moveName] = []
        number = 0
        if includeNumber:
            number = int(tr.find("td", class_="cell-num").getText().lower())
        moves[moveName].append((versionText, dexText, number))
    
def addMissedMoves(pkid: int, existingMoves: list[list[Union[str, tuple[str, str, str]]]]):
    r = requests.get(f"https://pokemondb.net/pokedex/{pkid}/moves/8")
    soup = BeautifulSoup(r.text, "html.parser")
    moves: dict[str, list[tuple[str, str, str]]] = {}
    _addMovesFromPDB(soup, "sword-shield", "learns the following moves in Pokémon Sword & Shield", "level-up", moves, includeNumber=True)
    _addMovesFromPDB(soup, "sword-shield", "is compatible with these Technical Machines in Pokémon Sword & Shield", "machine", moves)
    _addMovesFromPDB(soup, "sword-shield", "is compatible with these Technical Records in Pokémon Sword & Shield", "record", moves)
    _addMovesFromPDB(soup, "sword-shield", "learns the following moves via breeding in Pokémon Sword & Shield", "egg", moves)
    _addMovesFromPDB(soup, "sword-shield", "can be taught these attacks in Pokémon Sword & Shield", "tutor", moves)
    r = requests.get(f"https://pokemondb.net/pokedex/{pkid}/moves/7")
    soup = BeautifulSoup(r.text, "html.parser")
    _addMovesFromPDB(soup, "ultra-sun-ultra-moon", "can be taught these attacks in Pokémon Ultra Sun & Ultra Moon", "tutor", moves)
    for moveName in moves:
        move = moves[moveName]
        existingMoveNames = [existingMove[0] for existingMove in existingMoves]
        if moveName in existingMoveNames:
            index = existingMoveNames.index(moveName)
            for method in move:
                existingMoves[index].append(method)
        else:
            existingMoves.append([moveName, *move])

def getTypes(raw: list[dict[str, Union[int, NamedResource]]]):
    types: list[str] = []
    for rawType in sorted(raw, key=lambda rawType: rawType["slot"]):
        types.append(getName(rawType["type"]))
    return types

def getStats(raw: list[dict[str, Union[NamedResource, int]]]):
    stats: dict[str, tuple[int, int]] = {}
    for rawStat in raw:
        stats[getName(rawStat["stat"])] = (rawStat["base_stat"], rawStat["effort"])
    return stats

EvolutionDetail = dict[str, Union[NamedResource, int, bool, str]]
ChainLink =       dict[str, Union[bool, NamedResource, EvolutionDetail, dict]]
EvolutionChain =  dict[str, Union[int, NamedResource, ChainLink]]
def getEvolutions(rawLink: dict[str, str]):
    raw = json.loads(requests.get(rawLink["url"]).text)
    evolutions: dict[str, str] = {}
    toCheck = [raw["chain"]]
    while len(toCheck):
        current = toCheck.pop()
        evoName, evolution, toAdd = _getEvolutions(current)
        evolutions[evoName] = evolution
        toCheck += toAdd
    return evolutions

def _getEvolutions(current: ChainLink):
    details = current["evolution_details"]
    evoDetails: list[dict[str, str]] = []
    for detail in details:
        existing = {}
        for detailName in detail:
            if not detail[detailName] in [None, "", False]:
                if isinstance(detail[detailName], dict):
                    existing[detailName] = getName(detail[detailName])
                else:
                    existing[detailName] = detail[detailName]
        evoDetails.append(existing)
        
    return getName(current["species"]), evoDetails, current["evolves_to"]

def getEggGroups(raw: list[NamedResource]):
    groups = []
    for group in raw:
        groups.append(getName(group))
    return groups

####
# Moves
####

def getMove(rawMove: dict):    
    move = {}

    move["name"] = getDispName(rawMove["names"])
    move["type"] = getName(rawMove["type"])
    move["power"] = rawMove["power"]
    move["accuracy"] = rawMove["accuracy"]
    move["class"] = getName(rawMove["damage_class"])
    move["effectChance"] = rawMove["effect_chance"]
    move["target"] = getName(rawMove["target"])
    move["pp"] = rawMove["pp"]
    move["gen"] = getName(rawMove["generation"])
    
    return move

def getEffect(raw: list[dict[str, Union[str, NamedResource]]]):
    for lang in raw:
        if getName(lang["language"]) == "en":
            return lang["effect"]

####
# Abilities
####

def getAbility(rawAbility: dict):
    ability = {}

    ability["name"] = getDispName(rawAbility["names"])
    ability["effect"] = getEffect(rawAbility["effect_entries"])
    ability["gen"] = getName(rawAbility["generation"])

####
# Main
####

def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        elif isinstance(value, list):
            for lValue in value:
                print("\t" * (indent + 1) + str(lValue))
        else:
            print('\t' * (indent+1) + str(value))

def getDex(url: str, func: Callable[[int], dict[str, dict]]):
    resources = json.loads(requests.get(url).text)["results"]
    dex = {}
    for resource in resources:
        data = requests.get(resource["url"]).text
        try:
            item = func(json.loads(data))
        except json.decoder.JSONDecodeError as e:
            print(data)
            raise e
        dex[getName(resource)] = item
        print(getName(resource))
    return dex

def main():
    pokedex = getDex("https://pokeapi.co/api/v2/pokemon?limit=10000", getPokemon)
    with open("./pokedex.json", "x") as f:
        json.dump(pokedex, f)
    movedex = getDex("https://pokeapi.co/api/v2/move?limit=10000", getMove)
    with open("./movedex.json", "x") as f:
        json.dump(movedex, f)
    abilitydex = getDex("https://pokeapi.co/api/v2/ability?limit=10000", getAbility)
    with open("./abilitydex.json", "x") as f:
        json.dump(abilitydex, f)

main()