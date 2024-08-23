# import.standard
from typing import List

# import.thirdparty
from discord.ext import commands

# import.local
from mysqldb import DatabaseCore

class CurseTable(commands.Cog):
    """ Class for managing the curse table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_cursed_member(self, ctx) -> None:
        """ (ADM) Creates the CursedMember table. """

        await self.db.execute_query("CREATE TABLE CursedMember (user_id bigint)")
        return await ctx.send("**Table CursedMember was created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_cursed_member(self, ctx) -> None:
        """ (ADM) Drops the CursedMember table. """

        await self.db.execute_query("DROP TABLE CursedMember")
        return await ctx.send("**Table CursedMember was dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_cursed_member(self, ctx) -> None:
        """ (ADM) Resets the CursedMember table. """

        await self.db.execute_query("DELETE FROM CursedMember")
        return await ctx.send("**Table CursedMember was reseted!**", delete_after=3)

    async def insert_cursed_member(self, user_id: int) -> None:
        """ Insert the cursed member into the database.
        :param user_id: The ID of the user that's being cursed. """

        await self.db.execute_query("INSERT INTO CursedMember (user_id) VALUES (%s)", (user_id))

    async def get_cursed_member(self, user_id: int) -> List[List[int]]:
        """ Gets the cursed member from the database. """

        return await self.db.execute_query("SELECT * FROM CursedMember WHERE user_id = %s", (user_id,), fetch="one")

    async def delete_cursed_member(self) -> bool:
        """ Deletes the cursed member from the database. """

        cursed_member = await self.db.execute_query("SELECT * FROM CursedMember", fetch="one")
        if not cursed_member:
            return False

        await self.db.execute_query("DELETE FROM CursedMember WHERE user_id = %s", (cursed_member[0],))
        return True
