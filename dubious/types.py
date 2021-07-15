
from typing import Optional, TypedDict
from dubious.raw import RawApplication, RawGuild, RawMessage, RawRole, RawSnowflake, RawUser

class Snowflake:
    def __init__(self, raw: RawSnowflake):
        self.id = int(raw)
        self.timestamp = (self.id >> 22) + 1420070400000
        self.workerID = (self.id & 0x3E0000) >> 17
        self.processID = (self.id & 0x1F000) >> 12
        self.increment = self.id & 0xFFF
    
    def __repr__(self):
        return self.id
    
    def __str__(self) -> str:
        return str(self.id)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Snowflake):
            return False
        return o.id == self.id

class IDable:
    def __init__(self, raw: dict):
        self.id = Snowflake(raw["id"])

class User(IDable):
    def __init__(self, raw: RawUser):

        super().__init__(raw)

        self.username = raw["username"]
        self.discriminator = raw["discriminator"]
        self.avatar = raw["avatar"]

        self.isBot = raw.get("bot")
        self.system = raw.get("system")

class Role(IDable):
    def __init__(self, raw: RawRole):

        super().__init__(raw)

        self.name = raw["name"]
        self.color = raw["color"]
        self.hoist = raw["hoist"]
        self.position = raw["position"]
        self.permissions = raw["permissions"]
        self.managed = raw["managed"]
        self.mentionable = raw["mentionable"]

class Guild(IDable):
    def __init__(self, raw: RawGuild):

        super().__init__(raw)

        self.name = raw["name"]
        self.ownerID = raw["owner_id"]
        self.roles = raw["roles"]
        self.systemChannelID = raw["system_channel_id"]
        
        self.ownerID = Snowflake(self.ownerID)
        self.roles = [Role(rawRole) for rawRole in self.roles]
        self.systemChannelID = Snowflake(self.systemChannelID) if self.systemChannelID else self.systemChannelID

class Message(IDable):
    def __init__(self, raw: RawMessage):

        super().__init__(raw)

        self.channelID = raw["channel_id"]
        self.author = raw["author"]
        self.content = raw["content"]
        self.timestamp = raw["timestamp"]
        self.lastEditTimestamp = raw["edited_timestamp"]
        self.attachments = raw["attachments"]
        self.embeds = raw["embeds"]
        self.type = raw["type"]

        self.webhookID = raw.get("webhook_id")

        self.channelID = Snowflake(self.channelID)
        self.webhookID = Snowflake(self.webhookID)