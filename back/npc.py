

import re
import discord
from discord.ext import commands

Ctx = commands.Context

path = "./sources/npc.json"
defaultImage = "https://cdn.discordapp.com/attachments/797494897229430854/845347013583437845/transparent.png"

NPC = tuple[str, str]

class NPC:
    def __init__(self, name: str, image: str):
        self.name = name
        self.image = image
    
    def getName(self): return self.name
    def getImage(self): return self.image

    def setImage(self): return self.image

class NPCList:
    def __init__(self, raw: dict[str, tuple[str, str]]):
        self.npcs: dict[str, NPC] = raw
    
    def match(self, text: str):
        return self.npcs.get(text.lower())
    
    def add(self, name: str, image: str):
        if self.match(name):
            return False
        newNPC = NPC(name=name, image=image)
        self.npcs[name.lower()] = newNPC
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