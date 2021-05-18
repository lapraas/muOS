
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

import json

class JIDS:
    rpChannels: set[int]
    def __init__(self, j: dict[str, set[int]]):
        self.j = j
    
    @classmethod
    def fromJson(cls, raw):
        j = {}
        for setName in raw:
            if setName in cls.__dict__:
                pass
            j[setName] = set(j[setName])
        return cls(j)
    
    def _rpChannels(self):
        if not JIDS.rpChs in self.j: self.j[JIDS.rpChs] = set()
        return self.j[JIDS.rpChs]
    
    def addRPChannel(self, chID: int):
        if not self.j[JIDS.rpChs]: self.j[JIDS.rpChs] = set()
        if chID in self.j[JIDS.rpChs]: return False
        self.j

with open("./sources/ids.json", "r") as f:
    _J = json.load(f)
    RP_CHANNELS = set(_J["rp-channels"])

def addRPChannel(chID: int):
    if chID in RP_CHANNELS:
        return False
    RP_CHANNELS.add(chID)
    with open("./sources/ids.json", "w") as f:
        json.dump(_J, f)
    return True

def removeRPChannel(chID: int):
    if not chID in RP_CHANNELS:
        return False
    RP_CHANNELS.discard(chID)
    return True