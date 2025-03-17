# import.standard
import os
import re
from typing import List

# import.thirdparty
import discord
from discord.ext import commands

# import.local
from extra import utils
from extra.moderation.modactivity import ModActivityTable
from extra.prompt.menu import ConfirmButton, Confirm
from mysqldb import DatabaseCore

# variables.id
guild_id = int(os.getenv('SERVER_ID', 123))

# variables.role
senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID', 123))
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))

class ModActivity(ModActivityTable):
    """ A cog related to the Moderators' activity. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.Cog.listener()
    async def on_ready(self):
        print('ModActivity cog is ready!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if message.author.bot:
            return
        guild = self.client.get_guild(guild_id)
        moderator_role = discord.utils.get(guild.roles, id=mod_role_id)
        if moderator_role not in message.author.roles:
            return

        await self.get_moderator_current_messages(message.author.id)
        await self.update_moderator_message(message.author.id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        guild = self.client.get_guild(guild_id)
        moderator_role = discord.utils.get(guild.roles, id=mod_role_id)
        if moderator_role not in member.roles:
            return

        current_ts = await utils.get_timestamp()
        old_time = await self.get_moderator_current_timestamp(member.id, current_ts)
        addition = current_ts - old_time

        if not before.channel:
            return await self.update_moderator_timestamp(member.id)

        if not after.channel:
            await self.update_moderator_time(member.id, addition)


    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    @commands.command(aliases=['mods_reputation', 'mod_rep'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def modrep(self, ctx):
        """ (STAFF) Shows all the moderators and their statuses in embedded messages. """

        mod_activities = await self.get_mod_activities()
        member: discord.Member = ctx.author

        def create_embed(is_first: bool) -> discord.Embed:
            embed = discord.Embed(
                url='https://discordapp.com', color=discord.Color.dark_green(),
                timestamp=ctx.message.created_at)
            embed.set_footer(text='Activity Report', icon_url=self.client.user.display_avatar)
            embed.set_thumbnail(url=ctx.guild.icon.url)

            if is_first:
                embed.title = "Moderator's Activity"
                embed.set_author(name=ctx.guild.name)

            return embed

        async def add_mods_to_embed(embed: discord.Embed, mods: List):
            nonlocal field_count
            for mod in mods:
                embed.add_field(
                name=f"{mod['icon']}**{mod['user']}**",
                value=(
                    f"**Voice Chat Activity:**\n"
                    f"{mod['hours']:d} hours, {mod['minutes']:02d} minutes and {mod['seconds']:02d} seconds\n"
                    f"**Text Chat Activity:**\n{mod['messages']} messages"
                ),
                inline=False
            )
                field_count += 1
                if field_count >= 20:
                    await ctx.send(embed=embed)
                    embed = create_embed(is_first=False)
                    field_count = 0
            return embed


        active_mods = []
        inactive_mods = []

        for mod in mod_activities:
            mod_id, time_in_vc, _, messages = mod
            m, s = divmod(time_in_vc, 60)
            h, m = divmod(m, 60)
            user = discord.utils.get(ctx.guild.members, id=mod_id) 
            minimum_voice, minimum_text = await self.get_mod_activity_min_voice(), await self.get_mod_activity_min_text()
            if minimum_voice and minimum_text is not False:
                min_voice, min_text = minimum_voice[0], minimum_text[0]
            else:
                min_voice, min_text = 10800, 30
            is_active = time_in_vc >= min_voice or messages >= min_text
            icon = '🔹' if is_active else '🔸'
            moderator_data = {"user": user,"icon": icon, "hours": h, "minutes": m, "seconds": s, "messages": messages }
            if is_active:
                active_mods.append(moderator_data)
            else:
                inactive_mods.append(moderator_data)

        field_count = 0
        embed = create_embed(is_first=True)
        embed = await add_mods_to_embed(embed, active_mods)
        embed = await add_mods_to_embed(embed, inactive_mods)

        if field_count > 0:
            await ctx.send(embed=embed)

        confirm_view: discord.ui.View = ConfirmButton(member, timeout=60)
        msg = await ctx.send("**Do you want to reset the data?**", view=confirm_view)
        await confirm_view.wait()

        await utils.disable_buttons(confirm_view)
        await msg.edit(view=confirm_view)

        if confirm_view.value is None:
            await ctx.send(f"**Timeout, not deleting it, {member.mention}!**", delete_after=3)
        elif confirm_view.value:
            for mod in mod_activities:
                mod_id, time_in_vc, _, messages = mod
                user = discord.utils.get(ctx.guild.members, id=mod_id)
                minimum_voice, minimum_text = await self.get_mod_activity_min_voice(), await self.get_mod_activity_min_text()
                if minimum_voice and minimum_text is not False:
                    min_voice, min_text = minimum_voice[0], minimum_text[0]
                else:
                    min_voice, min_text = 10800, 30
                is_active = time_in_vc >= min_voice or messages >= min_text
                
                reason = (
                    f"Dear <@{mod_id}>,\n\n"
                    "This is a gentle **automated** reminder to remain active and engaged as a member of the staff team. "
                    "Consistent moderation, community interaction, and assistance are essential "
                    "to maintaining a positive and organized server environment.\n\n"
                    "**Please ensure that you are:**\n"
                    "✔ Taking on and handling cases efficiently.\n"
                    "✔ Addressing issues and concerns brought up by members.\n\n"
                    "If you are unable to stay active for any reason, kindly inform "
                    "the staff management team to make the necessary arrangements.\n\n"
                    "Thank you for your dedication and efforts in keeping the server running smoothly!"
                )
                
                if user and not is_active:
                    embed = discord.Embed(
                        title="Staff Activity Reminder",
                        description=reason,
                        color=discord.Color.orange()
                    ).set_footer(text="Your cooperation is highly appreciated.")
                    
                    try:
                        await user.send(embed=embed)
                        await self.log_automated_dm(ctx, user, reason)
                    except discord.Forbidden:
                        await ctx.send(f"**Failed to send message to `{user.name}`!** Their DM's may be closed.", delete_after=3)
                    except discord.HTTPException as e:
                        await ctx.send(f"**Failed to send message to `{user.name}`!** ERROR: `{e}`", delete_after=3)
            
            await self.reset_mod_activity()
            await ctx.send(f"**Mod Activity data reset, {member.mention}!**", delete_after=3)
        else:
            await ctx.send(f"**Not deleting it then, {member.mention}!**", delete_after=3)

        await msg.delete()
        
    async def log_automated_dm(self, ctx, user: discord.Member, message: str) -> None:
        """ Log's the automated DM message sent by the bot.
        :param ctx: The context.
        :param user: The member who's the receiver of the message.
        :param message: The message. """

        # Moderation log
        if not (demote_log := discord.utils.get(ctx.guild.text_channels, id=int(os.getenv('DM_LOG_CHANNEL_ID', 123)))):
            return

        dm_embed = discord.Embed(
            title="__DM Message__",
            description=f"{self.client.user.mention} DM'd {user.mention}.\n**Message:** {message}",
            color=discord.Color.orange(),
            timestamp=ctx.message.created_at
        )
        dm_embed.set_author(name=user, icon_url=user.display_avatar)
        dm_embed.set_footer(text=f"Sent by: Sloth")
        await demote_log.send(embed=dm_embed)

    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    @commands.command(aliases=['track_mod'])
    async def track_mod_activity(self, ctx, mod: discord.Member):
        """ (STAFF) Starts tracking a moderator activity. """
        guild = self.client.get_guild(guild_id)
        moderator_role = discord.utils.get(guild.roles, id=mod_role_id)

        if moderator_role not in mod.roles:
            return await ctx.send(f"**{mod.mention} is not a moderator!**")

        if await self.check_mod_activity_exists(mod.id):
            return await ctx.send(f"**Moderator {mod.mention} is already being tracked!**")

        await self.insert_moderator(mod.id)
        return await ctx.send(f"**Tracking {mod.mention} activity!**")

    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    @commands.command(aliases=['untrack_mod'])
    async def untrack_mod_activity(self, ctx, mod: discord.Member):
        """ (STAFF) Stop tracking a moderator activity. Use this command if an user is no longer a moderator. """

        guild = self.client.get_guild(guild_id)
        moderator_role = discord.utils.get(guild.roles, id=mod_role_id)

        if moderator_role not in mod.roles:
            return await ctx.send(f"**{mod.mention} is not a moderator!**")

        if not await self.check_mod_activity_exists(mod.id):
            return await ctx.send(f"**Moderator {mod.mention} is not being tracked!**")

        await self.remove_moderator(mod.id)
        return await ctx.send(f"**Untracking {mod.mention} activity!**")

    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    @commands.command(aliases=['sync_mods'])
    async def sync_mod_activity(self, ctx):
        await self.delete_mod_activity()
        guild = self.client.get_guild(guild_id)
        mods_role = discord.utils.get(guild.roles, id=mod_role_id)
        mods = [m for m in guild.members if mods_role in m.roles]

        if not mods:
            return await ctx.send("**There are no mods to track**")

        for mod in mods:
            await self.insert_moderator(mod.id)

        return await ctx.send(f"**Tracking {len(mods)} activity!**")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def modrep_min_text(self, ctx, *, message : str = None) -> None:
        """ Changes the minimum text message limit for the mod activity list. """

        member = ctx.author

        if not await self.check_mod_activity_settings_table_exists():
            return await ctx.send(f"**It looks like the mod activity list is on maintenance, {member.mention}!**")

        if not message:
            return await ctx.send("**Please specify the amount of messages that would be the minimum for the inactivity limit.**")

        try:
            total_messages = int(message)
        except ValueError:
            return await ctx.send(f"**Invalid input, {member.mention}. Please specify a number.**")

        modactivity_min_text = await self.get_mod_activity_min_text()
        if modactivity_min_text:
            confirm = await Confirm(f"Current mod activity minimum text message limit is `{modactivity_min_text[0]} messages`.\nAre you sure you want to change it to `{total_messages} messages`, {member.mention}?").prompt(ctx)
            if confirm:
                await self.set_mod_activity_min_text(total_messages)
                await ctx.send(f"**Mod activity minimum text message limit has been changed to `{total_messages}`!**")
        else:
            return await ctx.send(f"**Can't get minimum text message limit information. Try resetting the mod activity settings database before changing the limit.**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def modrep_min_voice(self, ctx, *, message : str = None) -> None:
        """ Changes the minimum voice time limit for the mod activity list. """

        member = ctx.author
        
        await ctx.message.delete()

        if not await self.check_mod_activity_settings_table_exists():
            return await ctx.send(f"**It looks like the mod activity list is on maintenance, {member.mention}!**")

        if not message:
            return await ctx.send("**Please specify a time, all these examples work: `1w`, `3d 12h`, `12h 30m 30s` or you can also provide the time like this `43200` directly in seconds.**")

        def look_at_the_time_whoa(time):
            pattern = r'((?P<weeks>\d+)w)?\s*((?P<days>\d+)d)?\s*((?P<hours>\d+)h)?\s*((?P<minutes>\d+)m)?\s*((?P<seconds>\d+)s)?'
            match = re.match(pattern, time)
            
            if not match:
                return None
            
            time_data = match.groupdict(default="0")
            total_seconds = (
                int(time_data["weeks"]) * 604800 +
                int(time_data["days"]) * 86400 +
                int(time_data["hours"]) * 3600 +
                int(time_data["minutes"]) * 60 +
                int(time_data["seconds"])
            )
            
            return total_seconds

        try:
            total_seconds = int(message)
        except ValueError:
            total_seconds = look_at_the_time_whoa(message)
            if total_seconds is None:
                return await ctx.send(f"**Invalid time format, {member.mention}. Examples of working formats: `1w`, `3d 12h`, `12h 30m 30s` or you can also provide the time like this `43200` directly in seconds.**")

        modactivity_min_voice = await self.get_mod_activity_min_voice()
        if modactivity_min_voice:
            confirm = await Confirm(f"Current mod activity minimum voice time limit is `{modactivity_min_voice[0]} seconds`.\nAre you sure you want to change it to `{total_seconds} seconds`, {member.mention}?").prompt(ctx)
            if confirm:
                await self.set_mod_activity_min_voice(total_seconds)
                await ctx.send(f"**Mod activity minimum voice time limit has been changed to `{total_seconds}`!**")
        else:
            return await ctx.send(f"**Can't get minimum voice time limit information. Try resetting the mod activity settings database before changing the limit.**")

def setup(client):
    client.add_cog(ModActivity(client))
