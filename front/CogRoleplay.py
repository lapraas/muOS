
from back.general import EMPTY
import datetime as dt
from front.CogMod import CogMod
from typing import Literal, Optional, Union

import discord
import sources.text.cogrp as R
from back.ids import IDS, IDs
from back.npc import defaultImage
from back.utils import Fail, paginate
from discord.ext import commands

Ctx = commands.Context
_webhookName = "muOS Tupperhook"
_webhookShortName = "muOS"

class CogRoleplay(commands.Cog):
    def __init__(self, bot: commands.Bot, cogMod: CogMod):
        self.bot = bot
        self.cogMod = cogMod

        self.listen: set[int] = set()
        self.webhooks: dict[int, discord.Webhook] = {}
    
    async def onReady(self):
        for channelID in IDS.getAll(IDs.rpChannels):
            channel: discord.TextChannel = await self.bot.fetch_channel(channelID)
            webhook: Optional[discord.Webhook] = None
            for webhook in await channel.webhooks():
                if webhook.name == _webhookName:
                    self.webhooks[channelID] = webhook
                    print(f"Found existing webhook for RP channel `{channel.name}`.")
                    break
            if not self.webhooks.get(channelID):
                self.webhooks[channelID] = await channel.create_webhook(name=_webhookName)
                print(f"Created new webhook for RP channel `{channel.name}`.")
    
    def _listenTo(self, message: discord.WebhookMessage):
        self.listen.add(message.id)
    
    async def replaceWithLink(self, channel: discord.TextChannel, notif: str):
        if not notif == R.SCENE.BREAK:
            return notif
        channelMessage: discord.Message
        found = False
        async for channelMessage in channel.history(limit=200):
            if channelMessage.author.bot and "<><>" in channelMessage.content:
                found = True
                break
        if found:
            notif = R.SCENE.ADD_LINK(notif, channelMessage.jump_url)
        return notif
    
    async def getSceneNotif(self, channel: discord.TextChannel, notif: str):
        notif = await self.replaceWithLink(channel, notif)
        return notif
    
    async def sendSceneNotif(self, channel: discord.TextChannel, notif: str):
        notif = await self.getSceneNotif(channel, notif)
        webhook = self.webhooks[channel.id]
        newMessage: discord.Message = await webhook.send(notif, wait=True, username=_webhookShortName, avatar_url=defaultImage)
        return newMessage
    
    async def onMessage(self, message: discord.Message):
        pass
        #if not message.author.bot:
        #    res = TUPPER_LISTS.match(message.author.id, message.content)
        #    if not isinstance(res, tuple): return
        #    tupper, emote = res
#
        #    self.cogMod.addDeleteIgnore(message.id)
        #    await message.delete()
        #    content: str = message.content
        #    content = content.removeprefix(emote.getPrefix()).removesuffix(emote.getSuffix())
        #    webhook = self.webhooks[message.channel.id]
        #    await webhook.send(content, username=tupper.getName(), avatar_url=emote.getURL())
    
    async def onReaction(self, message: discord.Message, emoji: str, user: Union[discord.User, discord.Member]):
        if message.id in self.listen and not user.bot:
            if emoji == "❌":
                self.listen.discard(message.id)
                await message.delete()
                return
            else:
                return
            #await message.remove_reaction(emoji, user)
    
    @commands.command(**R.SCENE.meta)
    async def scene(self, ctx: Ctx, *, op: str):
        if not IDS.check(IDs.rpChannels, ctx.channel.id):
            raise Fail(R.ERR.NOT_IN_RP_CHANNEL)
        if any(x in op for x in ["resume", "unpause"]):
            message = await self.sendSceneNotif(ctx.channel, R.SCENE.RESUMED)
        elif any(x in op for x in ["pause"]):
            message = await self.sendSceneNotif(ctx.channel, R.SCENE.PAUSED)
        elif any(x in op for x in ["break"]):
            message = await self.sendSceneNotif(ctx.channel, R.SCENE.BREAK)
        else:
            raise Fail(R.SCENE.FAIL(op))
        self._listenTo(message)
        await ctx.message.delete()
    
    @commands.command(**R.ADD_TUPPER.meta)
    @commands.check(IDS.dmCheck)
    async def newNPC(self, *, args: str):
        split = args.split(";", 1)
        if len(split) != 2: raise Fail()
        name, link = split