
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

class PWU:
    ID = 546872429621018635

    class CHANNEL:
        MISC = 546881598189207583
        HUMOR = 547580983860396051
        BOT_SPAM = 555898099747389479
        PLAZA = 799018833364123668
    
    class ROLE:
        MOD = 550518609714348034
        JOKE_OWNER = 826971344834265128
    
    class EMOTE:
        AGONIZED_AXEW = "<:AgonizedAxew:698049607862714428>"
        LAUGHING_HENRY = "<:LaughingHenry:714352502358802455>"
        SEAN_DAB = "<:SeanDab:777619661285621774>"
        ANGRY_SLINK = "<:AngrySlink:749492163015999510>"
        ZANGOOSE_HUG = "<:ZangooseHug:731270215870185583>"

import json

with open("./sources/rpchannels.json", "r") as f:
    RP_CHANNELS = set(json.load(f))

def addRPChannel(chID: int):
    if chID in RP_CHANNELS:
        return False
    RP_CHANNELS.add(chID)
    with open("./sources/rpchannels.json", "w") as f:
        json.dump(list(RP_CHANNELS), f)
    return True

def removeRPChannel(chID: int):
    if not chID in RP_CHANNELS:
        return False
    RP_CHANNELS.discard(chID)
    return True