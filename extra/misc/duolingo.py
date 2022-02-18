from discord.ext import commands
from mysqldb import the_database
from typing import List, Union

class DuolingoProfileTable(commands.Cog):
    """ Class for managing the DuolingoProfile table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_duolingo_profile(self, ctx: commands.Context) -> None:
        """ Creates the DuolingoProfile table. """

        member = ctx.author
        await ctx.message.delete()

        if await self.check_duolingo_profile_exists():
            return await ctx.send(f"**Table `DuolingoProfile` already exists, {member.mention}!**")
        
        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE DuolingoProfile (
                user_id BIGINT NOT NULL,
                duo_name VARCHAR(100),
                PRIMARY KEY(user_id),
                CONSTRAINT fk_duo_user_id FOREIGN KEY (user_id) REFERENCES UserCurrency (user_id) ON DELETE CASCADE ON UPDATE CASCADE
            )""")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `DuolingoProfile` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_duolingo_profile(self, ctx: commands.Context) -> None:
        """ Creates the DuolingoProfile table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_duolingo_profile_exists():
            return await ctx.send(f"**Table `DuolingoProfile` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE DuolingoProfile")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `DuolingoProfile` dropped, {member.mention}!**")


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_duolingo_profile(self, ctx: commands.Context) -> None:
        """ Creates the DuolingoProfile table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_duolingo_profile_exists():
            return await ctx.send(f"**Table `DuolingoProfile` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM DuolingoProfile")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `DuolingoProfile` reset, {member.mention}!**")

    async def check_duolingo_profile_exists(self) -> bool:
        """ Checks whether the DuolingoProfile table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'DuolingoProfile'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_duo_profile(self, user_id: int, duo_name: str) -> None:
        """ Inserts a Duolingo Profile.
        :param user_id: The ID of the user to insert.
        :param duo_name: The user's duolingo username. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO DuolingoProfile (user_id, duo_name) VALUES (%s, %s)", (user_id, duo_name))
        await db.commit()
        await mycursor.close()

    async def get_duo_profile(self, user_id: int) -> List[Union[int, str]]:
        """ Gets a Duolingo Profile.
        :param user_id: The ID of the user to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM DuolingoProfile WHERE user_id = %s", (user_id,))
        duo_profile = await mycursor.fetchone()
        await mycursor.close()
        return duo_profile

    async def update_duo_profile(self, user_id: int, duo_name: str) -> None:
        """ Updates a Duolingo Profile.
        :param user_id: The ID of the user to update.
        :param duo_name: The user's new duolingo username. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE DuolingoProfile SET duo_name = %s WHERE user_id = %s", (duo_name, user_id))
        await db.commit()
        await mycursor.close()

    async def delete_duo_profile(self, user_id: int) -> None:
        """ Deletes a Duolingo Profile.
        :param user_id: The ID of the user to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM DuolingoProfile WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()