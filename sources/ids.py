
from __future__ import annotations
import json
from typing import Any, Type

MY_USER_ID = 194537964657704960

BRONZOS_USER_ID = 824105108132200468
BRONZOS_BETA_USER_ID = None
BOT_USER_IDS = [BRONZOS_USER_ID, BRONZOS_BETA_USER_ID]

LOG_CHANNEL_IDS = {
    827334108094005248: 837505731258613790
}

class TEST:
    ID = 798023066718175252

    class CHANNEL:
        TEST = 799830678912499752
    
    class ROLE:
        MOD = 804128653687783424

class IOA:
    ID = 827334108094005248

    class ROLE:
        MOD = 827339658282270800
        DM = 828822110372757575

class JIDsKeyError(KeyError):
    def __init__(self, name: str, cls: Type[IDLists]) -> None:
        super().__init__(f"Name {name} did not match any variables for the class {cls}")

class IDLists:
    def __init__(self, j: dict[str, set[int]]):
        for name in j:
            self._check(name)
            j[name] = set(j[name])
        for cVarName in self.__class__.__dict__:
            cVar = self.__class__.__dict__[cVarName]
            if isinstance(cVar, str):
                if not j.get(cVar):
                    j[cVar] = set()
        self.j = j
    
    @classmethod
    def _error(cls, name: str):
        return JIDsKeyError(name, cls)
    
    def _check(self, target: str):
        if not target in [s for s in self.__class__.__dict__.values() if isinstance(s, str)]:
            raise self.__class__._error(target)

    def _write(self, idsFile: str="./sources/ids.json"):
        j = {}
        for jName in self.j:
            jVal = self.j[jName]
            j[jName] = list(jVal)
        with open(idsFile, "w") as f:
            json.dump(j, f)
    
    def getAll(self, target):
        self._check(target)
        return self.j[target]
        
    def check(self, target: str, value: int):
        self._check(target)
        return value in self.j[target]
    
    def add(self, target: str, value: int):
        self._check(target)
        if self.check(target, value):
            return False
        self.j[target].add(value)
        self._write()
        return True
    
    def remove(self, target: str, value: int):
        self._check(target)
        if not self.check(target, value):
            return False
        self.j[target].discard(value)
        self._write()
        return True

class IDs(IDLists):
    modRoles = "mod-roles"
    
    dmRoles = "dm-roles"
    rpChannels = "rp-channels"

with open("./sources/ids.json", "r") as f:
    IDS = IDs(json.load(f))