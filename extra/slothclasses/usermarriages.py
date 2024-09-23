# import.standard
from typing import List, Optional, Union

# import.thirdparty
import discord
from discord.ext import commands

# import.local
from extra import utils
from mysqldb import DatabaseCore


class UserMarriagesTable(commands.Cog):
    """ Class for the UserMarriages table and its commands and methods. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_marriages(self, ctx) -> None:
        """ Creates the UserMarriages table in the database. """

        member: discord.Member = ctx.author
        if await self.check_user_marriages_table_exists():
            return await ctx.send(f"**The UserMarriages table already exists, {member.mention}!**")

        await self.db.execute_query("""CREATE TABLE UserMarriages (
            user_id BIGINT NOT NULL,
            partner_id BIGINT NOT NULL,
            married_ts BIGINT NOT NULL,
            honeymoon_ts BIGINT DEFAULT NULL,
            PRIMARY KEY (user_id, partner_id)
            )
        """)

        await ctx.send(f"**`UserMarriages` table created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_marriages(self, ctx) -> None:
        """ Drops the UserMarriages table from the database. """

        member: discord.Member = ctx.author
        if not await self.check_user_marriages_table_exists():
            return await ctx.send(f"**The UserMarriages table doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE UserMarriages")

        await ctx.send(f"**`UserMarriages` table dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_marriages(self, ctx) -> None:
        """ Resets the UserMarriages table in the database. """

        member: discord.Member = ctx.author
        if not await self.check_user_marriages_table_exists():
            return await ctx.send(f"**The UserMarriages table doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM UserMarriages")

        await ctx.send(f"**`UserMarriages` table reset, {member.mention}!**")

    async def check_user_marriages_table_exists(self) -> bool:
        """ Checks whether the UserMarriages table exists in the database. """

        return await self.db.table_exists("UserMarriages")

    async def insert_user_marriage(self, user_id: int, partner_id: int) -> None:
        """ Inserts a user marriage.
        :param user_id: The ID of the user who proposed.
        :param partner_id: The proposed user's ID. """

        current_ts = await utils.get_timestamp()

        await self.db.execute_query("""
            INSERT INTO UserMarriages (
                user_id, partner_id, married_ts
            ) VALUES (%s, %s, %s)""", (user_id, partner_id, current_ts)
        )

    async def _get_user_marriage(self, user_id: int, partner_id: int) -> List[Union[str, int]]:
        """ Gets a specific user marriage.
        :param user_id: The married person's ID.
        :param """

        return await self.db.execute_query("""
            SELECT * FROM UserMarriages
            WHERE (user_id = %s AND partner_id = %s) OR (user_id = %s AND partner_id = %s)
        """, (user_id, partner_id, partner_id, user_id), fetch="one")

    async def _get_user_marriages(self, user_id: int) -> List[Union[str, int]]:
        """ Get the user's marriages.
        :param user_id: The user ID. """

        return await self.db.execute_query("SELECT * FROM UserMarriages WHERE user_id = %s OR partner_id = %s", (user_id, user_id), fetch="all")

    async def update_user_honeymoon_ts(self, user_id: int, partner_id: str) -> None:
        """ Updates the a marriage's honeymoon timestamp.
        :param user_id: The married user's ID.
        :param partner_id: The suitor's ID. """

        current_ts = await utils.get_timestamp()

        await self.db.execute_query("UPDATE UserMarriages SET honeymoon_ts = %s WHERE user_id = %s AND partner_id = %s", (current_ts, user_id, partner_id))

    async def delete_user_marriage(self, user_id: int, partner_id: int) -> None:
        """ Deletes a user marriage.
        :param user_id: The married user's ID.
        :param partner_id: The suitor's ID. """

        await self.db.execute_query("DELETE FROM UserMarriages WHERE user_id = %s AND partner_id = %s", (user_id, partner_id))
