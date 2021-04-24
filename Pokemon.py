
from typing import Callable, Generic, Optional, TypeVar, Union

class Move:
    def __init__(self, name: str):
        self.name = name
    
    def getName(self):
        return self.name
    
    def dispName(self):
        return self.name.title()

class METHODS:
    LEVEL = "level"
    TM = "tm"
    TR = "tr"
    EGG = "egg"
    TUTOR = "tutor"
    TRANSFER = "transfer"

    HAS_NUM = [LEVEL, TM, TR]

class LearnedMove(Move):
    def __init__(self, name: str, gen: str, method: str, num: Optional[str]=None):
        super().__init__(name)
        self.gens = {gen}
        self.method = method
        self.nums = [num]

    def getMethod(self):
        return self.method
    def getNums(self):
        return self.nums
    def getFirstNum(self):
        return self.nums[0]
    
    def dispNums(self):
        return ", ".join(self.nums)


class Evolution:
    def __init__(self, thresh: str, into: str):
        self.thresh = thresh
        self.into = into
    
    def isByLevel(self):
        return all(char in "1234567890" for char in self.thresh)
    def getThresh(self):
        return self.thresh
    def getInto(self):
        return self.into
    
    def dispThresh(self):
        return self.thresh.title()
    def dispInto(self):
        return self.into.title()

class Pokemon:
    def __init__(self, name: str, data: dict[str, Union[str, list[str], dict[str, str], dict[str, dict[str, Union[list[tuple[str, str]]], dict[str, tuple[str, str]]]]]]):
        self.name = name
        self.id: str = data["id"]
        self.image: str = data["image"]
        self.types: list[str] = data["types"]
        self.height: str = data["height"]
        self.weight: str = data["weight"]
        self.abilities: list[str] = data["abilities"]
        self.hiddenAbility: str = data["hiddenAbility"]
        self.evolutions: list[Evolution] = []
        for thresh in data["evoLine"]:
            into = data["evoLine"][thresh]
            self.evolutions.append(Evolution(thresh, into))
        self.moves: list[LearnedMove] = []
        for gen in data["moves"]:
            methods = data["moves"][gen]
            for method in methods:
                moves = methods[method]
                if method in METHODS.HAS_NUM:
                    for num in moves:
                        for name in moves[num]:
                            self.addMove(name, gen, method, num)
                else:
                    for name in moves:
                        self.addMove(name, gen, method)
    
    def addMove(self, name: str, gen: str, method: str, num: Optional[str]=None):
        for move in self.moves:
            if move.name == name and move.method == method:
                move.gens.add(gen)
                if num:
                    if not num in move.nums:
                        move.nums.append(num)
                return
        self.moves.append(LearnedMove(name, gen, method, num))

    def hasType(self, typ: str):
        return typ in self.types
    def getImage(self):
        return self.image
    def getEvolutions(self):
        return self.evolutions
    def hasAbility(self, ability: str):
        return ability in self.abilities + [self.hiddenAbility]
    def hasHiddenAbility(self):
        return self.hiddenAbility != "NONE"
    def getMove(self, name: str):
        for move in self.moves:
            if move.name == name:
                return move
        return False
    
    def dispName(self):
        return self.name.title()
    def dispTypes(self):
        return [type.title() for type in self.types]
    def dispAbilities(self):
        return [ability.title() for ability in self.abilities]
    def dispHiddenAbility(self):
        return self.hiddenAbility.title()
    
    def getAllMovesWithMethod(self, method: str):
        moves = []
        for move in self.moves:
            if move.method == method:
                moves.append(move)
        return moves

T = TypeVar("T")
class Dex(Generic[T]):
    items: dict[str, T]
    def __init__(self, data: dict):
        self.items = {}
        self.build(data)
    
    def build(self, data: dict):
        pass
    
    def get(self, name: str):
        return self.items.get(name)
    
    def getAllNames(self):
        return list(self.items.keys())
    
    def collect(self, key: Callable[[T], bool]):
        collected: list[T] = []
        for itemName in self.items:
            if key(self.items[itemName]):
                collected.append(self.items[itemName])
        return collected

class Pokedex(Dex[Pokemon]):
    def build(self, data: dict[str, dict[str, Union[str, list[str], dict[str, str], dict[str, dict[str, Union[list[tuple[str, str]]], dict[str, tuple[str, str]]]]]]]):
        for name in data:
            self.items[name] = Pokemon(name, data[name])