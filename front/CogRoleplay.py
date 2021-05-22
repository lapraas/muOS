
import datetime as dt
from typing import Optional, Union

import discord
import sources.text.cogrp as R
from back.ids import IDS, IDs
from back.tupper import Codes, Emote, TUPPER_LISTS, reLink
from back.utils import Fail, paginate
from discord.ext import commands

Ctx = commands.Context
_webhookName = "muOS Tupperhook"

class CogRoleplay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.listen: dict[int, Optional[int]] = {}
        self.timers: dict[int, dt.datetime] = {}
        self.webhooks: dict[int, discord.Webhook] = {}
    
    async def onReady(self):
        for channelID in IDS.getAll(IDs.rpChannels):
            channel: discord.TextChannel = await self.bot.fetch_channel(channelID)
            webhook: Optional[discord.Webhook] = None
            for webhook in await channel.webhooks():
                print(webhook.name)
                if webhook.name == _webhookName:
                    self.webhooks[channelID] = webhook
                    break
            if not self.webhooks.get(channelID):
                self.webhooks[channelID] = await channel.create_webhook(name=_webhookName)
    
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
            res = TUPPER_LISTS.match(message.author.id, message.content)
            if not isinstance(res, tuple): return
            tupper, emote = res

            await message.delete()
            content: str = message.content
            content = content.removeprefix(emote.getPrefix()).removesuffix(emote.getSuffix())
            webhook = self.webhooks[message.channel.id]
            await webhook.send(content, username=tupper.getName(), avatar_url=emote.getURL())
    
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