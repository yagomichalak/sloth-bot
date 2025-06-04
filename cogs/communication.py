# import.standard
import os
from random import randint
from typing import List, Optional

# import.thirdparty
import discord
from discord.errors import NotFound
from discord.ext import commands, tasks

# import.local
from extra import utils
from extra.tool.scheduled_events import ScheduledEventsTable
from mysqldb import DatabaseCore

# variables.role
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
staff_manager_role_id = int(os.getenv('STAFF_MANAGER_ROLE_ID', 123))
lesson_manager_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID', 123))
event_manager_role_id = int(os.getenv('EVENT_MANAGER_ROLE_ID', 123))
allowed_roles = [int(os.getenv('OWNER_ROLE_ID', 123)), int(os.getenv('ADMIN_ROLE_ID', 123)), mod_role_id]

# variables.textchannel
bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID', 123))
announcement_channel_id = int(os.getenv('ANNOUNCEMENT_CHANNEL_ID', 123))
general_channel_id = int(os.getenv('GENERAL_CHANNEL_ID', 123))

# variable.slothsubscription
sloth_subscriber_sub_id = int(os.getenv("SLOTH_SUBSCRIBER_SUB_ID", 123))

tool_cogs: List[commands.Cog] = [ScheduledEventsTable]

class Communication(*tool_cogs):
    """ A cog related to communication commands. """

    def __init__(self, client):
        self.client = client
        self.db = DatabaseCore()

    @commands.Cog.listener()
    async def on_ready(self):

        self.advertise_patreon.start()
        self.advertise_sloth_subscription.start()
        print('[.cogs] Communication cog is ready!')

    @tasks.loop(seconds=60)
    async def advertise_patreon(self) -> None:
        """ Checks the time for advertising Patreon. """

        ad_interval = 43200  # 12 hours in seconds

        current_ts = await utils.get_timestamp()
        # Checks whether Patreon advertising event exists
        if not await self.get_advertising_event(event_label='patreon_ad'):
            # If not, creates it
            return await self.insert_advertising_event(event_label='patreon_ad', current_ts=current_ts-ad_interval)

        # Checks whether advertising time is due
        if not await self.check_advertising_time(
            current_ts=int(current_ts), event_label="patreon_ad", ad_time=ad_interval):
            return

        # Updates time and advertises.
        await self.update_advertising_time(event_label="patreon_ad", current_ts=current_ts)
        general_channel = self.client.get_channel(general_channel_id)

        random_message = ""
        i = randint(1, 5)
        with open(f'./extra/random/texts/other/patreon_ad_{i}.txt', 'r', encoding="utf-8") as f:
            random_message = f.read()

        await general_channel.send(random_message)

    @tasks.loop(seconds=60)
    async def advertise_sloth_subscription(self) -> None:
        """ Checks the time for advertising the Sloth Subscription. """

        ad_interval = 43200  # 12 hours in seconds

        current_ts = await utils.get_timestamp()
        # Checks whether Patreon advertising event exists
        if not await self.get_advertising_event(event_label='sloth_sub_ad'):
            # If not, creates it
            return await self.insert_advertising_event(event_label='sloth_sub_ad', current_ts=current_ts-ad_interval)

        # Checks whether advertising time is due
        if not await self.check_advertising_time(
            current_ts=int(current_ts), event_label="sloth_sub_ad", ad_time=ad_interval):
            return

        # Updates time and advertises.
        await self.update_advertising_time(event_label="sloth_sub_ad", current_ts=current_ts)
        bots_and_commands_channel = self.client.get_channel(bots_and_commands_channel_id)

        random_message = ""
        i = randint(1, 5)
        with open(f'./extra/random/texts/other/sloth_sub_ad_{i}.txt', 'r', encoding="utf-8") as f:
            random_message = f.read()

        # Embed
        embed = discord.Embed(
            title="__Did you know?__",
            description=f"> {random_message}",
            color=discord.Color.green(),
            url=f"https://discord.com/discovery/applications/{self.client.application_id}/store/{sloth_subscriber_sub_id}"
        )

        # Subscription Views
        view = discord.ui.View()
        view.add_item(discord.ui.Button(sku_id=sloth_subscriber_sub_id))
        await bots_and_commands_channel.send(embed=embed, view=view)

    # Says something by using the bot
    @commands.command()
    @utils.is_allowed([*allowed_roles, lesson_manager_role_id, event_manager_role_id], throw_exc=True)
    async def say(self, ctx):
        """ (MOD) Makes the bot say something. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        msg = ctx.message.content.split('!say', 1)
        await ctx.send(msg[1])

    # Edits a message sent by the bot
    @commands.command()
    @commands.has_any_role(*allowed_roles)
    async def edit(self, ctx, message_id : int = None, *, text : str = None):
        """ (Mod) Edits a message sent by the bot.
        :param message_id: The message id."""

        await ctx.message.delete()

        if not message_id:
            return await ctx.send("**Please, insert a message id**", delete_after=3)

        if not text:
            return await ctx.send("**Please, insert a message**", delete_after=3)
        
        channel = ctx.message.channel
        
        try:
            message = await channel.fetch_message(message_id)
            await message.edit(text)

        except NotFound:
            return await ctx.send("**Message not found. Send the command in the same channel as the original message.**", delete_after=5)

    # Replies a message by using the bot
    @commands.command()
    @utils.is_allowed([*allowed_roles, lesson_manager_role_id, event_manager_role_id], throw_exc=True)
    async def reply(self, ctx, message_id : int = None, *, text : str = None):
        """ (Mod) Replies a message with the bot.
        :param message_id: The message id to reply.
        :param message: The message to send"""

        await ctx.message.delete()

        if not message_id:
            return await ctx.send("**Please, insert a message id to reply to it**", delete_after=3)
        
        if not text:
            return await ctx.send("**Please, insert a message**", delete_after=3)

        channel = ctx.message.channel
        
        try:
            message = await channel.fetch_message(message_id)
            await message.reply(text)

        except NotFound:
            return await ctx.send("**Message not found. Send the command in the same channel as the original message.**", delete_after=5)

    # Sends a reminder to the users to hydrate theirselves (BD Event)
    @commands.command()
    @utils.is_allowed([*allowed_roles, lesson_manager_role_id, event_manager_role_id], throw_exc=True)
    async def hydrate(self, ctx):
        """ (Mod) Sends a reminder to the users to hydrate theirselves (BD Event). """

        await ctx.message.delete()
        message = "Hey there! You're doing an amazing job, and I’m proud of you! 💪 Don’t forget to **hydrate** and **take a deep breath**. You’ve got this! 💧✨"
        await ctx.send(message)

    # Spies a channel
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def spy(self, ctx, cid):
        """ (ADM) Makes the bot send a message to a given channel.
        :param cid: The ID of the channel. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 3:
            return await ctx.send('You must inform all parameters!')

        spychannel = self.client.get_channel(int(cid))
        msg = ctx.message.content.split(cid)
        embed = discord.Embed(description=msg[1], colour=discord.Colour.dark_green())
        await spychannel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx):
        """ (ADM) Announces a message in the announcements channel using the bot. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        announce_channel = discord.utils.get(ctx.guild.channels, id=announcement_channel_id)
        msg = ctx.message.content.split('!announce', 1)
        await announce_channel.send(msg[1])
            
    #greedy_dm
    @commands.command()
    @utils.is_allowed([staff_manager_role_id, lesson_manager_role_id, event_manager_role_id], throw_exc=True)
    async def dm(self, ctx, *, message: Optional[str] = None):
        """ (SeniorMod | Manager) Sends a Direct Message to one or more users.
        :param members: The @ or the ID of one or more users to mute.
        :param message: The message to send. """

        members, reason = await utils.greedy_member_reason(ctx, message)

        await ctx.message.delete()
        author: discord.Member = ctx.author

        # No message to be sent
        if not reason:
            return await ctx.send("**Inform a message to send!**", delete_after=3)

        # No users to be messaged
        if not members:
            return await ctx.send("**Inform a member!**", delete_after=3)
        
        # If there's a user, DM them
        for member in members:
            if ctx.guild.get_member(member.id):
                await member.send(reason) # Sends DM message
                await self.log_dm(ctx, author, member, reason) # Triggers DM log
            else:
                await ctx.send(f"**Member: {member} not found!", delete_after=3)
        
    async def log_dm(self, ctx, author: discord.Member, member: discord.Member, message: str) -> None:
        """ Log's a DM message.
        :param ctx: The context.
        :param author: The author of the message.
        :param member: The member who's the receiver of the message.
        :param message: The message. """

        # Moderation log
        if not (demote_log := discord.utils.get(ctx.guild.text_channels, id=int(os.getenv('DM_LOG_CHANNEL_ID', 123)))):
            return

        dm_embed = discord.Embed(
            title="__DM Message__",
            description=f"{author.mention} DM'd {member.mention}.\n**Message:** {message}",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        dm_embed.set_author(name=member, icon_url=member.display_avatar)
        dm_embed.set_footer(text=f"Sent by: {author}", icon_url=author.display_avatar)
        await demote_log.send(embed=dm_embed)


def setup(client):
    """ Cog's setup function. """

    client.add_cog(Communication(client))
