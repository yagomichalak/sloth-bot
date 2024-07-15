import discord
from discord import slash_command, Option
from discord.ext import commands

import os
from typing import List, Dict, Optional
from extra import utils
from mysqldb import DatabaseCore

guild_ids: List[int] = [int(os.getenv("SERVER_ID", 123))]
sponsored_by_category_id: int = int(os.getenv("SPONSORED_BY_CATEGORY_ID", 123))


class SponsoredBy(commands.Cog):
    """ A category for managing the Sponsored by category
    and its features. """

    ping_cache: Dict[int, float] = {}

    def __init__(self, client: commands.Bot) -> None:
        """ The class init method. """

        self.client = client
        self.db = DatabaseCore()

    # Events

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to go. """

        print("The SponsoredBy cog is ready!")

    # Commands

    @slash_command(name="ping_role", guild_ids=guild_ids)
    @commands.has_permissions(administrator=True)
    async def ping_role(self, ctx: discord.ApplicationContext,
        role: Option(discord.Role, name="role_to_ping", description="Select the role to ping.", required=True)
    ) -> None:
        """ Pings a role in the 'SPONSERED BY:' category. """

        if not ctx.channel.category or ctx.channel.category.id != sponsored_by_category_id:
            return await ctx.respond(f"**You can only use this command in __<#{sponsored_by_category_id}>__ category!**", ephemeral=True)

        member_ts = self.ping_cache.get(ctx.author.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 300:
                return await ctx.respond(
                    f"**You are on cooldown to apply, try again in {(300-sub)/60:.1f} minutes**", ephemeral=True)

        if not await self.get_user_ping_permission(ctx.author.id):
            return await ctx.respond(f"**You don't have permission to ping here with this command!**", ephemeral=True)

        # self.ping_cache[ctx.author.id] = time_now
        role_ping = role.mention if role.name[0] != "@" else role
        await ctx.respond(content=role_ping, allowed_mentions=discord.AllowedMentions.all())

    @slash_command(name="add_ping_permission", guild_ids=guild_ids)
    @commands.has_permissions(administrator=True)
    async def add_ping_permission(self, ctx: discord.ApplicationContext,
        user: Option(discord.Member, description="The person to give the permission to.", required=True)
    ) -> None:
        """ Adds permission for a user to ping everyone
        in the 'SPONSORED BY:' category. """

        user_has_ping_perms = await self.get_user_ping_permission(user.id)
        if user_has_ping_perms:
            return await ctx.respond(f"**This user already has permission to ping in the __<#{sponsored_by_category_id}>__ category!**", ephemeral=True)

        await self.insert_user_ping_permission(user.id)
        await ctx.respond(f"**Now {user.mention} can ping __everyone__ in the __<#{sponsored_by_category_id}>__ category!**", ephemeral=True)

    @slash_command(name="delete_ping_permission", guild_ids=guild_ids)
    @commands.has_permissions(administrator=True)
    async def delete_ping_permission(self, ctx: discord.ApplicationContext,
        user: Option(discord.Member, description="The person to remove the permission from.", required=True)
    ) -> None:
        """ Removes permission from a user to ping everyone
        in the 'SPONSORED BY:' category. """

        user_has_ping_perms = await self.get_user_ping_permission(user.id)
        if not user_has_ping_perms:
            return await ctx.respond(f"**This user doesn't even have permission to ping in the __<#{sponsored_by_category_id}>__!**", ephemeral=True)

        await self.delete_user_ping_permission(user.id)
        await ctx.respond(f"**Now {user.mention} can no longer ping __everyone__ in the __<#{sponsored_by_category_id}>__ category!**", ephemeral=True)

    # Database

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def create_table_user_ping_permission(self, ctx) -> None:
        """ (ADM) Creates the UserPingPermission table. """

        await ctx.message.delete()
        if await self.table_user_ping_permission():
            return await ctx.send("**Table __UserPingPermission__ already exists!**")
        await self.db.execute_query("CREATE TABLE UserPingPermission (user_id BIGINT NOT NULL, PRIMARY KEY(user_id));")

        return await ctx.send("**Table __UserPingPermission__ created!**", delete_after=5)

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def drop_table_user_ping_permission(self, ctx) -> None:
        """ (ADM) Drops the UserPingPermission table. """

        await ctx.message.delete()
        if not await self.table_user_ping_permission():
            return await ctx.send("**Table __UserPingPermission__ doesn't exist!**")
        await self.db.execute_query("DROP TABLE UserPingPermission;")

        return await ctx.send("**Table __UserPingPermission__ dropped!**", delete_after=5)

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def reset_table_user_ping_permission(self, ctx) -> None:
        """ (ADM) Resets the UserPingPermission table. """

        await ctx.message.delete()
        if not await self.table_user_ping_permission():
            return await ctx.send("**Table __UserPingPermission__ doesn't exist yet!**")
        await self.db.execute_query("DELETE FROM UserPingPermission;")

        return await ctx.send("**Table __UserPingPermission__ reset!**", delete_after=5)

    async def table_user_ping_permission(self) -> bool:
        """ Checks whether the UserPingPermission table exists. """

        return await self.db.table_exists("UserPingPermission")

    async def insert_user_ping_permission(self, user_id: int) -> None:
        """ Inserts a row into the UserPingPermission table for
        a specific user.
        :param user_id: The ID of the user to insert it for. """

        await self.db.execute_query("INSERT INTO UserPingPermission (user_id) VALUES (%s);", (user_id,))

    async def get_user_ping_permission(self, user_id: int) -> Optional[Dict[str, int]]:
        """ Gets the data from the UserPingPermission for
        a specific user.
        :param user_id: The ID of the user to fetch. """

        return await self.db.execute_query("SELECT * FROM UserPingPermission WHERE user_id = %s;", (user_id,), fetch="one")

    async def delete_user_ping_permission(self, user_id: int) -> None:
        """ Deletes a row from the UserPingPermission table for
        a specific user.
        :param user_id: The ID of the user to remove it for. """

        await self.db.execute_query("DELETE FROM UserPingPermission WHERE user_id = %s;", (user_id,))


def setup(client: commands.Bot) -> None:
    """ The cog's setup function. """

    client.add_cog(SponsoredBy(client))
