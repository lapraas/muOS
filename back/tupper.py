
from enum import Enum
import json
import re
from typing import Optional

import discord
from discord.ext import commands

Ctx = commands.Context

reLink = re.compile(r"(?!<)(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*))(?!>)")
path = "./sources/tupper.json"

_RawLink = Optional[str]
_RawEmote = tuple[str, str, _RawLink]
_RawEmotes = list[_RawEmote]
_RawTupper = tuple[_RawEmotes, bool]
_RawTupperList = dict[str, _RawTupper]
_RawTupperLists = dict[int, _RawTupperList]

class Emote:
    DEFAULT = "default"
    def __init__(self, name: str, key: str, url: _RawLink):
        self.name = name
        self.key = key
        self.prefix, self.suffix = self.key.split("text")
        self.url = url
    
    def getName(self): return self.name
    def getPrefix(self): return self.prefix
    def getSuffix(self): return self.suffix
    def getURL(self): return self.url
    
    def json(self):
        return (self.name, self.key, self.url)
    
    def match(self, text: str):
        return text.startswith(self.prefix) and text.endswith(self.suffix)

class Tupper:
    def __init__(self, ownerID: int, name: str, emotes: _RawEmotes, public: bool=False):
        self.ownerID = ownerID
        self.name = name
        self.emotes = [Emote(*key) for key in emotes]
        self.public = public
    
    def getOwnerID(self): return self.ownerID
    def getName(self): return self.name
    def isPublic(self): return self.public
    def getEmote(self, name=Emote.DEFAULT):
        for emote in self.emotes:
            if emote.name == name:
                return emote
    def getEmotes(self): return self.emotes
    
    def json(self) -> _RawTupper:
        emotes = [emote.json() for emote in self.emotes]
        return (emotes, self.public)
    
    def match(self, text: str):
        for emote in self.emotes:
            if emote.match(text):
                return emote

class Codes(Enum):
    """ List of codes for TupperLists. """
    EXISTS = 10
    EXISTS_PUBLIC = 11
    NO_TUPPERS = 20
    NOT_FOUND = 30


class TupperLists:
    def __init__(self, j: _RawTupperLists):
        self.tupperLists: dict[int, dict[str, Tupper]] = {}
        for uid in j:
            tupperList = j[uid]
            self.tupperLists[int(uid)] = {}
            for name in tupperList:
                tupper = tupperList[name]
                self.tupperLists[int(uid)][name] = Tupper(int(uid), name, *tupper)
    
    def _write(self):
        with open(path, "w") as f:
            json.dump(self.json(), f)
    
    def json(self):
        j: _RawTupperLists = {}
        for uid in self.tupperLists:
            tupperList = self.tupperLists[uid]
            j[str(uid)] = {}
            for name in tupperList:
                tupper = tupperList[name]
                j[str(uid)][name] = tupper.json()
        return j
    
    def getAllPublic(self):
        """ Retrieves all of the registered public tuppers. """
        public: dict[str, Tupper] = {}
        for uid in self.tupperLists:
            tupperList = self.tupperLists[uid]
            for tupper in tupperList.values():
                if tupper.isPublic():
                    public[tupper.name] = tupper
        return public
        
    def add(self, uid: int, name: str, prefix: str, public: bool, url: Optional[str]=None):
        """ Create and add a tupper with the given info.
            Assumes the URL, if existent, is a valid URL. """
        tupperList = self.tupperLists.get(uid)
        if not tupperList: self.tupperLists[uid] = tupperList = {}
        if name in tupperList: return Codes.EXISTS
        if public:
            allPublic = self.getAllPublic()
            if name in allPublic:
                return Codes.EXISTS_PUBLIC

        tupperList[name] = Tupper(uid, name, [("default", prefix, url)], public)
        self._write()
        return tupperList[name]
        
    def remove(self, uid: int, name: str):
        """ Remove a tupper with the given name created by the given user. """
        tupperList = self.tupperLists.get(uid)
        if not tupperList: return Codes.NO_TUPPERS
        if not tupperList.get(name): return Codes.NOT_FOUND
        tupper = tupperList.pop(name)
        # if the tupper was the only one registered under this user, remove them from the list
        #  this makes Codes.NO_TUPPERS happen
        if not tupperList: self.tupperLists.pop(uid)
        self._write()
        return tupper
    
    def get(self, uid: int, name: str):
        """ Retrieve a tupper with the given name for the given user. """
        tupperList = self.tupperLists.get(uid)
        if not tupperList: return Codes.NO_TUPPERS
        if not tupperList.get(name): return Codes.NOT_FOUND
        return tupperList[name]
    
    def getPublic(self, name: str):
        """ Retrieve a public tupper with the given name. """
        for uid in self.tupperLists:
            tupperList = self.tupperLists[uid]
            if tupperList.get(name):
                return tupperList[name]
        return Codes.NOT_FOUND
    
    def match(self, uid: int, text: str):
        """ Match text against the prefixes for all tupper emotes, returning a emote if found. """
        tupperList = self.tupperLists.get(uid)
        if not tupperList: return Codes.NO_TUPPERS
        for tupperName in tupperList:
            tupper = tupperList[tupperName]
            emote = tupper.match(text)
            if emote: return emote
        allPublic = self.getAllPublic()
        for tupperName in allPublic:
            emote = allPublic[tupperName].match(text)
            if emote: return emote
        return Codes.NOT_FOUND

with open(path, "r") as f:
    TUPPER_LISTS = TupperLists(json.load(f))