
from typing import Optional, TypedDict
from dubious.raw import RawApplication, RawGuild, RawMessage, RawRole, RawSnowflake, RawUser

class Snowflake:
    def __init__(self, raw: RawSnowflake):
        self.value = int(raw)
        self.timestamp = (self.value >> 22) + 1420070400000
        self.workerID = (self.value & 0x3E0000) >> 17
        self.processID = (self.value & 0x1F000) >> 12
        self.increment = self.value & 0xFFF
    
    def __repr__(self):
        return self.value
    
    def __hash__(self):
        return hash(self.value)
    
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Snowflake):
            return False
        return o.value == self.value

class User:
    def __init__(self, raw: RawUser):
        self.id = raw["id"]
        self.username = raw["username"]
        self.discriminator = raw["discriminator"]
        self.avatar = raw["avatar"]

        self.isBot = raw.get("bot")
        self.system = raw.get("system")

        self.id = Snowflake(self.id)

class Role:
    def __init__(self, raw: RawRole):
        
        self.id = raw["id"]
        self.name = raw["name"]
        self.color = raw["color"]
        self.hoist = raw["hoist"]
        self.position = raw["position"]
        self.permissions = raw["permissions"]
        self.managed = raw["managed"]
        self.mentionable = raw["mentionable"]

        self.id = Snowflake(self.id)

class Guild:
    def __init__(self, raw: RawGuild):

        self.id = raw["id"]
        self.name = raw["name"]
        self.ownerID = raw["owner_id"]
        self.roles = raw["roles"]
        self.systemChannelID = raw["system_channel_id"]

        self.id = Snowflake(self.id)
        self.ownerID = Snowflake(self.ownerID)
        self.roles = [Role(rawRole) for rawRole in self.roles]
        self.systemChannelID = Snowflake(self.systemChannelID) if self.systemChannelID else self.systemChannelID

class Message:
    def __init__(self, raw: RawMessage):

        self.id = raw["id"]
        self.channelID = raw["channel_id"]
        self.author = raw["author"]
        self.content = raw["content"]
        self.timestamp = raw["timestamp"]
        self.lastEditTimestamp = raw["edited_timestamp"]
        self.attachments = raw["attachments"]
        self.embeds = raw["embeds"]
        self.type = raw["type"]

        self.webhookID = raw.get("webhook_id")

        self.id = Snowflake(self.id)
        self.channelID = Snowflake(self.id)
        self.webhookID = Snowflake(self.webhookID)