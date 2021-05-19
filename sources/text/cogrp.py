
from sources.general import Cmd, BOT_PREFIX as mew

class COG:
    NAME = "Roleplay Cog"
    DESC = "A cog that offers various different utility functions to help with roleplaying."

ADD_RP_CHANNEL = Cmd(
    "addrpchannel",
    f"""
        This command allows moderators to add RP channels to the bot's list of valid RP channels.
    """
)

SCENE = Cmd(
    "scene",
    f"""
        This command provides a standardized way to break / pause / resume scenes.
        React to messages created by this command with ❌ to clear them, ⏸ to change their text to signify a scene pause, and ▶️ to send a new message signifying a scene resume.
    """,
    usage=[
        "pause",
        "hold",
        "unpause",
        "resume"
    ]
)

class ERR:
    NOT_IN_RP_CHANNEL = "This command can't be used in a channel that's not for RP."

class INFO:
    SCENE_BREAK = "<><><><><>"
    SCENE_PAUSED = "(Scene paused)"
    SCENE_RESUMED = "(Scene unpaused)"
    OTHER_USER = lambda message, oid: f"You can't alter posts other users have made. The message {message} belongs to <@{oid}>."
    ADD_RP_CHANNEL_SUCCESS = lambda channel: f"Successfully added <#{channel}> as a RP channel"