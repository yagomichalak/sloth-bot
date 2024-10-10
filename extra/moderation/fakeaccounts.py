# import.standard
import os
from typing import List, Union

# import.thirdparty
import discord
from discord.ext import commands

# import.local
from extra import utils
from extra.prompt.menu import Confirm
from mysqldb import DatabaseCore

# variables.role
allowed_roles = [int(os.getenv('OWNER_ROLE_ID', 123)), int(os.getenv('ADMIN_ROLE_ID', 123)), int(os.getenv('MOD_ROLE_ID', 123))]

class ModerationFakeAccountsTable(commands.Cog):
    
    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

    @commands.command(aliases=['link_fake', 'linkfake', 'add_fake', 'addfake', 'lfa'])
    @utils.is_allowed(allowed_roles, throw_exc=True)
    async def link_fake_account(self, ctx, member: Union[discord.User, discord.Member] = None, fake_member: Union[discord.User, discord.Member] = None) -> None:
        """ Links a member to their fake account.
        :param member: The member's main account.
        :param fake_member: The member's fake account.
        
        PS: The order you link the accounts doesn't matter. """

        author = ctx.author

        if not member:
            return await ctx.send(f"**Please, inform the member to link the account to, {author.mention}!**")

        if not fake_member:
            return await ctx.send(f"**Please, inform the member's fake account to link to the other one, {author.mention}!**")

        if member.id == fake_member.id:
            return await ctx.send(f"**Accounts can't be the same, {author.mention}!**")

        
        if await self.get_fake_account(member.id, fake_member.id):
            return await ctx.send(f"**<@{member.id}> is already associated with <@{fake_member.id}>, {author.mention}!**")

        await self.insert_fake_account(member.id, fake_member.id)
        await ctx.send(f"**Successfully associated `{member}` with `{fake_member}`, {author.mention}!**")

    @commands.command(aliases=['unlink_fakes', 'unlinkfakes', 'dissociate_fakes', 'remove_fakes', 'removefakes', 'ufa'])
    @utils.is_allowed(allowed_roles, throw_exc=True)
    async def unlink_fake_accounts(self, ctx, member: Union[discord.Member, discord.User] = None) -> None:
        """ Unlinks all associations with a specific member.
        :param member: The member to dissociate.
        :param fake_member: The member's fake account.
        
        PS: The order you link the accounts doesn't matter. """

        author = ctx.author

        if not member:
            return await ctx.send(f"**Please, inform the member to link the account to, {author.mention}!**")
        
        if not (fakes := await self.get_fake_accounts(member.id)):
            return await ctx.send(f"**There are no accounts associated with <@{member.id}>, {author.mention}!**")

        confirm = await Confirm(f"Are you sure you want to dissociate **{member}** from `{len(fakes)}` accounts, {author.mention}?").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it, then, {author.mention}!**")

        await self.delete_fake_accounts(member.id)
        await ctx.send(f"**Successfully dissociated `{member}` from `{len(fakes)}` accounts, {author.mention}!**")

    @commands.command(aliases=['fakes'])
    @utils.is_allowed(allowed_roles, throw_exc=True)
    async def fake_accounts(self, ctx, member: Union[discord.Member, discord.User] = None) -> None:
        """ Shows fake accounts associated with a user.
        :param member: The user to show the fake accounts from. """

        author = ctx.author

        if not member:
            return await ctx.send(f"**Please, inform a member to check, {author.mention}!**")

        fake_accounts = await self.get_fake_accounts(member.id)
        if not fake_accounts:
            return await ctx.send(f"**{member.display_name} doesn't have fake accounts, {author.mention}!**")
        users = []
        for user in fake_accounts:
            users.append(f"<@{user[0]}>")
            users.append(f"<@{user[1]}>")
        
        users = set(users)
        users.discard(f"<@{member.id}>")
        users = list(users)

        formatted_users = ', '.join(users)

        embed = discord.Embed(
            title="__Fake Accounts__:",
            description=f"Fake accounts associated with {member.display_name}:\n{formatted_users}",
            color=member.color
        )

        embed.set_thumbnail(url=member.display_avatar)
        embed.set_author(name=f"{member} ({member.id})", icon_url=member.display_avatar)
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_fake_accounts(self, ctx) -> None:
        """ (ADM) Creates the FakeAccounts table. """

        if await self.check_table_fake_accounts_exists():
            return await ctx.send("**Table __FakeAccounts__ already exists!**")

        await ctx.message.delete()
        await self.db.execute_query("""CREATE TABLE FakeAccounts (
            user_id BIGINT NOT NULL, 
            fake_user_id BIGINT NOT NULL,
            PRIMARY KEY (user_id, fake_user_id)
            )""")

        return await ctx.send("**Table __FakeAccounts__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_fake_accounts(self, ctx) -> None:
        """ (ADM) Creates the FakeAccounts table """
        
        if not await self.check_table_fake_accounts_exists():
            return await ctx.send("**Table __FakeAccounts__ doesn't exist!**")
        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE FakeAccounts")

        return await ctx.send("**Table __FakeAccounts__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_fake_accounts(self, ctx):
        """ (ADM) Resets the FakeAccounts table. """

        if not await self.check_table_fake_accounts_exists():
            return await ctx.send("**Table __FakeAccounts__ doesn't exist yet**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM FakeAccounts")

        return await ctx.send("**Table __FakeAccounts__ reset!**", delete_after=3)

    async def check_table_fake_accounts_exists(self) -> bool:
        """ Checks if the FakeAccounts table exists """

        return await self.db.table_exists("FakeAccounts")

    async def get_fake_account(self, member_id: int, fake_member_id: int) -> List[int]:
        """ Gets a specific fake account.
        :param member_id: The ID of the user's main account.
        :param fake_member_id: The ID of the user's fake account. """

        return await self.db.execute_query("""
        SELECT * FROM FakeAccounts 
        WHERE user_id = %s AND fake_user_id = %s
        OR user_id = %s AND fake_user_id = %s
        """, (member_id, fake_member_id, fake_member_id, member_id), fetch="one")

    async def get_fake_accounts(self, account_id: int) -> List[List[int]]:
        """ Gets all fake account associations with a user account.
        :param account_id: The ID of the account to get the associations from. """

        all_fake_accounts = []

        sql = "SELECT * FROM FakeAccounts WHERE user_id = %s OR fake_user_id = %s"
        origin = await self.db.execute_query(sql, (account_id, account_id), fetch="all")
        all_fake_accounts.extend(origin)

        for fake_account in all_fake_accounts:
            accounts = []

            # First combination
            first = await self.db.execute_query(sql, (fake_account[0], fake_account[0]), fetch="all")
            accounts.extend(first)

            # Second combination
            second = await self.db.execute_query(sql, (fake_account[1], fake_account[1]), fetch="all")
            accounts.extend(second)

            for account in list(set(accounts)):
                if account not in all_fake_accounts:
                    all_fake_accounts.append(account)

        return list(set(all_fake_accounts))
    
    async def insert_fake_account(self, user_id: int, fake_account_id: int) -> None:
        """ Inserts a fake account association into the database.
        :param user_id: The ID of the user's main account.
        :param fake_account_id: The ID of the user's fake account. """

        await self.db.execute_query("INSERT INTO FakeAccounts (user_id, fake_user_id) VALUES (%s, %s)", (user_id, fake_account_id))

    async def delete_fake_account(self, fake_account_id: int) -> None:
        """ Deletes associations with a fake account.
        :param fake_account_id: The ID of the fake account. """

        await self.db.execute_query("DELETE FROM FakeAccounts WHERE fake_user_id = %s", (fake_account_id,))

    async def delete_fake_accounts(self, user_id: int) -> None:
        """ Deletes associations with all fake accounts.
        :param user_id: The ID of the user's main account. """

        await self.db.execute_query("DELETE FROM FakeAccounts WHERE user_id = %s OR fake_user_id = %s", (user_id, user_id))
