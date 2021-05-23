
from back.general import EMPTY
import datetime as dt
from front.CogMod import CogMod
from typing import Literal, Optional, Union

import discord
import sources.text.cogrp as R
from back.ids import IDS, IDs
from back.tupper import Codes, TUPPER_LISTS, reLink, defaultImage
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
                    break
            if not self.webhooks.get(channelID):
                self.webhooks[channelID] = await channel.create_webhook(name=_webhookName)
    
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
    
    @classmethod
    def _getTupper(cls, ctx: Ctx, name: str, *, ignoreDMCheck: bool=False):
        """ Gets the tupper made by the context's author with the given name.
            If the context's author is a DM, it also matches against the public tuppers.
            If the name wasn't found, it raises the correct error. """
        if ignoreDMCheck or IDs.dmCheck(ctx):
            res = TUPPER_LISTS.getPublic(name)
            if res != Codes.NOT_FOUND:
                return res
        res = TUPPER_LISTS.get(ctx.author.id, name)
        if res == Codes.NO_TUPPERS: raise Fail(R.ERR.NO_TUPPERS)
        if res == Codes.NOT_FOUND: raise Fail(R.ERR.NOT_FOUND(name))
        return res
    
    @commands.command(**R.SCENE.meta)
    async def scene(self, ctx: Ctx, *, op: str):
        await ctx.message.delete()
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
    
    def _parseTupperArgs(self, args: list[str]):
        newURL = None
        if not len(args) >= 2: raise Fail(R.ADD_TUPPER.TOO_FEW_ARGS(len(args)))
        newName, newPrefix, *args = args
        if args: newURL, *args = args
        if args: raise Fail(R.ADD_TUPPER.TOO_MANY_ARGS(len(args)))

        if newURL and not reLink.match(newURL): raise Fail(R.ADD_TUPPER.BAD_URL(newURL))
        if not "text" in newPrefix: raise Fail(R.ADD_TUPPER.BAD_PREFIX(newPrefix))

        return newName, newPrefix, newURL
    
    @commands.command(**R.ADD_TUPPER.meta)
    async def addTupper(self, ctx: Ctx, *, args: str):
        split = [arg.strip() for arg in args.split(";")]
        public = False
        if split[0].lower() == "public":
            if not IDs.dmCheck(ctx): raise Fail(R.ADD_TUPPER.BAD_PUBLIC)
            public = True
            split = split[1:]
        
        newName, newPrefix, newURL = self._parseTupperArgs(split)

        res = TUPPER_LISTS.add(ctx.author.id, newName, newPrefix, public, newURL)
        if res == Codes.EXISTS: await ctx.send(R.ADD_TUPPER.FAIL(newName))
        elif res == Codes.EXISTS_PUBLIC: await ctx.send(R.ADD_TUPPER.FAIL_PUBLIC(newName))
        else:
            await paginate(ctx, R.ADD_TUPPER.SUCCESS(res), ignoreIndex=True)
    
    @commands.command(**R.REMOVE_TUPPER.meta)
    async def removeTupper(self, ctx: Ctx, *, name: str):
        tupper = self._getTupper(ctx, name)
        TUPPER_LISTS.remove(tupper.getOwnerID(), tupper.getName())
        await ctx.send(R.REMOVE_TUPPER.SUCCESS(name))
    
    @commands.command(**R.GET_TUPPER.meta)
    async def getTupper(self, ctx: Ctx, *, name: str):
        tupper = self._getTupper(ctx, name, ignoreDMCheck = True)
        await ctx.send(R.GET_TUPPER.SUCCESS(tupper))
    
    @commands.command(**R.ADD_TUPPER_EMOTE.meta)
    async def addTupperEmote(self, ctx: Ctx, *, args: str):
        split = [arg.strip() for arg in args.split(";")]
        tupperName, newName, newPrefix, newURL = self._parseTupperArgs(split)

        tupper = self._getTupper(ctx, tupperName)
        newEmote = tupper.addEmote(newName, newPrefix, newURL)
        await ctx.send(R.ADD_TUPPER_EMOTE.SUCCESS(tupper, newEmote))
    
    @commands.command(**R.REMOVE_TUPPER_EMOTE.meta)
    async def removeTupperEmote(self, ctx: Ctx, *, args: str):
        split = [arg.strip() for arg in args.split(";")]
        if len(split) < 2: raise Fail(R.ADD_TUPPER.TOO_FEW_ARGS(len(split)))
        tupperName, name, *split = split
        if split: raise Fail(R.ADD_TUPPER.TOO_MANY_ARGS(len(split)))
        
        tupper = self._getTupper(ctx, tupperName)
        res = tupper.removeEmote(name)
        if res == Codes.NOT_FOUND: raise Fail(R.ERR.EMOTE_NOT_FOUND(tupper.getName(), name))
        await ctx.send(R.REMOVE_TUPPER_EMOTE.SUCCESS(tupper.getName(), res.getName()))
    
    @commands.command(**R.ADD_TUPPER_IMAGE.meta)
    async def addTupperImage(self, ctx: Ctx, *, args: str):
        split = [arg.strip() for arg in args.split(";")]
        tupperName, emoteName, emoteURL = self._parseTupperArgs(split)