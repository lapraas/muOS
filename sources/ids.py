
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
            if not name in self.__class__.__dict__:
                raise self.__class__._error(name)
            j[name] = set(j[name])
        self.j = j
    
    @classmethod
    def _error(cls, name: str):
        return JIDsKeyError(name, cls)

    def _write(self, idsFile: str="./source/ids.json"):
        with open(idsFile, "w") as f:
            json.dump(self.j, f)
    
    def add(self, to: str, value: Any):
        if not to in self.__class__.__annotations__:
            raise self._error(to)
        if value in self.j[to]:
            return False
        self.j[to].add(value)
        self._write()
        return True
    
    def remove(self, from: str, value: Any):
        if not from in self.__class__.__annotations__:
            raise self._error(from)
        if not value in self.j[from]:
            return False
        self.j[from].discard(value)
        self._write()
        return True

class IDs(IDLists):
    modRoles = "mod-roles"
    
    dmRoles = "dm-roles"
    rpChannels = "rp-channels"

with open("./sources/ids.json", "r") as f:
    IDS = IDs(json.load(f))