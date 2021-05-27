
from front.CogMod import CogMod
from typing import Optional, Union

import discord
import sources.text.cogrp as R
from back.ids import IDS, IDs
from back.utils import Fail
from discord.ext import commands

Ctx = commands.Context
_webhookName = "muOS Tupperhook"

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
    
    async def getMsgToReference(self, channel: discord.TextChannel, notif: str):
        if notif == R.SCENE.BREAK:
            find = ["scene unpaused", "scene resumed", "<><>"]
        elif notif == R.SCENE.PAUSED:
            find = ["<><>"]
        elif notif == R.SCENE.RESUMED:
            find = ["scene paused"]
        channelMessage: discord.Message
        found = False
        async for channelMessage in channel.history(limit=1000):
            if any(s in channelMessage.content.lower() for s in find):
                found = True
                break
        if found:
            return channelMessage
        return None
    
    async def sendSceneNotif(self, channel: discord.TextChannel, notif: str, manualRef: discord.Message=None):
        ref = await self.getMsgToReference(channel, notif)
        newMessage: discord.Message = await channel.send(notif, reference=ref if not manualRef else manualRef)
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
        if not user.bot and message.author.id == self.bot.user.id:
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
    
    @commands.command(**R.NEW_NPC.meta)
    @commands.check(IDS.dmCheck)
    async def newNPC(self, *, args: str):
        split = args.split(";", 1)
        if len(split) != 2: raise Fail()
        name, link = split