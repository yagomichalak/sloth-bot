from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List


class BypassFirewallTable(commands.Cog):
    """ Category for the BypassFirewall table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_bypass_firewall(self, ctx) -> None:
        """ (ADM) Creates the BypassFirewall table. """

        if await self.check_table_bypass_firewall_exists():
            return await ctx.send("**Table __BypassFirewall__ already exists!**")

        await ctx.message.delete()
        await self.db.execute_query("""
            CREATE TABLE BypassFirewall (
                user_id BIGINT NOT NULL,
                PRIMARY KEY (user_id)
            )""")
        await self.db.execute_query("INSERT INTO Firewall VALUES(0)")

        return await ctx.send("**Table __BypassFirewall__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_bypass_firewall(self, ctx) -> None:
        """ (ADM) Creates the BypassFirewall table """

        if not await self.check_table_bypass_firewall_exists():
            return await ctx.send("**Table __BypassFirewall__ doesn't exist!**")
        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE BypassFirewall")

        return await ctx.send("**Table __BypassFirewall__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_bypass_firewall(self, ctx):
        """ (ADM) Resets the BypassFirewall table. """

        if not await self.check_table_bypass_firewall_exists():
            return await ctx.send("**Table __BypassFirewall__ doesn't exist yet**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM BypassFirewall")

        return await ctx.send("**Table __BypassFirewall__ reset!**", delete_after=3)

    # ===== SHOW ===== 
    async def check_table_bypass_firewall_exists(self) -> bool:
        """ Checks if the BypassFirewall table exists """

        return await self.db.table_exists("BypassFirewall")

    # ===== INSERT =====
    async def insert_bypass_firewall_user(self, user_id: int) -> None:
        """ Inserts a user into the BypassFirewall table.
        :param user_id: The ID of the user to insert. """

        await self.db.execute_query("INSERT INTO BypassFirewall (user_id) VALUES (%s)", (user_id,))

    # ===== SELECT =====
    async def get_bypass_firewall_user(self, user_id: int) -> List[int]:
        """ Gets a user from the BypassFirewall table.
        :param user_id: The ID of the user to get. """

        return await self.db.execute_query("SELECT * FROM BypassFirewall WHERE user_id = %s", (user_id,), fetch="one")

    async def get_bypass_firewall_users(self) -> List[List[int]]:
        """ Gets all users from the BypassFirewall table. """

        return await self.db.execute_query("SELECT * FROM BypassFirewall", fetch="all")

    # ===== DELETE =====
    async def delete_bypass_firewall_user(self, user_id: int) -> None:
        """ Deletes a user from the BypassFirewall table.
        :param user_id: The ID of the user to delete. """

        await self.db.execute_query("DELETE FROM BypassFirewall WHERE user_id = %s", (user_id,))
    

class ModerationFirewallTable(commands.Cog):
    """ Category for the Firewall system and its commands and methods. """

    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_firewall(self, ctx) -> None:
        """ (ADM) Creates the Firewall table. """

        if await self.check_table_firewall_exists():
            return await ctx.send("**Table __Firewall__ already exists!**")

        await ctx.message.delete()
        await self.db.execute_query("""CREATE TABLE Firewall (
            state TINYINT(1) NOT NULL DEFAULT 0)""")
        await self.db.execute_query("INSERT INTO Firewall VALUES(0)")

        return await ctx.send("**Table __Firewall__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_firewall(self, ctx) -> None:
        """ (ADM) Creates the Firewall table """

        if not await self.check_table_firewall_exists():
            return await ctx.send("**Table __Firewall__ doesn't exist!**")
        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE Firewall")

        return await ctx.send("**Table __Firewall__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_firewall(self, ctx):
        """ (ADM) Resets the Firewall table. """

        if not await self.check_table_firewall_exists():
            return await ctx.send("**Table __Firewall__ doesn't exist yet**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM Firewall")
        await self.db.execute_query("INSERT INTO Firewall VALUES(0)")

        return await ctx.send("**Table __Firewall__ reset!**", delete_after=3)

    async def check_table_firewall_exists(self) -> bool:
        """ Checks if the Firewall table exists """

        return await self.db.table_exists("Firewall")

    async def set_firewall_state(self, state: int) -> None:
        """ Sets the firewall state to either true or false. 
        :param state: The state of the firewall to set. """

        await self.db.execute_query("UPDATE Firewall SET state = %s", (state,))

    async def get_firewall_state(self) -> int:
        """ Gets the firewall's current state. """

        return await self.db.execute_query("SELECT state FROM Firewall", fetch="one")

