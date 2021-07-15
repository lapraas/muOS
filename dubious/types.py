
from typing import Generic, TypeVar

import dubious.http as http
from dubious.raw import  RawChannel, RawGuild, RawMessage, RawRole, RawSnowflake, RawUser


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
        self.raw = raw

        self.id = Snowflake(raw["id"])

T = TypeVar("T", bound="IDable")
class Cache(Generic[T]):
    def __init__(self, itemType: type[T], endpoint: str, size=1000):
        self.itemType = itemType
        self.endpoint = endpoint
        self.size = size

        self.items: dict[Snowflake, T] = {}
        self.earliest: list[Snowflake] = []
    
    def add(self, item: T):
        self.earliest.append(item.id)
        self.items[item.id] = item
        while len(self.items) > self.size:
            snowflake = self.earliest.pop(0)
            self.items.pop(snowflake)
        return item
    
    def get(self, snowflake: Snowflake):
        gotten = self.items.get(snowflake)
        if not gotten:
            j = http.req(f"{self.endpoint}/{snowflake}")
            gotten = self.add(self.itemType(j))
        return gotten

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
        self.webhookID = Snowflake(self.webhookID) if self.webhookID else self.webhookID

class Channel(IDable):
    TEXT = 0
    DM = 1
    VOICE = 2
    GROUP_DM = 3
    CATEGORY = 4
    NEWS = 5
    STORE = 6
    NEWS_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    STAGE = 13

    def __init__(self, raw: RawChannel):

        super().__init__(raw)

        self.type = raw["type"]

        # guild channels
        self.guildID = raw.get("guild_id")
        self.position = raw.get("position")
        self.name = raw.get("name")
        self.categoryID = raw.get("parent_id")

        # text channels
        self.topic = raw.get("topic")
        self.isNSFW = raw.get("nsfw")
        self.slowModeLimit = raw.get("rate_limit_per_user")
        
        # voice channels
        self.bitrate = raw.get("bitrate")
        self.userLimit = raw.get("userLimit")

        # DM channels
        self.recipients = raw.get("recipients")
        self.icon = raw.get("icon")
        self.ownerID = raw.get("owner_id")
        self.applicationID = raw.get("application_id")