
from back.npc import NPC_LIST
from front.CogMod import CogMod
from typing import Optional, Union

import discord
import sources.text.cogrp as R
import re
from back.ids import IDS, IDs
from back.utils import Fail
from discord.ext import commands

Ctx = commands.Context
_webhookName = "muOS Tupperhook"

linkRe = re.compile(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")

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
        if not message.author.bot:
            tupper = NPC_LIST.match(message.content)
            if not tupper: return

            self.cogMod.addDeleteIgnore(message.id)
            await message.delete()
            webhook = self.webhooks.get(message.channel.id)
            if not webhook:
                self.webhooks[message.channel.id] = await message.channel.create_webhook(name=_webhookName)
                print(f"Created new webhook for RP channel `{message.channel.name}`.")
                
            await webhook.send(tupper.removePrefixFrom(message.content), username=tupper.getName(), avatar_url=tupper.getImage())
    
    async def onReaction(self, message: discord.Message, emoji: str, user: Union[discord.User, discord.Member]):
        if (not user.bot) and message.author.id == self.bot.user.id:
            if emoji == "❌":
                print("why the fuck is it not deleting")
                print(type(message))
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
    async def newNPC(self, ctx: Ctx, *, args: str):
        split = args.split(";", 1)
        if len(split) != 2: raise Fail(R.NEW_NPC.BAD_ARGS(len(split)))
        name, link = [part.strip() for part in split]
        
        if not linkRe.match(link): raise Fail(R.NEW_NPC.BAD_LINK)

        res = NPC_LIST.add(name, link)
        if not res: raise Fail(R.NEW_NPC.EXISTS(name))
        else: await ctx.send(R.NEW_NPC.SUCCESS(name))
    
    @commands.command(**R.RM_NPC.meta)
    @commands.check(IDS.dmCheck)
    async def rmNPC(self, ctx: Ctx, *, name: str):
        res = NPC_LIST.remove(name)
        if not res: raise Fail(R.RM_NPC.NOT_FOUND(name))
        else: await ctx.send()