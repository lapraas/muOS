
from enum import Enum
from sources.text.cogdex import GET_PKMN_LIST_PAGES, GET_PKMN_PAGES
from typing import Callable, Generic, Optional, Type, TypeVar
from discord.ext import commands

from Dexes import Ability, Dex, DexItem, Move, POKEDEX, MOVEDEX, ABILITYDEX, Pokemon
from sources.text import DEX as D
import re
from utils import Fail, paginateDict, paginateEmbeds, shuffleWord

Ctx = commands.Context

spacePat = re.compile(r"\s+")

M = TypeVar("M", bound="DexItem")
class Mode():
    def __init__(self, names: list[str]):
        self.name = names[0]
        self.names = set(names)
    
    def match(self, against: str):
        return against in self.names
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"
    
class Qualifier(Mode, Generic[M]):
    def __init__(self, names: list[str], key: Callable[[set[str]], Callable[[M], bool]]):
        super().__init__(names)
        self.key = key
    
    def getKey(self):
        return self.key

class ModifierMode(Mode, Generic[M]):
    def __init__(self, names: list[str], key: Callable[[M], bool]):
        super().__init__(names)
        self.key = key
    
    def getKey(self):
        return self.key

class BaseMode(Mode, Generic[M]):
    def __init__(self, names: list[str], cls: Type[M], dex: Dex[M], dispFunc: Callable[[Ctx, M], None], dispListFunc: Callable[[Ctx, str, list[M]], None], extraModes: list[Qualifier[M]], modifiers: list[ModifierMode[M]]):
        super().__init__(names)
        self.cls = cls
        self.dex = dex
        self.dispFunc = dispFunc
        self.dispListFunc = dispListFunc
        self.extraModes = extraModes
        self.modifiers = modifiers
    
    def getCls(self):
        return self.cls

    def getDex(self):
        return self.dex
    
    def getDispFunc(self):
        return self.dispFunc
    
    def getDispListFunc(self):
        return self.dispListFunc
    
    def getQualifier(self, target: str):
        for mode in self.extraModes:
            if mode.match(target):
                return mode
        return None
    
    def getModifier(self, target: str):
        for mode in self.modifiers:
            if mode.match(target):
                return mode
        return None

async def sendPkmn(ctx: Ctx, pkmn: Pokemon):
    pages = GET_PKMN_PAGES(pkmn)
    await paginateEmbeds(ctx, pages)

async def sendPkmnList(ctx: Ctx, query: str, pkmnList: list[Pokemon]):
    pages = GET_PKMN_LIST_PAGES(query, pkmnList)
    await paginateEmbeds(ctx, pages)

POKEMON = BaseMode(
    ["pokemon", "pkmn"],
    Pokemon, POKEDEX, sendPkmn, sendPkmnList,
    [
        Qualifier(
            ["move", "moves"],
            lambda targets: lambda pkmn: pkmn.hasMove(targets)
        ),
        Qualifier(
            ["ability", "abilities"],
            lambda targets: lambda pkmn: pkmn.hasAbility(targets)
        ),
        Qualifier(
            ["type", "types"],
            lambda targets: lambda pkmn: any(typ in targets for typ in pkmn.getTypes())
        ),
        Qualifier(
            ["color"],
            lambda targets: lambda pkmn: pkmn.getColor() in targets
        ),
        Qualifier(
            ["group", "egg", "groups", "eggs"],
            lambda targets: lambda pkmn: any(group in targets for group in pkmn.getEggGroups())
        )
    ],
    [
        ModifierMode(
            ["baby", "smol"],
            lambda pkmn: pkmn.getIsBaby()
        ),
        ModifierMode(
            ["legendary"],
            lambda pkmn: pkmn.getIsLegendary()
        ),
        ModifierMode(
            ["mythical", "mythic"],
            lambda pkmn: pkmn.getIsMythical()
        )
    ]
)
MOVE = BaseMode(
    ["move", "moves", "learns", "learn"],
    Move, MOVEDEX, None, None,
    [

    ],
    [

    ]
)
ABILITY = BaseMode(
    ["ability", "abilities", "has"],
    Ability, ABILITYDEX, None, None,
    [

    ],
    [

    ]
)
MODES: list[BaseMode] = [POKEMON, MOVE, ABILITY]

def match(name: str):
    for member in MODES:
        if member.match(name):
            return member

def matchType(typ: Type[DexItem]):
    for member in MODES:
        if member.getCls() == typ:
            return member

withPat = re.compile(r"\s+with\s+")
andOrPat = re.compile(r"(?:\s*,)?((?:\s+and\s+)|(?:\s+or\s+))|(?:\s*,\s*)")

class CogDex(commands.Cog, name=D.COG.NAME, description=D.COG.DESC):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.lastSearch: dict[int, list] = {}

    @commands.command(**D.QUERY.meta)
    async def query(self, ctx: Ctx, *, query: str):
        # A list of all matched items.
        matches: set[DexItem] = set()
        # The type of item to match.
        mode: Optional[BaseMode] = None
        
        # Split by 'with'
        if withPat.search(query):
            split = withPat.split(query, 1)
            # The string with the type of item to match; everything after
            modeStr, qualifiersStr = split
        else:
            # The string with the type of item to match; everything after
            modeStr = query
        # Split by space to collect modifiers to the item to match (baby, legendary, etc.)
        split = spacePat.split(modeStr)
        # List of modifiers.
        modifs = split[:-1]
        # The BaseMode object for the type of item to match.
        mode = match(split[-1])

        if not mode:
            # If we don't have a mode, we want to do a specific search.
            matches |= set(self.specificSearch(query))
            # If we don't have a mode and the specific search fails, error.
            if not matches:
                raise Fail(D.ERR.NO_MODE(query))
        else:
            matches = self.modeSearch(mode, qualifiersStr, query)
        if not matches:
            await ctx.send(D.INFO.NO_MATCH(query))
            return
        if not mode:
            for item in matches: break
            mode = matchType(item.__class__)
        if len(matches) == 1:
            await mode.getDispFunc()(ctx, *matches)
        else:
            await mode.getDispListFunc()(ctx, query, matches)
        
    def specificSearch(self, query: str):
        query = query.lower()
        if POKEDEX.get(query):
            return [POKEDEX.get(query)]
        shuffled = shuffleWord(query)
        pkmn = POKEDEX.searchByNames(shuffled)
        if pkmn: return [pkmn]
        move = MOVEDEX.searchByNames(shuffled)
        if move: return [move]
        ability = ABILITYDEX.searchByNames(shuffled)
        if ability: return [ability]
        return []
    
    def modeSearch(self, mode: BaseMode, qualifiersStr: str, query: str):
        matches = set()
        # If we do have a mode, get the dex from the mode.
        dex = mode.getDex()
        
        # The attributes each matched item must have.
        qualifier: Optional[Qualifier] = None
        # Each boolean operator in the rest of the query.
        print(andOrPat.findall(qualifiersStr))
        opFinds = [s.strip() for s in andOrPat.findall(qualifiersStr)]
        # We can only have one operator. The default is "and".
        op = "and" if not opFinds else opFinds[0]
        # Make sure no other operators exist - can't mix.
        for otherOp in opFinds:
            if otherOp != op: raise Fail(D.ERR.MIXING_OPS(query))

        # Iterate through each qualifier.
        for qualifierStr in andOrPat.split(qualifiersStr):
            if not qualifiersStr.strip(): continue
            # Split by the first space - the first word of the qualifier string can be the qualifier mode.
            split = spacePat.split(qualifierStr, 1)
            # We want to be able to use the same qualifier mode if none exists after the first.
            if mode.getQualifier(split[0]):
                qualifier = mode.getQualifier(split[0])
                rest = split[1]
            else:
                rest = qualifierStr
            # If the first qualifier string doesn't have a qualifier mode, fail.
            if not qualifier: raise Fail(D.ERR.NO_EXTRA_MODE(query, qualifierStr))
            key = qualifier.getKey()(rest)
            extraMatches = dex.collect(key)
            if op == "or" or not op or not matches:
                matches |= extraMatches
            else:
                matches.intersection_update(extraMatches)
                if not matches:
                    break
        return matches