
from __future__ import annotations
from typing import Optional, TypedDict, Union

class PayloadData:
    def __init__(self):
        pass

RawSnowflake = str
class RawUser(TypedDict):
    # guaranteed
    id: RawSnowflake
    username: str
    discrimiator: str
    avatar: Optional[str]

    # not guaranteed
    bot: bool
    system: bool
    mfa_enabled: bool
    locale: str
    verified: bool
    email: Optional[str]
    flags: int
    premium_type: int
    public_flags: int

class RawTeam(TypedDict):
    pass

class RawPartialApplication(TypedDict):
    # guaranteed
    id: RawSnowflake
    flags: int

class RawApplication(TypedDict):
    # guaranteed
    id: RawSnowflake
    name: str
    icon: str
    description: str
    bot_public: bool
    bot_require_code_grant: bool
    summary: str
    verify_key: str
    team: RawTeam

    # not guaranteed
    rpc_origins: Optional[list[str]]
    terms_of_service_url: Optional[str]
    privacy_policy_url: Optional[str]
    owner: Optional[RawUser]
    guild_id: Optional[RawSnowflake]
    primary_sku_id: Optional[RawSnowflake]
    slug: Optional[str]
    cover_image: Optional[str]
    flags: int

class RawUnavailableGuild(TypedDict):
    # guaranteed
    id: RawSnowflake
    available: bool

class RawRoleTags(TypedDict):
    # not guaranteed
    bot_id: RawSnowflake
    integration_id: RawSnowflake
    premium_subscriber: None

class RawRole(TypedDict):
    # guaranteed
    id: RawSnowflake
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool

    #not guaranteed
    tags: RawRoleTags

class RawEmoji(TypedDict):
    # guaranteed
    id: Optional[RawSnowflake]
    name: Optional[str]

    # not guaranteed
    roles: list[RawSnowflake]
    user: RawUser
    required_colons: bool
    managed: bool
    animated: bool

class RawWelcomeScreenChannel(TypedDict):
    # guaranteed
    channel_id: RawSnowflake
    description: str
    emoji_id: Optional[RawSnowflake]
    emoji_name: Optional[RawSnowflake]

class RawWelcomeScreen(TypedDict):
    # guaranteed
    description: Optional[str]
    welcome_channels: list[RawWelcomeScreenChannel]

class RawMember(TypedDict):
    # guaranteed
    roles: list[RawSnowflake]
    joined_at: str
    deaf: bool
    mute: bool

    # not guaranteed
    user: RawUser
    nick: Optional[str]
    premium_since: str
    pending: bool
    permissions: str

class RawVoiceState(TypedDict):
    # guaranteed
    channel_id: Optional[RawSnowflake]
    user_id: RawSnowflake
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    suppress: bool
    request_to_speak_timestamp: str

    # not guaranteed
    guild_id: RawSnowflake
    member: RawMember
    self_stream: bool
    self_video: bool

class RawOverwrite(TypedDict):
    # guaranteed
    id: RawSnowflake
    type: int
    allow: str
    deny: str

class RawThreadMetadata(TypedDict):
    # guaranteed
    archived: bool
    auto_archive_duration: int
    archive_timestamp: str

    # not guaranteed
    locked: bool

class RawThreadMember(TypedDict):
    # guaranteed
    join_timestamp: str
    flags: int

    # not guaranteed
    id: RawSnowflake
    user_id: RawSnowflake

class RawChannel(TypedDict):
    # guaranteed
    id: RawSnowflake
    type: int
    
    # not guaranteed
    guild_id: RawSnowflake
    position: int
    permission_overwrites: list[RawOverwrite]
    name: str
    topic: Optional[str]
    nsfw: bool
    last_message_id: Optional[RawSnowflake]
    bitrate: int
    user_limit: int
    rate_limit_per_user: int
    recipients: list[RawUser]
    icon: Optional[str]
    owner_id: RawSnowflake
    application_id: RawSnowflake
    parent_id: Optional[RawSnowflake]
    last_pin_timestamp: Optional[str]
    rtc_region: Optional[str]
    video_quality_mode: int
    message_count: int
    member_count: int
    thread_metadata: RawThreadMetadata
    member: RawThreadMember
    default_auto_archive_duration: int

class RawActivityTimestamps(TypedDict):
    # not guaranteed
    start: int
    end: int

class RawActivityEmoji(TypedDict):
    # guaranteed
    name: str

    # not guaranteed
    id: RawSnowflake
    animated: bool

class RawActivityParty(TypedDict):
    # not guaranteed
    id: str
    size: tuple[int, int]

class RawActivityAssets(TypedDict):
    # not guaranteed
    large_image: str
    large_text: str
    small_image: str
    small_text: str

class RawActivitySecrets(TypedDict):
    # not guaranteed
    join: str
    spectate: str
    match: str

class RawActivityButton(TypedDict):
    # guaranteed
    label: str
    url: str

class RawActivity(TypedDict):
    # guaranteed
    name: str
    type: int
    created_at: int

    # not guaranteed
    url: Optional[str]
    timestamps: RawActivityTimestamps
    application_id: RawSnowflake
    details: Optional[str]
    state: Optional[str]
    emoji: Optional[RawActivityEmoji]
    party: RawActivityParty
    assets: RawActivityAssets
    secrets: RawActivitySecrets
    instance: bool
    flags: int
    buttons: list[RawActivityButton]

class RawClientStatus(TypedDict):
    # not guaranteed
    desktop: str
    mobile: str
    web: str

class RawPresenceUpdate(TypedDict):
    # guaranteed
    user: RawUser
    guild_id: RawSnowflake
    status: str
    activities: list[RawActivity]
    client_status: RawClientStatus

class RawStageInstance(TypedDict):
    # guaranteed
    id: RawSnowflake
    guild_id: RawSnowflake
    channel_id: RawSnowflake
    topic: str
    privacy_level: int
    discoverable_disabled: bool

class RawGuild(TypedDict):
    # guaranteed
    id: RawSnowflake
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    owner_id: RawSnowflake
    afk_channel_id: Optional[RawSnowflake]
    afk_timeout: int
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    roles: list[RawRole]
    emojis: list[RawEmoji]
    features: list[str]
    mfa_level: int
    application_id: Optional[RawSnowflake]
    system_channel_id: Optional[RawSnowflake]
    system_channel_flags: int
    rules_channel_id: Optional[RawSnowflake]
    vanity_url_code: Optional[str]
    description: Optional[str]
    banner: Optional[str]
    premium_tier: int
    preferred_locale: int
    public_updates_channel_id: Optional[RawSnowflake]
    nsfw_level: int

    # guaranteed in GUILD_CREATE
    widget_enabled: bool
    widget_channel_id: Optional[RawSnowflake]
    joined_at: str
    large: bool
    unavailable: bool
    member_count: int
    voice_states: list[RawVoiceState]
    members: list[RawMember]
    channels: list[RawChannel]
    presences: list[RawPresenceUpdate]
    stage_instances: list[RawStageInstance]

    # not guaranteed
    icon_hash: Optional[str]
    region: Optional[str]
    max_presences: Optional[int]
    max_members: int
    premium_subscription_count: int
    max_video_channel_users: int
    approximate_member_count: int
    approximate_presence_count: int
    welcome_screen: RawWelcomeScreen

class RawUserWithPartialMember(RawUser):
    pass

class RawAttachment(TypedDict):
    # guaranteed
    id: RawSnowflake
    filename: str
    size: int
    url: str
    proxy_url: str

    # not guaranteed
    content_type: str
    height: Optional[int]
    width: Optional[int]

class RawEmbedFooter(TypedDict):
    # guaranteed
    text: str

    # not guaranteed
    icon_url: str
    proxy_icon_url: str

class RawEmbedMedia(TypedDict):
    # not guaranteed
    url: str
    proxy_url: str
    height: int
    width: int

class RawEmbedProvider(TypedDict):
    # not guaranteed
    name: str
    url: str

class RawEmbedAuthor(TypedDict):
    # not guaranteed
    name: str
    url: str
    icon_url: str
    proxy_icon_url: str

class RawEmbedField(TypedDict):
    # guaranteed
    name: str
    value: str

    # not guaranteed
    inline: bool

class RawEmbed(TypedDict):
    # not guaranteed
    title: str
    type: str
    description: str
    url: str
    timestamp: str
    color: int
    footer: RawEmbedFooter
    image: RawEmbedMedia
    thumbnail: RawEmbedMedia
    video: RawEmbedMedia
    provider: RawEmbedProvider
    author: RawEmbedAuthor
    fields: list[RawEmbedField]

class RawChannelMention(TypedDict):
    # guaranteed
    id: RawSnowflake
    guild_id: RawSnowflake
    type: int
    name: str

class RawReaction(TypedDict):
    # guaranteed
    count: int
    me: bool
    emoji: RawEmoji

class RawMessageActivity(TypedDict):
    # guaranteed
    type: int

    # not guaranteed
    party_id: str

class RawMessageReference(TypedDict):
    # not guaranteed
    message_id: RawSnowflake
    channel_id: RawSnowflake
    guild_id: RawSnowflake
    fail_if_not_exists: bool

class RawSticker(TypedDict):
    # guaranteed
    id: RawSnowflake
    name: str
    description: str
    tags: str
    format_type: int

    # not guaranteed
    pack_id: RawSnowflake
    available: bool
    guild_id: RawSnowflake
    user: RawUser
    sort_value: int

class RawMessageComponent(TypedDict):
    # guaranteed
    type: int

    # not guaranteed
    style: int
    label: str
    emoji: RawEmoji
    custom_id: str
    url: str
    disabled: bool
    
    components: list[RawMessageComponent]

class RawMessage(TypedDict):
    # guaranteed
    id: RawSnowflake
    channel_id: RawSnowflake
    author: RawUser
    content: str
    timestamp: str
    edited_timestamp: str
    tts: bool
    mention_everyone: bool
    mentions: list[RawUserWithPartialMember]
    mention_roles: list[RawRole]
    attachments: list[RawAttachment]
    embeds: list[RawEmbed]
    pinned: bool
    type: int

    # not guaranteed
    guild_id: RawSnowflake
    member: RawMember
    mention_channels: list[RawChannelMention]
    reactions: list[RawReaction]
    nonce: Union[int, str]
    webhook_id: RawSnowflake
    activity: RawMessageActivity
    application: RawApplication
    application_id: RawSnowflake
    message_reference: RawMessageReference
    flags: int
    stickers: list[RawSticker]
    referenced_message: Optional[RawMessage]
    thread: RawChannel
    components: list[RawMessageComponent]