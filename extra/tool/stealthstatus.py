# import.standard
from typing import List

# import.thirdparty
from discord.ext import commands

# import.local
from mysqldb import DatabaseCore

class StealthStatusTable(commands.Cog):
    """ Class for the StealthStatus table and its commands and methods. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_stealth_status(self, ctx) -> None:
        """ (ADM) Creates the StealthStatus table. """

        if await self.check_table_stealth_status_exists():
            return await ctx.send("**Table __StealthStatus__ already exists!**")

        await ctx.message.delete()
        await self.db.execute_query("""
            CREATE TABLE StealthStatus (
                user_id BIGINT NOT NULL,
                state TINYINT(1) DEFAULT 0,
                PRIMARY KEY (user_id)
            )
        """)

        return await ctx.send("**Table __StealthStatus__ created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_stealth_status(self, ctx) -> None:
        """ (ADM) Creates the StealthStatus table """

        if not await self.check_table_stealth_status_exists():
            return await ctx.send("**Table __StealthStatus__ doesn't exist!**")
        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE StealthStatus")

        return await ctx.send("**Table __StealthStatus__ dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_stealth_status(self, ctx):
        """ (ADM) Resets the StealthStatus table. """

        if not await self.check_table_stealth_status_exists():
            return await ctx.send("**Table __StealthStatus__ doesn't exist yet**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM StealthStatus")

        return await ctx.send("**Table __StealthStatus__ reset!**")

    async def check_table_stealth_status_exists(self) -> bool:
        """ Checks whether the StealthStatus table exists """

        return await self.db.table_exists("StealthStatus")

    async def insert_stealth_status(self, user_id: int, state: int = 1) -> None:
        """ Inserts a stealth status for a user.
        :param user_id: The ID of the user to insert.
        :param state: The initial stealth status to insert. [DEFAULT = 1] """

        await self.db.execute_query("INSERT INTO StealthStatus (user_id, state) VALUES (%s, %s)", (user_id, state))

    async def get_stealth_status(self, user_id: int) -> List[int]:
        """ Gets the user's current StealthStatus state.
        :parma user_id: The ID of the user from whom to get the status. """

        return await self.db.execute_query("SELECT * from StealthStatus where user_id = %s", (user_id,), fetch="one")

    async def update_stealth_status(self, user_id: int, state: int) -> None:
        """ Updates the user's StealthStatus state.
        :param user_id: The ID of the user to update.
        :param state: The state of the StealthStatus to set. """

        await self.db.execute_query("UPDATE StealthStatus SET state = %s WHERE user_id = %s", (state, user_id))
