
from typing import Callable, Coroutine, Optional, TypedDict

from dubious.raw import RawGuild, RawPartialApplication, RawSnowflake, RawUnavailableGuild, RawUser

Payload = TypedDict("Payload", {
    "op": int,
    "t": Optional[str],
    "d": dict,
    "s": Optional[int]
})

class EVENT:
    onHello = "HELLO" # defines the heartbeat interval
    onReady = "READY" # contains the initial state information
    onResumed = "RESUMED" # response to Resume
    onReconnect = "RECONNECT" # server is going away, client should reconnect to gateway and resume
    onInvalidSession = "INVALID_SESSION" # failure response to Identify or Resume or invalid active session
    onApplicationCommandCreate = "APPLICATION_COMMAND_CREATE" # new Slash Command was created
    onApplicationCommandUpdate = "APPLICATION_COMMAND_UPDATE" # Slash Command was updated
    onApplicationCommandDelete = "APPLICATION_COMMAND_DELETE" # Slash Command was deleted
    onChannelCreate = "CHANNEL_CREATE" # new guild channel created
    onChannelUpdate = "CHANNEL_UPDATE" # channel was updated
    onChannelDelete = "CHANNEL_DELETE" # channel was deleted
    onChannelPinsUpdate = "CHANNEL_PINS_UPDATE" # message was pinned or unpinned
    # Threads can be thought of as temporary sub-channels inside an existing channel, to help better organize conversation in a busy channel.
    onThreadCreate = "THREAD_CREATE" # thread created, also sent when being added to a private thread
    onThreadUpdate = "THREAD_UPDATE" # thread was updated
    onThreadDelete = "THREAD_DELETE" # thread was deleted
    onThreadListSync = "THREAD_LIST_SYNC" # sent when gaining access to a channel, contains all active threads in that channel
    onThreadMemberUpdate = "THREAD_MEMBER_UPDATE" # thread member for the current user was updated
    onThreadMembersUpdate = "THREAD_MEMBERS_UPDATE" # some user(s) were added to or removed from a thread
    onGuildCreate = "GUILD_CREATE" # lazy-load for unavailable guild, guild became available, or user joined a new guild
    onGuildUpdate = "GUILD_UPDATE" # guild was updated
    onGuildDelete = "GUILD_DELETE" # guild became unavailable, or user left/was removed from a guild
    onGuildBanAdd = "GUILD_BAN_ADD" # user was banned from a guild
    onGuildBanRemove = "GUILD_BAN_REMOVE" # user was unbanned from a guild
    onGuildEmojisUpdate = "GUILD_EMOJIS_UPDATE" # guild emojis were updated
    onGuildIntegrationsUpdate = "GUILD_INTEGRATIONS_UPDATE" # guild integration was updated
    onGuildMemberAdd = "GUILD_MEMBER_ADD" # new user joined a guild
    onGuildMemberRemove = "GUILD_MEMBER_REMOVE" # user was removed from a guild
    onGuildMemberUpdate = "GUILD_MEMBER_UPDATE" # guild member was updated
    onGuildMembersChunk = "GUILD_MEMBERS_CHUNK" # response to Request Guild Members
    onGuildRoleCreate = "GUILD_ROLE_CREATE" # guild role was created
    onGuildRoleUpdate = "GUILD_ROLE_UPDATE" # guild role was updated
    onGuildRoleDelete = "GUILD_ROLE_DELETE" # guild role was deleted
    onGuildIntegrationCreate = "GUILD_INTERACTION_CREATE" # guild integration was created
    onGuildIntegrationUpdate = "GUILD_INTEGRATION_UPDATE" # guild integration was updated
    onGuildIntegrationDelete = "GUILD_INTEGRATION_DELETE" # guild integration was deleted
    onInteractionCreate = "INTERACTION_CREATE" # user used an interaction, such as a Slash Command
    onInviteCreate = "INVITE_CREATE" # invite to a channel was created
    onInviteDelete = "INVITE_DELETE" # invite to a channel was deleted
    onMessageCreate = "MESSAGE_CREATE" # message was created
    onMessageEdit = "MESSAGE_EDIT" # message was edited
    onMessageDelete = "MESSAGE_DELETE" # message was deleted
    onMessageDeleteBulk = "MESSAGE_DELETE_BULK" # multiple messages were deleted at once
    onMessageReactionAdd = "MESSAGE_REACTION_ADD" # user reacted to a message
    onMessageReactionRemove = "MESSAGE_REACTION_REMOVE" # user removed a reaction from a message
    onMessageReactionRemoveAll = "MESSAGE_REACTION_REMOVE_ALL" # all reactions were explicitly removed from a message
    onMessageReactionRemoveEmoji = "MESSAGE_REACTION_REMOVE_EMOJI" # all reactions for a given emoji were explicitly removed from a message
    onPresenceUpdate = "PRESENCE_UPDATE" # user was updated
    onStageInstanceCreate = "STAGE_INSTANCE_CREATE" # stage instance was created
    onStageInstanceDelete = "STAGE_INSTANCE_DELETE" # stage instance was deleted or closed
    onStageInstanceUpdate = "STAGE_INSTANCE_UPDATE" # stage instance was updated
    onTypingStart = "TYPING_START" # user started typing in a channel
    onUserUpdate = "USER_UPDATE" # properties about the user changed
    onVoiceStateUpdate = "VOICE_STATE_UPDATE" # someone joined, left, or moved a voice channel
    onVoiceServerUpdate = "VOICE_SERVER_UPDATE" # guild's voice server was updated
    onWebhooksUpdate = "WEBHOOKS_UPDATE" # guild channel webhook was created, update, or deleted

class HandlesEvents:
    handlers: dict[int, Callable[[Payload], Coroutine]]

    def __init__(self):
        self.handlers = {}
        for attrName in dir(self):
            attr = self.__getattribute__(attrName)
            if not callable(attr): continue
            if attrName in EVENT.__dict__:
                self.handlers[EVENT.__dict__[attrName]] = attr
    
    def getHandler(self, t: str):
        if not t in EVENT.__dict__.values():
            raise Exception(f"{t} is not a valid event.")
        return self.handlers.get(t)

class Hello(TypedDict):
    heartbeat_interval: int
    _trace: list[str]

class Ready(TypedDict):
    v: int
    user: RawUser
    guilds: list[RawUnavailableGuild]
    session_id: str
    shard: Optional[tuple[int, int]]
    application: RawPartialApplication

Resumed = type(None)
Reconnect = type(None)
InvalidSession = bool

####
# Gateway
####

class GuildCreate(RawGuild):
    pass

class MessageCreate(TypedDict):
    pass

####
# HTTP
####

class GetCurrentUserGuilds():
    id: RawSnowflake
    name: str
    icon: str
    owner: bool
    permissions: str
    features: list[str]
