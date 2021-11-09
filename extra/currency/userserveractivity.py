import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union


class UserServerActivityTable(commands.Cog):
    """ Class for the UserServerActivity table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    # ===== Discord commands =====
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_server_activity(self, ctx):
        """ (ADM) Creates the UserServerActivity table. """

        await ctx.message.delete()
        if await self.check_user_server_activity_table_exists():
            return await ctx.send("The `UserServerActivity` already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("CREATE TABLE UserServerActivity (user_id bigint, user_messages bigint, user_time bigint, user_timestamp bigint DEFAULT NULL)")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table `UserServerActivity` created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_server_activity(self, ctx):
        """ (ADM) Drops the UserServerActivity table. """

        await ctx.message.delete()

        if not await self.check_user_server_activity_table_exists():
            return await ctx.send("The `UserServerActivity` doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserServerActivity")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table `UserServerActivity` dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_server_activity(self, ctx):
        """ (ADM) Resets the UserServerActivity table. """

        await ctx.message.delete()
        if not await self.check_user_server_activity_table_exists():
            return await ctx.send("The `UserServerActivity` doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserServerActivity")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table `UserServerActivity` reset!**")

    # ===== SHOW =====

    async def check_user_server_activity_table_exists(self) -> bool:
        """ Checks whether the UserServerActivity table exists. """
        
        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'UserServerActivity'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    # ===== INSERT =====
    async def insert_user_server_activity(self, user_id: int, add_msg: int, new_ts: int = None) -> None:
        """ Inserts a user into the UserServerActivity table.
        :param user_id: The ID of the user to insert.
        :param add_msg: The initial message counter for the user to have.
        :param new_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute(
            "INSERT INTO UserServerActivity (user_id, user_messages, user_time, user_timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, add_msg, 0, new_ts))
        await db.commit()
        await mycursor.close()

    # ===== SELECT =====

    async def get_user_activity_info(self, user_id: int) -> List[List[int]]:
        """ Gets a user from the UserServerActivity table.
        :param user_id: The ID of the user to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserServerActivity WHERE user_id = %s", (user_id,))
        user_info = await mycursor.fetchall()
        await mycursor.close()
        return user_info

    # ===== UPDATE =====
    async def update_user_server_messages(self, user_id: int, add_msg: int) -> None:
        """ Updates the user's message counter.
        :param user_id: The ID of the user to update.
        :param add_msg: The increment to apply to their current message counter. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserServerActivity SET user_messages = user_messages + %s WHERE user_id = %s", (add_msg, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_server_time(self, user_id: int, add_time: int) -> None:
        """ Updates the user's time counter.
        :param user_id: The ID of the user to update.
        :param add_time: The increment value to apply to the user's current time counter. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserServerActivity SET user_time = user_time + %s WHERE user_id = %s", (add_time, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_server_timestamp(self, user_id: int, new_ts: int) -> None:
        """ Updates the user's Server Activity timestamp.
        :param user_id: The ID of the user to update.
        :param new_ts: The new timestamp to set to. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserServerActivity SET user_timestamp = %s WHERE user_id = %s", (new_ts, user_id))
        await db.commit()
        await mycursor.close()
