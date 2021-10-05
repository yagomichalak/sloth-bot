import discord
from discord.ext import commands
from mysqldb import the_database
from abc import abstractclassmethod, ABC
from typing import Any, Union, Tuple
import asyncio
import os
import __future__


server_id: int = int(os.getenv('SERVER_ID'))

class SmartRoom(ABC):
    """ Base class for SmartRooms. """

    @abstractclassmethod
    async def format_data(cls) -> Any:
        return cls

    @abstractclassmethod
    async def insert(cls) -> Any: pass

    @abstractclassmethod
    async def update(cls) -> Any: pass

    @abstractclassmethod
    async def delete(cls) -> Any: pass


class BasicRoom(SmartRoom):
    """ Class for BasicRooms. """

    def __init__(self, 
        owner: Union[discord.Member, discord.User], vc: discord.VoiceChannel, creation_ts: int, edited_ts: int
        ) -> None:

        self.owner = owner
        self.vc = vc
        self.creation_ts = creation_ts
        self.edited_ts = edited_ts

    @staticmethod
    async def format_data(client: commands.Bot, data: Tuple[Union[int, str]]) -> SmartRoom:
        """ Formats the database data into Discord objects. """

        guild: discord.Guild = client.get_guild(server_id)
        owner: Union[discord.Member, discord.User] = guild.get_member(data[0])
        vc: discord.VoiceChannel = discord.utils.get(guild.voice_channels, id=data[2])

        return BasicRoom(
            owner=owner, vc=vc, creation_ts=data[10], edited_ts=data[11]
        )

    async def insert(self) -> Any: pass

    async def update(self) -> Any: pass

    async def delete(self) -> Any: pass

class PremiumRoom(SmartRoom):
    """ Class for PremiumRooms. """


    def __init__(self, 
        owner: Union[discord.Member, discord.User], vc: discord.VoiceChannel, txt: discord.TextChannel, creation_ts: int, edited_ts: int
        ) -> None:
        self.owner = owner
        self.vc = vc
        self.txt = txt
        self.creation_ts = creation_ts
        self.edited_ts = edited_ts

    @staticmethod
    async def format_data(client: commands.Bot, data: Tuple[Union[int, str]]) -> SmartRoom:
        """ Formats the database data into Discord objects. """

        guild: discord.Guild = client.get_guild(server_id)
        owner: Union[discord.Member, discord.User] = guild.get_member(data[0])
        vc: discord.VoiceChannel = discord.utils.get(guild.voice_channels, id=data[2])
        txt: discord.TextChannel = discord.utils.get(guild.text_channels, id=data[4])
        
        return PremiumRoom(
            owner=owner, vc=vc, txt=txt, creation_ts=data[10], edited_ts=data[11]
        )

    async def insert(self) -> Any:

        print('Inserting Premium Room into the database...')

    async def update(self) -> Any: pass

    async def delete(self) -> Any: pass

class GalaxyRoom(SmartRoom):
    """ Class for GalaxyRooms. """

    def __init__(self, 
        owner: Union[discord.Member, discord.User], vc: discord.VoiceChannel, vc2: discord.VoiceChannel,
        txt: discord.TextChannel, th: discord.Thread, th2: discord.Thread, th3: discord.Thread, th4: discord.Thread,
        cat: discord.CategoryChannel, creation_ts: int, edited_ts: int
        ) -> None:

        self.owner = owner
        self.vc = vc
        self.vc2 = vc2
        self.txt = txt
        self.th = th
        self.th2 = th2
        self.th3 = th3
        self.th4 = th4
        self.cat = cat
        self.creation_ts = creation_ts
        self.edited_ts = edited_ts

    @staticmethod
    async def format_data(client: commands.Bot, data: Tuple[Union[int, str]]) -> SmartRoom:
        """ Formats the database data into Discord objects. """

        guild: discord.Guild = client.get_guild(server_id)
        owner: Union[discord.Member, discord.User] = guild.get_member(data[0])

        vc: discord.VoiceChannel = discord.utils.get(guild.voice_channels, id=data[2])
        vc2: discord.VoiceChannel = discord.utils.get(guild.voice_channels, id=data[3])

        txt: discord.TextChannel = discord.utils.get(guild.text_channels, id=data[4])
        th: discord.Thread = discord.utils.get(guild.threads, id=data[5])
        th2: discord.Thread = discord.utils.get(guild.threads, id=data[6])
        th3: discord.Thread = discord.utils.get(guild.threads, id=data[7])
        th4: discord.Thread = discord.utils.get(guild.threads, id=data[8])

        cat: discord.CategoryChannel = discord.utils.get(guild.categories, id=data[9])
        
        return GalaxyRoom(
            owner=owner, vc=vc, vc2=vc2, 
            txt=txt, th=th, th2=th2, th3=th3, th4=th4,
            cat=cat, creation_ts=data[10], edited_ts=data[11]
        )

    async def insert(self) -> Any:

        print('Inserting Galaxy Room into the database...')

    async def update(self) -> Any: pass

    async def delete(self) -> Any: pass


# galaxy_room = GalaxyRoom()

# asyncio.run(galaxy_room.insert())