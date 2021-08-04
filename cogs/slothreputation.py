import discord
from discord import components
from discord.ext import commands
from mysqldb import *
from datetime import datetime
import os
from typing import List
from extra.view import ExchangeActivityView
from .slothclass import classes

commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class SlothReputation(commands.Cog):
    '''
    Reputation commands
    '''

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("SlothReputation cog is ready!")

    # In-game commands
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return

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
        # else:
        #     return await self.insert_user(user.id, 5, 1, time_xp, 0, time_xp - 36001)

    async def level_up(self, user):
        epoch = datetime.utcfromtimestamp(0)
        the_user = await self.get_specific_user(user.id)
        lvl_end = int(the_user[0][1] ** (1 / 5))
        if the_user[0][2] < lvl_end:
            await self.update_user_money(user.id, (the_user[0][2] + 1) * 5)
            await self.update_user_lvl(user.id)
            await self.update_user_score_points(user.id, 100)
            channel = discord.utils.get(user.guild.channels, id=commands_channel_id)
            return await channel.send(f"**{user.mention} has leveled up to lvl {the_user[0][2] + 1}! <:zslothrich:701157794686042183> Here's {(the_user[0][2] + 1) * 5}łł! <:zslothrich:701157794686042183>**")


    async def get_progress_bar(self, xp: int, goal_xp, length_progress_bar: int = 17) -> str:
        """ Gets a string/emoji progress bar.
        :param xp: The current XP of the user.
        :param goal_xp: The XP they are trying to achieve.
        :param length_progress_bar: The amount of blocks in the bar. Default=20 """


        percentage = int((xp / goal_xp) * 100)
        boxes = int((percentage * length_progress_bar) / 100)
        progress_bar = f"{xp}xp / {goal_xp}xp\n{':blue_square:' * boxes}{':white_large_square:' * (length_progress_bar - boxes)}"
        return progress_bar

    @commands.command(aliases=['status', 'exchange', 'level', 'lvl', 'exp', 'xp', 'money', 'balance'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx, member: discord.Member = None):
        """ Shows the user's level and experience points. """

        if not await self.check_table_exist():
            return await ctx.send("**This command may be on maintenance!**")

        if not member:
            member = ctx.author

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))

        # Gets users ranking info, such as level and experience points
        user = await self.get_specific_user(member.id)
        if not user:
            if ctx.author.id == member.id:
                return await ctx.send(
                    embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                    view=view)
            else:
                return await ctx.send(f"**{member} doesn't have an account yet!**")

        # Gets user's currency info, such as money balance, class participations, sloth class, etc.
        ucur = await self.get_user_currency(member.id)
        sloth_profile = await self.client.get_cog('SlothClass').get_sloth_profile(member.id)
        if not ucur or not sloth_profile:
            if ctx.author.id == member.id:
                return await ctx.send(
                    embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                    view=view)
            else:
                return await ctx.send(f"**{member} doesn't have an account yet!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')

        SlothClass = self.client.get_cog('SlothClass')
        effects = await SlothClass.get_user_effects(member=member)

        if 'hacked' in effects:
            await SlothCurrency.send_hacked_image(ctx, member)
            # if ctx.author.id != member.id:
            #      await SlothClass.check_virus(ctx=ctx, target=member)
            return

        all_users = await self.get_all_users_by_score_points()
        position = [[i+1, u[4]] for i, u in enumerate(all_users) if u[0] == member.id]
        position = [it for subpos in position for it in subpos] if position else ['??', 0]

        # Gets user Server Activity info, such as messages sent and time in voice channels
        user_info = await SlothCurrency.get_user_activity_info(member.id)
        if not user_info and member.id == ctx.author.id:
            return await ctx.send(f"**For some reason you are not in the system, {ctx.author.mention}! Try again**")

        elif not user_info and not member.id == ctx.author.id:
            return await ctx.send("**Member not found in the system!**")
    

        embed = discord.Embed(title="__All Information__", colour=member.color, timestamp=ctx.message.created_at)
        xp = user[0][1]
        goal_xp = ((user[0][2]+1)**5)
        lvl = user[0][2]
        embed.add_field(name="📊 __**Level:**__", value=f"{lvl}.", inline=True)
        embed.add_field(name="🍃 __**Balance:**__", value=f"{ucur[0][1]}łł", inline=True)
        progress_bar = await self.get_progress_bar(xp=xp, goal_xp=goal_xp)
        embed.add_field(name="🔮 __**Progress Bar:**__", value=progress_bar, inline=False)

        embed.add_field(name="🧑‍🎓 __**Participated in:**__", value=f"{ucur[0][3]} classes.", inline=True)
        embed.add_field(name="🌟 __**Rewarded in:**__", value=f"{ucur[0][4]} classes.", inline=True)
        embed.add_field(name="🧑‍🏫 __**Hosted:**__", value=f"{ucur[0][5]} classes.", inline=True)

        emoji = user_class.emoji if (user_class := classes.get(sloth_profile[1].lower())) else ''
        embed.add_field(name="🕵️ __**Sloth Class:**__", value=f"{sloth_profile[1]} {emoji}", inline=True)
        embed.add_field(name="🍯 __**Has Potion:**__", value=f"{True if sloth_profile[5] else False}", inline=True)
        marriage = await SlothClass.get_user_marriage(member.id)
        if not marriage['partner']:
            embed.add_field(name="💍 __**Rings:**__", value=f"{sloth_profile[7]}/2 rings." if sloth_profile else '0 rings.', inline=True)

        embed.add_field(name="🛡️ __**Protected:**__", value=f"{await SlothClass.has_effect(effects, 'protected')}", inline=True)
        embed.add_field(name="😵 __**Knocked Out:**__", value=f"{await SlothClass.has_effect(effects, 'knocked_out')}", inline=True)
        embed.add_field(name="🔌 __**Wired:**__", value=f"{await SlothClass.has_effect(effects, 'wired')}", inline=True)
        embed.add_field(name="🐸 __**Frogged:**__", value=f"{await SlothClass.has_effect(effects, 'frogged')}", inline=True)
        embed.add_field(name="🔪 __**Knife Sharpness Stack:**__", value=f"{sloth_profile[6]}/5", inline=True)
        embed.add_field(name="🧤 __**Sabotaged:**__", value=f"{await SlothClass.has_effect(effects, 'sabotaged')}", inline=True)
        m, s = divmod(user_info[0][2], 60)
        h, m = divmod(m, 60)

        embed.add_field(name=f"💰 __**Exchangeable Activity:**__", value=f"{h:d} hours, {m:02d} minutes and {user_info[0][1]} messages.", inline=True)
        embed.add_field(name=f"🏆 __**Leaderboard Info:**__", value=f"{position[1]}. pts | #{position[0]}", inline=True)
        embed.add_field(name="🧮 __**Skills Used:**__", value=f"{sloth_profile[2]} skills.")

        # Gets tribe information for the given user
        if sloth_profile[3]:
            tribe_member = await SlothClass.get_tribe_member(user_id=member.id)
            user_tribe = await SlothClass.get_tribe_info_by_name(name=sloth_profile[3])
            tribe_owner = tribe_member[0] == tribe_member[2]
            embed.add_field(
                name="🏕️ __**Tribe:**__", 
                value=f"[{user_tribe['name']}]({user_tribe['link']}) ({user_tribe['two_emojis']}){' 👑' if tribe_owner else ''}", 
                inline=True)
                
        else:
            embed.add_field(name="🏕️ __**Tribe:**__", value="None", inline=True)

        
        if marriage['partner']:
            embed.add_field(name="💍 __**Marriage:**__", value=f"Married to <@{marriage['partner']}> (<t:{marriage['timestamp']}:R>)." if sloth_profile else '0 rings.', inline=False)

        embed.set_thumbnail(url=member.avatar.url)
        embed.set_author(name=member, icon_url=member.avatar.url, url=member.avatar.url)
        embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon.url)

        if ctx.author.id != member.id:
            return await ctx.send(embed=embed)
        else:
            view = ExchangeActivityView(self.client, user_info[0])
            if 'sabotaged' in effects:
                view.children[0].disabled = True

            await ctx.send(embed=embed, view=view)

    @commands.command(aliases=['leaderboard', 'lb', 'scoreboard'])
    async def score(self, ctx):
        """ Shows the top ten members in the reputation leaderboard. """

        if not await self.check_table_exist():
            return await ctx.send("**This command may be on maintenance!**")

        # users = await self.get_users()
        top_ten_users = await self.get_top_ten_users()
        # sorted_members = sorted(users, key=lambda tup: tup[4], reverse=True)
        leaderboard = discord.Embed(title="__The Language Sloth's Leaderboard__", colour=discord.Colour.dark_green(),
                                    timestamp=ctx.message.created_at)
        # user_score = await self.get_specific_user(ctx.author.id)
        # user_score = await self.get_user_score_position(ctx.author.id)
        all_users = await self.get_all_users_by_score_points()
        position = [[i+1, u[4]] for i, u in enumerate(all_users) if u[0] == ctx.author.id]
        position = [it for subpos in position for it in subpos] if position else ['??', 0]

        leaderboard.set_footer(text=f"Your score: {position[1]} | #{position[0]}", icon_url=ctx.author.avatar.url)
        leaderboard.set_thumbnail(url=ctx.guild.icon.url)

        # Embeds each one of the top ten users.
        for i, sm in enumerate(top_ten_users):
            member = discord.utils.get(ctx.guild.members, id=sm[0])
            leaderboard.add_field(name=f"[{i + 1}]# - __**{member}**__", value=f"__**Score:**__ `{sm[4]}`",
                                  inline=False)
            if i + 1 == 10:
                break
        return await ctx.send(embed=leaderboard)

    @commands.command(aliases=['level_board', 'levelboard', 'levels'])
    async def level_score(self, ctx):
        """ Shows the top ten members in the level leaderboard. """

        # users = await self.get_users()
        top_ten_users = await self.get_top_ten_xp_users()
        # sorted_members = sorted(users, key=lambda tup: tup[4], reverse=True)
        leaderboard = discord.Embed(title="__The Language Sloth's Level Ranking Leaderboard__", colour=discord.Colour.dark_green(),
                                    timestamp=ctx.message.created_at)
        # user_score = await self.get_specific_user(ctx.author.id)
        # user_score = await self.get_user_score_position(ctx.author.id)
        all_users = await self.get_all_users_by_xp()
        position = [[i+1, u[1]] for i, u in enumerate(all_users) if u[0] == ctx.author.id]
        position = [it for subpos in position for it in subpos] if position else ['??', 0]

        leaderboard.set_footer(text=f"Your XP: {position[1]} | #{position[0]}", icon_url=ctx.author.avatar.url)
        leaderboard.set_thumbnail(url=ctx.guild.icon.url)

        # Embeds each one of the top ten users.
        for i, sm in enumerate(top_ten_users):
            member = discord.utils.get(ctx.guild.members, id=sm[0])
            leaderboard.add_field(name=f"[{i + 1}]# - __**{member}**__", value=f"__**Level:**__ `{sm[2]}` | __**XP:**__ `{sm[1]}`",
                                  inline=False)
            if i + 1 == 10:
                break
        return await ctx.send(embed=leaderboard)

    @commands.command()
    async def rep(self, ctx, member: discord.Member = None):
        '''
        Gives someone reputation points.
        :param member: The member to give the reputation.
        '''
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
            if ctx.author.id == member.id:

                view = discord.ui.View()
                view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))
                return await ctx.send(
                    embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                    view=view)
            else:
                return await ctx.send("**This member is not on the leaderboard yet!**", delete_after=3)

        SlothClass = self.client.get_cog('SlothClass')

        perpetrator_fx = await SlothClass.get_user_effects(ctx.author)
        if 'sabotaged' in perpetrator_fx:
            return await ctx.send(f"**You can't rep anyone because you have been sabotaged, {ctx.author.mention}!**")

        target_fx = await SlothClass.get_user_effects(member)
        if 'sabotaged' in target_fx:
            return await ctx.send(f"**You can't rep {member.mention} because they have been sabotaged, {ctx.author.mention}!**")

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
    @commands.command(hidden=True)
    async def create_table_member_score(self, ctx):
        '''
        (ADM) Creates the MembersScore table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute(
            "CREATE TABLE MembersScore (user_id bigint, user_xp bigint, user_lvl int, user_xp_time int, score_points bigint, rep_time bigint)")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table *MembersScore* created!**", delete_after=3)

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def drop_table_member_score(self, ctx):
        '''
        (ADM) Drops the MembersScore table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE MembersScore")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table *MembersScore* dropped!**", delete_after=3)

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def reset_table_member_score(self, ctx):
        '''
        (ADM) Resets the MembersScore table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM MembersScore")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table *MembersScore* reseted!**", delete_after=3)

    async def insert_user(self, id: int, xp: int, lvl: int, xp_time: int, score_points: int, rep_time: int):
        mycursor, db = await the_database()
        await mycursor.execute(
            f"INSERT INTO MembersScore VALUES({id}, {xp}, {lvl}, {xp_time}, {score_points}, {rep_time})")
        await db.commit()
        await mycursor.close()

    async def update_user_xp(self, id: int, xp: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE MembersScore SET user_xp = user_xp+{xp} WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def update_user_lvl(self, id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE MembersScore set user_lvl = user_lvl+1 WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def update_user_xp_time(self, id: int, time: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE MembersScore SET user_xp_time = {time} WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def update_user_money(self, user_id: int, money: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE UserCurrency SET user_money = user_money + {money} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_score_points(self, user_id: int, score_points: int):
        mycursor, db = await the_database()
        await mycursor.execute(
            f"UPDATE MembersScore SET score_points = score_points + {score_points} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_rep_time(self, user_id: int, rep_time: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE MembersScore SET rep_time = {rep_time} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def get_users(self):
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore")
        members = await mycursor.fetchall()
        await mycursor.close()
        return members

    async def get_top_ten_users(self) -> List[List[int]]:
        """ Gets the top ten users in the reputation score. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore ORDER BY score_points DESC LIMIT 10")
        top_ten_members = await mycursor.fetchall()
        await mycursor.close()
        return top_ten_members

    async def get_top_ten_xp_users(self) -> List[List[int]]:
        """ Gets the top ten users in the experience points. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore ORDER BY user_xp DESC LIMIT 10")
        top_ten_members = await mycursor.fetchall()
        await mycursor.close()
        return top_ten_members

    async def get_specific_user(self, user_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM MembersScore WHERE user_id = {user_id}")
        member = await mycursor.fetchall()
        await mycursor.close()
        return member

    async def remove_user(self, id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"DELETE FROM MembersScore WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def clear_user_lvl(self, id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE MembersScore SET user_xp = 0, user_lvl = 1 WHERE user_id = {id}")
        await db.commit()
        await mycursor.close()

    async def check_table_exist(self) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'MembersScore'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

    async def get_user_currency(self, user_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM UserCurrency WHERE user_id = {user_id}")
        user_currency = await mycursor.fetchall()
        await mycursor.close()
        return user_currency

    async def insert_user_currency(self, user_id: int, the_time: int):
        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO UserCurrency (user_id, user_money, last_purchase_ts) VALUES (%s, %s, %s)",
                               (user_id, 0, the_time))
        await db.commit()
        await mycursor.close()

    async def get_all_users_by_score_points(self) -> List[List[int]]:
        """ Gets all users from the MembersScore table ordered by score points. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore ORDER BY score_points DESC")
        users = await mycursor.fetchall()
        await mycursor.close()
        return users

    async def get_all_users_by_xp(self) -> List[List[int]]:
        """ Gets all users from the MembersScore table ordered by XP. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore ORDER BY user_xp DESC")
        users = await mycursor.fetchall()
        await mycursor.close()
        return users


def setup(client):
    client.add_cog(SlothReputation(client))
