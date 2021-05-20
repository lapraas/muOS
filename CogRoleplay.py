
from utils import Fail
from sources.ids import IDS, IDs
import discord
from discord.ext import commands
import datetime as dt
from typing import Optional, Union

import sources.text.cogrp as R

Ctx = commands.Context

class CogRoleplay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.listen: dict[int, Optional[int]] = {}
        self.timers: dict[int, dt.datetime] = {}
    
    def listenTo(self, message: discord.Message, uid: Optional[int]=None):
        self.listen[message.id] = uid
    
    async def tick(self):
        now = dt.datetime.now()
        for channelID in self.timers:
            lastMsgTime = self.timers[channelID]
            if now - lastMsgTime > dt.timedelta(hours=1):
                channel = await self.bot.fetch_channel(channelID)
                newMessage: discord.Message = await channel.send(R.INFO.SCENE_PAUSED)
                self.listenTo(newMessage)
    
    async def onMessage(self, message: discord.Message):
        if message.author.bot:
            replace = None
            if any(x in message.content for x in
                ["<><>"]
            ): replace = R.INFO.SCENE_BREAK
            if any(x in message.content.lower() for x in
                ["scene paused", "scene on hold", "scene on pause"]
            ): replace = R.INFO.SCENE_PAUSED
            if any(x in message.content.lower() for x in
                ["scene unpaused", "scene resumed"]
            ): replace = R.INFO.SCENE_RESUMED
            if replace:
                await message.delete()
                newMessage: discord.Message = await message.channel.send(replace).id
                self.listenTo(newMessage)
            else:
                self.timers[message.channel.id] = dt.datetime.now()
    
    async def onReaction(self, message: discord.Message, emoji: str, user: Union[discord.User, discord.Member]):
        if message.id in self.listen and not user.bot:
            if self.listen[message.id] and user.id != self.listen[message.id]:
                await user.send(R.INFO.OTHER_USER(message.content, self.listen[message.id]))
            elif emoji == "❌":
                await message.delete()
            elif emoji == "⏹️":
                await message.edit(R.INFO.SCENE_BREAK)
            elif emoji == "⏸":
                await message.edit(R.INFO.SCENE_PAUSED)
            elif emoji == "▶️":
                newMessage = await message.channel.send(R.INFO.SCENE_RESUMED)
                self.listen[newMessage.id] = self.listen[message.id]
                self.listenTo(newMessage, self.listen[message.id])

            else:
                return
            await message.remove_reaction(emoji, user)
    
    @commands.command(**R.SCENE.meta)
    async def scene(self, ctx: Ctx, *, op: str):
        if not IDS.check(IDs.rpChannels, ctx.channel.id):
            raise Fail(R.ERR.NOT_IN_RP_CHANNEL)
        if any(x in op for x in ["pause", "hold"]):
            message = ctx.send(R.INFO.SCENE_PAUSED)
        elif any(x in op for x in ["resume", "unpause"]):
            message = ctx.send(R.INFO.SCENE_RESUMED)
        else:
            message = ctx.send(R.INFO.SCENE_BREAK)
        self.listen[message.id] = ctx.author.id