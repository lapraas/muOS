
from sources.general import Cmd

class COG:
    NAME = "Moderation Cog"
    DESCRIPTION = "This part of the bot has a few tools to make moderation easier."




ADD_RP_CHANNEL = Cmd(
    "addrpchannel",
    f"""
        This command allows moderators to add RP channels to the bot's list of valid RP channels.
    """
)

_addChannelSuccess = lambda thing: lambda channel: f"Successfuly added <#{channel}> as {thing}."
_addChannelFail = lambda thing: lambda channel: f"The channel <#{channel}> is already registered as {thing}."

_RPChannel = "a RP channel"
class INFO:
    DELETED_MESSAGE = lambda authorID, deleterID, link: f"> Message from <@{authorID}> deleted by <@{deleterID}>:\n<{link}>"

    ADD_RP_CHANNEL_SUCCESS = _addChannelSuccess(_RPChannel)
    ADD_RP_CHANNEL_FAIL = _addChannelFail(_RPChannel)