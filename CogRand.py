
from sources.pkmn import MISSINGNO
from Pokemon import Dex, LearnedMove, METHODS, Pokedex, Pokemon
from typing import Any, Callable, Generic, Optional, TypeVar, Union
from utils import Fail, getMuOSEmbed, paginateDEPR, shuffleWord
import discord
from discord.ext import commands
import json
import random
import re

import sources.text as T

R = T.RAND

dicePat = re.compile(r"^(\d+)d(\d+)$")
whitespacePat = re.compile(r"\s")
commaPat = re.compile(r",")

class CogRand(commands.Cog, name=R.COG.NAME, description=R.COG.DESC):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open(R.PATH.TABLES, "r") as f:
            self.lootTables = json.load(f)
        with open(R.PATH.POKEDEX, "r") as f:
            self.pokedex = Pokedex(json.load(f))
        
        self.lastSearch: dict[int, list] = {}

    async def trySub(self, sub, *args, **kwargs):
        try:
            res = await sub(*args, **kwargs)
            if res == None: res = True
            return res
        except Fail:
            return False
    
    def getPokemonByName(self, name: str):
        name = name.strip().lower()
        pkmn = self.pokedex.get(name)
        if pkmn:
            return pkmn
        shuffleSet = shuffleWord(name)
        for shuffledName in shuffleSet:
            pkmn = self.pokedex.get(shuffledName)
            if pkmn:
                return pkmn
        return None
        
    async def sendPkmn(self, ctx: commands.Context, pkmn: Pokemon):
        pages = []
        pageEmbeds = R.GET_PKMN_PAGES(pkmn)
        for embed in pageEmbeds:
            pages.append({"embed": getMuOSEmbed(**embed)})
        await paginateDEPR(ctx, pages)
    
    async def sendPkmnList(self, ctx: commands.Context, title: str, pkmnList: list[Pokemon]):
        pages = []
        pageEmbeds = R.GET_PKMN_LIST_PAGES(title, pkmnList)
        for embed in pageEmbeds:
            pages.append({"embed": getMuOSEmbed(**embed)})
        await paginateDEPR(ctx, pages)
    
    async def sendPkmnShort(self, ctx: commands.Context, pkmn: Pokemon):
        embed = getMuOSEmbed(**R.GET_PKMN_EMBED(pkmn))
        await ctx.send(embed=embed)
    
    @commands.group(**R.RAND.meta, invoke_without_command=True)
    async def random(self, ctx: commands.Context, *args: str):
        if not args:
            await ctx.send(R.RAND.desc)
            return
        
        if not ctx.invoked_subcommand:
            args = " ".join(args)
            if await self.trySub(self.randDice, ctx, dice=args): return
            raise Fail(R.ERR.INVALID_SUBCOMMAND(args))
    
    @random.command(**R.RAND_DICE.meta)
    async def randDice(self, ctx: commands.Context, *, dice: str):
        args = whitespacePat.split(dice)
        if not args:
            await ctx.send(R.RAND_DICE.desc)
            return
        
        rolls: dict[str, list[int]] = {}
        for arg in args:
            match = dicePat.search(arg)
            if not match:
                raise Fail(R.ERR.BAD_DICE_FORMAT(arg))
            
            number, sides = match.groups()
            rolls[arg] = [str(random.randint(1, int(sides))) for _ in range(int(number))]
        res = R.INFO.ROLL(rolls)
        if len(res) > 2000:
            await ctx.send(R.INFO.TOO_MANY_DICE(" ".join(args)))
            return
        await ctx.send(res)
    
    @random.command(**R.RAND_PKMN.meta)
    async def randPkmn(self, ctx: commands.Context, *, args: Optional[str]=None):
        name = random.choice(self.pokedex.getAllNames())
        pkmn = self.pokedex.get(name)
        await self.sendPkmnShort(ctx, pkmn)
    
    @random.command(**R.RAND_LAST.meta)
    async def randLast(self, ctx: commands.Context, *, args: Optional[str]=None):
        lastSearch = self.lastSearch.get(ctx.author.id)
        if not lastSearch:
            raise Fail(R.ERR.NO_LAST)
        choice = random.choice(lastSearch)
        if isinstance(choice, Pokemon):
            await self.sendPkmnShort(ctx, choice)
        else:
            raise NotImplementedError()

    @commands.group(**R.DEX.meta, invoke_without_command=True)
    async def dex(self, ctx: commands.Context, *args: Optional[str]):
        if not args:
            await ctx.send(R.DEX.desc)
            return
        
        if not ctx.invoked_subcommand:
            args = " ".join(args)
            if await self.trySub(self.pokemon, ctx, args): return
            raise Fail(R.ERR.INVALID_SUBCOMMAND(args))
    
    @dex.group(**R.DEX_PKMN.meta, invoke_without_command=True)
    async def pokemon(self, ctx: commands.Context, *args: Optional[str]):
        if not args:
            await ctx.send(R.DEX_PKMN.desc)
            return
        
        if not ctx.invoked_subcommand:
            args = " ".join(args)
            if await self.trySub(self.pkmnName, ctx, name=args): return
            if await self.trySub(self.pkmnMove, ctx, move=args): return
            raise Fail(R.ERR.INVALID_SUBCOMMAND(args))
    
    @pokemon.group()
    async def query(self, ctx: commands.Context, *, query: Optional[str]=None):
        if not query:
            return
        
        op = None
        allMatches = set()
        for chunk in commaPat.split(query):
            failText = ""
            words = whitespacePat.split(chunk)
            moveKws = ["learns", "knows", "move", "moves"]
            abilityKws = ["has", "ability", "abilities"]
            typeKws = ["is", "type", "types"]
            allKws = moveKws + abilityKws + typeKws
            if not words[0] in allKws:
                if not op:
                    raise Fail(f"For the chunk `{chunk}`: The first chunk should start with one of {', '.join([f'`{kw}`' for kw in allKws])}.")
                else:
                    args = words
            else:
                op, *args = words
            or_ = any(x in args for x in ["or", "any"])
            and_ = any(x in args for x in ["and", "all"])
            if or_ and and_:
                failText += f"For the chunk `{chunk}`: Chunks with both `or` and `and` aren't implemented yet, sorry."
            targets = [arg for arg in args if not arg in ["or", "any", "and", "all"]]
            chunkMatches = set()
            for target in targets:
                target = target.lower()
                if op in moveKws:
                    matches = self.pokedex.collect(lambda pkmn: pkmn.getMove(target))
                    if not matches: failText += f"For the target `{target}` in the chunk `{chunk}`: No Pokemon were found with this move."
                elif op in abilityKws:
                    matches = self.pokedex.collect(lambda pkmn: pkmn.hasAbility(target))
                    if not matches: failText += f"For the target `{target}` in the chunk `{chunk}`: No Pokemon were found with this ability."
                elif op in typeKws:
                    matches = self.pokedex.collect(lambda pkmn: pkmn.hasType(target))
                    if not matches: failText += f"For the target `{target}` in the chunk `{chunk}`: No Pokemon were found with this type."
                if not chunkMatches:
                    chunkMatches |= matches
                else:
                    if or_:
                        chunkMatches |= matches
                    else:
                        chunkMatches &= matches
            if not allMatches:
                allMatches |= matches
            else:
                allMatches &= matches
        
    @pokemon.command(**R.DEX_PKMN_NAME.meta)
    async def pkmnName(self, ctx: commands.Context, *, name: Optional[str]=None):
        if not name:
            await ctx.send(R.DEX_PKMN_NAME.desc)
            return
        

        pkmn = self.getPokemonByName(name)
        if name.lower() == "missingno":
            pkmn = MISSINGNO
        if pkmn:
            await self.sendPkmn(ctx, pkmn)
        else:
            raise Fail(R.ERR.BAD_POKEMON(name))
    
    T = TypeVar("T")
    async def collectAndSend(self, ctx: commands.Context, dex: Dex[T], key: Callable[[T], bool], title: str, fail: str):
        matched = dex.collect(key)
        
        if matched:
            await self.sendPkmnList(ctx, title, matched)
            self.lastSearch[ctx.author.id] = matched
        else:
            raise Fail(fail)
    
    @pokemon.command(**R.DEX_PKMN_MOVE.meta)
    async def pkmnMove(self, ctx: commands.Context, *, move: Optional[str]=None):
        if not move:
            await ctx.send(R.DEX_PKMN_MOVE.desc)
            return
        
        await self.collectAndSend(
            ctx,
            self.pokedex,
            lambda pkmn: pkmn.getMove(move.lower()),
            R.INFO.DEX_PKMN_MOVE_TITLE(move.title()),
            R.ERR.MOVE_NOT_FOUND(move.title())
        )
    
    @pokemon.command(**R.DEX_PKMN_ABILITY.meta)
    async def pkmnAbility(self, ctx: commands.Context, *, ability: Optional[str]=None):
        if not ability:
            await ctx.send(R.DEX_PKMN_ABILITY.desc)
            return
        
        await self.collectAndSend(
            ctx,
            self.pokedex,
            lambda pkmn: pkmn.hasAbility(ability.lower()),
            R.INFO.DEX_PKMN_ABILITY_TITLE(ability.title()),
            R.ERR.ABILITY_NOT_FOUND(ability.title())
        )
    
    @pokemon.command(**R.DEX_PKMN_TYPE.meta)
    async def pkmnType(self, ctx: commands.Context, *, typ: Optional[str]=None):
        if not typ:
            await ctx.send(R.DEX_PKMN_TYPE.desc)
            return
        
        await self.collectAndSend(
            ctx,
            self.pokedex,
            lambda pkmn: pkmn.hasType(typ.lower()),
            R.INFO.DEX_PKMN_TYPE_TITLE(typ.title()),
            R.ERR.TYPE_NOT_FOUND(typ.title())
        )