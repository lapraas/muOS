
import json
from typing import Any, Callable, Optional, Union
from bs4 import BeautifulSoup
import requests
import time

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

def _getFormName(realID: int, baseID: int):
    r = requests.get(f"https://pokemondb.net/pokedex/{baseID}")
    soup = BeautifulSoup(r.text, "html.parser")
    p = soup.find("a", href=f"#tab-basic-{realID + 42}")
    if not p:
        raise Exception(f"No tab found with ID {realID} (+ 42 {realID + 42})")
    return p.getText()

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
        moves[getName(rawMove["move"])] = methods
    return moves

def _addMovesFromPDB(moveSoup: BeautifulSoup, versionText: str, checkText: str, dexText: str, moves: RawMoves, *, includeNumber: bool=False):
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
    for moveName in moves:
        move = moves[moveName]
        existingMoveNames = [existingMove[0] for existingMove in existingMoves]
        if moveName in existingMoveNames:
            index = existingMoveNames.index(moveName)
            for method in move:
                existingMoves[index].append(method)
        else:
            existingMoves.append([moveName, *move])

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
    move["typ"] = getName(aMove["type"])
    move["pow"] = aMove["power"]
    move["acc"] = aMove["accuracy"]
    move["clas"] = getName(aMove["damage_class"]) if aMove["damage_class"] else None
    move["effect"] = getEffect(aMove["effect_entries"])
    move["effectChance"] = aMove["effect_chance"]
    move["target"] = getName(aMove["target"])
    move["pp"] = aMove["pp"]
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

def createNewDex(fileName: str, apiName: str, func: Callable[[dict], dict]):
    arbitrarilyLargeNumber = 1000000
    dex = getDex(f"https://pokeapi.co/api/v2/{apiName}?limit={arbitrarilyLargeNumber}", func)
    try:
        f = open(fileName, "x")
    except FileExistsError:
        f = open(fileName, "w")
    json.dump(dex, f)
    f.close()

def createNew(apiName: str, itemName: str, func: Callable[[dict], dict]):
    item = get(f"https://pokeapi.co/api/v2/{apiName}/{itemName}", func)
    return item

def main():
    createNewDex("./pokedex.json", "pokemon", getPokemon)
    #createNewDex("./movedex.json", "move", getMove)
    #createNewDex("./abilitydex.json", "ability", getAbility)

if __name__ == "__main__":
    main()
    #pretty(createNew("pokemon", "sandslash-alola", getPokemon))