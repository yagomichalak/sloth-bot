import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List

class ModerationFakeAccountsTable(commands.Cog):
    
    def __init__(self, client) -> None:
        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_fake_accounts(self, ctx) -> None:
        """ (ADM) Creates the FakeAccounts table. """

        if await self.check_table_fake_accounts_exists():
            return await ctx.send("**Table __FakeAccounts__ already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE FakeAccounts (
            user_id BIGINT NOT NULL, 
            fake_user_id BIGINT NOT NULL,
            PRIMARY KEY (user_id, fake_user_id)
            )""")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __FakeAccounts__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_fake_accounts(self, ctx) -> None:
        """ (ADM) Creates the FakeAccounts table """
        
        if not await self.check_table_fake_accounts_exists():
            return await ctx.send("**Table __FakeAccounts__ doesn't exist!**")
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE FakeAccounts")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __FakeAccounts__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_fake_accounts(self, ctx):
        """ (ADM) Resets the FakeAccounts table. """

        if not await self.check_table_fake_accounts_exists():
            return await ctx.send("**Table __FakeAccounts__ doesn't exist yet**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM FakeAccounts")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __FakeAccounts__ reset!**", delete_after=3)

    async def check_table_fake_accounts_exists(self) -> bool:
        """ Checks if the FakeAccounts table exists """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'FakeAccounts'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True

    async def get_fake_accounts(self, account_id: int) -> List[List[int]]:
        """ Gets all fake account associations with a user account.
        :param account_id: The ID of the account to get the associations from. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM FakeAccounts WHERE user_id = %s OR fake_account_id = %s", (account_id, account_id))
        fake_accounts = await mycursor.fetchall()
        await mycursor.close()
        return fake_accounts

    
    async def insert_fake_account(self, user_id: int, fake_account_id: int) -> None:
        """ Inserts a fake account association into the database.
        :param user_id: The ID of the user's main account.
        :param fake_account_id: The ID of the user's fake account. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO FakeAccounts (user_id, fake_account_id) VALUES (%s, %s)", (user_id, fake_account_id))
        await db.commit()
        await mycursor.close()

    async def delete_fake_account(self, fake_account_id: int) -> None:
        """ Deletes associations with a fake account.
        :param fake_account_id: The ID of the fake account. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM FakeAccounts WHERE fake_account_id = %s", (fake_account_id,))
        await db.commit()
        await mycursor.close()

    async def delete_fake_accounts(self, user_id: int) -> None:
        """ Deletes associations with all fake accounts.
        :param user_id: The ID of the user's main account. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM FakeAccounts WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()
