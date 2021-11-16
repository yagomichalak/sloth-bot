import discord
from discord.ext import commands
from abc import abstractclassmethod, ABC
from typing import Any, Union, Tuple, List, Optional
import os
import __future__
from PIL import Image, ImageDraw, ImageFont

server_id: int = int(os.getenv('SERVER_ID'))

class SmartRoom(ABC):
    """ Base class for SmartRooms. """

    
    @abstractclassmethod
    async def format_data(cls) -> Any: pass

    @abstractclassmethod
    async def insert(cls) -> Any: pass

    @abstractclassmethod
    async def update(cls) -> Any: pass

    @abstractclassmethod
    async def delete(cls) -> Any: pass

    @abstractclassmethod
    async def image_preview(cls) -> Any: pass

    @staticmethod
    async def overwrite_image(member_id, text, coords, color, image) -> None:
        """ Writes a text on a Smartroom's image preview, and overwrites the original one.
        :param member_id: The ID of the user who's creating it.
        :param text: The text that's gonna be written.
        :param coords: The coordinates for the text.
        :param color: The color of the text.
        :param image: The image to write on. """

        small = ImageFont.truetype("./images/smart_vc/uni-sans-regular.ttf", 40)
        base = Image.open(image)
        draw = ImageDraw.Draw(base)
        draw.text(coords, text, color, font=small)
        base.save(f'./images/smart_vc/user_previews/{member_id}.png')

    @staticmethod
    async def overwrite_image_with_image(member_id, coords, size) -> None:
        """ Pastes a voice channel image on top of a SmartRoom's image preview
        and overwrites the original one.
        :param member_id: The ID of the user who's creating it.
        :param coords: The coordinates for the image that's gonna be pasted on top of it.
        :param size: The size of the voice channel. """

        path = f'./images/smart_vc/user_previews/{member_id}.png'
        user_preview = Image.open(path)
        size_image = Image.open(size).resize((78, 44), Image.LANCZOS)
        user_preview.paste(size_image, coords, size_image)
        user_preview.save(path)

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

    @classmethod
    async def image_preview(cls, user_id: int, vc_name: str, vc_user_limit: int) -> Image:
        """ Makes a creation preview image for a Basic Room.
        :param user_id: The ID of the user who's creating it.
        :param vc_name: The Voice Channel name.
        :param vc_user_limit: The Voice Channel size; user limit. """

        preview_template = './images/smart_vc/basic/1 preview2.png'
        color = (132, 142, 142)
        await cls.overwrite_image(user_id, vc_name, (585, 870), color, preview_template)
        if int(vc_user_limit) != 0:
            await cls.overwrite_image_with_image(user_id, (405, 870), f'./images/smart_vc/sizes/voice channel ({vc_user_limit}).png')

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

    @classmethod
    async def image_preview(cls, user_id, vc_name, vc_user_limit, txt_name) -> None:
        """ Makes a creation preview image for a Premium Room.
        :param user_id: The ID of the user who's creating it.
        :param vc_name: The voice channel name.
        :param vc_user_limit: The voice channel size; user limit.
        :param txt_name: The name o the first text channel. """

        preview_template = './images/smart_vc/premium/2 preview2.png'
        color = (132, 142, 142)
        await cls.overwrite_image(user_id, txt_name.lower(), (585, 760), color, preview_template)
        await cls.overwrite_image(user_id, vc_name, (585, 955), color, f'./images/smart_vc/user_previews/{user_id}.png')
        if int(vc_user_limit) != 0:
            await cls.overwrite_image_with_image(user_id, (405, 955), f'./images/smart_vc/sizes/voice channel ({vc_user_limit}).png')

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
        owner: Union[discord.Member, discord.User] = await guild.fetch_member(data[0])

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

        set_keywords: List[str] = list(map(lambda kw: "{k} = {v}".format(k=kw[0], v=kw[1]), list(kwargs.items())))
        set_clauses: str = 'SET ' + ', '.join(set_keywords)

        sql: str = "UPDATE SmartRooms " + set_clauses + f" WHERE user_id = {self.owner.id} AND room_type = 'galaxy'"
        await cog.update_smartroom(sql)

    async def delete(self, cog: commands.Cog) -> None:
        """ Deletes the GalaxyRoom from Discord and from the database. """

        for channel in self.channels:
            try:
                await channel.delete()
            except:
                pass

        await cog.delete_smartroom(room_type='galaxy', owner_id=self.owner.id)

    @property
    def raw_voice_channels(self):
        """ Gets all Voice Channels from the GalaxyRoom. """

        return [self.vc, self.vc2]

    @property
    def voice_channels(self):
        """ Gets all Voice Channels from the GalaxyRoom. """

        return list(filter(lambda vc: vc is not None, [self.vc, self.vc2]))

    @property
    def raw_text_channels(self):
        """ Gets all Text Channels from the GalaxyRoom. """

        return [self.txt, self.th, self.th2, self.th3, self.th4]

    @property
    def text_channels(self):
        """ Gets all Text Channels from the GalaxyRoom. """

        return list(filter(lambda txt: txt is not None, [
            self.txt, self.th, self.th2, self.th3, self.th4
        ]))

    @property
    def raw_channels(self):
        """ Gets all Guild Channels from the GalaxyRoom. """

        return [self.vc, self.vc2, self.txt, self.th, self.th2, self.th3, self.th4, self.cat]

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

    async def try_to_create(
        self, 
        kind: str, category: discord.CategoryChannel = None, 
        channel: discord.TextChannel = None, guild: Optional[discord.Guild] = None, owner: Optional[discord.Member] = None, **kwargs: Any
        ) -> Union[bool, discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.Thread]:
        """ Try to create something.
        :param thing: The thing to try to create.
        :param kind: Kind of creation. (txt, vc, cat, thread)
        :param category: The category in which it will be created. (Optional)
        :param channel: The channel in which the thread be created in. (Optional)(Required for threads)
        :param guild: The guild in which it will be created in. (Optional)(Required for categories)
        :param owner: The owner of the Galaxy Rooms. (Optional)
        :param kwargs: The arguments to inform the creations. """

        try:
            if kind == 'text':
                the_thing = await category.create_text_channel(**kwargs)
            elif kind == 'voice':
                the_thing = await category.create_voice_channel(**kwargs)
            elif kind == 'category':
                the_thing = await guild.create_category(**kwargs)
            elif kind == 'thread':
                start_message = await channel.send(kwargs['name'])
                await start_message.pin(reason="Galaxy Room's Thread Creation")
                the_thing = await start_message.create_thread(**kwargs)
                if owner:
                    await the_thing.add_user(owner)
        except Exception as e:
            print(e)
            return False
        else:
            return the_thing

    async def delete_channels(self, channels: List[discord.abc.GuildChannel]) -> None:
        """ Deletes a list of Guild Channels.
        :param channels: The channels to delete. """

        for channel in channels:
            try:
                await channel.delete()
            except:
                pass

    @classmethod
    async def image_preview(cls, user_id: int, vc_name: str, vc_user_limit: int, txt_name: str, cat_name: str) -> None:
        """ Makes a creation preview for a Galaxy Room.
        :param user_id: The ID of the user who's creating it.
        :param vc_name: The main Voice Channel name.
        :param vc_user_limit: The Voice Channel size; user limit. 
        :param txt_name: The name of the Text Channel.
        :param cat_name: The category name. """

        preview_template = './images/smart_vc/galaxy/3 preview2.png'
        color = (132, 142, 142)
        await cls.overwrite_image(user_id, cat_name, (505, 730), color, preview_template)
        await cls.overwrite_image(user_id, txt_name.lower(), (585, 840), color, f'./images/smart_vc/user_previews/{user_id}.png')
        await cls.overwrite_image(user_id, vc_name, (585, 970), color, f'./images/smart_vc/user_previews/{user_id}.png')
        if int(vc_user_limit) != 0:
            await cls.overwrite_image_with_image(user_id, (375, 965), f'./images/smart_vc/sizes/voice channel ({vc_user_limit}).png')