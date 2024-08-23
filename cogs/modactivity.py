import discord
from discord.ext import commands
from mysqldb import DatabaseCore
import os
from extra import utils
from extra.moderation.modactivity import ModActivityTable
from extra.prompt.menu import ConfirmButton

senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID', 123))
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
guild_id = int(os.getenv('SERVER_ID', 123))


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
            
            if is_first:  # Aggiungi il titolo e l'autore solo al primo embed
                embed.title = "Moderator's Activity"
                embed.set_author(name=ctx.guild.name)
                
            return embed
        embed = create_embed(is_first_embed)
        field_count = 0
        for mod in mod_activities:
            m, s = divmod(mod[1], 60)
            h, m = divmod(m, 60)
            user = discord.utils.get(ctx.guild.members, id=mod[0])
            embed.add_field(
                name=f'👤**{user}**',
                value=f"**Voice Chat Activity:**\n{h:d} hours, {m:02d} minutes and {s:02d} seconds\n**Text Chat Activity:**\n{mod[3]} messages",
                inline=False)

            field_count += 1
            # Quando raggiungiamo 20 campi, inviamo l'embed e ne creiamo uno nuovo
            if field_count >= 1:
                await ctx.send(embed=embed)
                is_first_embed = False  # Imposta il flag a False dopo il primo embed
                embed = create_embed(is_first_embed)
                field_count = 0

        # Invia l'ultimo embed se ha campi residui
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
            await self.delete_mod_activity()
            await ctx.send(f"**Mod Activity data reset, {member.mention}!**", delete_after=3)
        else:
            await ctx.send(f"**Not deleting it then, {member.mention}!**", delete_after=3)

        await msg.delete()

                

def setup(client):
    client.add_cog(ModActivity(client))
