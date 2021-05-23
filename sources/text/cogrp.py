
from copy import deepcopy
from typing import Callable

from back.general import Cmd
from back.tupper import Emote, Tupper
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
            ❌ to delete them,
            ⏹️ to change their text to signify a scene break,
            ⏸ to change their text to signify a scene pause, and
            ▶️ to send a new message signifying a scene resume.
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
    ADD_LINK: Callable[[str, str], str] = lambda message, link: f"[{message}]({link})"

class ADD_TUPPER(Cmd,
    meta=[
        "addtupper", "register",
        f"""
            This command adds a new tupper with a given name and bracket.
            The format for this command is `[name]; [bracket](; [url])` where
            ```
                [name] is the desired name for the tupper,
                [bracket] is the desired set of brackets to trigger the tupper, and
                [url] is an optional link to a default profile picture for the tupper.
            ```
            `[name]` can't contain a semicolon.
            `[bracket]` must include the word `text` to specify what the tupper will say when it triggers.
            `[url]`, if present, must be a valid URL.
            
            Those with a DM role can add tuppers which are publicly available by prepending `public;` to the entry, before `[name]`.
        """
    ],
    usage=[
        "muOS; muOS:text",
        "Olvi; OB text",
        "Olvi Breloom; OB text",
        "Summer; <text>",
        "public; Clavis; Clavis: text"
    ]
):
    BAD_PUBLIC = "You don't have the role required to make a public tupper."
    TOO_FEW_ARGS: Callable[[int], str] = lambda args: f"This command was given too few (`{args}`) arguments."
    TOO_MANY_ARGS: Callable[[int], str] = lambda args: f"This command was given too many (`{args}`) arguments."
    BAD_URL: Callable[[str], str] = lambda url: f"The url `{url}` isn't a valid url."
    BAD_PREFIX: Callable[[str], str] = lambda prefix: f"The brackets `{prefix}` don't have `text` in them."

    SUCCESS: Callable[[Tupper], RawPages] = lambda tupper: FORMAT_TUPPER(f"Successfully added tupper **{tupper.getName()}**", tupper)
    FAIL: Callable[[str], str] = lambda name: f"Couldn't create a tupper named **{name}** because a tupper with that name already exists."
    FAIL_PUBLIC: Callable[[str], str] = lambda name: f"Couldn't create a public tupper named **{name}** because a public tupper with that name already exists."

class REMOVE_TUPPER(Cmd,
    meta=[
        "removetupper", "rmtupper", "delete",
        f"""
            This command removes a tupper with the given name. If you don't have a tupper with the given name, the command fails.

            Those with a DM role can remove tuppers which are publicly available.
        """
    ],
    usage=[
        "muOS",
        "Olvi Breloom"
    ]
):
    SUCCESS: Callable[[str], str] = lambda name: f"Successfully removed the tupper named **{name}**."

class GET_TUPPER(Cmd,
    meta=[
        "gettupper",
        f"""
            This command gets a tupper you own with the given name. If you don't have a tupper with the given name, this command fails.
        """
    ],
    usage=[
        "muOS",
        "Olvi Breloom"
    ]
):
    SUCCESS: Callable[[Tupper], RawPages] = lambda tupper: FORMAT_TUPPER(tupper.getName(), tupper)

class ADD_TUPPER_EMOTE(Cmd,
    meta=[
        "addtupperemote", "addemote",
        f"""
            This command adds an emote to a tupper. Emotes allow for one tupper to have different pictures, each triggered by different brackets.
            The format for this command is `[tupper name]; [name]; [bracket](; [url])` where
            ```
                [tupper name] is the name for the target tupper,
                [name] is the desired name for the emote,
                [bracket] is the desired set of brackets to trigger the emote, and
                [url] is an optional link to a default profile picture for the emote.
            ```
            `[tupper name]` must be a valid tupper name or the command will fail.
            `[name]` can't contain a semicolon.
            `[bracket]` must include the word `text` to specify what the tupper will say when it triggers.
            `[url]`, if present, must be a valid URL.

            Those with a DM role can add emotes to a public tupper.
        """
    ],
    usage=[
        "muOS; upside down; muOS (UD): text; https://cdn.discordapp.com/attachments/284520081700945921/845475853446152242/ag-muOS.png",
        "Olvi Breloom; sailing; OB S text; https://cdn.discordapp.com/attachments/284520081700945921/830335179729666068/image0.png"
    ]
):
    SUCCESS: Callable[[Tupper, Emote], RawPages] = lambda tupper, emote: FORMAT_TUPPER(f"Successfully added **{emote.getName()}** emote to **{tupper.getName()}**", tupper)

class REMOVE_TUPPER_EMOTE(Cmd,
    meta=[
        "removetupperemote", "rmtupperemote", "removeemote", "rmemote",
        f"""
            This command removes an emote from a tupper.
            The format for this command is `[tupper name]; [name]` where
            ```
                [tupper name] is the name of the tupper from which to remove the emote and
                [name] is the name of the emote to remove.
            ```
            `[tupper name]` must be a valid tupper name or the command will fail.
            `[name]` must be a valid emote for that tupper or the command will fail.
        """
    ],
    usage=[
        "muOS; upside down",
        "Olvi Breloom; sailing (lol this is canon)",
    ]
):
    SUCCESS: Callable[[str, str], str] = lambda tupper, emote: f"Successfully removed the emote **{emote}** from **{tupper}**."

class ADD_TUPPER_IMAGE(Cmd,
    meta=[
        "addtupperimage", "addtupperemoteimage", "addimage", "avatar", "settupperimage", "settupperemoteimage", "setimage",
        f"""
            This command sets the image for a tupper's emote. If no emote is specified, the default tupper image is set.
            The format for this command is `[tupper name]; [emote name]; [url]` where
            ```
                [tupper name] is the name of the tupper for which to update the emote,
                [emote name] is the name of the emote from that tupper to update, and
                [url] is a link to the desired image.
            ```
            `[tupper name]` must be a valid tupper name or the command will fail.
            `[emote name]` must be a valid emote for that tupper or the command will fail.
        """
    ],
    usage=[
        "muOS; upside down; https://cdn.discordapp.com/attachments/284520081700945921/845475853446152242/ag-muOS.png",
        "Olvi Breloom; sailing; https://cdn.discordapp.com/attachments/284520081700945921/830335179729666068/image0.png"
    ]
):
    SUCCESS: Callable[[str, str, str], str] = lambda tupper, emote, link: f"Successfully set the image for **{tupper}**'s emote **{emote}** to <{link}>."

def _formatEmote(emote: Emote, *, bold: bool=False):
    return (emote.getName() if not bold else f"**{emote.getName()}**", f"`{emote.getPrefix()}text here{emote.getSuffix()}`", True)
def FORMAT_TUPPER(title: str, tupper: Tupper):
    base: RawEmbed = {
        "title": title,
        "description": f"{'private' if not tupper.isPublic() else 'public'} tupper named `{tupper.getName()}`",
        "fields": [
            _formatEmote(prefix) for prefix in tupper.getEmotes()
        ]
    }
    pages: RawPages = []
    for i, selectedPrefix in enumerate(tupper.getEmotes()):
        page = deepcopy(base)
        page["fields"][i] = _formatEmote(selectedPrefix, bold=True)
        page["thumbnail"] = selectedPrefix.getURL()
        pages.append(page)
    return pages

class ERR:
    NOT_IN_RP_CHANNEL = "This command can't be used in a channel that's not for RP."
    NO_TUPPERS = "You don't have any tuppers registered with this bot."
    NOT_FOUND: Callable[[str], str] = lambda name: f"A tupper with the name **{name}** wasn't found."
    EMOTE_NOT_FOUND: Callable[[str, str], str] = lambda tupper, emote: f"An emote with the name **{emote}** wasn't found for the tupper named **{tupper}**."

class INFO:
    OTHER_USER = lambda message, oid: f"You can't alter posts other users have made. The message {message} belongs to <@{oid}>."
