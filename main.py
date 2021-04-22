
from typing import Union
import datetime as dt
import discord
from discord.ext import commands, tasks
import os

from sources.general import BOT_PREFIX, MENTION_ME
from utils import Fail, getRandomAvatarImageAndTime, handlePaginationReaction
from Help import Help

def determinePrefix(bot: commands.Bot, message: discord.Message):
    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith(BOT_PREFIX):
            return BOT_PREFIX
        return ""
    else:
        return BOT_PREFIX

client = commands.Bot(
    command_prefix=determinePrefix,
    case_insensitive=True,
    help_command=Help(verify_checks=False)
)

@tasks.loop(hours=24 * 2)
async def changeAvatar():
    print("Changing avatar")
    return
    im = getRandomAvatarImageAndTime()
    await client.user.edit(avatar=im)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}.")
    now = dt.datetime.today()
    then = now.replace(day=now.day + now.day % 2, hour=0, minute=0, second=0, microsecond=0)
    changeAvatar.next_iteration = then

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    
    await client.process_commands(message)

@client.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.User, discord.Member]):
    if user.bot: return
    await handlePaginationReaction(reaction, user)

@client.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    toRaise = None
    toSend = ""
    if isinstance(error, commands.MissingRequiredArgument):
        toSend += f"You missed a required argument `{error.param.name}`."
    elif isinstance(error, commands.BadUnionArgument):
        toSend += f"There was an error converting the argument `{error.param.name}`."
    elif isinstance(error, commands.CommandNotFound):
        toSend += f"This command does not exist!"
    elif isinstance(error, commands.CommandInvokeError):
        error: Exception = error.original
        if isinstance(error, Fail):
            toSend += error.message
        else:
            toSend += f"An unexpected error occurred. Please let {MENTION_ME} know."
            toRaise = error
    else:
        toSend += f"An unexpected error occurred. Please let {MENTION_ME} know."
        toRaise = error
    toSend += f"\nIf you need help with this command, please use `{BOT_PREFIX}help {ctx.command.name}`."
    await ctx.send(toSend)
    if toRaise:
        raise toRaise

@client.check
async def globalCheck(ctx: commands.Context):
    channelName = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else "DM"
    print(f"[{str(dt.datetime.now().time())[:-7]}, #{channelName}] {ctx.message.author.name}: {ctx.message.content}")
    return True

client.run(os.getenv("DISCORD_SECRET_BRONZOS"))