
from types import MethodType
from typing import Callable, Coroutine, NamedTuple, Optional, TypedDict, Union

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
    onChannelCreate = "ON_CHANNEL_CREATE" # new guild channel created
    onChannelUpdate = "ON_CHANNEL_UPDATE" # channel was updated
    onChannelDelete = "ON_CHANNEL_DELETE" # channel was deleted
    onChannelPinsUpdate = "ON_CHANNEL_PINS_UPDATE" # message was pinned or unpinned
    # Threads can be thought of as temporary sub-channels inside an existing channel, to help better organize conversation in a busy channel.
    onThreadCreate = "ON_THREAD_CREATE" # thread created, also sent when being added to a private thread
    onThreadUpdate = "ON_THREAD_UPDATE" # thread was updated
    onThreadDelete = "ON_THREAD_DELETE" # thread was deleted
    onThreadListSync = "ON_THREAD_LIST_SYNC" # sent when gaining access to a channel, contains all active threads in that channel
    onThreadMemberUpdate = "ON_THREAD_MEMBER_UPDATE" # thread member for the current user was updated
    onThreadMembersUpdate = "ON_THREAD_MEMBERS_UPDATE" # some user(s) were added to or removed from a thread
    onGuildCreate = "ON_GUILD_CREATE" # lazy-load for unavailable guild, guild became available, or user joined a new guild
    onGuildUpdate = "ON_GUILD_UPDATE" # guild was updated
    onGuildDelete = "ON_GUILD_DELETE" # guild became unavailable, or user left/was removed from a guild
    onGuildBanAdd = "ON_GUILD_BAN_ADD" # user was banned from a guild
    onGuildBanRemove = "ON_GUILD_BAN_REMOVE" # user was unbanned from a guild
    onGuildEmojisUpdate = "ON_GUILD_EMOJIS_UPDATE" # guild emojis were updated
    onGuildIntegrationsUpdate = "ON_GUILD_INTEGRATIONS_UPDATE" # guild integration was updated
    onGuildMemberAdd = "ON_GUILD_MEMBER_ADD" # new user joined a guild
    onGuildMemberRemove = "ON_GUILD_MEMBER_REMOVE" # user was removed from a guild
    onGuildMemberUpdate = "ON_GUILD_MEMBER_UPDATE" # guild member was updated
    onGuildMembersChunk = "ON_GUILD_MEMBERS_CHUNK" # response to Request Guild Members
    onGuildRoleCreate = "ON_GUILD_ROLE_CREATE" # guild role was created
    onGuildRoleUpdate = "ON_GUILD_ROLE_UPDATE" # guild role was updated
    onGuildRoleDelete = "ON_GUILD_ROLE_DELETE" # guild role was deleted
    onGuildIntegrationCreate = "ON_GUILD_INTERACTION_CREATE" # guild integration was created
    onGuildIntegrationUpdate = "ON_GUILD_INTEGRATION_UPDATE" # guild integration was updated
    onGuildIntegrationDelete = "ON_GUILD_INTEGRATION_DELETE" # guild integration was deleted
    onInteractionCreate = "ON_INTERACTION_CREATE" # user used an interaction, such as a Slash Command
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

RawSnowflake = str
RawUser = TypedDict("RawUser", {
    "id": RawSnowflake, "username": str, "discriminator": str, "avatar": str,
    "bot": Optional[bool], "system": Optional[bool], "mfa_enabled": Optional[bool], "locale": Optional["str"], "verified": Optional[bool], "email": Optional[str], "flags": Optional[int], "premium_type": Optional[int], "public_flags": Optional[int]
})
RawTeam = TypedDict("RawTeam", {

})
RawApplication = TypedDict("RawApplication", {
    "id": RawSnowflake, "name": str, "icon": str, "description": str, "bot_public": bool, "bot_require_code_grant": bool, "owner": RawUser, "summary": str, "verify_key": str, "team": RawTeam, "flags": int,
    "rpc_origins": Optional[list[str]], "terms_of_service_url": Optional[str], "privacy_policy_url": Optional[str], "guild_id": Optional[RawSnowflake], "primary_sku_id": Optional[RawSnowflake], "slug": Optional[str], "cover_image": Optional[str]
})
UnavailableGuild = TypedDict("RawUnavailableGuild", {
    "id": RawSnowflake, "available": bool
})

Hello = TypedDict("RawHello", {
    "heartbeat_interval": int,
    "_trace": list[str]
})
Ready = TypedDict("RawReady", {
    "v": int,
    "user": RawUser,
    "guilds": list[UnavailableGuild],
    "session_id": str,
    "shard": Optional[tuple[int, int]],
    "application": RawApplication
})