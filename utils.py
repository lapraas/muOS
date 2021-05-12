
import re
import discord
from discord.ext import commands
import json
import random
from typing import Optional, Union

from sources.general import EMPTY, GRAPHICS, MUOS_GRAPHIC_URL, stripLines
import sources.text as T

U = T.UTIL

class Fail(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

def getRandomAvatarImageAndTime():
    with open(U.PATHS.AVATAR_ROTATION, "r") as f:
        rotation: dict[str, list[tuple[str, str]]] = json.load(f)
    if not rotation.get("unused"):
        rotation["unused"] = list(U.PATHS.AVATARS.items())
    if rotation.get("current") in rotation["unused"]:
        rotation["unused"].remove(rotation.get("current"))

    path = random.choice(rotation["unused"])
    rotation["unused"].remove(path)
    rotation["current"] = path
    with open(U.PATHS.AVATAR_ROTATION, "w") as f:
        json.dump(rotation, f)
    with open(path[1], "rb") as im:
        return im.read()

dashPat = re.compile(r"-")
spacePat = re.compile(r"\s+")
ePat = re.compile(r"e")
def shuffleWord(word):
    alphabet = "qwertyuiopasdfghjklzxcvbnm"
    alphanum = "1234567890qwertyuiopasdfghjklzxcvbnm"
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    shuffles = set(deletes + transposes + replaces + inserts)
    for w in ["".join(let for let in shuffle if let in alphanum) for shuffle in shuffles]: shuffles.add(w)
    for w in [re.sub(dashPat, " ", shuffle) for shuffle in shuffles]: shuffles.add(w)
    for w in [re.sub(spacePat, "-", shuffle) for shuffle in shuffles]: shuffles.add(w)
    for w in [re.sub(ePat, "\u00e9", shuffle) for shuffle in shuffles]: shuffles.add(w) # accented e (for flabebe)
    return shuffles

def getEmbed(title: str, description: str=None, fields: list[Union[tuple[str, str], tuple[str, str, bool]]]=None, imageURL: str=None, footer=None, url=None, thumbnail=None):
    """ Creates a custom embed. """
    
    if not description: description = ""
    if not fields: fields = []
    
    e = discord.Embed(
        title=title,
        description=stripLines(description),
        color=0xD67AE2,
    )
    if url:
        e.url = url
    if thumbnail:
        e.set_thumbnail(url=thumbnail)
    for field in fields:
        e.add_field(
            name=field[0],
            value=EMPTY if not len(field) >= 2 else field[1],
            inline=False if not len(field) == 3 else field[2]
        )
    if imageURL:
        e.set_image(url=imageURL)
    if footer:
        e.set_footer(text=footer)
    return e

def getMuOSEmbed(title: str, description: str=None, fields: list[Union[tuple[str, str], tuple[str, str, bool]]]=None, imageURL: str=None, footer=None, url=None, thumbnail=None):
    if not thumbnail: thumbnail = random.choice(GRAPHICS)
    e = getEmbed(title, description, fields, imageURL, footer, url, thumbnail)
    return e

class Page:
    def __init__(self, content: Optional[str]=None, embed: Optional[discord.Embed]=None):
        self.content = content
        self.embed = embed
    
    def dump(self):
        return {
            "content": self.content,
            "embed": self.embed
        }

class Paginator:
    def __init__(self, pages: list[Page], issuerID: int, ignoreIndex: bool):
        self.pages = pages
        self.issuerID = issuerID
        self.ignoreIndex = ignoreIndex
        
        self.length = len(self.pages)
        self.focused = 0
        self.locked = False
        self.numbers = False
        
        if not self.ignoreIndex:
            for i, page in enumerate(pages):
                if not page.embed:
                    page.embed = discord.Embed(
                        title=EMPTY,
                        description=U.paginationIndex(i + 1, self.length)
                    )
                else:
                    page.embed.set_footer(
                        text=U.paginationIndex(i + 1, self.length)
                    )
    
    def lock(self):
        self.locked = True
    
    def unlock(self):
        self.locked = False
    
    def getReactions(self, isDM: bool):
        reactions = []
        amLarg = self.length > len(U.indices)
        
        if self.numbers and not amLarg:
            reactions = U.indices[:self.length]
        else:
            reactions = U.arrows
        
        if not isDM and not amLarg:
            reactions.append(U.switches[int(self.numbers)])
        
        return reactions
    
    def refocus(self, emoji: str):
        if emoji == U.emojiFirst:
            self.focused = 0
        elif emoji == U.emojiPrior and self.focused > 0:
            self.focused -= 1
        elif emoji == U.emojiNext and self.focused < self.length - 1:
            self.focused += 1
        elif emoji == U.emojiLast:
            self.focused = self.length - 1
            
        elif emoji in U.indices:
            self.focused = U.indices.index(emoji)
        elif emoji in U.switches:
            # yes MasN this works how you think it does
            self.numbers = not self.numbers
        
        return self.getFocused()
    
    def getFocused(self):
        return self.pages[self.focused]
    

class DictPaginator(Paginator):
    pages: dict[str, list[Page]]

    def __init__(self, pages: dict[str, list[Page]], issuerID: int, startFocused: str):
        self.pages = pages
        self.issuerID = issuerID
        self.ignoreIndex = True

        self.focused = startFocused
        self.subFocused = 0
    
    def getReactions(self, _):
        reactions = self.pages.keys()
        if len(self.pages[self.focused]) > 1:
            reactions += U.smolArrows
        return reactions
    
    def refocus(self, emoji: str):
        if emoji in self.pages:
            self.focused = emoji
        elif emoji == U.emojiPrior and self.subFocused > 0:
            self.subFocused -= 1
        elif emoji == U.emojiNext and self.subFocused < len(self.pages[self.focused]):
            self.subFocused += 1
        
        return self.getFocused()
    
    def getFocused(self):
        return self.pages[self.focused][self.subFocused]


toListen: dict[int, Paginator] = {}
        
async def updatePaginatedMessage(message: discord.Message, user: discord.User, paginator: Paginator, emoji: Optional[str]=None):
    if not user.id == paginator.issuerID: return
    oldFocused = paginator.getFocused()
    if emoji:
        focused = paginator.refocus(emoji)
        if not oldFocused is focused:
            await message.edit(content=focused.content, embed=focused.embed)
    isDM = isinstance(message.channel, discord.DMChannel)
    if emoji in U.switches and not isDM:
        newReactions = paginator.getReactions(isDM)
        await message.clear_reactions()
        for reaction in newReactions:
            await message.add_reaction(reaction)
    elif emoji == None:
        newReactions = paginator.getReactions(isDM)
        for reaction in newReactions:
            await message.add_reaction(reaction)
        

async def paginate(ctx: commands.Context, contents: list[dict[str, Union[str, discord.Embed]]], ignoreIndex: bool=False):
    pages = []
    for page in contents:
        pages.append(Page(**page))
    if not pages:
        raise IndexError("No pages were given to the pagination function.")
    
    paginator = Paginator(pages, ctx.author.id, ignoreIndex)
    await sendPaginator(ctx, paginator)

async def paginateEmbeds(ctx: commands.Context, contents: list[dict[str, str]], ignoreIndex: bool=False):
    if not contents: raise IndexError("No embeds were given to the pagination function.")
    pages = []
    for page in contents:
        pages.append(Page(embed=getMuOSEmbed(**page)))
    
    paginator = Paginator(pages, ctx.author.id, ignoreIndex)
    await sendPaginator(ctx, paginator)

async def paginateDict(ctx: commands.Context, contents: dict[str, list[dict[str, str]]], startFocused = str):
    pages: dict[str, list[Page]] = {}
    for emoji in contents:
        pages[emoji] = []
        for page in contents[emoji]:
            pages[emoji].append(Page(embed=getMuOSEmbed(**page)))
    if not pages:
        raise IndexError("No pages were given to the pagination function.")
    
    paginator = DictPaginator(pages, ctx.author.id, startFocused)
    await sendPaginator(ctx, paginator)

async def sendPaginator(ctx: commands.Context, paginator: Paginator):
    focused = paginator.getFocused()
    message: discord.Message = await ctx.send(content=focused.content, embed=focused.embed)
    if len(paginator.pages) == 1: return
    toListen[message.id] = paginator
    await updatePaginatedMessage(message, ctx.author, paginator)

async def handlePaginationReaction(message: discord.Message, emoji: str, user: Union[discord.Member, discord.User]):
    if not message.id in toListen:
        return
    paginator = toListen[message.id]
    
    emoji = str(emoji)
    await updatePaginatedMessage(message, user, paginator, emoji)
    if not isinstance(message.channel, discord.DMChannel):
        await message.remove_reaction(emoji, user)
