
import json
import re
import time
from typing import Any, Callable, Optional, Union

import bs4
import requests
from bs4 import BeautifulSoup

NamedResource = dict[str, str]

spacePat = r"[^\w]"
apostrophePat = r"\'"

PAVarieties = list[dict[str, Union[NamedResource, bool]]]
PANames = list[dict[str, Union[NamedResource, str]]]
PAAbilities = list[dict[str, Union[NamedResource, bool]]]
PAForms = list[dict[str, Union[NamedResource, str]]]
PAMoves = list[dict[str, Union[NamedResource, list[dict[str, Union[NamedResource, int]]]]]]
PATypes = list[dict[str, Union[int, NamedResource]]]
PAStats = list[dict[str, Union[NamedResource, int]]]
_PAEvolutionDetail = dict[str, Union[NamedResource, int, bool, str]]
_PAChainLink = dict[str, Union[bool, NamedResource, _PAEvolutionDetail, dict]]
PAEvolutionChain =  dict[str, Union[int, NamedResource, _PAChainLink]]
PAEggGroups = list[NamedResource]
PASpecies = dict[str, Union[
    int,
    str,
    bool,
    NamedResource,
    PAEggGroups,
    PAEvolutionChain,
    PANames,
    PAVarieties
]]
PAForm = dict[str, Union[
    int,
    str,
    bool,
    NamedResource,
    PANames
]]
PAPokemon = dict[str, Union[
    int,
    str,
    bool,
    PAAbilities,
    PAForms,
    PAMoves,
    NamedResource,
    PAStats,
    PATypes
]]

RawAbilities = list[str]
RawVarieties = list[str]
RawMoves = dict[str, list[tuple[str, str, str]]]
RawStats = dict[str, tuple[int, int]]
RawTypes = list[str]
_RawDetails = list[tuple[str, dict[str, str]]]
RawEvolutions = list[tuple[str, _RawDetails]]
RawEggGroups = list[str]

RawPkmn = dict[str, Union[
    int,
    str,
    RawAbilities,
    RawVarieties,
    RawMoves,
    RawStats,
    RawTypes,
    RawEvolutions,
    bool,
    RawEggGroups
]]

####
# Pokemon
####

def getPokemon(aPkmn: PAPokemon):
    aSpcs: PASpecies = json.loads(requests.get(aPkmn["species"]["url"]).text)

    pkmn: RawPkmn = {}

    pkmn["id"], pkmn["name"], pkmn["battleOnly"] = getIDAndName(aPkmn["id"], aSpcs["varieties"], aPkmn["forms"], aSpcs["names"])
    pkmn["height"] = aPkmn["height"]
    pkmn["weight"] = aPkmn["weight"]
    pkmn["abilities"], pkmn["hiddenAbility"] = getAbilities(aPkmn["abilities"])
    pkmn["varieties"] = getVarieties(aSpcs["varieties"])
    pkmn["moves"] = getMoves(aPkmn["moves"])
    addMissedMoves(aPkmn["id"], pkmn["moves"])
    pkmn["stats"] = getStats(aPkmn["stats"])
    pkmn["types"] = getTypes(aPkmn["types"])
    pkmn["evolutions"] = getEvolutions(aSpcs["evolution_chain"])
    pkmn["baby"] = aSpcs["is_baby"]
    pkmn["legendary"] = aSpcs["is_legendary"]
    pkmn["mythical"] = aSpcs["is_mythical"]
    pkmn["groups"] = getEggGroups(aSpcs["egg_groups"])
    pkmn["color"] = getName(aSpcs["color"])
    pkmn["shape"] = getName(aSpcs["shape"])
    pkmn["gen"] = getName(aSpcs["generation"])

    return pkmn

def getName(raw: NamedResource):
    return raw["name"]

def getIDAndName(rawID: int, aVarieties: PAVarieties, aForms: PAForms, aNames: PANames):
    baseID = rawID
    for variety in aVarieties:
        if variety["is_default"]:
            defaultPokemon = json.loads(requests.get(variety["pokemon"]["url"]).text)
            if rawID != defaultPokemon["id"]:
                baseID = defaultPokemon["id"]
    for resource in aForms:
        form: PAForm = json.loads(requests.get(resource["url"]).text)
        if form["is_default"]:
            name = getNameFromLangs(form["names"])
            if not name:
                name = getNameFromLangs(aNames)
            battleOnly = form["is_battle_only"]
            break

    return baseID, name, battleOnly

def getAbilities(aAbilities: PAAbilities):
    abilities: RawAbilities = []
    hidden: Optional[str] = None
    for ability in aAbilities:
        if not ability["is_hidden"]:
            abilities.append(getName(ability["ability"]))
        else:
            hidden = getName(ability["ability"])
    return abilities, hidden

def getVarieties(aVarieties: PAVarieties):
    varieties: RawVarieties = []
    for form in aVarieties:
        varieties.append(getName(form["pokemon"]))
    return varieties

def getMoves(aMoves: PAMoves):
    moves: RawMoves = {}
    for rawMove in aMoves:
        methods = []
        for rawVersion in rawMove["version_group_details"]:
            version = getName(rawVersion["version_group"])
            if version in ["ultra-sun-ultra-moon"]:
                method = getName(rawVersion["move_learn_method"])
                level = rawVersion["level_learned_at"]
                methods.append((version, method, level))
        if not methods: continue # ignore unmatched versions of the game (we only want us/um)
        name = getName(rawMove["move"])
        if name == "vise-grip":
            print("fuck you, pokeapi", end=" ", flush=True)
            name = "vice-grip"
        moves[name] = methods
    return moves

def _addMovesFromPDB(moveSoup: BeautifulSoup, versionText: str, checkText: str, dexText: str, moves: RawMoves, *, includeNumber: bool=False):
    def findP(tag: bs4.Tag):
        if tag.name == "p" and checkText in tag.getText(): return True
    p: bs4.Tag = moveSoup.find(findP)
    if not p:
        return
    elem: bs4.Tag = p.find_next("table", class_="data-table")

    tr: bs4.Tag
    for number, tr in enumerate(elem.findAll("tr")):
        if (tr.find("th")): continue
        
        moveName: str = tr.find("a", class_="ent-name")["href"].split("/")[2].lower()
        if moveName == "vise-grip":
            print("fuck you pokemondb", end=" ", flush=True)
            moveName = "vice-grip"
        if not moveName in moves:
            moves[moveName] = []
        number = 0
        if includeNumber:
            number = int(tr.find("td", class_="cell-num").getText())
        moves[moveName].append((versionText, dexText, number))
    
def addMissedMoves(pkid: int, existingMoves: RawMoves):
    r = requests.get(f"https://pokemondb.net/pokedex/{pkid}/moves/8")
    soup = BeautifulSoup(r.text, "html.parser")
    moves: RawMoves = {}
    _addMovesFromPDB(soup, "sword-shield", "learns the following moves in Pokémon Sword & Shield", "level-up", moves, includeNumber=True)
    _addMovesFromPDB(soup, "sword-shield", "is compatible with these Technical Machines in Pokémon Sword & Shield", "machine", moves)
    _addMovesFromPDB(soup, "sword-shield", "is compatible with these Technical Records in Pokémon Sword & Shield", "record", moves)
    _addMovesFromPDB(soup, "sword-shield", "learns the following moves via breeding in Pokémon Sword & Shield", "egg", moves)
    _addMovesFromPDB(soup, "sword-shield", "can be taught these attacks in Pokémon Sword & Shield", "tutor", moves)
    r = requests.get(f"https://pokemondb.net/pokedex/{pkid}/moves/7")
    soup = BeautifulSoup(r.text, "html.parser")
    _addMovesFromPDB(soup, "ultra-sun-ultra-moon", "can be taught these attacks in Pokémon Ultra Sun & Ultra Moon", "tutor", moves)
    _addMovesFromPDB(soup, "ultra-sun-ultra-moon", "can only learn these moves in previous generations", "transfer", moves)
    _addMovesFromPDB(soup, "ultra-sun-ultra-moon", "learns the following moves via breeding in Pokémon Ultra Sun & Ultra Moon", "egg", moves)
    for moveName in moves:
        move = moves[moveName]
        existingMoveNames = [existingMove[0] for existingMove in existingMoves]
        if moveName in existingMoveNames:
            index = existingMoveNames.index(moveName)
            existingMoves[index] += move
        else:
            existingMoves[moveName] = move

def getTypes(aTypes: PATypes):
    types: RawTypes = []
    for rawType in sorted(aTypes, key=lambda rawType: rawType["slot"]):
        types.append(getName(rawType["type"]))
    return types

def getStats(aStats: PAStats):
    stats: RawStats = {}
    for rawStat in aStats:
        stats[getName(rawStat["stat"])] = (rawStat["base_stat"], rawStat["effort"])
    return stats

def getEvolutions(aLink: NamedResource):
    a: PAEvolutionChain = json.loads(requests.get(aLink["url"]).text)
    evolutions: RawEvolutions = []
    toCheck = [a["chain"]]
    while len(toCheck):
        current = toCheck.pop()
        evoName, details, toAdd = _getEvolutions(current)
        evolutions.append((evoName, details))
        toCheck += toAdd
    return evolutions

def _getEvolutions(current: _PAChainLink):
    details = current["evolution_details"]
    evoDetails: _RawDetails = []
    for detail in details:
        trigger: str = None
        existing = {}
        for detailName in detail:
            if detailName == "trigger":
                trigger = getName(detail[detailName])
            elif not detail[detailName] in [None, "", False]:
                if isinstance(detail[detailName], dict):
                    existing[detailName] = getName(detail[detailName])
                else:
                    existing[detailName] = detail[detailName]
        evoDetails.append((trigger, existing))
        
    return getName(current["species"]), evoDetails, current["evolves_to"]

def getEggGroups(aEggGroups: PAEggGroups):
    groups: RawEggGroups = []
    for group in aEggGroups:
        groups.append(getName(group))
    return groups

####
# Moves
####

PAEffects = list[dict[str, Union[str, NamedResource]]]
PAMove = dict[str, Union[
    int,
    str,
    bool,
    PANames,
    PAEffects
]]

RawMove = dict[str, Union[
    str,
    int
]]

def getMove(aMove: PAMove):    
    move: RawMove = {}

    move["name"] = getNameFromLangs(aMove["names"])
    move["clas"] = getName(aMove["damage_class"]) if aMove["damage_class"] else None
    move["typ"] = getName(aMove["type"])
    move["pow"] = aMove["power"]
    move["acc"] = aMove["accuracy"]
    move["pp"] = aMove["pp"]
    move["effect"] = getEffect(aMove["effect_entries"])
    move["effectChance"] = aMove["effect_chance"]
    move["target"] = getName(aMove["target"])
    move["gen"] = getName(aMove["generation"])
    
    return move

def getNameFromLangs(a: PANames):
    for name in a:
        if getName(name["language"]) == "en":
            return name["name"]

def getEffect(a: PAEffects):
    for lang in a:
        if getName(lang["language"]) == "en":
            return lang["effect"]

def _getNumForTD(d: bs4.Tag) -> tuple[Union[int, None], bs4.Tag]:
    nextD: bs4.Tag = d.find_next()
    text: str = nextD.get_text()
    num = int(text) if text and not text in "—∞" else None
    return num, nextD

suburlPat = re.compile(r"move\/(.+)$")
def addGen8MovesToDex(movedex: dict[str, str]):
    r = requests.get(f"https://pokemondb.net/move/generation/8")
    soup = BeautifulSoup(r.text, "html.parser")
    
    table: bs4.Tag = soup.find("table", id="moves", class_="data-table")
    tr: bs4.Tag
    for tr in table.find_all("tr"):
        if tr.find("th"): continue

        nameD: bs4.Tag = tr.find("td", class_="cell-name")
        nameA: bs4.Tag = nameD.find("a")
        name = nameA["href"].split("/")[2].lower()
        dispName: str = nameA.get_text()

        typeD: bs4.Tag = nameD.find_next("td")
        typeA: bs4.Tag = typeD.find("a")
        typ = typeA["href"].split("/")[2].lower()

        classD: bs4.Tag = typeD.find_next("td")
        clas: str = classD["data-sort-value"]

        power, powerD = _getNumForTD(classD)
        acc, accD = _getNumForTD(powerD)
        pp, ppD = _getNumForTD(accD)

        effectD: bs4.Tag = ppD.find_next("td")
        effect = effectD.get_text()

        movedex[name] = {
            "name": dispName,
            "typ": typ,
            "clas": clas,
            "pow": power,
            "acc": acc,
            "pp": pp,
            "effect": effect,
            "effectChance": None,
            "target": None,
            "gen": 8
        }
        

####
# Abilities
####

PAAbility = dict[str, Union[
    str,
    PAEffects
]]

RawAbility = dict[str, Union[
    str
]]

def getAbility(aAbility: PAAbility):
    ability: RawAbility = {}

    ability["name"] = getIDAndName(aAbility["names"])
    ability["effect"] = getEffect(aAbility["effect_entries"])
    ability["gen"] = getName(aAbility["generation"])

    return ability

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
        dex[getName(resource)] = get(resource["url"], func)
    return dex

def get(url: str, func: Callable[[dict], dict]):
    print(url, end="... ", flush=True)
    tic = time.perf_counter()
    data = requests.get(url).text
    obj = json.loads(data)
    item = func(obj)
    toc = time.perf_counter()
    print(f"Got {getName(item)} in {round(toc - tic, 2)}s")
    return item

def editFile(fileName: str):
    try:
        return open(fileName, "x")
    except FileExistsError:
        return open(fileName, "w")

def createNewDex(fileName: str, apiName: str, func: Callable[[dict], dict]):
    tic = time.perf_counter()
    arbitrarilyLargeNumber = 1000000
    dex = getDex(f"https://pokeapi.co/api/v2/{apiName}?limit={arbitrarilyLargeNumber}", func)
    with editFile(fileName) as f:
        json.dump(dex, f)
    toc = time.perf_counter()
    print(f"Built dex for {apiName} in {round((toc - tic)/60, 2)}m")

def completeMovedex(movedexSource: str, writeSource: Optional[str]):
    """ This doesn't need to be here, pokemondb is stupid and decided to spell "Vice Grip" as "Vise Grip". """
    if not writeSource: writeSource = movedexSource
    with open(movedexSource, "r") as f:
        movedex = json.load(f)
    addGen8MovesToDex(movedex)
    with editFile(writeSource) as f:
        json.dump(movedex, f)

def createNew(apiName: str, itemName: str, func: Callable[[dict], dict]):
    item = get(f"https://pokeapi.co/api/v2/{apiName}/{itemName}", func)
    return item

def main():
    createNewDex("./pokedex.json", "pokemon", getPokemon)
    #createNewDex("./movedex.json", "move", getMove)
    #completeMovedex("./sources/dexes/movedex.json", "./movedex.json")
    #createNewDex("./abilitydex.json", "ability", getAbility)

if __name__ == "__main__":
    main()
    #pretty(createNew("pokemon", "gardevoir", getPokemon))
