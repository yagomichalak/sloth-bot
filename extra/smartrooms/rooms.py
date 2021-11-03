import discord
from discord.ext import commands
from abc import abstractclassmethod, ABC
from typing import Any, Union, Tuple, List
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

        self._channels: List[discord.abc.GuildChannel] = []

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
    async def insert(cog: commands.Cog, user_id: int, vc_id: int, txt_id: int, cat_id: int, creation_ts: int) -> None:
        """ Inserts a GalaxyRoom into the database.
        :param user_id: The ID of the owner of the room.
        :param vc_id: The Voice Channel ID.
        :param txt_id: The Text Channel ID.
        :param cat_id: The Category ID.
        :param creation_ts: The current timestamp. """

        await cog.insert_smartroom(user_id=user_id, room_type='galaxy', vc_id=vc_id, txt_id=txt_id, cat_id=cat_id, creation_ts=creation_ts)

    async def update(self, cog: commands.Cog, **kwargs) -> None:
        """ Updates a GalaxyRoom value.
        :param cog: The cog to get database methods from.
        :param kwargs: The keyword arguments to update. """

        """
        user_id: int,
        vc_id: int = None, vc2_id: int = None, txt_id: int = None, th_id: int = None, 
        th2_id: int = None, th3_id: int = None, th4_id: int = None, cat_id: int = None
        """

        set_keywords: List[str] = list(map(lambda kw: f"{kw[0]} = {kw[1]}", list(kwargs.items())))
        set_clauses: str = 'SET ' + ', '.join(set_keywords)

        sql: str = "UPDATE SmartRooms " + set_clauses + f" WHERE user_id = {self.owner.id} AND room_type = 'galaxy'"

        await cog.update_smartroom(sql)

    @staticmethod
    async def delete() -> None: pass

    @property
    def voice_channels(self):
        """ Gets all Voice Channels from the GalaxyRoom. """

        return list(filter(lambda vc: vc is not None, [self.vc, self.vc2]))

    @property
    def text_channels(self):
        """ Gets all Text Channels from the GalaxyRoom. """

        return list(filter(lambda txt: txt is not None, [
            self.txt, self.th, self.th2, self.th3, self.th4
        ]))

    @property
    def channels(self):
        """ Gets all Guild Channels from the GalaxyRoom. """

        return list(filter(lambda channel: channel is not None, [
            self.vc, self.vc2, self.txt, self.th, self.th2, self.th3, self.th4, self.cat
        ]))

    async def handle_permissions(self, members: List[discord.Member], allow: bool = True) -> List[str]:
        """ Handles permissions for a member in one's Galaxy Room.
        :param members: The list of members to handle permissions for.
        :param allow: Whether to allow or disallow the member and their permissions from the Galaxy Room. [Default=True]"""

        channels = self.channels
        actioned: List[str] = []

        for m in members:
            try:
                for c in channels:
                    if not isinstance(c, discord.Thread):
                        if c:
                            if allow:
                                await c.set_permissions(
                                    m, read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)
                            else:
                                await c.set_permissions(m, overwrite=None)
                    else:
                        if allow:
                            await c.add_user(m)
                        else:
                            await c.remove_user(m)

            except Exception as e:
                print(e)
                pass
            else:
                actioned.append(m.mention)

        return actioned

    async def get_rent_price(self) -> int:
        """ Gets the rent price that the user has to pay, according to the amount of
        channels that they have in their Galaxy Room. """

        money = 1500 # Minimum renting price
        money += (len(self.text_channels) - 1) * 250
        money += (len(self.voice_channels) - 1) * 500
        return money


# galaxy_room = GalaxyRoom()

# asyncio.run(galaxy_room.insert())