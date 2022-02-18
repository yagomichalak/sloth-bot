import discord
from discord.ext import commands
from datetime import datetime
from mysqldb import *
import asyncio
import os
from extra import utils
from extra.moderation.aspirants import AspirantsTable
from typing import List

senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID'))
mod_role_id = int(os.getenv('MOD_ROLE_ID'))
guild_id = int(os.getenv('SERVER_ID'))


class AspirantActivity(AspirantsTable):
    """ A cog related to the Aspirant's activity. """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to run. """

        print('AspirantActivity cog is ready!')

    ### Listeners
    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        """ Listens to aspirants' messages. """
        
        if not message.guild:
            return
        if message.author.bot:
            return

        # Gets all aspirants
        if users := await self.get_all_aspirants():

            if message.author.id not in users:
                return
        else:
            return

        await self.get_aspirant_current_messages(message.author.id)
        await self.update_aspirant_message(message.author.id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after) -> None:
        """ Listenins to aspirants' voice activity. """

        if member.bot:
            return

        # Gets all aspirants
        if users := await self.get_all_aspirants():
            if member.id not in users:
                return
        else:
            return

        current_ts = await utils.get_timestamp()
        old_time = await self.get_aspirant_current_timestamp(member.id, int(current_ts))
        addition = current_ts - old_time

        if not before.channel:
            return await self.update_aspirant_time(member.id)

        if not after.channel:
            await self.add_aspirant_time(member.id, addition)

    ### Commands
    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    @commands.command(aliases=['asprep', 'asp_rep'])
    async def aspirant_rep(self, ctx) -> None:
        """ (STAFF) Shows all the aspirants and their statuses in an embedded message. """

        if not (users_id := await self.get_all_aspirants()):
            return await ctx.send("**There is no aspirants being moderated**")

        mycursor, _ = await the_database()
        await mycursor.execute(f'SELECT * FROM AspirantActivity')
        users = await mycursor.fetchall()
        await mycursor.close()

        description = ["Aspirants' activity statuses.\n\n"]

        embed = discord.Embed(title="**Free work labor candidates**",
                              url="https://www.cbp.gov/trade/forced-labor",
                              colour=discord.Colour.dark_green(), timestamp=ctx.message.created_at)
        embed.set_footer(text='Activity Report', icon_url=self.client.user.display_avatar)
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/459195345419763713/a_866e6fe442bfb651353df72826238f54.jpg")
        embed.set_author(name=ctx.guild.name)

        for user_id, time, timestamp, messages in users:
            m, s = divmod(time, 60)
            h, m = divmod(m, 60)
            description.append(f"👤 <@{user_id}>\n**- Voice Chat Activity:**\n{h:d} hours, {m:02d} minutes and {s:02d} seconds\n**- Text Chat Activity:**\n{messages} messages\n\n")
        embed.description= ' '.join(description)

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
                for id in users_id:
                    await self.reset_users_activity(user_id=id)
                resp = await ctx.send("**Log reset!**")
            else:
                resp = await ctx.send("**Not reset!**")
            await the_msg.delete()
            await asyncio.sleep(2)
            return await resp.delete()


    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    @commands.command(aliases=['addasp', 'add_asp'])
    async def add_aspirant(self, ctx, member: discord.Member = None) -> None:
        """Adds an aspirant from the activity monitor
        :param member: The user_id, mention or name#0000 of the user"""

        await ctx.message.delete()

        if not member:
            return await ctx.send("**Please, inform a member**")

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO AspirantActivity (user_id, time, timestamp, messages) VALUES (%s, %s, %s, %s)",
                               (member.id, 0, None, 1))
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**The member {member} was successfully added**")


    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    @commands.command(aliases=['del_asp', 'delasp'])
    async def remove_aspirant(self, ctx, member: discord.Member = None) -> None:
        """Removes an aspirant from the activity monitor
        :param member: The user_id, mention or name#0000 of the user"""

        await ctx.message.delete()

        if not member:
            return await ctx.send("**Please, inform a member**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM AspirantActivity WHERE user_id = %s", (member.id))
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**The member {member} was successfully removed**")

def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(AspirantActivity(client))