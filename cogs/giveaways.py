import discord
from discord import SlashCommandGroup, option, Option, ApplicationContext, slash_command
from discord.ext import commands, tasks
from typing import List, Union, Any, Optional
import os

from extra import utils
from extra.view import GiveawayView
from extra.prompt.menu import ConfirmButton
from extra.misc.giveaways import GiveawaysTable, GiveawayEntriesTable

server_id = int(os.getenv('SERVER_ID', 123))
giveaway_manager_role_id: int = int(os.getenv('GIVEAWAY_MANAGER_ROLE_ID', 123))
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))

allowed_roles: List[int] = [giveaway_manager_role_id, mod_role_id, int(os.getenv('ADMIN_ROLE_ID'))]
guild_ids: List[int] = [server_id]

giveaway_cogs: List[commands.Cog] = [GiveawaysTable, GiveawayEntriesTable]

class Giveaways(*giveaway_cogs):
    """ Category for commands related to giveaways. """

    def __init__(self, client) -> None:
        self.client = client

    _giveaway = SlashCommandGroup("giveaway", "Various greeting from cogs!", guild_ids=guild_ids)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to go. """

        # Makes all registered giveaways consistent
        giveaways = await self.get_giveaways()
        for giveaway in giveaways:
            try:
                self.client.add_view(view=GiveawayView(self.client, giveaway[6]), message_id=giveaway[0])
            except:
                pass

        self.check_old_giveaways.start() # Deletes old giveaways
        self.check_due_giveaways.start() # Checks due giveaways
        print('Giveaways cog is online!')


    @tasks.loop(minutes=1)
    async def check_due_giveaways(self) -> None:
        """ Checks due giveaways and ends them. """


        current_ts = await utils.get_timestamp()
        giveaways = await self.get_due_giveaways(current_ts)
        for giveaway in giveaways:

            if giveaway[5]:
               continue 

            # Gets the channel and message
            channel = message = None
            try:
                channel = await self.client.fetch_channel(giveaway[1])
            except discord.NotFound:
                await self.delete_giveaway(giveaway[0])
                continue
            
            try:
                message = await channel.fetch_message(giveaway[0])
            except discord.NotFound:
                await self.delete_giveaway(giveaway[0])
                continue

            entries = await self.get_giveaway_entries(giveaway[0])

            winners = await self.get_winners(giveaway, entries)

            # Edits the embed
            embed = message.embeds[0]
            embed.title += ' (Ended)'
            embed.color = discord.Color.red()

            view = discord.ui.View.from_message(message)

            await utils.disable_buttons(view)
            await message.edit(embed=embed, view=view)
            # Sends last message
            await message.reply(
                f"**Giveaway is over, we had a total of `{len(entries)}` people participating, and the `{giveaway[3]}` winners are: {winners}!**"
            )
            # Notifies the giveaway's termination
            await self.update_giveaway(giveaway[0])

    @tasks.loop(minutes=1)
    async def check_old_giveaways(self) -> None:
        """ Looks for old giveaways and deletes them.
        
        PS: It looks for giveaways that ended at least 2 days ago. """

        current_ts: int = await utils.get_timestamp()
        await self.delete_old_giveaways(current_ts)

    async def _giveaway_start_callback(
        self, ctx, host: discord.Member, title: str, description: str, prize: str, winners: int = 1, days: int = 0, 
        hours: int = 0, minutes: int = 0, role: Optional[discord.Role] = None, thumbnail: Optional[str] = None, 
        image: Optional[str] = None
    ) -> None:
        """ Callback for the giveaway command.
        :param host: The host of the giveaway..
        :param title: Title for the giveaway.
        :param description: Description of giveaway.
        :param prize: Prize giveaway.
        :param winners: Amount of winners. [Optional] [Default = 1]
        :param days: Amount of days until the giveaway ends. [Optional]
        :param hours: Amount of hours until the giveaway ends. [Optional]
        :param minutes: Amount of minutes until the giveaway ends. [Optional]
        :param role: The role for role-only giveaways. [Optional]
        :param thumbnail: The thumbnail for the giveaway message. [Optional]
        :param image: The image for the giveaway message. [Optional]
        
        PS: The total time summing up days, minutes and minutes MUST be greater than 0. """

        member = ctx.author
        guild = ctx.guild
        files: List[discord.File] = []

        giveaway_time = await self.get_giveaway_time(minutes, hours, days)

        if giveaway_time == 0:
            return await ctx.respond(f"**Please, inform the time, {member.mention}!**", ephemeral=True)

        current_time = await utils.get_time_now()
        current_ts = current_time.timestamp()

        embed = discord.Embed(
            title=f"__{title}__",
            description=description,
            color=member.color,
            timestamp=current_time
        )

        if thumbnail:
            # files.append(thumbnail)
            embed.set_thumbnail(url=thumbnail)
        else:
            embed.set_thumbnail(url=guild.icon.url)

        if image:
            # files.append(image)
            embed.set_image(url=image)
        else:
            if guild.banner:
                embed.set_image(url=guild.banner.url)
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)

        deadline_ts = int(current_ts+giveaway_time)

        embed.add_field(
            name="__Info__:",
            value=f"""
            **Hosted by:** {host.mention}
            **Ends:** <t:{deadline_ts}:R>
            **Winners:** {winners}
            **Prize:** {prize}
            **Required Role:** {role.mention if role else None}
            """, inline=False
        )

        try:
            view = GiveawayView(self.client, role.id if role else None)
            msg = await ctx.respond(embed=embed, view=view)#, files=files)
            self.client.add_view(view=view, message_id=msg.id)

            await self.insert_giveaway(
                message_id=msg.id, channel_id=msg.channel.id, user_id=host.id, prize=prize,
                winners=winners, deadline_ts=deadline_ts, role_id=role.id if role else None,
            )
        except Exception as e:
            print(e)
            await ctx.respond(f"**Something went wrong with it, {member.mention}!**", ephemeral=True)

    async def _giveaway_list_callback(self, ctx) -> None:
        """ Deletes an existing giveaway. """

        member = ctx.author

        giveaways: List[List[Union[str, int]]] = []

        if await utils.is_allowed([mod_role_id]).predicate(ctx):
            giveaways = await self.get_giveaways()
        else:
            giveaways = await self.get_user_giveaways(member.id)

        if not giveaways:
            return await ctx.respond(f"**You have no active giveaways registered, {member.mention}!**", ephemeral=True)

        message_url = 'https://discord.com/channels/{server_id}/{channel_id}/{message_id}'

        formatted_giveaways: List[str] = '\n'.join([
            f"Msg • [{ga[0]}]({message_url.format(server_id=server_id, channel_id=ga[1], message_id=ga[0])}) - **P:** `{ga[2]}` **W:** `{ga[3]}` | <t:{ga[4]}:R>"
            for ga in giveaways
        ])

        current_time = await utils.get_time_now()
        embed = discord.Embed(
            title="__Registered Giveaways__",
            description=f"**Msg** = `Message`\n**P** = `Prize`\n**W** = `Winners`\n\n{formatted_giveaways}",
            color=member.color,
            timestamp=current_time
        )

        embed.set_footer(text=f"Requested by: {member}", icon_url=member.display_avatar)

        await ctx.respond(embed=embed, ephemeral=True)

    async def _giveaway_reroll_callback(self, ctx, message_id: int) -> None:
        """ Rerolls a giveaway.
        :param message_id: The ID of the giveaway message. """

        member = ctx.author

        if not message_id:
            return await ctx.respond(f"**Please, inform a message ID, {member.mention}!**", ephemeral=True)

        giveaway = await self.get_giveaway(message_id)
        if not giveaway:
            return await ctx.respond(f"**The specified giveaway doesn't exist, {member.mention}!**", ephemeral=True)

        if giveaway[7] != member.id and not await utils.is_allowed([mod_role_id]).predicate(ctx):
            return await ctx.send(f"**You cannot reroll someone else's giveaway, {member.mention}!**", ephemeral=True)

        if not giveaway[5]:
            return await ctx.respond(f"**This giveaway hasn't ended yet, you can't reroll it, {member.mention}!**", ephemeral=True)

        entries = await self.get_giveaway_entries(giveaway[0])

        winners = await self.get_winners(giveaway, entries)

        # Sends last message
        await ctx.respond(
            f"**Rerolling giveaway with `{len(entries)}` people participating, and the new `{giveaway[3]}` winners are: {winners}!**"
        )

    async def _giveaway_delete_callback(self, ctx, message_id: int) -> None:
        """ Deletes an existing giveaway.
        :param message_id: The ID of the giveaway message. """

        member = ctx.author
        if not message_id:
            return await ctx.respond(f"**Please, inform a message ID, {member.mention}!**", ephemeral=True)

        giveaway = await self.get_giveaway(message_id)
        if not giveaway:
            return await ctx.respond(f"**The specified giveaway message doesn't exist, {member.mention}!**", ephemeral=True)

        if giveaway[7] != member.id and not await utils.is_allowed([mod_role_id]).predicate(ctx):
            return await ctx.send(f"**You cannot delete someone else's giveaway, {member.mention}!**")
            
        confirm_view = ConfirmButton(member, timeout=60)
        embed = discord.Embed(description=f"**Are you sure you wanna delete the giveaway with ID `{giveaway[0]}`, {member.mention}?**", color=member.color)
        await ctx.respond(embed=embed, view=confirm_view, ephemeral=True)
        await confirm_view.wait()
        if confirm_view.value is None:
            return await ctx.respond(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            return await ctx.respond(f"**Not doing it then, {member.mention}!**", ephemeral=True)

        await self.delete_giveaway(giveaway[0])
        await ctx.respond(f"**Successfully deleted the giveaway with ID: `{giveaway[0]}`, {member.mention}!**", ephemeral=True)
        try:
            channel = discord.utils.get(ctx.guild.text_channels, id=giveaway[1])
            message = await channel.fetch_message(giveaway[0])
            await message.delete()
        except:
            pass

    async def _giveaway_end_callback(self, ctx, message_id: int = None) -> None:
        """ Force-ends an on-going giveaway.
        :param message_id: The ID of the giveaway message. """

        member = ctx.author
        if not message_id:
            return await ctx.respond(f"**Please, inform a message ID, {member.mention}!**", ephemeral=True)

        giveaway = await self.get_giveaway(message_id)
        if not giveaway:
            return await ctx.respond(f"**The specified giveaway message doesn't exist, {member.mention}!**", ephemeral=True)

        if giveaway[5]:
            return await ctx.respond(f"**This giveaway has been ended already, consider using rerolling or deleting it, {member.mention}!**", ephemeral=True)

        confirm_view = ConfirmButton(member, timeout=60)
        embed = discord.Embed(description=f"**Are you sure you want to end the giveaway with ID: `{giveaway[0]}`, {member.mention}?**", color=member.color)
        await ctx.respond(embed=embed, view=confirm_view, ephemeral=True)
        await confirm_view.wait()
        if confirm_view.value is None:
            return await ctx.respond(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            return await ctx.respond(f"**Not doing it then, {member.mention}!**", ephemeral=True)

         # Gets the channel and message
        channel = message = None
        try:
            channel = await self.client.fetch_channel(giveaway[1])
        except discord.errors.NotFound:
            await self.delete_giveaway(giveaway[0])
            return await ctx.respond(f"**Channel of the given giveaway doesn't exist anymore, {member.mention}!**", ephemeral=True)
        
        try:
            message = await channel.fetch_message(giveaway[0])
        except discord.errors.NotFound:
            await self.delete_giveaway(giveaway[0])
            return await ctx.respond(f"**Message of the given giveaway doesn't exist anymore, {member.mention}!**", ephemeral=True)

        try:
            entries = await self.get_giveaway_entries(giveaway[0])
            winners = await self.get_winners(giveaway, entries)

            # Edits the embed
            embed = message.embeds[0]
            embed.title += ' (Ended)'
            embed.color = discord.Color.red()

            view = discord.ui.View.from_message(message)

            await utils.disable_buttons(view)
            await message.edit(embed=embed, view=view)
            # Sends last message
            await message.reply(
                f"**Giveaway is over, we had a total of `{len(entries)}` people participating, and the `{giveaway[3]}` winners are: {winners}!**"
            )
            # Notifies the giveaway's termination
            await self.update_giveaway(giveaway[0])
            current_ts: int = await utils.get_timestamp()
            await self.update_giveaway_deadline(giveaway[0], current_ts)
        except Exception as e:
            print('Error at force-ending giveaway: ', e)
            await ctx.respond(f"**Something went wrong with it, please contact an admin, {member.mention}!**", ephemeral=True)

    async def get_giveaway_time(self, minutes: int, hours: int, days: int) -> int:
        """ Gets the giveaway timeout time in seconds.
        :param minutes: The amount of minutes.
        :param hours: The amount of hours.
        :param dayss: The amount of days. """

        minutes  *= 60
        hours  *= 3600
        days  *= 86400

        return minutes + hours + days
    
    @utils.is_allowed(allowed_roles, throw_exc=True)
    @_giveaway.command(name="start")
    async def _giveaway_start_slash(self,
        ctx: ApplicationContext, 
        prize: Option(str, name="prize", description="The prize of the giveaway.", required=True), 
        title: Option(str, name="title", description="The title for the giveaway.", required=False, default="Giveaway"), 
        description: Option(str, name="description", description="The description of the giveaway.", required=False), 
        winners: Option(int, name="winners", description="The amount of winners.", required=False, default=1),
        days: Option(int, name="days", description="The days for the giveaway.", required=False), 
        hours: Option(int, name="hours", description="The hours for the giveaway.", required=False), 
        minutes: Option(int, name="minutes", description="The minutes for the giveaway.", required=False), 
        role: Option(discord.Role, name="role", description="The role for role-only giveaways.", required=False), 
        host: Option(discord.Member, name="host", description="The person hosting the giveaway.", required=False), 
        thumbnail: Option(str, name="thumbnail_url", description="The thumbnail for the giveaway.", required=False), 
        image: Option(str, name="image_url", description="The image for the giveaway.", required=False)
    ) -> None:
        """ Starts a giveaway. """

        await ctx.defer()

        winners = 1 if not winners else winners
        minutes = 0 if minutes is None else minutes
        hours = 0 if hours is None else hours
        days = 0 if days is None else days
        host = host if host else ctx.author

        await self._giveaway_start_callback(ctx=ctx,
            host=host, prize=prize, title=title, description=description, 
            winners=winners, days=days, hours=hours, minutes=minutes, role=role,
            thumbnail=thumbnail, image=image
        )

    @utils.is_allowed(allowed_roles, throw_exc=True)
    @_giveaway.command(name="reroll")
    @option("message_id", str, description="The message ID of the giveaway to reroll.")
    async def _giveaway_reroll_slash(self, ctx, message_id: str) -> None:
        """ Rerolls a giveaway. """

        try:
            message_id: int = int(message_id)
        except ValueError:
            await ctx.respond(f"**This is not a valid message ID, {ctx.author.mention}!**", ephemeral=True)
        else:
            await self._giveaway_reroll_callback(ctx=ctx, message_id=message_id)

    @utils.is_allowed(allowed_roles, throw_exc=True)
    @_giveaway.command(name="delete")
    @option("message_id", str, description="The message ID of the giveaway to delete.")
    async def _giveaway_delete_slash(self, ctx, message_id: str) -> None:
        """ Deletes a giveaway. """

        try:
            message_id: int = int(message_id)
        except ValueError:
            await ctx.respond(f"**This is not a valid message ID, {ctx.author.mention}!**", ephemeral=True)
        else:
            await self._giveaway_delete_callback(ctx=ctx, message_id=message_id)

    @utils.is_allowed(allowed_roles, throw_exc=True)
    @_giveaway.command(name="end")
    @option("message_id", str, description="The message ID of the giveaway to end.")
    async def _giveaway_end_slash(self, ctx, message_id: str) -> None:
        """ Ends a giveaway. """

        try:
            message_id: int = int(message_id)
        except ValueError:
            await ctx.respond(f"**This is not a valid message ID, {ctx.author.mention}!**", ephemeral=True)
        else:
            await self._giveaway_end_callback(ctx=ctx, message_id=message_id)

    @utils.is_allowed(allowed_roles, throw_exc=True)
    @_giveaway.command(name="list")
    async def _giveaway_list_slash(self, ctx) -> None:
        """ Lists all giveaways. """

        await self._giveaway_list_callback(ctx=ctx)
"""
Setup:

z!create_table_giveaways
z!create_table_giveaway_entries
"""

def setup(client) -> None:
    client.add_cog(Giveaways(client))