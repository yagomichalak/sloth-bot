from mysqldb import the_database
from discord.ext import commands
import enum
from typing import List, Optional, Union
from .rooms import SmartRoom, BasicRoom, PremiumRoom, GalaxyRoom

class SmartRoomEnum(enum.Enum):

    basic: SmartRoom = BasicRoom
    premium: SmartRoom = PremiumRoom
    galaxy: SmartRoom = GalaxyRoom

    basic_room: SmartRoom = BasicRoom
    premium_room: SmartRoom = PremiumRoom
    galaxy_room: SmartRoom = GalaxyRoom

    ONE: SmartRoom = BasicRoom
    TWO: SmartRoom = PremiumRoom
    THREE: SmartRoom = GalaxyRoom

class SmartRoomDatabase(commands.Cog):
    """ Class containing database methods
    for the SmartRooms. """

    def __init__(self) -> None:
        super().__init__()
    
    # =====  CRUD  =====

    # ===== CREATE =====
    # =====  READ  =====
    async def get_smartroom(self, user_id: Optional[int] = None, 
        vc_id: Optional[int] = None, txt_id: Optional[int] = None, cat_id: Optional[int] = None,
        multiple: bool = False
    ) -> Union[List[SmartRoom], List[List[SmartRoom]]]:
        """ Gets one or more SmartRooms.
        :param room_type: The type of SmartRoom.
        :param user_id: The owner ID of the SmartRoom. [Optional]
        :param vc_id: The Voice Channel ID of the SmartRoom. [Optional]
        :param txt_id: The Text Channel ID of the SmartRoom. [Optional]
        :param cat_id: The Category ID of the SmartRoom. [Optional]
        :param multiple: Whether to get multiple values. [Default=False] """

        mycursor, _ = await the_database()

        if user_id:
            await mycursor.execute("SELECT * FROM SmartRooms WHERE user_id = %s", (user_id,))
        elif vc_id:
            await mycursor.execute("SELECT * FROM SmartRooms WHERE vc_id = %s", (vc_id,))
        elif txt_id:
            await mycursor.execute("SELECT * FROM SmartRooms WHERE txt_id = %s", (txt_id,))
        elif cat_id:
            await mycursor.execute("SELECT * FROM SmartRooms WHERE cat_id = %s", (cat_id,))

        if multiple:
            results = await mycursor.fetchall()
            smart_rooms: List[SmartRoom] = [
                SmartRoomEnum.__getitem__(name=result[1]).format_data(result)
                for result in results
            ]
            await mycursor.close()
            return smart_rooms
        else:
            result = await mycursor.fetchone()
            smart_room: SmartRoom = SmartRoomEnum.__getitem__(name=result[1]).format_data(result)
            await mycursor.close()
            return smart_room
    
    # ===== UPDATE =====
    # ===== DELETE =====

    # ===== OTHER  =====


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_smartrooms(self, ctx) -> None:
        """ (ADM) Creates the SmartRooms table. """

        if await self.table_exists():
            return await ctx.reply("**Table `SmartRooms` already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
        CREATE TABLE SmartRooms (
            user_id BIGINT NOT NULL,
            room_type VARCHAR(7) NOT NULL,
            vc_id BIGINT NOT NULL,
            vc2_id BIGINT DEFAULT NULL,
            txt_id BIGINT NOT NULL,
            th_id BIGINT DEFAULT NULL,
            th2_id BIGINT DEFAULT NULL,
            th3_id BIGINT DEFAULT NULL,
            th4_id BIGINT DEFAULT NULL,
            creation_ts BIGINT NOT NULL,
            edited_ts BIGINT DEFAULT NULL,
            PRIMARY KEY(user_id, room_type)
        )""")
        await db.commit()
        await mycursor.close()
        await ctx.reply("**Successfully created the `SmartRooms` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_smartrooms(self, ctx) -> None:
        """ (ADM) Drops the SmartRooms table. """

        if not await self.table_exists():
            return await ctx.reply("**Table `SmartRooms` doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SmartRooms")
        await db.commit()
        await mycursor.close()
        await ctx.reply("**Successfully dropped the `SmartRooms` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_smartrooms(self, ctx) -> None:
        """ (ADM) Resets the SmartRooms table. """

        if not await self.table_exists():
            return await ctx.reply("**Table `SmartRooms` doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SmartRooms")
        await db.commit()
        await mycursor.close()
        await ctx.reply("**Successfully reset the `SmartRooms` table!**")


    async def table_exists(self) -> bool:
        """ Checks whether the SmartRooms table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'SmartRooms'")
        exists = await mycursor.fetchone()
        await mycursor.close()

        if exists:
            return True

        return False
