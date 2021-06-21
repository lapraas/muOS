
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
        self.id = raw["id"]
        self.username = raw["username"]
        self.discriminator = raw["discriminator"]
        self.avatar = raw["avatar"]

        self.isBot = raw.get("bot")
        self.usesTwoFactor = raw.get("mfa_enabled")
        self.isVerified = raw.get("verified")
        self.email = raw.get("email")
        self.flags = raw.get("flags")
        self.system = raw.get("system")
        self.locale = raw.get("locale")
        self.premiumType = raw.get("premium_type")
        self.publicFlags = raw.get("public_flags")

        self.id = Snowflake(self.id)

class Application:
    def __init__(self, raw: RawApplication):

        self.id = raw["id"]
        self.name = raw["name"]
        self.icon = raw["icon"]
        self.description = raw["description"]
        self.isPublic = raw["bot_public"]
        self.requiresAuth = raw["bot_require_code_grant"]
        
        self.owner = raw.get("owner")

        self.id = Snowflake(self.id)
        self.owner = User(self.owner) if self.owner else None
