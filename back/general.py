
from __future__ import annotations

import math
from typing import Callable, TypeVar, Union

import back.ids as IDS

BOT_PREFIX = "mew."

MENTION_ME = f"<@{IDS.MY_USER_ID}>"
EMPTY = "\u200b"
NEWLINE = "\n"

MUOS_GRAPHIC_URL = "https://cdn.discordapp.com/attachments/284520081700945921/834659148061736970/muOS-graphic.png"
MUOS_GRAPHIC_URL_2 = "https://cdn.discordapp.com/attachments/284520081700945921/835412740871946261/mu_alt.png"
MUOS_GRAPHIC_URL_3 = "https://cdn.discordapp.com/attachments/284520081700945921/835412799756173382/mu.png"
MUOS_GRAPHIC_URL_4 = "https://cdn.discordapp.com/attachments/284520081700945921/835413757353394206/mu_alt3.png"

GRAPHICS = [MUOS_GRAPHIC_URL]

stripLines = lambda text: "\n".join([line.strip() for line in text.split("\n")])
class Cmd:
    def __init_subclass__(cls, *, meta: list[str], usage: list[str]=None, parent: Cmd=None) -> None:
        cls.name: str = meta[0]
        cls.aliases: list[str] = meta[1:-1]
        cls.desc: Union[list[str], str] = meta[-1]
        cls.parent = parent
        cls.qualifiedName = cls.name
        if cls.parent:
            cls.qualifiedName = f"{parent.qualifiedName} {cls.qualifiedName}"
        
        if usage:
            cls.desc += "\n**Usage:**```\n" + "\n".join([f"{BOT_PREFIX}{cls.qualifiedName} {case}" for case in usage]) + "```"
        
        cls.desc = stripLines(cls.desc)
        
        cls.meta = {"name": cls.name, "aliases": cls.aliases, "help": cls.desc}
        cls.ref = f"{BOT_PREFIX}{cls.name}"
        cls.refF = f"`{cls.ref}`"

_FORMAT = "%I:%M:%S%p, %b %d (%a), %Y"
intable = lambda t: all([d in "1234567890-" for d in t])

def chunks(lst: list, n: int):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def evenChunks(lst: list, n: int=3):
    return chunks(lst, math.ceil(len(lst)/n))

RawField = Union[tuple[str, str], tuple[str, str, bool]]
RawDictPaginatorPage = list[dict[str, Union[str, list[RawField]]]]
RawDictPaginator = dict[str, RawDictPaginatorPage]

T = TypeVar("T")
def padItems(items: list[T], lenKey: Callable[[T], str], separator: str, rest: Callable[[T], str]):
    strs: list[str] = []
    maxLen = max(len(lenKey(item)) for item in items)
    for item in items:
        threshSpacing = " " * (maxLen - len(lenKey(item)))
        strs.append(f"{lenKey(item)}{separator}{threshSpacing}{rest(item)}")
    return strs
