import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union

class ModerationUserInfractionsTable(commands.Cog):
    
    def __init__(self, client) -> None:
        self.client = client


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_infractions(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table. """

        if await self.check_table_user_infractions():
            return await ctx.send("**Table __UserInfractions__ already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE UserInfractions (
            user_id BIGINT NOT NULL,
            infraction_type VARCHAR(7) NOT NULL,
            infraction_reason VARCHAR(100) DEFAULT NULL,
            infraction_ts BIGINT NOT NULL,
            infraction_id BIGINT NOT NULL AUTO_INCREMENT,
            perpetrator BIGINT NOT NULL,
            PRIMARY KEY (infraction_id)
            ) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci""")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __UserInfractions__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_infractions(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table """
        if not await self.check_table_user_infractions():
            return await ctx.send("**Table __UserInfractions__ doesn't exist!**")
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserInfractions")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __UserInfractions__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_infractions(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table """

        if not await self.check_table_user_infractions():
            return await ctx.send("**Table __UserInfractions__ doesn't exist yet!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserInfractions")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __UserInfractions__ reset!**", delete_after=3)

    async def check_table_user_infractions(self) -> bool:
        """ Checks if the UserInfractions table exists """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'UserInfractions'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True


    async def insert_user_infraction(self, user_id: int, infr_type: str, reason: str, timestamp: int, perpetrator: int) -> None:
        """ Insert a warning into the system. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO UserInfractions (
            user_id, infraction_type, infraction_reason,
            infraction_ts, perpetrator)
            VALUES (%s, %s, %s, %s, %s)""",
            (user_id, infr_type, reason, timestamp, perpetrator))
        await db.commit()
        await mycursor.close()

    async def get_user_infractions(self, user_id: int) -> List[List[Union[str, int]]]:
        """ Gets all infractions from a user. """

        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM UserInfractions WHERE user_id = {user_id}")
        user_infractions = await mycursor.fetchall()
        await mycursor.close()
        return user_infractions

    async def get_user_infraction_by_infraction_id(self, infraction_id: int) -> List[List[Union[str, int]]]:
        """ Gets a specific infraction by ID. """

        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM UserInfractions WHERE infraction_id = {infraction_id}")
        user_infractions = await mycursor.fetchall()
        await mycursor.close()
        return user_infractions

    async def remove_user_infraction(self, infraction_id: int) -> None:
        """ Removes a specific infraction by ID. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserInfractions WHERE infraction_id = %s", (infraction_id,))
        await db.commit()
        await mycursor.close()

    async def remove_user_infractions(self, user_id: int) -> None:
        """ Removes all infractions of a user by ID. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserInfractions WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

    async def edit_user_infractions(self, infraction_id: int, new_reason: str) -> None:
        """ Edits a infraction of a user by ID. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserInfractions SET infraction_reason = %s WHERE infraction_id = %s", (new_reason, infraction_id,))
        await db.commit()
        await mycursor.close()
