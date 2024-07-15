import discord
from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List
import os
from extra import utils
from typing import List

allowed_roles = [int(os.getenv('OWNER_ROLE_ID', 123)), int(os.getenv('ADMIN_ROLE_ID', 123)), int(os.getenv('MOD_ROLE_ID', 123))]
watchlist_channel_id: int = int(os.getenv('WATCHLIST_CHANNEL_ID', 123))


class ModerationWatchlistTable(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.db = DatabaseCore()

    @commands.command(aliases=['wl'])
    @utils.is_allowed(allowed_roles, throw_exc=True)
    async def watchlist(self, ctx, *, message: str = None) -> None:
        """ Puts one or more members in the watchlist. If the user is already in the watchlist another reason will be added.

        :param member: The member to put in the watchlist.
        :param reason: The reason for putting the member(s) in the watchist. """

        members, reason = await utils.greedy_member_reason(ctx, message)

        author = ctx.author

        if not members:
            return await ctx.send(f"**Please, inform a member to put in the watchlist, {author.mention}!**")

        for member in members:
            if not await self.get_user_watchlist(member.id):
                watchlist_channel = self.client.get_channel(watchlist_channel_id)

                embed = discord.Embed(
                    description=f"<@{member.id}>\n\n**Reason 1:** ```{reason}```",
                    color=member.color,
                    timestamp=ctx.message.created_at,
                    url=member.display_avatar
                )
                embed.set_thumbnail(url=member.display_avatar)
                embed.set_author(name=f"{member}", icon_url=member.display_avatar, url=member.display_avatar)
                embed.set_footer(text=f"Watchlisted by {author}", icon_url=author.display_avatar)
                msg = await watchlist_channel.send(embed=embed)

                await self.insert_user_watchlist(member.id, msg.id)

                view = discord.ui.View()
                view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Check WL Entry!", emoji="⚠️", url=msg.jump_url))
                await ctx.send(f"**Successfully put `{member}` into the watchlist, {author.mention}!**", view=view)

            else:
                watchlist_channel = self.client.get_channel(watchlist_channel_id)
                msg_id = (await self.get_user_watchlist(member.id))[1]
                msg = await watchlist_channel.fetch_message(msg_id)
                embeds = msg.embeds

                embed = discord.Embed(
                    description=f"\n**Reason {len(embeds) + 1}:** ```{reason}```",
                    color=member.color,
                    timestamp=ctx.message.created_at,
                )
                embed.set_footer(text=f"Watchlisted by {author}", icon_url=author.display_avatar)

                embeds.append(embed)
                await msg.edit(embeds=embeds)

                view = discord.ui.View()
                view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Check WL Entry!", emoji="⚠️", url=msg.jump_url))
                await ctx.send(f"**Successfully added another reason to `{member}`'s watchlist, {author.mention}!**", view=view)

    @commands.command(aliases=['remove_watchlist', 'delete_watchlist', 'del_watchlist', 'uwl'])
    @utils.is_allowed(allowed_roles, throw_exc=True)
    async def unwatchlist(self, ctx, *, message: str = None) -> None:
        """ Removes the members from the watchlist or remove just one reason.
        :param member: The members to remove of the watchlist.
        :param index: The reason number to delete (Optional). """

        author = ctx.author

        members, reason_id = await utils.greedy_member_reason(ctx, message)

        if not members:
            return await ctx.send(f"**Please, inform a member to remove from the watchlist, {author.mention}!**")

        for member in members:
            if (wl_entry := await self.get_user_watchlist(member.id)):
                if not reason_id:
                    try:
                        watchlist_channel = self.client.get_channel(watchlist_channel_id)
                        msg = await watchlist_channel.fetch_message(wl_entry[1])
                        await msg.delete()
                    except:
                        pass

                    await self.delete_user_watchlist(member.id)
                    await ctx.send(f"**Successfully removed `{member}` from the watchlist, {author.mention}!**")
                else:
                    watchlist_channel = self.client.get_channel(watchlist_channel_id)
                    msg = await watchlist_channel.fetch_message(wl_entry[1])
                    embeds = msg.embeds

                    reason_id = int(reason_id)

                    del embeds[reason_id - 1]

                    for i, embed in enumerate(embeds[reason_id - 1:], start=reason_id):
                        if i - 1 == 0:
                            embed.description = embed.description.replace(f"**Reason {i + 1}:**", f"<@{member.id}>\n\n**Reason {i}:**")
                            embed.set_thumbnail(url=member.display_avatar)
                            embed.set_author(name=f"{member}", icon_url=member.display_avatar, url=member.display_avatar)
                        else:
                            embed.description = embed.description.replace(f"**Reason {i + 1}:**", f"**Reason {i}:**")

                    await msg.edit(embeds=embeds)

                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Check WL Entry!", emoji="⚠️", url=msg.jump_url))
                    await ctx.send(f"**Successfully removed the reason `{reason_id}` from `{member}`, {author.mention}!**", view=view)

            else:
                await ctx.send(f"**{member} is not in the watchlist, {author.mention}**")

    @commands.command(aliases=['e_watchlist', 'change_watchlist', 'ewl'])
    @utils.is_allowed(allowed_roles, throw_exc=True)
    async def edit_watchlist(self, ctx, *, message: str = None) -> None:
        """ Edits a specific reason from the user's watchlist.
        :param member: The members to remove from the watchlist.
        :param index: Number of the reason.
        :param reason: The new reason."""

        author = ctx.author

        members, reason = await utils.greedy_member_reason(ctx, message)

        if not members:
            return await ctx.send(f"**Please, inform a member to edit the watchlist, {author.mention}!**", delete_after=3)

        if reason:
            index = (reason.split())[0]
            if not index.isdigit() or int(index) <= 0:
                return await ctx.send("**Usage: z!edit_watchlist [member] [reason_number] [new_reason]**", delete_after=5)
        else:
            return await ctx.send("**Usage: z!edit_watchlist [member] [reason_number] [new_reason]**", delete_after=5)

        index = int(index)
        reason = ' '.join(reason.split()[1:])

        if reason == ' ':
            reason = None

        for member in members:
            if (wl_entry := await self.get_user_watchlist(member.id)):
                watchlist_channel = self.client.get_channel(watchlist_channel_id)
                msg = await watchlist_channel.fetch_message(wl_entry[1])
                embeds = msg.embeds

                if index <= len(embeds):
                    embed=embeds[index-1]

                    # Changes the reason
                    if index == 1:
                        # include the member mention for the first embed in the watchlist
                        embed.description = f"<@{member.id}>\n\n**Reason 1:** ```{reason}```"
                    else:
                        embed.description = f"\n**Reason {index}:** ```{reason}```"

                    # Removes the title for the old members
                    embed.title = ''

                    embeds[index-1] = embed

                    await msg.edit(embeds=embeds)

                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Check WL Entry!", emoji="⚠️", url=msg.jump_url))
                    await ctx.send(f"**The reason `{index}` for `{member}` was successfully edited, {author.mention}!**", view=view)

                else:
                    await ctx.send(f"**The reason {index} for the user was not found, {author.mention}**", delete_after=3)
            else:
                await ctx.send(f"**{member} is not in the watchlist, {author.mention}**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_watchlist(self, ctx) -> None:
        """ (ADM) Creates the Watchlist table. """

        if await self.check_table_watchlist_exists():
            return await ctx.send("**Table __Watchlist__ already exists!**")

        await ctx.message.delete()
        await self.db.execute_query("""CREATE TABLE Watchlist (
            user_id BIGINT NOT NULL,
            message_id BIGINT NOT NULL,
            PRIMARY KEY (user_id)
            )""")

        return await ctx.send("**Table __Watchlist__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_watchlist(self, ctx) -> None:
        """ (ADM) Creates the Watchlist table """

        if not await self.check_table_watchlist_exists():
            return await ctx.send("**Table __Watchlist__ doesn't exist!**")
        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE Watchlist")

        return await ctx.send("**Table __Watchlist__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_watchlist(self, ctx):
        """ (ADM) Resets the Watchlist table. """

        if not await self.check_table_watchlist_exists():
            return await ctx.send("**Table __Watchlist__ doesn't exist yet**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM Watchlist")

        return await ctx.send("**Table __Watchlist__ reset!**", delete_after=3)

    async def check_table_watchlist_exists(self) -> bool:
        """ Checks if the Watchlist table exists """

        return await self.db.table_exists("Watchlist")

    async def get_user_watchlist(self, user_id: int) -> List[int]:
        """ Gets a user from the watchlist.
        :param user_id: The ID of the user to get.. """

        return await self.db.execute_query("SELECT * FROM Watchlist WHERE user_id = %s", (user_id,), fetch="one")
    
    async def insert_user_watchlist(self, user_id: int, message_id: int) -> None:
        """ Inserts a user into the watchlist.
        :param user_id: The ID of the user to insert.
        :param message_id: The ID of the message in the watchlist channel. """

        await self.db.execute_query("INSERT INTO Watchlist (user_id, message_id) VALUES (%s, %s)", (user_id, message_id))

    async def delete_user_watchlist(self, user_id: int) -> None:
        """ Deletes a user from the watchlist.
        :param user_id: The ID of the user to delete. """

        await self.db.execute_query("DELETE FROM Watchlist WHERE user_id = %s", (user_id,))
