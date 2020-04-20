import discord
from discord.ext import commands
from mysqldb2 import *
from datetime import datetime

commands_channel_id = 562019654017744904


class SlothReputation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("SlothReputation cog is ready!")

    # In-game commands
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        elif not await self.check_table_exist():
            return

        epoch = datetime.utcfromtimestamp(0)
        time_xp = (datetime.utcnow() - epoch).total_seconds()
        await self.update_data(message.author, time_xp)

    async def update_data(self, user, time_xp):
        the_member = await self.get_specific_user(user.id)
        if the_member:
            if time_xp - the_member[0][3] >= 3 or the_member[0][1] == 0:
                await self.update_user_xp_time(user.id, time_xp)
                await self.update_user_xp(user.id, 5)
                return await self.level_up(user)
        else:
            return await self.insert_user(user.id, 5, 1, time_xp, 0, time_xp - 36001)

    async def level_up(self, user):
        epoch = datetime.utcfromtimestamp(0)
        time_xp = (datetime.utcnow() - epoch).total_seconds()
        the_user = await self.get_specific_user(user.id)
        lvl_end = int(the_user[0][1] ** (1 / 5))
        if the_user[0][2] < lvl_end:
            await self.update_user_money(user.id, 10)
            await self.update_user_lvl(user.id)
            await self.update_user_score_points(user.id, 100)
            channel = discord.utils.get(user.guild.channels, id=commands_channel_id)
            return await channel.send(f"**{user.mention} has leveled up to lvl {the_user[0][2] + 1}! <:zslothrich:701157794686042183> Here's 5łł! <:zslothrich:701157794686042183>**")


    @commands.command()
    async def level(self, ctx):
        if not await self.check_table_exist():
            return await ctx.send("**This command may be on maintenance!**", delete_after=3)
        user = await self.get_specific_user(ctx.author.id)
        if not user:
            return await self.level(ctx)

        await ctx.message.delete()
        embed = discord.Embed(title="Rank", description=f"__**Level:**__ {user[0][2]}\n__**EXP:**__ {user[0][1]} / {((user[0][2]+1)**5)}.",
                              colour=discord.Colour.dark_green())
        embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url)
        return await ctx.send(content=None, embed=embed)

    @commands.command()
    async def score(self, ctx):
        await ctx.message.delete()
        if not await self.check_table_exist():
            return await ctx.send("**This command may be on maintenance!**", delete_after=3)
        users = await self.get_users()
        sorted_members = sorted(users, key=lambda tup: tup[4], reverse=True)
        leaderboard = discord.Embed(title="__The Language Sloth's Leaderboard__", colour=discord.Colour.dark_green(),
                                    timestamp=ctx.message.created_at)
        user_score = await self.get_specific_user(ctx.author.id)
        leaderboard.set_footer(text=f"Your score: {user_score[0][4]}")
        leaderboard.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/562019489642709022/676564604087697439/ezgif.com-gif-maker_1.gif')
        for i, sm in enumerate(sorted_members):
            member = discord.utils.get(ctx.guild.members, id=sm[0])
            leaderboard.add_field(name=f"[{i + 1}]# - __**{member}**__", value=f"__**Score:**__ `{sm[4]}`",
                                  inline=False)
            if i + 1 == 10:
                break
        return await ctx.send(embed=leaderboard)

    @commands.command()
    async def rep(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.message.delete()
            return await ctx.send(f"**Inform a member to rep to!**", delete_after=3)

        if member.id == ctx.author.id:
            await ctx.message.delete()
            return await ctx.send(f"**You cannot rep yourself!**", delete_after=3)

        user = await self.get_specific_user(ctx.author.id)
        if not user:
            return await self.rep(ctx)

        await ctx.message.delete()

        target_user = await self.get_specific_user(member.id)
        if not target_user:
            return await ctx.send("**This member is not on the leaderboard yet!**", delete_after=3)

        epoch = datetime.utcfromtimestamp(0)
        time_xp = (datetime.utcnow() - epoch).total_seconds()
        sub_time = time_xp - user[0][5]
        cooldown = 36000
        if int(sub_time) >= int(cooldown):
            await self.update_user_score_points(ctx.author.id, 100)
            await self.update_user_score_points(member.id, 100)
            await self.update_user_rep_time(ctx.author.id, time_xp)
            await self.update_user_money(ctx.author.id, 5)
            await self.update_user_money(member.id, 5)
            return await ctx.send(
                f"**{ctx.author.mention} repped {member.mention}! :leaves:Both of them got 5łł:leaves:**")
        else:
            m, s = divmod(int(cooldown) - int(sub_time), 60)
            h, m = divmod(m, 60)
            if h > 0:
                return await ctx.send(f"**Rep again in {h:d} hours, {m:02d} minutes and {s:02d} seconds!**",
                                      delete_after=10)
            elif m > 0:
                return await ctx.send(f"**Rep again in {m:02d} minutes and {s:02d} seconds!**", delete_after=10)
            elif s > 0:
                return await ctx.send(f"**Rep again in {s:02d} seconds!**", delete_after=10)

    # Database commands

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def create_table_member_score(self, ctx):
        await ctx.message.delete()
        mycursor, db = await the_data_base3()
        await mycursor.execute(
            "CREATE TABLE MembersScore (user_id bigint, user_xp bigint, user_lvl int, user_xp_time int, score_points bigint, rep_time bigint)")
        await mycursor.close()
        await ctx.send("**Table *MembersScore* created!**", delete_after=3)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def drop_table_member_score(self, ctx):
        await ctx.message.delete()
        mycursor, db = await the_data_base3()
        await mycursor.execute("DROP TABLE MembersScore")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table *MembersScore* dropped!**", delete_after=3)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def reset_table_member_score(self, ctx):
        await ctx.message.delete()
        mycursor, db = await the_data_base3()
        await mycursor.execute("DROP TABLE MembersScore")
        await db.commit()
        await mycursor.execute(
            "CREATE TABLE MembersScore (user_id bigint, user_xp bigint, user_lvl int, user_xp_time int, score_points bigint, rep_time bigint)")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table *MembersScore* reseted!**", delete_after=3)

    async def insert_user(self, id: int, xp: int, lvl: int, xp_time: int, score_points: int, rep_time: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(
            f"INSERT INTO MembersScore VALUES({id}, {xp}, {lvl}, {xp_time}, {score_points}, {rep_time})")
        await db.commit()
        await mycursor.close()

    async def update_user_xp(self, id: int, xp: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"UPDATE MembersScore SET user_xp = user_xp+{xp} WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def update_user_lvl(self, id: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"UPDATE MembersScore set user_lvl = user_lvl+1 WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def update_user_xp_time(self, id: int, time: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"UPDATE MembersScore SET user_xp_time = {time} WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def update_user_money(self, user_id: int, money: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserCurrency SET user_money = user_money + {money} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_score_points(self, user_id: int, score_points: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(
            f"UPDATE MembersScore SET score_points = score_points + {score_points} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_rep_time(self, user_id: int, rep_time: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"UPDATE MembersScore SET rep_time = {rep_time} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def get_users(self):
        mycursor, db = await the_data_base3()
        await mycursor.execute("SELECT * FROM MembersScore")
        members = await mycursor.fetchall()
        await mycursor.close()
        return members

    async def get_specific_user(self, user_id: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"SELECT * FROM MembersScore WHERE user_id = {user_id}")
        member = await mycursor.fetchall()
        await mycursor.close()
        return member

    async def remove_user(self, id: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"DELETE FROM MembersScore WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def clear_user_lvl(self, id: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"UPDATE MembersScore SET user_xp = 0, user_lvl = 1 WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def check_table_exist(self):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'MembersScore'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True


def setup(client):
    client.add_cog(SlothReputation(client))
