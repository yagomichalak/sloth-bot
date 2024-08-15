from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List


class EventRoomsTable(commands.Cog):
    """ Class for managing the EventRooms table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_event_rooms(self, ctx) -> None:
        """ (ADM) Creates the EventRooms table. """

        if await self.table_event_rooms_exists():
            return await ctx.send("**The `EventRooms` table already exists!**")

        await mycursor.execute("""
            CREATE TABLE EventRooms (
                user_id BIGINT NOT NULL, vc_id BIGINT DEFAULT NULL,
                txt_id BIGINT DEFAULT NULL
            )""")
        await ctx.send("**Created `EventRooms` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_event_rooms(self, ctx) -> None:
        """ (ADM) Drops the EventRooms table. """

        if not await self.table_event_rooms_exists():
            return await ctx.send("**The `EventRooms` table doesn't exist!**")

        await mycursor.execute("DROP TABLE EventRooms")
        await ctx.send("**Dropped `EventRooms` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_event_rooms(self, ctx) -> None:
        """ (ADM) Resets the EventRooms table. """

        if not await self.table_event_rooms_exists():
            return await ctx.send("**The `EventRooms` table doesn't exist yet!**")

        await mycursor.execute("DELETE FROM EventRooms")
        await ctx.send("**Reset `EventRooms` table!**")

    async def table_event_rooms_exists(self) -> bool:
        """ Checks whether the EventRooms table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'EventRooms'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if table_info:
            return True
        else:
            return False

    async def insert_event_room(self, user_id: int, vc_id: int = None, txt_id: int = None) -> None:
        """ Inserts an Event Room by VC ID.
        :param user_id: The ID of the user who's gonna be attached to the rooms.
        :param vc_id: The ID of the VC.
        :param txt_id: The ID of the txt. """

        await mycursor.execute("""
            INSERT INTO EventRooms (user_id, vc_id, txt_id)
            VALUES (%s, %s, %s)""", (user_id, vc_id, txt_id))

    async def get_event_room_by_user_id(self, user_id: int) -> List[int]:
        """ Gets an Event Room by VC ID.
        :param user_id: The ID of the user that you are looking for. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM EventRooms WHERE user_id = %s", (user_id,))
        event_room = await mycursor.fetchone()
        await mycursor.close()
        return event_room

    async def get_event_room_by_vc_id(self, vc_id: int) -> List[int]:
        """ Gets an Event Room by VC ID.
        :param vc_id: The ID of the VC that you are looking for. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM EventRooms WHERE vc_id = %s", (vc_id,))
        event_room = await mycursor.fetchone()
        await mycursor.close()
        return event_room

    async def get_event_room_by_txt_id(self, txt_id: int) -> List[int]:
        """ Gets an Event Room by VC ID.
        :param txt_id: The ID of the txt that you are looking for. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM EventRooms WHERE txt_id = %s", (txt_id,))
        event_room = await mycursor.fetchone()
        await mycursor.close()
        return event_room

    async def delete_event_room_by_user_id(self, user_id: int) -> None:
        """ Deletes an Event Room by VC ID.
        :param user_id: The ID of the user that you want to delete event rooms from. """

        await mycursor.execute("DELETE FROM EventRooms WHERE user_id = %s", (user_id,))

    async def delete_event_room_by_vc_id(self, vc_id: int) -> None:
        """ Deletes an Event Room by VC ID.
        :param vc_id: The ID of the txt that you want to delete. """

        await mycursor.execute("DELETE FROM EventRooms WHERE vc_id = %s", (vc_id,))

    async def delete_event_room_by_txt_id(self, txt_id: int) -> None:
        """ Deletes an Event Room by VC ID.
        :param txt_id: The ID of the txt that you want to delete. """

        await mycursor.execute("DELETE FROM EventRooms WHERE txt_id = %s", (txt_id,))
