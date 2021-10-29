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
        owner: Union[discord.Member, discord.User], room_type: str, vc: discord.VoiceChannel, creation_ts: int, edited_ts: int
        ) -> None:

        self.owner = owner
        self.vc = vc
        self.creation_ts = creation_ts
        self.edited_ts = edited_ts
        self.room_type = room_type

    @staticmethod
    async def format_data(client: commands.Bot, data: Tuple[Union[int, str]]) -> SmartRoom:
        """ Formats the database data into Discord objects. """

        guild: discord.Guild = client.get_guild(server_id)
        owner: Union[discord.Member, discord.User] = guild.get_member(data[0])
        vc: discord.VoiceChannel = discord.utils.get(guild.voice_channels, id=data[2])

        return BasicRoom(
            owner=owner, room_type='basic', vc=vc, creation_ts=data[10], edited_ts=data[11]
        )

    @staticmethod
    async def insert(cog: commands.Cog, user_id: int, vc_id: int, creation_ts: int) -> None:
        """ Inserts a BasicRoom into the database.
        :param user_id: The ID of the owner of the room.
        :param vc_id: The Voice Channel ID.
        :param creation_ts: The current timestamp. """

        await cog.insert_smartroom(user_id=user_id, room_type='basic', vc_id=vc_id, creation_ts=creation_ts)

    @staticmethod
    async def update() -> None: pass

    @staticmethod
    async def delete() -> None: pass

class PremiumRoom(SmartRoom):
    """ Class for PremiumRooms. """


    def __init__(self, 
        owner: Union[discord.Member, discord.User],  room_type: str, vc: discord.VoiceChannel, txt: discord.TextChannel, creation_ts: int, edited_ts: int
        ) -> None:
        self.owner = owner
        self.room_type = room_type
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
            owner=owner, room_type='premium', vc=vc, txt=txt, creation_ts=data[10], edited_ts=data[11]
        )

    @staticmethod
    async def insert(cog: commands.Cog, user_id: int, vc_id: int, txt_id: int, creation_ts: int) -> Any:
        """ Inserts a PremiumRoom into the database.
        :param user_id: The ID of the owner of the room.
        :param vc_id: The Voice Channel ID.
        :param txt_id: The Text Channel ID.
        :param creation_ts: The current timestamp. """

        await cog.insert_smartroom(user_id=user_id, room_type='premium', vc_id=vc_id, txt_id=txt_id, creation_ts=creation_ts)

    @staticmethod
    async def update() -> Any: pass

    @staticmethod
    async def delete() -> Any: pass

class GalaxyRoom(SmartRoom):
    """ Class for GalaxyRooms. """

    def __init__(self, 
        owner: Union[discord.Member, discord.User],  room_type: str, vc: discord.VoiceChannel, vc2: discord.VoiceChannel,
        txt: discord.TextChannel, th: discord.Thread, th2: discord.Thread, th3: discord.Thread, th4: discord.Thread,
        cat: discord.CategoryChannel, creation_ts: int, edited_ts: int
        ) -> None:

        self.owner = owner
        self.room_type = room_type
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
            owner=owner, room_type='galaxy', vc=vc, vc2=vc2, 
            txt=txt, th=th, th2=th2, th3=th3, th4=th4,
            cat=cat, creation_ts=data[10], edited_ts=data[11]
        )

    @staticmethod
    async def insert() -> Any:

        print('Inserting Galaxy Room into the database...')

    @staticmethod
    async def update() -> Any: pass

    @staticmethod
    async def delete() -> Any: pass


# galaxy_room = GalaxyRoom()

# asyncio.run(galaxy_room.insert())