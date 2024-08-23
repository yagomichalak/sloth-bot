# import.standard
from typing import List, Union

# import.thirdparty
import discord
from discord.ext import commands

# import.local
from mysqldb import DatabaseCore

class ModeratedNicknamesTable(commands.Cog):
    """ Class for the ModeratedNicknames table. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_moderated_nicknames(self, ctx) -> None:
        """ Creates the ModeratedNicknames table in the database. """

        member: discord.Member = ctx.author
        if await self.check_moderated_nicknames_table_exists():
            return await ctx.send(f"**The ModeratedNicknames table already exists, {member.mention}!**")

        await self.db.execute_query("""CREATE TABLE ModeratedNicknames (
            user_id BIGINT NOT NULL,
            nickname VARCHAR(100) NOT NULL,
            PRIMARY KEY (user_id)
            ) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)

        await ctx.send("**`ModeratedNicknames` table created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_moderated_nicknames(self, ctx) -> None:
        """ Drops the ModeratedNicknames table from the database. """

        member: discord.Member = ctx.author
        if not await self.check_moderated_nicknames_table_exists():
            return await ctx.send(f"**The ModeratedNicknames table doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE ModeratedNicknames")
        await ctx.send("**`ModeratedNicknames` table dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_moderated_nicknames(self, ctx) -> None:
        """ Resets the ModeratedNicknames table in the database. """

        member: discord.Member = ctx.author
        if not await self.check_moderated_nicknames_table_exists():
            return await ctx.send(f"**The ModeratedNicknames table doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM ModeratedNicknames")
        await ctx.send("**`ModeratedNicknames` table reset!**")

    async def check_moderated_nicknames_table_exists(self) -> bool:
        """ Checks whether the ModeratedNicknames table exists in the database. """

        return await self.db.table_exists("ModeratedNicknames")

    async def insert_moderated_nickname(self, user_id: int, nickname: str) -> None:
        """ Inserts a user into the ModeratedNicknames table.
        :param user_id: The ID of the user to insert.
        :param nickname: The nickname the user had. """

        await self.db.execute_query("INSERT INTO ModeratedNicknames (user_id, nickname) VALUES (%s, %s)", (user_id, nickname))

    async def get_moderated_nickname(self, user_id: int) -> List[Union[int, str]]:
        """ Gets a user from the ModeratedNickname table.
        :param user_id: The ID of the user to get. """

        return await self.db.execute_query("SELECT * FROM ModeratedNicknames WHERE user_id = %s", (user_id,), fetch="one")

    async def delete_moderated_nickname(self, user_id: int) -> None:
        """ Deletes a user from the ModeratedNicknames table.
        :param user_id: The ID of the user to delete. """

        await self.db.execute_query("DELETE FROM ModeratedNicknames WHERE user_id = %s", (user_id,))
