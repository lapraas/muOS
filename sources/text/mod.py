
from back.general import Cmd

class COG:
    NAME = "Moderation Cog"
    DESCRIPTION = "This part of the bot has a few tools to make moderation easier."

_modRoleBlurb =  "roles that give people access to the moderative functions of this bot"
ADD_MOD_ROLE = Cmd(
    "addmodrole",
    f"""
        This command allows lapras to add {_modRoleBlurb}.
    """
)
RM_MOD_ROLE = Cmd(
    "rmmodrole",
    f"""
        This command allows lapras to remove {_modRoleBlurb}.
    """
)
_dmRoleBlurb =  "roles that give people access to the DM functions in this bot"
ADD_DM_ROLE = Cmd(
    "adddmrole",
    f"""
        This command allows moderators to add {_dmRoleBlurb}.
    """
)
RM_DM_ROLE = Cmd(
    "rmdmrole",
    f"""
        This command allows moderators to remove {_dmRoleBlurb}.
    """
)
_rpChannelBlurb = "channels to the list of the bot's recognized RP channels"
ADD_RP_CHANNEL = Cmd(
    "addrpchannel",
    f"""
        This command allows moderators to add {_rpChannelBlurb}.
    """
)
RM_RP_CHANNEL = Cmd(
    "rmrpchannel",
    f"""
        This command allows moderators to add {_rpChannelBlurb}
    """
)

_addChannel = lambda thing: lambda channel, success: (
    f"Successfuly added <#{channel}> as {thing}." if success else
    f"<#{channel}> is already registered as {thing}."
)
_rmChannel = lambda thing: lambda channel, success: (
    f"<#{channel}> is no longer registered as {thing}." if success else
    f"<#{channel}> was never registered as {thing}."
)
_addRole = lambda thing: lambda role, success: (
    f"Successfully added `{role}` as {thing}." if success else
    f"The role `{role}` is already registered as {thing}."
)
_rmRole = lambda thing: lambda role, success: (
    f"`{role}` is no longer registered as {thing}." if success else
    f"`{role}` was never registered as {thing}."
)

_modRole = "a moderator role"
_dmRole = "a DM role"
_rpChannel = "a RP channel"
class INFO:
    DELETED_MESSAGE = lambda authorID, deleterID, link: f"> Message from <@{authorID}> deleted by <@{deleterID}>:\n<{link}>"

    ADD_MOD_ROLE = _addRole(_modRole)
    RM_MOD_ROLE = _rmRole(_modRole)
    ADD_DM_ROLE = _addRole(_dmRole)
    RM_DM_ROLE = _rmRole(_dmRole)
    ADD_RP_CHANNEL = _addChannel(_rpChannel)
    RM_RP_CHANNEL = _rmChannel(_rpChannel)