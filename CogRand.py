
from utils import Fail
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
    
    @commands.group(**R.RANDOM.meta, invoke_without_command=True)
    async def random(self, ctx: commands.Context, *, args: str=None):
        if not args:
            await ctx.send(R.RANDOM.desc)
            return
        splitArgs = whitespacePat.split(args)
        match = dicePat.search(splitArgs[0])
        if match:
            await self.dice(ctx, *splitArgs)
        elif not ctx.invoked_subcommand:
            raise Fail(R.ERR.INVALID_SUBCOMMAND(args))
    
    @random.command(**R.DICE.meta)
    async def dice(self, ctx: commands.Context, *args: str):
        if not args:
            await ctx.send(R.DICE.desc)
        
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
