
import json
from pokeapi import RawEvolutions, RawMoves, RawStats, getIDAndName
import re
from typing import Callable, Generic, Optional, Type, TypeVar

class DexItem:
    def __init__(self, name: str, fancy: str):
        self.name = name
        self.fancy = fancy
    
    def getName(self):
        return self.name
    
    def dispName(self):
        return self.fancy

_effectReplacer = re.compile(r"\$effect_chance")
class Move(DexItem):
    def __init__(self, rawName: str, name: str, typ: str, pow: int, acc: int, clas: str, effect: str, effectChance: int, target: str, pp: int, gen: str):
        super().__init__(rawName, name)
        self.typ = typ
        self.pow = pow
        self.acc = acc
        self.cls = clas
        self.effect = effect
        self.effectChance = effectChance
        self.target = target
        self.pp = pp
        self.gen = gen
    
    def getType(self): return self.typ
    def getPower(self): return self.pow
    def getAccuracy(self): return self.acc
    def getDamageClass(self): return self.cls
    def getEffect(self): return self.effect
    def getEffectChance(self): return self.effectChance
    def getTarget(self): return self.target
    def getPP(self): return self.pp
    def getGen(self): return self.gen
    
    def dispType(self): return self.typ.title()
    def dispDamageClass(self): return self.cls.title()
    def dispEffect(self): return _effectReplacer.sub(str(self.effectChance), self.effect)
    def dispTarget(self): return self.target.title()
    def getGen(self): return self.gen.title()

class Method:
    LEVEL = "level-up"
    TM = "machine"
    TR = "record"
    EGG = "egg"
    TUTOR = "tutor"

    def __init__(self, typ: str, gen: str, lvl: Optional[int]):
        self.typ = typ
        self.gen = gen
        self.lvl = lvl
    
    def getLvl(self):
        return self.lvl

class Ability(DexItem):
    def __init__(self, rawName: str, name: str, effect: str, gen: str):
        super().__init__(rawName, name)
        self.effect = effect
        self.gen = gen
    
    def getEffect(self):
        return self.effect
    def getGen(self):
        return self.gen

class LearnedMove:
    def __init__(self, name: str, methods: list[tuple[str, str, int]]):
        self.name = name
        self.methods = LearnedMove.populateMethods(methods)
    
    @staticmethod
    def populateMethods(raw: list[tuple[str, str, int]]):
        methods: dict[str, Method] = {}
        for gen, typ, lvl in raw:
            methods[typ] = Method(typ, gen, lvl if typ==Method.LEVEL else None)
        return methods
    
    def getName(self):
        return self.name
    def getMethod(self, method: str):
        return self.methods.get(method)
    
    def getFromDex(self):
        return MOVEDEX.get(self.name)


class Enum:
    @classmethod
    def match(cls, name: str):
        for key in cls.__dict__:
            item = cls.__dict__[key]
            if not isinstance(item, str): continue
            if item == name:
                return name
        raise KeyError(f"Couldn't find match for {name} in {cls}")

class STATS(Enum):
    HP = "hp"
    ATK = "attack"
    DEF = "defense"
    SPATK = "special-attack"
    SPDEF = "special-defense"
    SPD = "speed"

class TRIGGERS(Enum):
    LEVEL = "level-up"
    TRADE = "trade"
    ITEM = "use-item"
    SHEDINJA = "shed"
    OTHER = "other"

class Stat:
    def __init__(self, typ: str, val: int, ev: int):
        self.typ = typ,
        self.val = val,
        self.ev = ev
    
    def getTyp(self): return self.typ
    def getVal(self): return self.val
    def getEV(self): return self.ev

class Evolution:
    def __init__(self, into: str, method: str, details: dict[str, str]):
        self.into = into
        self.method = method
        self.details = details
    
    def getInto(self): return self.into
    def getMethod(self): return self.method
    def getDetails(self): return self.details

    def dispInto(self):
        return POKEDEX.get(self.into).dispName()
    def dispMethod(self):
        if not self.method:
            return "Base"
        method: list[str] = []
        if self.method == "level-up":
            method.append(f"Lv.{self.details['min_level'] if self.details.get('min_level') else ''}")
        elif self.method == "use-item":
            method.append(f"W/{self.details['item']}")
        elif self.method == "trade":
            if self.details.get("held_item"):
                method.append(f"Trade holding {self.details['held_item']}")
            else:
                method.append("Trade")
        elif self.method == "shed":
            method.append("Lv.20, empty spot, pokeball")
        elif self.method == "other":
            if self.into == "sirfetchd":
                method.append("3 crits in battle")
            else:
                method.append("idfk")
        else:
            raise KeyError("bad method")
        
        for detailName in self.details:
            if detailName in ["min_level", "item", "held_item"]: continue
            detail = self.details[detailName]
            if detailName == "gender":
                method.append("Male" if not detail else "Female")
            elif detailName == "known_move":
                method.append(f"Knows {detail}")
            elif detailName == "known_move_type":
                method.append(f"Knows type {detail}")
            elif detailName == "location":
                method.append(f"At {detail}")
            elif detailName == "min_happiness":
                method.append(f"Happiness {detail}")
            elif detailName == "min_beauty":
                method.append(f"Beauty {detail}")
            elif detailName == "min_affection":
                method.append(f"Affection {detail}")
            elif detailName == "needs_overworld_rain":
                method.append("While raining")
            elif detailName == "party_species":
                method.append(f"With {POKEDEX.get(detail).dispName()} in party")
            elif detailName == "party_type":
                method.append(f"With type {detail} in party")
            elif detailName == "relative_physical_stats":
                if detail == -1: method.append(f"Atk < def")
                elif detail == 0: method.append(f"Atk = def")
                elif detail == -1: method.append(f"Atk > def")
                else: raise KeyError("bad relative_pysical_stats (not 1, 0, -1)")
            elif detailName == "time_of_day":
                method.append(f"During {detail}")
            elif detailName == "trade_species":
                method.append(f"Trade for {POKEDEX.get(detail).dispName()}")
            elif detailName == "turn_upside_down":
                method.append("Turn your fucking device upside down")
        method = ", ".join(method)
        return method

class Pokemon(DexItem):
    def __init__(self,
        rawName: str, id: int, name: str,
        height: int, weight: int,
        abilities: list[str], hiddenAbility: Optional[str],
        moves: RawMoves,
        stats: RawStats,
        types: list[str], groups: list[str], varieties: list[str],
        evolutions: RawEvolutions,
        baby: bool, legendary: bool, mythical: bool, battleOnly: bool,
        color: str, shape: str, gen: str
    ):
        super().__init__(rawName, name)
        self.id = id
        self.battleOnly = battleOnly
        self.height = height
        self.weight = weight
        self.abilities = abilities
        self.hiddenAbility = hiddenAbility
        self.moves = Pokemon.populateMoves(moves)
        self.stats = Pokemon.populateStats(stats)
        self.types = types
        self.varieties = varieties
        self.evolutions = Pokemon.populateEvolutions(evolutions)
        self.eggGroups = groups
        self.isBaby = baby
        self.isLegendary = legendary
        self.isMythical = mythical
        self.color = color
        self.shape = shape
        self.gen = gen
    @staticmethod
    def populateMoves(raw: RawMoves):
        moves: dict[str, LearnedMove] = {}
        for name in raw:
            methods = raw[name]
            moves[name] = LearnedMove(name, methods)
        return moves
    @staticmethod
    def populateStats(raw: RawStats):
        stats: dict[str, Stat] = {}
        for statName in raw:
            stats[statName] = Stat(STATS.match(statName), *raw[statName])
        return stats
    @staticmethod
    def populateEvolutions(raw: RawEvolutions):
        evolutions: list[Evolution] = []
        for evo in raw:
            for trigger, details in evo[1]:
                evolutions.append(Evolution(evo[0], TRIGGERS.match(trigger), details))
        return evolutions
    
    def getID(self): return self.id
    def getHeight(self): return round(self.height * 0.1, 1)
    def getWeight(self): return round(self.weight * 0.1, 1)
    def getAbilities(self): return self.abilities
    def getHiddenAbility(self): return self.hiddenAbility
    def getMoves(self): return list(self.moves.keys())
    def getMove(self, move: str): return self.moves.get(move)
    def getBase(self, base: str): return self.stats.get(base)
    def getTypes(self): return self.types
    def getForms(self): return self.varieties
    def getEvolutions(self): return self.evolutions
    def getEggGroups(self): return self.eggGroups
    def getIsBaby(self): return self.isBaby
    def getIsLegendary(self): return self.isLegendary
    def getIsMythical(self): return self.isMythical
    def getBattleOnly(self): return self.battleOnly
    def getColor(self): return self.color
    def getShape(self): return self.shape
    def getGen(self): return self.gen

    def getImageURL(self): return f"https://img.pokemondb.net/sprites/home/normal/{self.name}.png"
    def dispHeight(self): return str(self.getHeight()) + "m"
    def dispWeight(self): return str(self.getWeight()) + "kg"
    def dispColor(self): return self.color.title()
    def dispShape(self): return self.shape.title()
    def dispGen(self): return self.gen.title()
    def dispTypes(self): return [typ.title() for typ in self.types]
    def dispAllAbilities(self):
        return [ability.title() for ability in self.abilities] + ([self.dispHiddenAbility() + " (hidden)"] if self.hasHiddenAbility() else [])
    def dispHiddenAbility(self): return self.hiddenAbility.title()
    def dispEggGroups(self): return [group.title() for group in self.eggGroups]
    def dispForms(self): return [POKEDEX.get(form).getName().title() for form in self.varieties]
    def dispEvolutions(self):
        if not self.evolutions: return ["Does not evolve"]
        evoStrs = []
        maxMethodLen = max(len(evo.dispMethod()) for evo in self.evolutions)
        for evo in self.evolutions:
            threshSpacing = " " * (maxMethodLen - len(evo.dispMethod()))
            evoStrs.append(f"{evo.dispMethod()}:{threshSpacing} {evo.dispInto()}")
        return evoStrs
    
    def dispMovesForMethod(self, targetMethod: str):
        if not targetMethod == Method.LEVEL:
            return sorted([move.getFromDex().dispName() for move in [move for move in self.moves.values() if move.getMethod(targetMethod)]])
        else:
            moves: list[LearnedMove] = []
            for moveName in self.moves:
                move = self.moves[moveName]
                method = move.getMethod(targetMethod)
                if not method: continue
                moves.append(move)
            moves.sort(key=lambda move: move.getMethod(targetMethod).getLvl())
            moveStrs: list[str] = []
            lastLvl = None
            for move in moves:
                method = move.getMethod(targetMethod)
                if lastLvl != method.getLvl():
                    lastLvl = method.getLvl()
                    moveStrs.append(f"{lastLvl}:\n{move.getFromDex().dispName()}")
                else:
                    moveStrs.append(f"{move.getFromDex().dispName()}")
            return moveStrs
    def dispClassifications(self):
        return (
            'Baby\n' if self.getIsBaby() else '' +
            'Legendary\n' if self.getIsLegendary() else '' +
            'Mythical\n' if self.getIsMythical() else ''
        )

    def hasHiddenAbility(self): return self.hiddenAbility != None
    def hasForms(self): return len(self.varieties) != 1
    def hasClassifications(self): return self.getIsBaby() or self.getIsLegendary() or self.getIsMythical()

    def hasMove(self, targets: set[str]):
        for moveName in self.moves:
            learnedMove = self.moves[moveName]
            move = learnedMove.getFromDex()
            if move.getName() in targets or move.dispName().lower() in targets:
                return True
        return False
    def hasAbility(self, targets: set[str]):
        for abilityName in self.getAbilities() + ([self.getHiddenAbility()] if self.hasHiddenAbility() else []):
            ability = ABILITYDEX.get(abilityName)
            if ability.getName() in targets or ability.dispName().lower() in targets:
                return True
        return False
    def hasType(self, targets: set[str]):
        for typ in self.getTypes():
            if typ in targets:
                return True
        return False
    
T = TypeVar("T", bound="DexItem")
class Dex(Generic[T]):
    items: dict[str, T]
    def __init__(self, data: dict[str, dict], cls: Type[T]):
        self.items = {}
        self.cls = cls
        for item in data:
            self.items[item] = self.cls(rawName=item, **data[item])
    
    def get(self, name: str):
        return self.items.get(name)
    
    def searchByNames(self, nameList: list[str]):
        for name in nameList:
            if self.items.get(name):
                return self.items.get(name)
        for item in self.items.values():
            if item.dispName().lower() in nameList:
                return item
    
    def getAllNames(self):
        return list(self.items.keys())
    
    def collect(self, key: Callable[[T], bool]):
        collected: set[T] = set()
        for itemName in self.items:
            if key(self.items[itemName]):
                collected.add(self.items[itemName])
        return collected

class Pokedex(Dex[Pokemon]):
    def collect(self, key: Callable[[Pokemon], bool]):
        collected: set[Pokemon] = set()
        for itemName in self.items:
            if key(self.items[itemName]) and not self.items[itemName].getBattleOnly():
                collected.add(self.items[itemName])
        return collected

def createDex(path: str, cls: Type[T], *, dexCls: Type[Dex]=Dex) -> Dex[T]:
    with open(path, "r") as f:
        return dexCls(json.load(f), cls)

POKEDEX = createDex("./sources/dexes/pokedex.json", Pokemon, dexCls=Pokedex)
MOVEDEX = createDex("./sources/dexes/movedex.json", Move)
ABILITYDEX = createDex("./sources/dexes/abilitydex.json", Ability)