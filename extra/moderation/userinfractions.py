from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List, Union


class ModerationUserInfractionsTable(commands.Cog):
    
    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_infractions(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table. """

        if await self.check_table_user_infractions():
            return await ctx.send("**Table __UserInfractions__ already exists!**")

        await ctx.message.delete()
        await self.db.execute_query("""CREATE TABLE UserInfractions (
            user_id BIGINT NOT NULL,
            infraction_type VARCHAR(7) NOT NULL,
            infraction_reason VARCHAR(100) DEFAULT NULL,
            infraction_ts BIGINT NOT NULL,
            infraction_id BIGINT NOT NULL AUTO_INCREMENT,
            perpetrator BIGINT NOT NULL,
            PRIMARY KEY (infraction_id)
            ) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci""")

        return await ctx.send("**Table __UserInfractions__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_infractions(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table """
        if not await self.check_table_user_infractions():
            return await ctx.send("**Table __UserInfractions__ doesn't exist!**")
        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE UserInfractions")

        return await ctx.send("**Table __UserInfractions__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_infractions(self, ctx) -> None:
        """ (ADM) Creates the UserInfractions table """

        if not await self.check_table_user_infractions():
            return await ctx.send("**Table __UserInfractions__ doesn't exist yet!**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM UserInfractions")

        return await ctx.send("**Table __UserInfractions__ reset!**", delete_after=3)

    async def check_table_user_infractions(self) -> bool:
        """ Checks if the UserInfractions table exists """

        return await self.db.table_exists("UserInfractions")

    async def insert_user_infraction(self, user_id: int, infr_type: str, reason: str, timestamp: int, perpetrator: int) -> None:
        """ Insert a warning into the system. """

        await self.db.execute_query("""
            INSERT INTO UserInfractions (
            user_id, infraction_type, infraction_reason,
            infraction_ts, perpetrator)
            VALUES (%s, %s, %s, %s, %s)""",
            (user_id, infr_type, reason, timestamp, perpetrator))

    async def get_user_infractions(self, user_id: int) -> List[List[Union[str, int]]]:
        """ Gets all infractions from a user. """

        return await self.db.execute_query(f"SELECT * FROM UserInfractions WHERE user_id = {user_id}", fetch="all")

    async def get_user_infraction_by_infraction_id(self, infraction_id: int) -> List[List[Union[str, int]]]:
        """ Gets a specific infraction by ID. """

        return await self.db.execute_query(f"SELECT * FROM UserInfractions WHERE infraction_id = {infraction_id}", fetch="all")

    async def remove_user_infraction(self, infraction_id: int) -> None:
        """ Removes a specific infraction by ID. """

        await self.db.execute_query("DELETE FROM UserInfractions WHERE infraction_id = %s", (infraction_id,))

    async def remove_user_infractions(self, user_id: int) -> None:
        """ Removes all infractions of a user by ID. """

        await self.db.execute_query("DELETE FROM UserInfractions WHERE user_id = %s", (user_id,))

    async def edit_user_infractions(self, infraction_id: int, new_reason: str) -> None:
        """ Edits a infraction of a user by ID. """

        await self.db.execute_query("UPDATE UserInfractions SET infraction_reason = %s WHERE infraction_id = %s", (new_reason, infraction_id,))
