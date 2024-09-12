# import.standard
import os

# import.thirdparty
import discord
from discord.ext import commands

# import.local
from extra import utils
from extra.moderation.modactivity import ModActivityTable
from extra.prompt.menu import ConfirmButton
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
        is_first_embed = True  # Flag per indicare il primo embed
        def create_embed(is_first):
            embed = discord.Embed(
                url='https://discordapp.com', color=discord.Color.dark_green(),
                timestamp=ctx.message.created_at)
            embed.set_footer(text='Activity Report', icon_url=self.client.user.display_avatar)
            embed.set_thumbnail(url=ctx.guild.icon.url)

            if is_first:
                embed.title = "Moderator's Activity"
                embed.set_author(name=ctx.guild.name)

            return embed

        embed = create_embed(is_first_embed)
        field_count = 0
        active_mods = []
        inactive_mods = []

        for mod in mod_activities:
            mod_id, time_in_vc, _, messages = mod
            m, s = divmod(time_in_vc, 60)
            h, m = divmod(m, 60)
            user = discord.utils.get(ctx.guild.members, id=mod_id)
            is_active =  h >= 3 or messages >= 30
            icon = '🔹' if is_active else '🔸'
            moderator_data = {"user": user,"icon": icon, "hours": h, "minutes": m, "seconds": s, "messages": messages }
            if is_active:
                active_mods.append(moderator_data)
            else:
                inactive_mods.append(moderator_data)

        async def add_mods_to_embed(mods):
            nonlocal field_count
            nonlocal embed
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
            return embed

        embed = await add_mods_to_embed(active_mods)
        embed = await add_mods_to_embed(inactive_mods)

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
            await self.reset_mod_activity()
            await ctx.send(f"**Mod Activity data reset, {member.mention}!**", delete_after=3)
        else:
            await ctx.send(f"**Not deleting it then, {member.mention}!**", delete_after=3)

        await msg.delete()

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


def setup(client):
    client.add_cog(ModActivity(client))
