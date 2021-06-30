

from typing import Callable
from back.jdict import JDict, JObj
import re
import discord
from discord.ext import commands
import json

Ctx = commands.Context


_rawNPC = tuple[str, str, str, str]

class NPC(JObj[_rawNPC]):
    _prefix: Callable[[str], str] = lambda name: f"npc {name.lower()}"

    name: str
    image: str
    descShort: str
    descLong: str
    
    def build(self, raw: _rawNPC):
        self.name, self.image = raw

    def serialize(self):
        return (self.name, self.image)#, self.descShort, self.descLong)
    
    def getName(self): return self.name
    def getImage(self): return self.image

    def setImage(self): return self.image

    def removePrefixFrom(self, text: str):
        return text.removeprefix(NPC._prefix(self.name))

class NPCList(JDict[str, NPC]):
    path = "./sources/npcs.json"
    jObjClass = NPC
    
    def match(self, text: str):
        for name in self.d:
            if text.lower().startswith(NPC._prefix(name)):
                return self.get(name)
    
    def add(self, name: str, image: str):
        if self.get(name):
            return False
        newNPC = NPC((
            name, image
        ))
        self.d[name.lower()] = newNPC
        self.dump()
        return newNPC
    
    def remove(self, name: str):
        if not self.get(name):
            return False
        removed = self.d.pop(name)
        self.dump()
        return removed
    
    def changeImage(self, name: str, image: str):
        npc = self.get(name)
        if not npc:
            return False
        npc.setImage(image)
        self.dump()

try:
    with open(NPCList.path, "r") as f:
        NPC_LIST = NPCList(json.load(f))
except FileNotFoundError:
    with open(NPCList.path, "x") as f:
        f.write("{}")
        NPC_LIST = NPCList({})