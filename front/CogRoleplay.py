
import datetime as dt
from typing import Optional, Union

import discord
import sources.text.cogrp as R
from back.ids import IDS, IDs
from back.tupper import Codes, Emote, TUPPER_LISTS, reLink
from back.utils import Fail, paginate
from discord.ext import commands

Ctx = commands.Context

class CogRoleplay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.listen: dict[int, Optional[int]] = {}
        self.timers: dict[int, dt.datetime] = {}
    
    def _listenTo(self, message: discord.Message, uid: Optional[int]=None):
        self.listen[message.id] = uid
    
    async def tick(self):
        now = dt.datetime.now()
        for channelID in self.timers:
            lastMsgTime = self.timers[channelID]
            if now - lastMsgTime > dt.timedelta(hours=1):
                channel = await self.bot.fetch_channel(channelID)
                newMessage: discord.Message = await channel.send(R.SCENE.PAUSED)
                self._listenTo(newMessage)
    
    async def onMessage(self, message: discord.Message):
        if message.author.bot:
            replace = None
            content: str = message.content

            if any(x in content for x in
                ["<><>"]
            ): replace = R.SCENE.BREAK
            elif not (content.startswith("(") and content.endswith(")")):
                pass
            elif any(x in content.lower() for x in
                ["scene paused", "scene on hold", "scene on pause"]
            ): replace = R.SCENE.PAUSED
            elif any(x in content.lower() for x in
                ["scene unpaused", "scene resumed"]
            ): replace = R.SCENE.RESUMED

            if replace:
                await message.delete()
                newMessage: discord.Message = await message.channel.send(replace)
                self._listenTo(newMessage)
            else:
                self.timers[message.channel.id] = dt.datetime.now()
        else:
            emote = TUPPER_LISTS.match(message.author.id, message.content)
            if not isinstance(emote, Emote): return

            await message.delete()
            content: str = message.content
            content = content.removeprefix(emote.getPrefix()).removesuffix(emote.getSuffix())
    
    async def onReaction(self, message: discord.Message, emoji: str, user: Union[discord.User, discord.Member]):
        if message.id in self.listen and not user.bot:
            if self.listen[message.id] and user.id != self.listen[message.id]:
                await user.send(R.INFO.OTHER_USER(message.content, self.listen[message.id]))
            elif emoji == "❌":
                await message.delete()
            elif emoji == "⏹️":
                await message.edit(R.SCENE.BREAK)
            elif emoji == "⏸":
                await message.edit(R.SCENE.PAUSED)
            elif emoji == "▶️":
                newMessage = await message.channel.send(R.SCENE.RESUMED)
                self.listen[newMessage.id] = self.listen[message.id]
                self._listenTo(newMessage, self.listen[message.id])

            else:
                return
            await message.remove_reaction(emoji, user)
    
    @classmethod
    def _getTupper(cls, ctx: Ctx, name: str):
        if IDs.dmCheck(ctx):
            if TUPPER_LISTS.getPublic(name):
                return TUPPER_LISTS.getPublic(name)
        return TUPPER_LISTS.get(ctx.author.id, name)
    
    @commands.command(**R.SCENE.meta)
    async def scene(self, ctx: Ctx, *, op: str=None):
        await ctx.message.delete()
        if not IDS.check(IDs.rpChannels, ctx.channel.id):
            raise Fail(R.ERR.NOT_IN_RP_CHANNEL)
        if any(x in op for x in ["pause", "hold"]):
            message = await ctx.send(R.SCENE.PAUSED)
        elif any(x in op for x in ["resume", "unpause"]):
            message = await ctx.send(R.SCENE.RESUMED)
        else:
            message = await ctx.send(R.SCENE.BREAK)
        self.listen[message.id] = ctx.author.id
    
    @commands.command(**R.ADD_TUPPER.meta)
    async def addTupper(self, ctx: Ctx, *, args: str):
        split = [arg.strip() for arg in args.split(";")]
        public = False
        if split[0].lower() == "public":
            if not IDs.dmCheck(ctx): raise Fail(R.ADD_TUPPER.BAD_PUBLIC)
            public = True
            split = split[1:]
        newURL = None
        if not len(split) >= 2: raise Fail(R.ADD_TUPPER.TOO_FEW_ARGS(len(split)))
        newName, newPrefix, *split = split
        if split: newURL, *split = split
        if split: raise Fail(R.ADD_TUPPER.TOO_MANY_ARGS(len(split)))

        if newURL and not reLink.match(newURL): raise Fail(R.ADD_TUPPER.BAD_URL(newURL))
        if not "text" in newPrefix: raise Fail(R.ADD_TUPPER.BAD_PREFIX(newPrefix))

        res = TUPPER_LISTS.add(ctx.author.id, newName, newPrefix, public, newURL)
        if res == Codes.EXISTS:
            await ctx.send(R.ADD_TUPPER.FAIL(newName))
        elif res == Codes.EXISTS_PUBLIC:
            await ctx.send(R.ADD_TUPPER.FAIL_PUBLIC(newName))
        else:
            await paginate(ctx, R.ADD_TUPPER.SUCCESS(res), ignoreIndex=True)
    
    @commands.command(**R.REMOVE_TUPPER.meta)
    async def removeTupper(self, ctx: Ctx, *, name: str):
        res = self._getTupper(ctx, name)
        if res == Codes.NO_TUPPERS: raise Fail(R.ERR.NO_TUPPERS)
        if res == Codes.NOT_FOUND: raise Fail(R.ERR.NOT_FOUND(name))
        TUPPER_LISTS.remove(res.getOwnerID(), res.getName())
        await ctx.send(R.REMOVE_TUPPER.SUCCESS(name))