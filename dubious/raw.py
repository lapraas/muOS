
from typing import NamedTuple, Optional, TypedDict

Payload = TypedDict("Payload", {
    "op": int,
    "t": Optional[str],
    "d": dict
})

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
RawUnavailableGuild = TypedDict("RawUnavailableGuild", {
    "id": RawSnowflake, "available": bool
})

RawHello = TypedDict("RawHello", {
    "heartbeat_interval": int,
    "_trace": list[str]
})
RawReady = TypedDict("RawReady", {
    "v": int,
    "user": RawUser,
    "guilds": list[RawUnavailableGuild],
    "session_id": str,
    "shard": Optional[tuple[int, int]],
    "application": RawApplication
})