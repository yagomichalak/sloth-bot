from discord.ext import commands
from mysqldb import the_database
from typing import List

class SlothboardTable(commands.Cog):
    """ Class for managing the Slothboard table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_slothboard(self, ctx) -> None:
        """ (ADM) Creates the Slothboard table. """

        if await self.table_slothboard_exists():
            return await ctx.send("**The `Slothboard` table already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE Slothboard (
                message_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                PRIMARY KEY (message_id, channel_id)
            )""")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Created `Slothboard` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_slothboard(self, ctx) -> None:
        """ (ADM) Drops the Slothboard table. """

        if not await self.table_slothboard_exists():
            return await ctx.send("**The `Slothboard` table doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Slothboard")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Dropped `Slothboard` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_slothboard(self, ctx) -> None:
        """ (ADM) Resets the Slothboard table. """

        if not await self.table_slothboard_exists():
            return await ctx.send("**The `Slothboard` table doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Slothboard")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Reset `Slothboard` table!**")

    async def table_slothboard_exists(self) -> bool:
        """ Checks whether the Slothboard table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Slothboard'")
        table_info = await mycursor.fetchone()
        await mycursor.close()
        if table_info:
            return True
        else:
            return False

    async def insert_slothboard_message(self, message_id: int, channel_id: int) -> None:
        """ Inserts a Slothboard message.
        :param message_id: The ID of the original message.
        :param channel_id: The ID of the message's original channel.  """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO Slothboard (message_id, channel_id) VALUES (%s, %s)", (
            message_id, channel_id))
        await db.commit()
        await mycursor.close()
        
    async def get_slothboard_message(self, message_id: int, channel_id: int) -> List[int]:
        """ Gets a Slothboard message.
        :param message_id: The ID of the original message.
        :param channel_id: The ID of the message's original channel. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Slothboard WHERE message_id = %s AND channel_id = %s", (message_id, channel_id))
        slothboard_message = await mycursor.fetchone()
        await mycursor.close()
        return slothboard_message