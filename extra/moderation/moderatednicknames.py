import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union


class ModeratedNicknamesTable(commands.Cog):
    """ Class for the ModeratedNicknames table. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_moderated_nicknames(self, ctx) -> None:
        """ Creates the ModeratedNicknames table in the database. """

        member: discord.Member = ctx.author
        if await self.check_moderated_nicknames_table_exists():
            return await ctx.send(f"**The ModeratedNicknames table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE ModeratedNicknames (
            user_id BIGINT NOT NULL,
            nickname VARCHAR(100) NOT NULL,
            PRIMARY KEY (user_id)
            ) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**`ModeratedNicknames` table created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_moderated_nicknames(self, ctx) -> None:
        """ Drops the ModeratedNicknames table from the database. """

        member: discord.Member = ctx.author
        if not await self.check_moderated_nicknames_table_exists():
            return await ctx.send(f"**The ModeratedNicknames table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE ModeratedNicknames")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**`ModeratedNicknames` table dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_moderated_nicknames(self, ctx) -> None:
        """ Resets the ModeratedNicknames table in the database. """

        member: discord.Member = ctx.author
        if not await self.check_moderated_nicknames_table_exists():
            return await ctx.send(f"**The ModeratedNicknames table doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ModeratedNicknames")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**`ModeratedNicknames` table reset!**")

    async def check_moderated_nicknames_table_exists(self) -> bool:
        """ Checks whether the ModeratedNicknames table exists in the database. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'ModeratedNicknames'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_moderated_nickname(self, user_id: int, nickname: str) -> None:
        """ Inserts a user into the ModeratedNicknames table.
        :param user_id: The ID of the user to insert.
        :param nickname: The nickname the user had. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO ModeratedNicknames (user_id, nickname) VALUES (%s, %s)", (user_id, nickname))
        await db.commit()
        await mycursor.close()

    async def get_moderated_nickname(self, user_id: int) -> List[Union[int, str]]:
        """ Gets a user from the ModeratedNickname table.
        :param user_id: The ID of the user to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM ModeratedNicknames WHERE user_id = %s", (user_id,))
        mn_user = await mycursor.fetchone()
        await mycursor.close()
        return mn_user

    async def delete_moderated_nickname(self, user_id: int) -> None:
        """ Deletes a user from the ModeratedNicknames table.
        :param user_id: The ID of the user to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ModeratedNicknames WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()