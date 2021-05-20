
import json
import re
from typing import Optional

import discord
from discord.ext import commands

Ctx = commands.Context

reLink = re.compile(r"(?!<)(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*))(?!>)")
path = "./sources/tupper.json"

_RawLink = Optional[str]
_RawPrefix = tuple[str, str, _RawLink]
_RawPrefixes = list[_RawPrefix]
_RawTupper = tuple[_RawPrefixes, bool]
_RawTupperList = dict[str, _RawTupper]
_RawTupperLists = dict[int, _RawTupperList]

class Prefix:
    def __init__(self, name: str, key: str, url: _RawLink):
        self.name = name
        self.key = key
        self.prefix, self.suffix = self.key.split("text")
        self.url = url
    
    def json(self):
        return (self.name, self.key, self.url)
    
    def match(self, text: str):
        return text.startswith(self.prefix) and text.endswith(self.suffix)

class Tupper:
    def __init__(self, ownerID: int, name: str, prefixes: _RawPrefixes, public: bool=False):
        self.ownerID = ownerID
        self.name = name
        self.prefixes = [Prefix(*key) for key in prefixes]
        self.public = public
    
    def json(self) -> _RawTupper:
        prefixes = [prefix.json() for prefix in self.prefixes]
        return (prefixes, self.public)
    
    def match(self, text: str):
        for prefix in self.prefixes:
            if prefix.match(text):
                return prefix

class TupperLists:
    def __init__(self, j: _RawTupperLists):
        self.tupperLists: dict[int, dict[str, Tupper]] = {}
        for uid in j:
            tupperList = j[uid]
            self.tupperLists[uid] = {}
            for name in tupperList:
                tupper = tupperList[name]
                self.tupperLists[uid][name] = Tupper(uid, name, *tupper)
    
    def _write(self):
        with open(path, "w") as f:
            json.dump(self.json(), f)
    
    def json(self):
        j: _RawTupperLists = {}
        for uid in self.tupperLists:
            tupperList = self.tupperLists[uid]
            j[uid] = {}
            for name in tupperList:
                tupper = tupperList[name]
                j[uid][name] = tupper.json()
        return j
    
    def add(self, uid: int, name: str, prefix: str):
        tupperList = self.tupperLists.get(uid)
        if tupperList:
            self.tupperLists[uid] = tupperList = {}
        if name in tupperList:
            return False
        tupperList[name] = Tupper(uid, name, [prefix, None])
        self._write()
        return tupperList[name]
    
    def remove(self, uid: int, name: str):
        tupperList = self.tupperLists.get(uid)
        if not tupperList or not not tupperList.get(name): return False
        tupper = tupperList.pop(name)
        self._write()
        return tupper
    
    def match(self, uid: int, text: str):
        tupperList = self.tupperLists.get(uid)
        if not tupperList: return None
        for tupperName in tupperList:
            tupper = tupperList[tupperName]
            prefix = tupper.match(text)
            if prefix: return prefix
        return None


with open(path, "r") as f:
    TUPPER_LISTS = TupperLists(json.load(f))