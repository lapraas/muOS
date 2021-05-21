
from copy import deepcopy
from typing import Callable

from back.general import Cmd
from back.tupper import Emote, Tupper
from back.utils import RawEmbed, RawPages


class COG:
    NAME = "Roleplay Cog"
    DESC = "A cog that offers various different utility functions to help with roleplaying."

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
        "pause",
        "hold",
        "unpause",
        "resume"
    ]
):
    BREAK = "<><><><><>"
    PAUSED = "(Scene paused)"
    RESUMED = "(Scene unpaused)"

class ADD_TUPPER(Cmd,
    meta=[
        "addtupper", "register",
        f"""
            This command adds a new tupper with a given name and bracket.

            The format for this command is `[name]; [bracket]` where
                `[name]` is the desired name for the tupper and
                `[bracket]` is the desired set of brackets to trigger the tupper.
            `[name]` can't contain a semicolon.
            `[bracket]` must include the word `text` to specify what the tupper will say when it triggers.
            Those with DM roles can add tuppers which are publicly available by prepending `public;` to the entry, before `[name]`.
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
    TOO_FEW_ARGS: Callable[[int], str] = lambda args: f"This command was given too few (`{args}`, needs `4`) arguments."
    TOO_MANY_ARGS: Callable[[int], str] = lambda args: f"This command was given too many (`{args}`, needs `4`) arguments."
    BAD_URL: Callable[[str], str] = lambda url: f"The url `{url}` isn't a valid url."
    BAD_PREFIX: Callable[[str], str] = lambda prefix: f"The brackets `{prefix}` don't have `text` in them."

    SUCCESS: Callable[[Tupper], RawPages] = lambda tupper: FORMAT_TUPPER(f"Successfully added tupper **{tupper.getName()}**", tupper)
    FAIL: Callable[[str], str] = lambda name: f"Couldn't create a tupper named `{name}` because a tupper with that name already exists."
    FAIL_PUBLIC: Callable[[str], str] = lambda name: f"Couldn't create a public tupper named `{name}` because a public tupper with that name already exists."

class REMOVE_TUPPER(Cmd,
    meta=[
        "removetupper", "rmtupper", "delete",
        f"""
            This command removes a tupper with the given name. If you don't have a tupper with the given name, the command fails.
        """
    ],
    usage=[
        "muOS",
        "Olvi Breloom"
    ]
):
    SUCCESS: Callable[[str], str] = lambda name: f"Successfully removed the tupper named `{name}`."

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
        page["imageURL"] = selectedPrefix.getURL()
        pages.append(page)
    return pages

class ERR:
    NOT_IN_RP_CHANNEL = "This command can't be used in a channel that's not for RP."
    NO_TUPPERS = "You don't have any tuppers registered with this bot."
    NOT_FOUND: Callable[[str], str] = lambda name: f"A tupper with the name `{name}` wasn't found."

class INFO:
    OTHER_USER = lambda message, oid: f"You can't alter posts other users have made. The message {message} belongs to <@{oid}>."
