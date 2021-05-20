
import json
import random
import re
from typing import Union

import requests
from bs4 import BeautifulSoup

pokedex = {}

heightPat = re.compile(r"^\d+\.\d+")

def fugma(dexNum):
    toPrint = []
    toPrint.append("num: " + dexNum)
    # now that we have the name, we head over to pokemondb which is actually formatted well
    r = requests.get("https://pokemondb.net/pokedex/" + dexNum)
    soup = BeautifulSoup(r.text, "html.parser")

    header = soup.find("h1") # first header is Pokemon name
    name = header.getText().lower()
    toPrint.append(name)
    pokedex[name] = {}
    pokedex[name]["id"] = dexNum

    imageName = "".join([char for char in name.lower() if char in "abcdefghijklmnopqrstuvwxyz -1234567890"])
    imageName = re.sub(r" ", "-", imageName)
    if name == "nidoran♀ (female)": imageName = "nidoran-f"
    if name == "nidoran♂ (male)": imageName = "nidoran-m"
    if name == "flabébé": imageName = "flabebe"
    if name == "urshifu": imageName = "urshifu-rapid-strike"
    pokedex[name]["image"] = f"https://img.pokemondb.net/sprites/home/normal/{imageName}.png"
    if "404 Not Found" in requests.get(pokedex[name]["image"]).text:
        raise Exception(f"Bad image for Pokemon {name} ({imageName})")

    types = []
    tableHeaders = soup.findAll("th")
    for th in tableHeaders:
        if th.getText() != "Type": continue
        tr = th.find_parent("tr")
        tds = tr.find_all("td")
        for td in tds:
            links = td.find_all("a")
            for link in links:
                types.append(link.getText().lower())
        break # break so that we don't continue to other tabs (mega evolutions)
    types = list(set(types))
    toPrint.append("types: " + str(types))
    pokedex[name]["types"] = types

    height = 0 # in meters
    for th in tableHeaders:
        if th.getText() != "Height": continue
        tr = th.find_parent("tr")
        td = tr.find("td") # only 1 td in the tr for height
        text = td.getText().lower()
        #height = float(text[text.index("(")+1 : text.index(")")-2]) # regex is fucking lame
        # regex isn't lame dumbass
        height = float(heightPat.search(text).group(0))
        break
    toPrint.append("height: " + str(height))
    pokedex[name]["height"] = height

    weight = 0 # in kilograms
    for th in tableHeaders:
        if th.getText() != "Weight": continue
        tr = th.find_parent("tr")
        td = tr.find("td") # only 1 td in the tr for weight
        text = td.getText().lower()
        weight = float(text[text.index("(")+1 : text.index(")")-3])
        break
    toPrint.append("weight: " + str(weight))
    pokedex[name]["weight"] = weight

    abilities = []
    hiddenAbility = "NONE"
    for th in tableHeaders:
        if th.getText() != "Abilities": continue
        tr = th.find_parent("tr")
        links = tr.find_all("a") # abilities are linked on the page
        for link in links[:-1]:
            abilities.append(link.getText().lower())
        if len(abilities) == 0:
            abilities.append(links[-1].getText().lower())
        else:
            hiddenAbility = links[-1].getText().lower()
        break
    toPrint.append("abilities: " + str(abilities) + " (hidden: " + hiddenAbility + ")")
    pokedex[name]["abilities"] = abilities
    pokedex[name]["hiddenAbility"] = hiddenAbility

    evoLine = {}
    arrowSpans = []
    try:
        evoDiv = soup.find("div", class_="infocard-list-evo")
        arrowSpans = evoDiv.findAll("span", class_="infocard infocard-arrow")
        originalEvo = evoDiv.find("span", class_="infocard-lg-data text-muted").find("a", class_="ent-name").getText().lower()
        evoLine[0] = originalEvo
    except AttributeError:
        evoLine[0] = name
    for span in arrowSpans:
        evoInfo = span.find("small")
        level = "".join(x for x in evoInfo.getText() if x in "1234567890")
        if level == "":
            evoCondA = evoInfo.find("a")
            if evoCondA:
                level = evoCondA.getText().lower()
            else:
                level = evoInfo.getText().lower()
        nextPokeNum = span.findNextSibling("div", class_="infocard").find("a", class_="ent-name").getText().lower()
        evoLine[level] = nextPokeNum
    toPrint.append("\nevo line")
    for key, value in evoLine.items():
        toPrint.append("  " + str(key) + ": " + str(value))
    pokedex[name]["evoLine"] = evoLine

    pokedex[name]["moves"] = {
        "8": {},
        "7": {}
    }
    def getMoves(moveSoup: BeautifulSoup, gen: str, headerText: str, checkText: str, dexText: str, *, hasNumber: bool=True):
        toPrint.append("\n" + headerText)
        moves: Union[dict[str, list], list[str]] = {} if hasNumber else []

        elem = moveSoup.find(string=headerText)
        if not elem:
            pokedex[name]["moves"][gen][dexText] = {}
            return
        elem = elem.find_next("p")
        if not checkText in elem.get_text():
            pokedex[name]["moves"][gen][dexText] = {}
            return
        elem = elem.find_next("table", class_="data-table")

        for number, tr in enumerate(elem.findAll("tr")):
            if (tr.find("th")): continue
            moveName = tr.find("a", class_="ent-name").getText().lower()
            if hasNumber:
                number = int(tr.find("td", class_="cell-num").getText().lower())
                if not moves.get(number):
                    moves[number] = []
                moves[number].append(moveName)
            else:
                moves.append(moveName)
        if hasNumber:
            for key, value in moves.items():
                toPrint.append("  " + str(key) + ": " + str(value))
        else:
            for move in moves:
                toPrint.append("  " + str(move))
        pokedex[name]["moves"][gen][dexText] = moves
    
    r = requests.get(f"https://pokemondb.net/pokedex/{dexNum}/moves/8")
    soup = BeautifulSoup(r.text, "html.parser")
    toPrint.append("for gen 8")
    getMoves(soup, "8", "Moves learnt by level up", "learns the following moves", "level")
    getMoves(soup, "8", "Moves learnt by TM", "is compatible with these", "tm")
    getMoves(soup, "8", "Moves learnt by TR", "is compatible with these", "tr")
    getMoves(soup, "8", "Egg moves", "learns the following moves", "egg", hasNumber=False)
    getMoves(soup, "8", "Move Tutor moves", "can be taught these", "tutor", hasNumber=False)
    getMoves(soup, "8", "Transfer-only moves", "can only learn these moves in previous generations", "transfer", hasNumber=False)
    r = requests.get(f"https://pokemondb.net/pokedex/{dexNum}/moves/7")
    soup = BeautifulSoup(r.text, "html.parser")
    toPrint.append("for gen 7")
    getMoves(soup, "7", "Moves learnt by level up", "learns the following moves", "level")
    getMoves(soup, "7", "Moves learnt by TM", "is compatible with these", "tm")
    getMoves(soup, "7", "Moves learnt by TR", "is compatible with these", "tr")
    getMoves(soup, "7", "Egg moves", "learns the following moves", "egg", hasNumber=False)
    getMoves(soup, "7", "Move Tutor moves", "can be taught these", "tutor", hasNumber=False)
    getMoves(soup, "7", "Transfer-only moves", "can only learn these moves in previous generations", "transfer", hasNumber=False)

    print("\n".join(toPrint))

    

def main():
    for i in range(1, 898 + 1):
        try:
            fugma(str(i))
        except Exception as e:
            raise e
    with open("pokedex.json", "w") as dexFile:
        dexFile.write(json.dumps(pokedex, indent=2))


def test():
    for _ in range(1, 4):
        fugma(str(random.randint(1, 898 + 1)))

main()
