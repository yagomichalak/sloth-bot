import discord
from discord.ext import commands
from datetime import datetime
from mysqldb import *
import asyncio
import os
from extra import utils
from typing import List

senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID'))
mod_role_id = int(os.getenv('MOD_ROLE_ID'))
guild_id = int(os.getenv('SERVER_ID'))


class AspirantActivity(commands.Cog):
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
    async def add_aspirant(self, ctx, members: commands.Greedy[discord.Member] = None) -> None:
        """Adds an aspirant from the activity monitor
        :param member: The user_id, mention or name#0000 of the user"""

        await ctx.message.delete()

        if not members:
            return await ctx.send("**Please, inform a member**")

        for member in members:
            # Checks if the user is already in the table
            if  not await self.get_user(member.id):
                mycursor, db = await the_database()
                await mycursor.execute("INSERT INTO AspirantActivity (user_id, time, timestamp, messages) VALUES (%s, %s, %s, %s)",
                                    (member.id, 0, None, 1))
                await db.commit()
                await mycursor.close()
                await ctx.send(f"**The member {member} was successfully added**")
            else:
                return await ctx.send(f"**The user {member} is already been monitored**")


    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    @commands.command(aliases=['del_asp', 'delasp'])
    async def remove_aspirant(self, ctx, members: commands.Greedy[discord.Member] = None) -> None:
        """Removes an aspirant from the activity monitor
        :param member: The user_id, mention or name#0000 of the user"""

        await ctx.message.delete()

        if not members:
            return await ctx.send("**Please, inform a member**")

        for member in members:
            mycursor, db = await the_database()
            await mycursor.execute("DELETE FROM AspirantActivity WHERE user_id = %s", (member.id))
            await db.commit()
            await mycursor.close()
            await ctx.send(f"**The member {member} was successfully removed**")


    ### Functions
    async def get_all_aspirants(self) -> List[List[int]]:
        """ Gets all aspirants. """

        mycursor, _ = await the_database()
        await mycursor.execute('SELECT user_id FROM AspirantActivity')
        users = await mycursor.fetchall()
        await mycursor.close()
        members = []
        for user in users:
            members.append(user[0])
        return members

    async def get_aspirant_current_timestamp(self, user_id: int, old_ts: int) -> int:
        """ Gets a specific aspirant's timestamp.
        :param user_id: The ID of the user from whom to get it.
        :param old_ts: The current timestamp. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM AspirantActivity WHERE user_id = %s", (user_id,))
        user = await mycursor.fetchall()
        await mycursor.close()

        if not user:
            await self.insert_aspirant(user_id, old_ts)
            return await self.get_aspirant_current_timestamp(user_id, old_ts)

        if user[0][2]:
            return user[0][2]
        else:
            return old_ts

    async def get_aspirant_current_messages(self, user_id: int) -> int:
        """ Gets a specific aspirant's messages counter.
        :param user_id: The ID of the user from whom to get it. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM AspirantActivity WHERE user_id = %s", (user_id,))
        user = await mycursor.fetchall()
        await mycursor.close()

        if not user:
            await self.insert_aspirant_message(user_id)
            return await self.get_aspirant_current_messages(user_id)

        return user[0][3]

    async def add_aspirant_time(self, user_id: int, addition: int) -> None:
        """ Updates an aspirant's time counter.
        :param user_id: The ID of the aspirant to add.
        :param addition: The addition to increment to their current time counter. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE AspirantActivity SET time = time + %s WHERE user_id = %s", (addition, user_id))
        await db.commit()
        await mycursor.close()
        await self.update_aspirant_time(user_id)


    async def update_aspirant_message(self, user_id: int) -> None:
        """ Updates an aspirant's message counter.
        :param user_id: The user for whom to update it. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE AspirantActivity SET messages = messages + 1 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()


    async def update_aspirant_time(self, user_id: int) -> None:
        """ Updates an aspirant's timestamp.
        :param user_id: The ID of the aspirant from whom to update it. """

        mycursor, db = await the_database()
        current_ts = await utils.get_timestamp()
        await mycursor.execute("UPDATE AspirantActivity SET timestamp = %s WHERE user_id = %s", (int(current_ts), user_id))
        await db.commit()
        await mycursor.close()


    async def insert_aspirant(self, user_id: int, old_ts: int) -> None:
        """ Inserts an aspirant to the database.
        :param user_id: The ID of the aspirant to add.
        :param old_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute(
            "INSERT INTO AspirantActivity (user_id, time, timestamp, messages) VALUES (%s, %s, %s, %s)", 
            (user_id, 0, old_ts, 0))
        await db.commit()
        await mycursor.close()


    async def reset_users_activity(self, user_id: int) -> None:
        """ Resets an aspirant's statuses.
        :param user_id: The ID of the user to reset. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE AspirantActivity SET messages = 0, time = 0 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

    async def get_user(self, user_id: int) -> None:
        """ Resets an aspirant's statuses.
        :param user_id: The ID of the user to reset. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM AspirantActivity WHERE user_id = %s", (user_id,))
        user = await mycursor.fetchall()
        await mycursor.close()

        if user:
            return True
        else:
            return False

    ### Database commands for aspirants activity
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_aspirants_table(self, ctx):
        """(ADM) Creates the AspirantActivity table."""
        
        member: discord.Member = ctx.author
        if await self.check_aspirant_activity_exists():
            return await ctx.send(f"**The AspirantActivity table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute(
            'CREATE TABLE AspirantActivity (user_id bigint , time bigint, timestamp bigint default null, messages int)')
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `AspirantActivity` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_aspirants(self, ctx):
        """(ADM) Drops the AspirantActivity table."""

        member: discord.Member = ctx.author
        if not await self.check_aspirant_activity_exists():
            return await ctx.send(f"**The AspirantActivity table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute('DROP TABLE AspirantActivity')
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `AspirantActivity` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_aspirants(self, ctx):
        """ (ADM) Resets the AspirantActivity table. """

        member: discord.Member = ctx.author
        if not await self.check_aspirant_activity_exists():
            return await ctx.send(f"**The AspirantActivity table doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM AspirantActivity")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `AspirantActivity` reset, {member.mention}!**")

    async def check_aspirant_activity_exists(self) -> bool:
        """ Checks whether the AspirantActivity table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'AspirantActivity'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False



def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(AspirantActivity(client))