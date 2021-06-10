
from back.utils import getEmojisFromText
from typing import Optional, Union
import discord
from discord.ext import commands
import json

_FORMAT = "%I:%M:%S%p, %b %d (%a), %Y"

class CogMisc(commands.Cog, **M.cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.votes: dict[int, dict[str, list[int]]] = {}
        with open("./sources/misc.json", "r") as f:
            self.channels: list[int] = json.load(f)
        with open(M.PATH.TZPREFS, "r") as f:
            self.tzprefs: dict[str, str] = json.load(f)
    
    async def handleVoteAdd(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        vote = self.votes.get(reaction.message.id)
        if not vote: return
        
        pEmoji = str(reaction.emoji)
        if not pEmoji in vote: await reaction.remove(user)
        
        for voteEmoji in vote:
            if user.id in vote[voteEmoji]:
                await reaction.remove(user)
                return
        vote[pEmoji].append(user.id)
    
    async def handleVoteRemove(self, messageID: int, pEmoji: discord.PartialEmoji, userID: int):
        vote = self.votes.get(messageID)
        if not vote: return
        
        pEmoji = str(pEmoji)
        
        if pEmoji in vote and userID in vote[pEmoji]:
            vote[pEmoji].remove(userID)
    
    @commands.command(**M.vote.meta)
    async def vote(self, ctx: commands.Context, *, voteText: Optional[str] = None):
        if not voteText:
            emojis = [M.emojiGreen, M.emojiRed]
        else:
            emojis = getEmojisFromText(voteText)

        vote: dict[str, list[str]] = {}
        for tEmoji in emojis:
            try:
                await ctx.message.add_reaction(tEmoji)
            except discord.HTTPException:
                await ctx.message.clear_reactions()
                await ctx.send(M.vote.emojiNotFound)
                return
            vote[tEmoji] = []
        
        self.votes[ctx.message.id] = vote