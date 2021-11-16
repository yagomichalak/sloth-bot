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

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    # =====  CRUD  =====

    # ===== CREATE =====
    async def insert_smartroom(self, 
        user_id: int, room_type: str, vc_id: int, creation_ts: int, txt_id: Optional[int] = None,
        vc2_id: Optional[int] = None, th_id: Optional[int] = None, th2_id: Optional[int] = None, 
        th3_id: Optional[int] = None, th4_id: Optional[int] = None, cat_id: Optional[int] = None
    ) -> None:
        """ Inserts a SmartRoom into the database.
        :param user_id: The ID of the owner of the SmartRoom.
        :param room_type: The type of the SmartRoom. (Basic/Premium/Galaxy)
        :param vc_id: The Voice Channel ID.
        :param creation_ts: The creation timestamp.
        :param txt_id: The Text Channel ID. [Optional]
        :param vc2_id: The 2nd Voice Channel ID. [Optional].
        :param th2_id: The Thread Channel ID. [Optional].
        :param th3_id: The 2nd Thread Channel ID. [Optional].
        :param th4_id: The 3rd Thread Channel ID. [Optional]. 
        :param cat_id: The 3rd Category ID. [Optional]. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO SmartRooms (
                user_id, room_type, vc_id, vc2_id,
                txt_id, th_id, th2_id, th3_id, th4_id,
                cat_id, creation_ts, edited_ts
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, room_type, vc_id, vc2_id, txt_id, th_id, th2_id, th3_id, th4_id, cat_id, creation_ts, creation_ts))
        await db.commit()
        await mycursor.close()


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

        if vc_id:
            await mycursor.execute("SELECT * FROM SmartRooms WHERE vc_id = %s", (vc_id,))
        elif txt_id:
            await mycursor.execute("SELECT * FROM SmartRooms WHERE txt_id = %s", (txt_id,))
        elif cat_id:
            await mycursor.execute("SELECT * FROM SmartRooms WHERE cat_id = %s", (cat_id,))
        elif user_id:
            await mycursor.execute("SELECT * FROM SmartRooms WHERE user_id = %s", (user_id,))

        if multiple:
            results = await mycursor.fetchall()
            await mycursor.close()
            if not results:
                return []

            smart_rooms: List[SmartRoom] = [
                await SmartRoomEnum.__getitem__(name=result[1]).value.format_data(self.client, result)
                for result in results
            ]
            return smart_rooms
        else:
            result = await mycursor.fetchone()
            await mycursor.close()
            if not result:
                return

            smart_room: SmartRoom = SmartRoomEnum.__getitem__(name=result[1]).value
            formatted_smart_room: SmartRoom = await smart_room.format_data(client=self.client, data=result)
            return formatted_smart_room

    async def get_galaxies_in_danger_zone(self, current_ts: int) -> List[List[GalaxyRoom]]:
        """ Gets all Galaxy Rooms in danger zone. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM SmartRooms WHERE room_type = 'galaxy' AND (edited_ts + 1209600) - %s <= 172800 AND notified = 0", (current_ts,))
        results = await mycursor.fetchall()
        await mycursor.close()
        
        if not results:
            return []

        smart_rooms: List[GalaxyRoom] = [
            await GalaxyRoom.format_data(self.client, result)
            for result in results
        ]
        return smart_rooms

    async def get_galaxies_expired(self, current_ts: int) -> List[List[GalaxyRoom]]:
        """ Gets all Galaxy Rooms that are expired. """

        mycursor, _ = await the_database()
        
        await mycursor.execute("SELECT * FROM SmartRooms WHERE room_type = 'galaxy' AND %s - edited_ts >= 1209600", (current_ts,))
        results = await mycursor.fetchall()
        await mycursor.close()
        
        if not results:
            return []

        smart_rooms: List[GalaxyRoom] = [
            await GalaxyRoom.format_data(self.client, result)
            for result in results
        ]
        return smart_rooms
    
    # ===== UPDATE =====
    async def update_smartroom(self, sql: str) -> None:
        """ Updates one or more values of a SmartRoom.
        :param sql: The SQL to run. """

        mycursor, db = await the_database()
        await mycursor.execute(sql)
        await db.commit()
        await mycursor.close()

    # ===== DELETE =====
    async def delete_smartroom(self,
        room_type: str, owner_id: Optional[int] = None, vc_id: Optional[int] = None) -> None:
        """ Deletes SmartRoom.
        :param room_type: The type of room. (Basic/Premium/Galaxy)
        :param owner_id: The owner ID. [Optional]
        :param vc_id: The Voice Channel ID. [Optional] """

        mycursor, db = await the_database()
        if owner_id:
            await mycursor.execute("DELETE FROM SmartRooms WHERE user_id = %s AND room_type = %s", (owner_id, room_type))
        if vc_id:
            await mycursor.execute("DELETE FROM SmartRooms WHERE vc_id = %s AND room_type = %s", (vc_id, room_type))


        await db.commit()
        await mycursor.close()

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
            txt_id BIGINT DEFAULT NULL,
            th_id BIGINT DEFAULT NULL,
            th2_id BIGINT DEFAULT NULL,
            th3_id BIGINT DEFAULT NULL,
            th4_id BIGINT DEFAULT NULL,
            cat_id BIGINT DEFAULT NULL,
            creation_ts BIGINT NOT NULL,
            edited_ts BIGINT DEFAULT NULL,
            notified TINYINT(1) DEFAULT 0,
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
