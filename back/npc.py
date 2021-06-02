

from back.jdict import JDict, JObj
import re
import discord
from discord.ext import commands
import json

Ctx = commands.Context


_rawNPC = tuple[str, str, str, str]

class NPC(JObj[_rawNPC]):
    name: str
    image: str
    descShort: str
    descLong: str
    
    def build(self, raw: _rawNPC):
        self.name, self.image, self.descShort, self.descLong = raw

    def serialize(self):
        return (self.name, self.image, self.descShort, self.descLong)
    
    def getName(self): return self.name
    def getImage(self): return self.image

    def setImage(self): return self.image

class NPCList(JDict[str, NPC]):
    path = "./sources/npcs.json"
    jObjClass = NPC
    
    def match(self, text: str):
        return self.d.get(text.lower())
    
    def add(self, name: str, image: str):
        if self.match(name):
            return False
        newNPC = NPC(name=name, image=image)
        self.d[name.lower()] = newNPC
        self.dump()
        return newNPC
    
    def remove(self, name: str):
        npc = self.match(name)
        if not npc:
            return False
        removed = self.d.pop(name)
        self.dump()
        return removed
    
    def changeImage(self, name: str, image: str):
        npc = self.match(name)
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