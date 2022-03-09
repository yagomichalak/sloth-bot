from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DiscordRole:
    id: int

@dataclass
class DiscordMember:
    id: int
    nick: Optional[str]
    premium_since: Optional[str]
    joined_at: str
    is_pending: bool
    pending: bool
    communication_disabled_until: Optional[str]
    username: str
    discriminator: str
    display_avatar: str
    avatar: DiscordIcon
    public_flags: int
    mute: bool
    deaf: bool
    roles: List[DiscordRole]
    guild: DiscordGuild

    def mention(self) -> None: ...

@dataclass
class DiscordGuild:
    id: int
    name: str
    roles: List[DiscordRole] 
    categories: List[DiscordCategory]
    channels: List[DiscordChannel]
    threads: List[DiscordChannel]
    icon: DiscordIcon
    members: List[DiscordMember]

@dataclass
class DiscordCategory:
    id: int
    name: str

@dataclass
class DiscordChannel:
    id: int

    async def send(self, *args, **kwargs) -> None: ...

    async def delete(self, *args, **kwargs) -> None: ...

@dataclass
class DiscordIcon:
    url: str

@dataclass
class DiscordMessage:
    id: 678