import bs4
from bs4 import BeautifulSoup
import json
import random
import re
import requests
import time

pokedex = {}

heightPat = re.compile(r"^\d+\.\d+")

def fugma(dexNum):
    print("\n"*3)
    print("num: " + dexNum)
    # now that we have the name, we head over to pokemondb which is actually formatted well
    r = requests.get("https://pokemondb.net/pokedex/" + dexNum)
    soup = BeautifulSoup(r.text, "html.parser")

    header = soup.find("h1") # first header is Pokemon name
    name = header.getText().lower()
    pokedex[name] = {}
    pokedex[name]["id"] = dexNum

    pokedex[name]["image"] = soup.find("img")["src"]

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
    print("types: " + str(types))
    pokedex[name]["types"] = types

    height = 0 # in meters
    for th in tableHeaders:
        if th.getText() != "Height": continue
        tr = th.find_parent("tr")
        td = tr.find("td") # only 1 td in the tr for height
        text = td.getText()
        #height = float(text[text.index("(")+1 : text.index(")")-2]) # regex is fucking lame
        # regex isn't lame dumbass
        height = float(heightPat.search(text).group(0))
        break
    print("height: " + str(height))
    pokedex[name]["height"] = height

    weight = 0 # in kilograms
    for th in tableHeaders:
        if th.getText() != "Weight": continue
        tr = th.find_parent("tr")
        td = tr.find("td") # only 1 td in the tr for weight
        text = td.getText()
        weight = float(text[text.index("(")+1 : text.index(")")-3])
        break
    print("weight: " + str(weight))
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
    print("abilities: " + str(abilities) + " (hidden: " + hiddenAbility + ")")
    pokedex[name]["abilities"] = abilities
    pokedex[name]["hiddenAbility"] = hiddenAbility

    expRate = ""
    for th in tableHeaders:
        if th.getText() != "Growth Rate": continue
        tr = th.find_parent("tr")
        td = tr.find("td")
        text = td.getText().split(" ")
        if len(text) == 2:
            expRate = text[0][0].lower() + text[1][0].lower()
        else:
            expRate = text[0][0].lower()
        break
    print("exp rate: " + expRate)
    pokedex[name]["expRate"] = expRate

    evoLine = {}
    arrowSpans = []
    try:
        evoDiv = soup.find("div", class_="infocard-list-evo")
        arrowSpans = evoDiv.findAll("span", class_="infocard infocard-arrow")
        originalEvo = evoDiv.find("span", class_="infocard-lg-data text-muted").find("a", class_="ent-name").getText()
        evoLine[0] = originalEvo
    except AttributeError:
        evoLine[0] = name
    for span in arrowSpans:
        evoInfo = span.find("small")
        level = "".join(x for x in evoInfo.getText() if x in "1234567890")
        if level == "":
            evoCondA = evoInfo.find("a")
            if evoCondA:
                level = evoCondA.getText()
            else:
                level = evoInfo.getText()
        nextPokeNum = span.findNextSibling("div", class_="infocard").find("a", class_="ent-name").getText()
        evoLine[level] = nextPokeNum
    print("\nevo line")
    for key, value in evoLine.items():
        print("  " + str(key) + ": " + str(value))
    pokedex[name]["evoLine"] = evoLine

    print("\nbase stats")
    baseHP = 0
    for th in tableHeaders:
        if th.getText() != "HP": continue
        tr = th.find_parent("tr")
        td = tr.find("td", class_="cell-num")
        baseHP = int(td.getText())
    print("  HP:     " + str(baseHP))
    pokedex[name]["baseHP"] = baseHP

    baseAtk = 0
    for th in tableHeaders:
        if th.getText() != "Attack": continue
        tr = th.find_parent("tr")
        td = tr.find("td", class_="cell-num")
        baseAtk = int(td.getText())
    print("  atk:    " + str(baseAtk))
    pokedex[name]["baseAtk"] = baseAtk

    baseDef = 0
    for th in tableHeaders:
        if th.getText() != "Defense": continue
        tr = th.find_parent("tr")
        td = tr.find("td", class_="cell-num")
        baseDef = int(td.getText())
    print("  def:    " + str(baseDef))
    pokedex[name]["baseDef"] = baseDef

    baseSpAtk = 0
    for th in tableHeaders:
        if th.getText() != "Sp. Atk": continue
        tr = th.find_parent("tr")
        td = tr.find("td", class_="cell-num")
        baseSpAtk = int(td.getText())
    print("  sp atk: " + str(baseSpAtk))
    pokedex[name]["baseSpAtk"] = baseSpAtk

    baseSpDef = 0
    for th in tableHeaders:
        if th.getText() != "Sp. Def": continue
        tr = th.find_parent("tr")
        td = tr.find("td", class_="cell-num")
        baseSpDef = int(td.getText())
    print("  sp def: " + str(baseSpDef))
    pokedex[name]["baseSpDef"] = baseSpDef

    baseSpeed = 0
    for th in tableHeaders:
        if th.getText() != "Speed": continue
        tr = th.find_parent("tr")
        td = tr.find("td", class_="cell-num")
        baseSpeed = int(td.getText())
    print("  speed:  " + str(baseSpeed))
    pokedex[name]["baseSpeed"] = baseSpeed

    print("\nmoveset")
    moveset = {}
    levelupMovesetTable = soup.find("table", class_="data-table")
    for tr in levelupMovesetTable.findAll("tr"):
        if (tr.find("th")): continue
        moveLevel = int(tr.find("td", class_="cell-num").getText())
        moveName = tr.find("td", class_="cell-name").find("a").getText().lower()
        moveset[moveLevel] = moveName
    for key, value in moveset.items():
        print("  " + str(key) + ": " + value)
    pokedex[name]["moveset"] = moveset

def main():
    print("\n"*3)
    for i in range(1, 898 + 1):
        try:
            fugma(str(i))
            time.sleep(0.25)
        except Exception as e:
            raise e
    with open("pokedex.json", "w") as dexFile:
        dexFile.write(json.dumps(pokedex, indent=2))


def test():
    print("\n"*3)
    for _ in range(1, 4):
        fugma(str(random.randint(1, 650)))

main()
