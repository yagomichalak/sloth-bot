import discord
from discord.ext import commands
from mysqldb import the_database


class ModerationFirewallTable(commands.Cog):
    """ Category for the Firewall system and its commands and methods. """

    def __init__(self, client) -> None:
        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_firewall(self, ctx) -> None:
        """ (ADM) Creates the Firewall table. """

        if await self.check_table_firewall_exists():
            return await ctx.send("**Table __Firewall__ already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE Firewall (
            state TINYINT(1) NOT NULL DEFAULT 0)""")
        await mycursor.execute("INSERT INTO Firewall VALUES(0)")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __Firewall__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_firewall(self, ctx) -> None:
        """ (ADM) Creates the Firewall table """

        if not await self.check_table_firewall_exists():
            return await ctx.send("**Table __Firewall__ doesn't exist!**")
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Firewall")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __Firewall__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_firewall(self, ctx):
        """ (ADM) Resets the Firewall table. """

        if not await self.check_table_firewall_exists():
            return await ctx.send("**Table __Firewall__ doesn't exist yet**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Firewall")
        await mycursor.execute("INSERT INTO Firewall VALUES(0)")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __Firewall__ reset!**", delete_after=3)

    async def check_table_firewall_exists(self) -> bool:
        """ Checks if the MutedMember table exists """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Firewall'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True

    async def set_firewall_state(self, state: int) -> None:
        """ Sets the firewall state to either true or false. 
        :param state: The state of the firewall to set. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE Firewall SET state = %s", (state,))
        await db.commit()
        await mycursor.close()


    async def get_firewall_state(self) -> int:
        """ Gets the firewall's current state. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT state FROM Firewall")
        fw_state = await mycursor.fetchone()
        await mycursor.close()
        return fw_state[0]

