

import re
import discord
from discord.ext import commands
import json

Ctx = commands.Context

path = "./sources/npc.json"
defaultImage = "https://cdn.discordapp.com/attachments/797494897229430854/845347013583437845/transparent.png"

NPC = tuple[str, str]

class NPC:
    def __init__(self, name: str, image: str):
        self.name = name
        self.image = image
    
    def json(self):
        return (self.name, self.image)
    
    def getName(self): return self.name
    def getImage(self): return self.image

    def setImage(self): return self.image

class NPCList:
    def __init__(self, path: str, raw: dict[str, tuple[str, str]]):
        self.npcs: dict[str, NPC] = raw
    
    
    def match(self, text: str):
        return self.npcs.get(text.lower())
    
    def add(self, name: str, image: str):
        if self.match(name):
            return False
        newNPC = NPC(name=name, image=image)
        self.npcs[name.lower()] = newNPC
        _write()
        return newNPC
    
    def remove(self, name: str):
        npc = self.match(name)
        if not npc:
            return False
        return self.npcs.pop(npc)
    
    def changeImage(self, name: str, image: str):
        npc = self.match(name)
        if not npc:
            return False
        npc.setImage(image)
    
path = "./sources/npcs.json"
try:
    with open(path, "r") as f:
        NPC_LIST = NPCList(json.load(f))
except FileNotFoundError:
    with open(path, "x") as f:
        f.write("{}")
        NPC_LIST = NPCList({})

def _write():
    with open(path, "w") as f:
        json.dump(NPC_LIST, f)