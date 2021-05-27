
from copy import deepcopy
from typing import Callable

from back.general import Cmd
from back.utils import RawEmbed, RawPages


class COG:
    NAME = "Roleplay Cog"
    DESC = "A cog that offers various different utility functions to help with roleplaying."

_scene = lambda description, color=None: {
    "description": description,
    "color": color if color else 0x000000
}
class SCENE(Cmd,
    meta=[
        "scene",
        f"""
            This command provides a standardized way to break / pause / resume scenes.

            React to messages created by this command with
            ❌ to delete them.
        """
    ],
    usage=[
        "break",
        "pause",
        "unpause",
        "resume"
    ]
):
    FAIL: Callable[[str], str] = lambda op: f"`{op}` isn't valid for this command."
    BREAK = "<><><><><><><><>"
    PAUSED = "(Scene paused)"
    RESUMED = "(Scene unpaused)"

class NEW_NPC(Cmd,
    meta=[
        "newnpc", "addnpc"
    ]
):
    BAD_ARGS: Callable[[int], str] = lambda leng: f"This command takes two semicolon-separated arguments (got {leng})."
    BAD_LINK = "The link given didn't match as a valid link."
    EXISTS: Callable[[str], str] = lambda name: f"A NPC with the name `{name}` already exists."

class ERR:
    NOT_IN_RP_CHANNEL = "This command can't be used in a channel that's not for RP."
    NO_TUPPERS = "You don't have any tuppers registered with this bot."
    NOT_FOUND: Callable[[str], str] = lambda name: f"A tupper with the name **{name}** wasn't found."
    EMOTE_NOT_FOUND: Callable[[str, str], str] = lambda tupper, emote: f"An emote with the name **{emote}** wasn't found for the tupper named **{tupper}**."

class INFO:
    OTHER_USER = lambda message, oid: f"You can't alter posts other users have made. The message {message} belongs to <@{oid}>."
