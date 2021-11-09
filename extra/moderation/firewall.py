import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List

class BypassFirewallTable(commands.Cog):
    """ Category for the BypassFirewall table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_bypass_firewall(self, ctx) -> None:
        """ (ADM) Creates the BypassFirewall table. """

        if await self.check_table_bypass_firewall_exists():
            return await ctx.send("**Table __BypassFirewall__ already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE BypassFirewall (
                user_id BIGINT NOT NULL,
                PRIMARY KEY (user_id)
            )""")
        await mycursor.execute("INSERT INTO Firewall VALUES(0)")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __BypassFirewall__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_bypass_firewall(self, ctx) -> None:
        """ (ADM) Creates the BypassFirewall table """

        if not await self.check_table_bypass_firewall_exists():
            return await ctx.send("**Table __BypassFirewall__ doesn't exist!**")
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE BypassFirewall")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __BypassFirewall__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_bypass_firewall(self, ctx):
        """ (ADM) Resets the BypassFirewall table. """

        if not await self.check_table_bypass_firewall_exists():
            return await ctx.send("**Table __BypassFirewall__ doesn't exist yet**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM BypassFirewall")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __BypassFirewall__ reset!**", delete_after=3)

    # ===== SHOW ===== 
    async def check_table_bypass_firewall_exists(self) -> bool:
        """ Checks if the BypassFirewall table exists """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'BypassFirewall'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True

    # ===== INSERT =====
    async def insert_bypass_firewall_user(self, user_id: int) -> None:
        """ Inserts a user into the BypassFirewall table.
        :param user_id: The ID of the user to insert. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO BypassFirewall (user_id) VALUES (%s)", (user_id,))
        await db.commit()
        await mycursor.close()

    # ===== SELECT =====
    async def get_bypass_firewall_user(self, user_id: int) -> List[int]:
        """ Gets a user from the BypassFirewall table.
        :param user_id: The ID of the user to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM BypassFirewall WHERE user_id = %s", (user_id,))
        bf_user = await mycursor.fetchone()
        await mycursor.close()
        return bf_user

    async def get_bypass_firewall_users(self) -> List[List[int]]:
        """ Gets all users from the BypassFirewall table. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM BypassFirewall")
        bf_users = await mycursor.fetchall()
        await mycursor.close()
        return bf_users

    # ===== DELETE =====
    async def delete_bypass_firewall_user(self, user_id: int) -> None:
        """ Deletes a user from the BypassFirewall table.
        :param user_id: The ID of the user to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM BypassFirewall WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()
    

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
        """ Checks if the Firewall table exists """

        mycursor, _ = await the_database()
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

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT state FROM Firewall")
        fw_state = await mycursor.fetchone()
        await mycursor.close()
        return fw_state[0]

