
from dubious.raw import RawApplication, RawSnowflake, RawUser


class Snowflake:
    def __init__(self, raw: RawSnowflake):
        self.value = int(raw)
        self.timestamp = (self.value >> 22) + 1420070400000
        self.workerID = (self.value & 0x3E0000) >> 17
        self.processID = (self.value & 0x1F000) >> 12
        self.increment = self.value & 0xFFF

class User:
    def __init__(self, raw: RawUser):
        print(f"making user from {raw}")
        self.id = Snowflake(raw["id"])
        print("made id")
        self.username = raw["username"]
        self.discriminator = raw["discriminator"]
        self.avatar = raw["avatar"]
        self.isBot = raw["bot"]
        self.usesTwoFactor = raw["mfa_enabled"]
        self.isVerified = raw["verified"]
        self.email = raw["email"]
        self.flags = raw["flags"]
        
        self.system = raw["system"]
        self.locale = raw["locale"]
        self.premiumType = raw["premium_type"]
        self.publicFlags = raw["public_flags"]

class Application:
    def __init__(self, raw: RawApplication):
        self.id = Snowflake(raw["id"])
        self.name = raw["name"]
        self.icon = raw["icon"]
        self.description = raw["description"]
        self.isPublic = raw["bot_public"]
        self.requiresAuth = raw["bot_require_code_grant"]
        self.owner = User(raw["owner"])
