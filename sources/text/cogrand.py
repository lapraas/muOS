
from sources.general import BOT_PREFIX as mew, Cmd

class COG:
    NAME = "Random Cog"
    DESC = "A cog that provides various ways to randomly generate numbers among other things."

class PATH:
    TABLES = "./sources/tables.json"

RANDOM = Cmd(
    "random", "rand", "r", "roll",
    f"""
        This is the base command for generating random things. See `{mew}help random` for ways to use this command.
    """
)
DICE = Cmd(
    "dice", "roll",
    f"""
        This command simulates a dice roll. Given a number of dice and a number of sides, it rolls that many die with that many sides.
    """,
    usage=[
        "4d6",
        "1d20"
    ]
)

class ERR:
    INVALID_SUBCOMMAND = lambda args: f"The entry `{args}` is invalid."
    BAD_DICE_FORMAT = lambda arg: f"The entry `{arg}` isn't a valid die. Format it like `4d6`, where `4` is the dice count and `6` is the number of sides on each die."

class INFO:
    ROLL = lambda rolls: "\n".join([f"{arg}: {', '.join(rolls[arg])}" for arg in rolls])