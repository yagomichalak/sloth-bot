import discord
from discord.ext import commands
from datetime import datetime
from mysqldb import *
import asyncio
import os
from extra import utils
from extra.moderation.modactivity import ModActivityTable

senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID'))
mod_role_id = int(os.getenv('MOD_ROLE_ID'))
guild_id = int(os.getenv('SERVER_ID'))


class ModActivity(ModActivityTable):
    """ A cog related to the Moderators' activity. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

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
        epoch = datetime.utcfromtimestamp(0)
        the_time = (datetime.utcnow() - epoch).total_seconds()
        old_time = await self.get_moderator_current_timestamp(member.id, int(the_time))
        addition = the_time - old_time

        if not before.channel:
            return await self.update_moderator(member.id)

        if not after.channel:
            await self.add_time_moderator(member.id, addition)


    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    @commands.command(aliases=['mods_reputation', 'mod_rep'])
    async def modrep(self, ctx):
        """ (STAFF) Shows all the moderators and their statuses in an embedded message. """

        mycursor, db = await the_database()
        await mycursor.execute('SELECT * FROM ModActivity')
        mods = await mycursor.fetchall()
        await mycursor.close()

        embed = discord.Embed(title="This Week's Report",
                              description="Moderators' activity statuses.",
                              url='https://discordapp.com',
                              colour=discord.Colour.dark_green(), timestamp=ctx.message.created_at)
        embed.set_footer(text='Activity Report',
                         icon_url=self.client.user.display_avatar)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/icons/459195345419763713/a_866e6fe442bfb651353df72826238f54.jpg')
        embed.set_author(name=ctx.guild.name)
        for mod in mods:
            m, s = divmod(mod[1], 60)
            h, m = divmod(m, 60)
            user = discord.utils.get(ctx.guild.members, id=mod[0])
            embed.add_field(name=f'👤__**{user}**__',
                            value=f"**- Voice Chat Activity:**\n{h:d} hours, {m:02d} minutes and {s:02d} seconds\n**- Text Chat Activity:**\n{mod[3]} messages",
                            inline=False)

        await ctx.send(embed=embed)
        the_msg = await ctx.send("**Do you want to reset the data?**")
        await the_msg.add_reaction('✅')
        await the_msg.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in '✅❌'

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            timeout = await ctx.send("**Timeout, not deleting it!**")
            await the_msg.delete()
            await asyncio.sleep(2)
            return await timeout.delete()
        else:
            if str(reaction.emoji) == "✅":
                await self.reset_table_mods(ctx)
                resp = await ctx.send("**Log reset!**")
            else:
                resp = await ctx.send("**Not reset!**")
            await the_msg.delete()
            await asyncio.sleep(2)
            return await resp.delete()


def setup(client):
    client.add_cog(ModActivity(client))
