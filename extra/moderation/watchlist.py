import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List
import os
from extra import utils
from extra.prompt.menu import Confirm
from typing import List, Union

allowed_roles = [int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')), int(os.getenv('MOD_ROLE_ID'))]
watchlist_channel_id: int = int(os.getenv('WATCHLIST_CHANNEL_ID'))


class ModerationWatchlistTable(commands.Cog):
    
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    @commands.command()
    @utils.is_allowed(allowed_roles)
    async def watchlist(self, ctx, member: Union[discord.Member, discord.User] = None, *, reason: str = None) -> None:
        """ Puts a member in the watchlist.
        :param member: The member to put in the watchlist.
        :param reason: The reason for putting the member in the watchist. """

        author = ctx.author

        if not member:
            return await ctx.send(f"**Please, inform a member to put in the watchlist, {author.mention}!**")

        if await self.get_user_watchlist(member.id):
            return await ctx.send(f"**{member} is already in the watchlist, {author.mention}**")

        watchlist_channel = self.client.get_channel(watchlist_channel_id)

        embed = discord.Embed(
            title="__Watchlist__:",
            description=f"{author.mention} watchlisted <@{member.id}>\n__**Reason:**__ ```{reason}```",
            color=member.color,
            timestamp=ctx.message.created_at,
            url=member.display_avatar
        )
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_author(name=f"{member} ({member.id})", icon_url=member.display_avatar, url=member.display_avatar)
        embed.set_footer(text=f"Watchlisted by {author} ({author.id})", icon_url=author.display_avatar)

        msg = await watchlist_channel.send(embed=embed)

        await self.insert_user_watchlist(member.id, msg.id)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Check WL Entry!", emoji="⚠️", url=msg.jump_url))
        await ctx.send(f"**Successfully put `{member}` into the watchlist, {author.mention}!**", view=view)


    @commands.command(aliases=['remove_watchlist', 'delete_watchlist', 'del_watchlist'])
    @utils.is_allowed(allowed_roles)
    async def unwatchlist(self, ctx, member: Union[discord.Member, discord.User] = None) -> None:
        """ Removes a member from the watchlist.
        :param member: The member to put in the watchlist. """

        author = ctx.author

        if not member:
            return await ctx.send(f"**Please, inform a member to remove from the watchlist, {author.mention}!**")

        if not (wl_entry := await self.get_user_watchlist(member.id)):
            return await ctx.send(f"**{member} is not in the watchlist, {author.mention}**")

        try:
            watchlist_channel = self.client.get_channel(watchlist_channel_id)
            msg = await watchlist_channel.fetch_message(wl_entry[1])
            await msg.delete()
        except:
            pass

        confirm = await Confirm(f"**Are you sure you want to remove `{member}` from the watchlist, {author.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it, then, {author.mention}!**")

        await self.delete_user_watchlist(member.id)
        await ctx.send(f"**Successfully removed `{member}` from the watchlist, {author.mention}!**")



    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_watchlist(self, ctx) -> None:
        """ (ADM) Creates the Watchlist table. """

        if await self.check_table_watchlist_exists():
            return await ctx.send("**Table __Watchlist__ already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE Watchlist (
            user_id BIGINT NOT NULL,
            message_id BIGINT NOT NULL,
            PRIMARY KEY (user_id)
            )""")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __Watchlist__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_watchlist(self, ctx) -> None:
        """ (ADM) Creates the Watchlist table """

        if not await self.check_table_watchlist_exists():
            return await ctx.send("**Table __Watchlist__ doesn't exist!**")
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Watchlist")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __Watchlist__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_watchlist(self, ctx):
        """ (ADM) Resets the Watchlist table. """

        if not await self.check_table_watchlist_exists():
            return await ctx.send("**Table __Watchlist__ doesn't exist yet**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Watchlist")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __Watchlist__ reset!**", delete_after=3)

    async def check_table_watchlist_exists(self) -> bool:
        """ Checks if the Watchlist table exists """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Watchlist'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True


    async def get_user_watchlist(self, user_id: int) -> List[int]:
        """ Gets a user from the watchlist.
        :param user_id: The ID of the user to get.. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Watchlist WHERE user_id = %s", (user_id,))
        watchlist = await mycursor.fetchone()
        await mycursor.close()
        return watchlist

    
    async def insert_user_watchlist(self, user_id: int, message_id: int) -> None:
        """ Inserts a user into the watchlist.
        :param user_id: The ID of the user to insert.
        :param message_id: The ID of the message in the watchlist channel. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO Watchlist (user_id, message_id) VALUES (%s, %s)", (user_id, message_id))
        await db.commit()
        await mycursor.close()

    async def delete_user_watchlist(self, user_id: int) -> None:
        """ Deletes a user from the watchlist.
        :param user_id: The ID of the user to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Watchlist WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()