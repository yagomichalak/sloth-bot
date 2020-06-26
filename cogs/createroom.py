import discord
from discord.ext import commands
from datetime import datetime
from mysqldb import *

create_room_channel_id = 693180716258689074
create_room_category_id = 693180588919750778


class SmartCreateRoom(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('SmartCreateRoom cog is online!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel:
            if before.channel.category:
                if before.channel.category.id == create_room_category_id:
                    user_voice_channel = discord.utils.get(member.guild.channels, id=before.channel.id)
                    len_users = len(user_voice_channel.members)
                    if len_users == 0 and user_voice_channel.id != create_room_channel_id:
                        return await user_voice_channel.delete()

        if not after.channel:
            return
        if after.channel.id == create_room_channel_id:
            epoch = datetime.utcfromtimestamp(0)
            the_time = (datetime.utcnow() - epoch).total_seconds()
            old_time = await self.get_user_vc_timestamp(member.id, the_time)
            if not the_time - old_time >= 60:
                await member.send(
                    f"**You're on a cooldown, try again in {round(60 - (the_time - old_time))} seconds!**",
                    delete_after=5)
                # return await member.move_to(None)
                return
            if the_time - old_time >= 60:
                await self.update_user_vc_ts(member.id, the_time)

            embed = discord.Embed(title='Create a Room',
                                  description='In this menu you can set how you want your Voice-Channel to be made.',
                                  colour=discord.Colour.dark_green())
            msg1 = await member.send(embed=embed)
            embed2 = discord.Embed(title='Voice-Channel size',
                                   description='How many users can access the Voice-Channel? Type a number between 0 and 10\nPs: if you type **0** it will be limitless',
                                   colour=discord.Colour.dark_green())
            msg2 = await member.send(embed=embed2)

            def check(m):
                value = m.content
                author = m.author
                if value.isnumeric() and author == member:
                    value = int(value)
                    if value >= 0 and value <= 10:
                        return True
                    else:
                        self.client.loop.create_task(member.send('**Value out of range!**'))
                elif not value.isnumeric() and author == member:
                    self.client.loop.create_task(member.send('**Inform a valid value!**'))

            try:
                limit = await self.client.wait_for('message', timeout=60.0, check=check)
                limit = limit.content
            except asyncio.TimeoutError:
                await msg1.delete()
                await msg2.delete()
                timeout = discord.Embed(title='Timeout',
                                        description='You took too long to answer the questions, try again later.',
                                        colour=discord.Colour.dark_red())
                return await member.send(embed=timeout, delete_after=3)

            embed3 = discord.Embed(title='Voice-Channel name',
                                   description='What name do you want the Voice-Channel to have?\nPs: Names bigger than 20 characters will be disconsidered.',
                                   colour=discord.Colour.dark_green())
            msg3 = await member.send(embed=embed3)

            def check2(m):
                value = m.content
                author = m.author
                if len(value) <= 20 and author == member:
                    return True
                elif not len(value) <= 20 and author == member:
                    self.client.loop.create_task(member.send('**Inform a shorter name!**'))

            try:
                name = await self.client.wait_for('message', timeout=60.0, check=check2)
                name = name.content
            except asyncio.TimeoutError:
                await msg1.delete()
                await msg2.delete()
                await msg3.delete()
                timeout = discord.Embed(title='Timeout',
                                        description='You took too long to answer the questions, try again later.',
                                        colour=discord.Colour.dark_red())
                return await member.send(embed=timeout, delete_after=3)
            else:
                if limit == 0:
                    limit = None
                the_category_test = discord.utils.get(member.guild.categories, id=create_room_category_id)
                creation = await the_category_test.create_voice_channel(name=f"{name}", user_limit=limit)
                embed4 = discord.Embed(title=f'Room {name} Created!',
                                       description=f'You are gonna be moved now to **{name}**, thank you for using me!',
                                       colour=discord.Colour.green())
                await member.send(embed=embed4)
                try:
                    await member.move_to(creation)
                except discord.errors.HTTPException:
                    await member.send("**You cannot be moved because you are not in a Voice-Channel!**",
                                      delete_after=3)
                    await creation.delete()

    async def get_user_vc_timestamp(self, user_id: int, the_time: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f'SELECT * FROM UserVCstamp WHERE user_id = {user_id}')
        user = await mycursor.fetchall()
        await mycursor.close()
        if not user:
            await self.insert_user_vc(user_id, the_time)
            return await self.get_user_vc_timestamp(user_id, the_time)

        return user[0][1]

    async def insert_user_vc(self, user_id: int, the_time: int):
        mycursor, db = await the_data_base()
        await mycursor.execute("INSERT INTO UserVCstamp (user_id, user_vc_ts) VALUES (%s, %s)", (user_id, the_time - 61))
        await db.commit()
        await mycursor.close()

    async def update_user_vc_ts(self, user_id: int, new_ts: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"UPDATE UserVCstamp SET user_vc_ts = {new_ts} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def create_table_user_vc_ts(self, ctx):
        mycursor, db = await the_data_base()
        await mycursor.execute("CREATE TABLE UserVCstamp (user_id bigint, user_vc_ts bigint)")
        await db.commit()
        await mycursor.close()

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def drop_table_user_vc_ts(self, ctx):
        mycursor, db = await the_data_base()
        await mycursor.execute("DROP TABLE UserVCstamp")
        await db.commit()
        await mycursor.close()

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def reset_table_user_vc_ts(self, ctx):
        await ctx.message.delete()
        await self.drop_table_user_vc_ts(ctx)
        await self.create_table_user_vc_ts(ctx)
        return await ctx.send("**Table reseted!**", delete_after=3)


def setup(client):
    client.add_cog(SmartCreateRoom(client))
