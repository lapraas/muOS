
from Pokemon import Pokedex, Pokemon
from typing import Optional, Union
from utils import Fail, getMuOSEmbed, paginate, shuffleWord
import discord
from discord.ext import commands
import json
import random
import re

import sources.text as T

R = T.RAND

dicePat = re.compile(r"^(\d+)d(\d+)$")
whitespacePat = re.compile(r"\s")

class CogRand(commands.Cog, name=R.COG.NAME, description=R.COG.DESC):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open(R.PATH.TABLES, "r") as f:
            self.lootTables = json.load(f)
        with open(R.PATH.POKEDEX, "r") as f:
            self.pokedex: Pokedex = Pokedex(json.load(f))

    async def trySub(self, sub, *args, **kwargs):
        try:
            await sub(*args, **kwargs)
            return True
        except Fail:
            return False
        
    async def sendPkmn(self, ctx: commands.Context, pkmn: Pokemon):
        pages = []
        pageEmbeds = R.GET_PKMN_PAGES(pkmn)
        for embed in pageEmbeds:
            pages.append({"embed": getMuOSEmbed(**embed)})
        await paginate(ctx, pages)
    
    async def sendPkmnShort(self, ctx: commands.Context, pkmn: Pokemon):
        embed = getMuOSEmbed(**R.GET_PKMN_EMBED(pkmn))
        await ctx.send(embed=embed)
    
    @commands.group(**R.RANDOM.meta, invoke_without_command=True)
    async def random(self, ctx: commands.Context, *, args: str=None):
        if not args:
            await ctx.send(R.RANDOM.desc)
            return
        
        if not ctx.invoked_subcommand:
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

    @commands.group(**R.DEX.meta, invoke_without_command=True)
    async def dex(self, ctx: commands.Context, *, args: Optional[str]=None):
        if not args:
            await ctx.send(R.DEX.desc)
            return
        
        if not ctx.invoked_subcommand:
            if await self.trySub(self.pokemon, ctx, args=args): return
            raise Fail(R.ERR.INVALID_SUBCOMMAND(args))
    
    @dex.group(**R.POKEMON.meta, invoke_without_context=True)
    async def pokemon(self, ctx: commands.Context, *, args: Optional[str]=None):
        if not args:
            await ctx.send(R.POKEMON.desc)
            return
        
        if not ctx.invoked_subcommand:
            if await self.trySub(self.pkmnName, ctx, name=args): return
            raise Fail(R.ERR.INVALID_SUBCOMMAND(args))
    
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
        
    @pokemon.command(**R.PKMN_NAME.meta)
    async def pkmnName(self, ctx: commands.Context, *, name: Optional[str]=None):
        if not name:
            await ctx.send(R.PKMN_NAME.desc)
            return
        
        pkmn = self.getPokemonByName(name)
        if pkmn:
            await self.sendPkmn(ctx, pkmn)
        else:
            raise Fail(R.ERR.BAD_POKEMON(name))
    
    #@pokemon.command(**R.PKMN_MOVE.meta)
    #async def pkmnMove(self, ctx: commands.Context, *, name: Optional[str]=None):
    #    if not name:
    #        await ctx.send(R.PKMN_MOVE.desc)
    #        return