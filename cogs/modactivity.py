import discord
from discord.ext import commands
from datetime import datetime
from mysqldb import *
import asyncio
import os

mod_role_id = int(os.getenv('MOD_ROLE_ID'))
guild_id = int(os.getenv('SERVER_ID'))


class ModActivity(commands.Cog):
    '''
    A cog related to the Moderators' activity.
    '''

    def __init__(self, client):
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
        if not moderator_role in message.author.roles:
            return

        await self.get_moderator_current_messages(message.author.id)
        await self.update_moderator_message(message.author.id)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        guild = self.client.get_guild(guild_id)
        moderator_role = discord.utils.get(guild.roles, id=mod_role_id)
        if not moderator_role in member.roles:
            return
        epoch = datetime.utcfromtimestamp(0)
        the_time = (datetime.utcnow() - epoch).total_seconds()
        old_time = await self.get_moderator_current_timestamp(member.id, int(the_time))
        addition = the_time - old_time

        if not before.channel:
            return await self.update_moderator(member.id)

        if not after.channel:
            await self.add_time_moderator(member.id, addition)

    async def update_moderator(self, mod_id: int):
        mycursor, db = await the_database()
        epoch = datetime.utcfromtimestamp(0)
        new_ts = (datetime.utcnow() - epoch).total_seconds()
        await mycursor.execute(f'UPDATE ModActivity SET timestamp = {int(new_ts)} WHERE mod_id = {mod_id}')
        await db.commit()
        await mycursor.close()

    async def add_time_moderator(self, mod_id: int, addition: int):
        mycursor, db = await the_database()
        await mycursor.execute(f'UPDATE ModActivity SET time = time + {addition} WHERE mod_id = {mod_id}')
        await db.commit()
        await mycursor.close()
        await self.update_moderator(mod_id)

    async def get_moderator_current_timestamp(self, mod_id: int, old_ts: int):
        mycursor, db = await the_database()
        await mycursor.execute(f'SELECT * FROM ModActivity WHERE mod_id = {mod_id}')
        mod = await mycursor.fetchall()
        await mycursor.close()

        if not mod:
            await self.insert_moderator(mod_id, old_ts)
            return await self.get_moderator_current_timestamp(mod_id, old_ts)

        if mod[0][2]:
            return mod[0][2]
        else:
            return old_ts

    async def insert_moderator(self, mod_id: int, old_ts: int):
        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO ModActivity (mod_id, time, timestamp, messages) VALUES (%s, %s, %s, %s)",
                               (mod_id, 0, old_ts, 0))
        await db.commit()
        await mycursor.close()

    async def get_moderator_current_messages(self, mod_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f'SELECT * FROM ModActivity WHERE mod_id = {mod_id}')
        mod = await mycursor.fetchall()
        await mycursor.close()

        if not mod:
            await self.insert_moderator_message(mod_id)
            return await self.get_moderator_current_messages(mod_id)

        return mod[0][3]

    async def insert_moderator_message(self, mod_id: int):
        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO ModActivity (mod_id, time, timestamp, messages) VALUES (%s, %s, %s, %s)",
                               (mod_id, 0, None, 1))
        await db.commit()
        await mycursor.close()

    async def update_moderator_message(self, mod_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f'UPDATE ModActivity SET messages = messages+1 WHERE mod_id = {mod_id}')
        await db.commit()
        await mycursor.close()

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def modrep(self, ctx):
        '''
        (ADM) Shows all the moderators and their statuses in an embedded message.
        '''
        mycursor, db = await the_database()
        await mycursor.execute('SELECT * FROM ModActivity')
        mods = await mycursor.fetchall()
        await mycursor.close()

        embed = discord.Embed(title="This Week's Report",
                              description="Moderators' activity statuses.",
                              url='https://discordapp.com',
                              colour=discord.Colour.dark_green(), timestamp=ctx.message.created_at)
        embed.set_footer(text='Activity Report',
                         icon_url=self.client.user.avatar_url)
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
                await self.drop_table_mods(ctx)
                await self.create_mod_table(ctx)
                resp = await ctx.send("**Log reseted!**")
            else:
                resp = await ctx.send("**Not reseted!**")
            await the_msg.delete()
            await asyncio.sleep(2)
            return await resp.delete()

    # Database commands
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_mod_table(self, ctx):
        '''
        (ADM) Creates the ModActivity table.
        '''
        mycursor, db = await the_database()
        await mycursor.execute(
            'CREATE TABLE ModActivity (mod_id bigint, time bigint, timestamp bigint default null, messages int)')
        await db.commit()
        await mycursor.close()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_mods(self, ctx):
        '''
        (ADM) Drops the ModActivity table.
        '''
        mycursor, db = await the_database()
        await mycursor.execute('DROP TABLE ModActivity')
        await db.commit()
        await mycursor.close()


def setup(client):
    client.add_cog(ModActivity(client))
