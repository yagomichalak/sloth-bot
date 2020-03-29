import discord
from discord.ext import commands
from datetime import datetime
from mysqldb import *
import asyncio

mod_role_id = 497522510212890655
guild_id = 459195345419763713


class ModActivity(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('ModActivity cog is ready!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = self.client.get_guild(guild_id)
        moderator_role = discord.utils.get(guild.roles, id=mod_role_id)
        if not moderator_role in member.roles:
            return
        epoch = datetime.utcfromtimestamp(0)
        the_time = (datetime.utcnow() - epoch).total_seconds()
        old_time = await self.get_moderator_current_timestamp(member.id, int(the_time))
        addition = int(the_time) - old_time

        if not before.channel:
            return await self.update_moderator(member.id)

        if not after.channel:
            await self.add_time_moderator(member.id, addition)

    async def update_moderator(self, mod_id: int):
        mycursor, db = await the_data_base()
        epoch = datetime.utcfromtimestamp(0)
        new_ts = (datetime.utcnow() - epoch).total_seconds()
        await mycursor.execute(f'UPDATE ModActivity SET timestamp = {int(new_ts)} WHERE mod_id = {mod_id}')
        await db.commit()
        await mycursor.close()

    async def add_time_moderator(self, mod_id: int, addition: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f'UPDATE ModActivity SET time = time + {addition} WHERE mod_id = {mod_id}')
        await db.commit()
        await self.update_moderator(mod_id)
        await mycursor.close()

    async def get_moderator_current_timestamp(self, mod_id: int, old_ts: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f'SELECT * FROM ModActivity WHERE mod_id = {mod_id}')
        mod = await mycursor.fetchall()
        await mycursor.close()
        if not mod:
            await self.insert_moderator(mod_id, old_ts)
            return await self.get_moderator_current_timestamp(mod_id, old_ts)

        return mod[0][2]

    async def insert_moderator(self, mod_id: int, old_ts: int):
        mycursor, db = await the_data_base()
        await mycursor.execute("INSERT INTO ModActivity (mod_id, time, timestamp) VALUES (%s, %s, %s)",
                               (mod_id, 0, old_ts))
        await db.commit()
        await mycursor.close()

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def showall(self, ctx):
        mycursor, db = await the_data_base()
        await mycursor.execute('SELECT * FROM ModActivity')
        mods = await mycursor.fetchall()
        await mycursor.close()
        embed = discord.Embed(title="Weekly Moderation Activity Log",
                              description="Time spent by the mods in Voice-Channels.",
                              colour=discord.Colour.dark_green(), timestamp=ctx.message.created_at)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        for mod in mods:
            user = discord.utils.get(ctx.guild.members, id=mod[0])
            embed.add_field(name=user, value=f"Hours spent: {((mod[1]) / 3600):.2f}", inline=False)

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
    @commands.command()
    async def create_mod_table(self, ctx):
        mycursor, db = await the_data_base()
        await mycursor.execute('CREATE TABLE ModActivity (mod_id bigint, time bigint, timestamp bigint)')
        await mycursor.close()

    @commands.command()
    async def drop_table_mods(self, ctx):
        mycursor, db = await the_data_base()
        await mycursor.execute('DROP TABLE ModActivity')
        await mycursor.close()


def setup(client):
    client.add_cog(ModActivity(client))
