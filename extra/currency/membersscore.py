import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union


class MembersScoreTable(commands.Cog):
    """ Class for the MembersScore table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    # ===== COMMANDS =====
    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def create_table_member_score(self, ctx):
        """ (ADM) Creates the MembersScore table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if await self.check_members_score_table_exists():
            return await ctx.send(f"**The `MembersScore` table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute(
            "CREATE TABLE MembersScore (user_id bigint, user_xp bigint, user_lvl int, user_xp_time int, score_points bigint, rep_time bigint)")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `MembersScore` created, {member.mention}!**")

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def drop_table_member_score(self, ctx):
        """ (ADM) Drops the MembersScore table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if not await self.check_members_score_table_exists():
            return await ctx.send(f"**The `MembersScore` table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE MembersScore")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `MembersScore` dropped, {member.mention}!**")

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def reset_table_member_score(self, ctx):
        """ (ADM) Resets the MembersScore table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if not await self.check_members_score_table_exists():
            return await ctx.send(f"**The `MembersScore` table doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM MembersScore")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `MembersScore` reset, {member.mention}!**")

    # ===== SHOW =====
    async def check_members_score_table_exists(self) -> bool:
        """ Checks whether the MembersScore table exists in the database. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'MembersScore'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    # ===== INSERT =====
    
    async def insert_member_score(self, user_id: int, xp: int, lvl: int, xp_time: int, score_points: int, rep_time: int) -> None:
        """ Inserts a user into the MembersScore table.
        :param user_id: The ID of the user to insert.
        :param xp: The amount of XP the user is gonna start with.
        :param lvl: The level the user is gonna start with.
        :param score_points: The intial score_points.
        :param rep_time: The initial rep timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO MembersScore VALUES (%s, %s, %s, %s, %s, %s)", (user_id, xp, lvl, xp_time, score_points, rep_time))
        await db.commit()
        await mycursor.close()

    # ===== SELECT =====

    async def get_specific_user(self, user_id: int) -> List[List[int]]:
        """ Gets a specifc user from the MembersScore table.
        :param user_id: The ID of the user to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore WHERE user_id = %s", (user_id,))
        member = await mycursor.fetchall()
        await mycursor.close()
        return member

    async def get_member_scores(self) -> List[List[int]]:
        """ Gets all users from the MembersScore table. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore")
        members = await mycursor.fetchall()
        await mycursor.close()
        return members

    async def get_top_ten_users(self) -> List[List[int]]:
        """ Gets the top ten users with the most reputation point. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore ORDER BY score_points DESC LIMIT 10")
        top_ten_members = await mycursor.fetchall()
        await mycursor.close()
        return top_ten_members

    async def get_top_ten_xp_users(self) -> List[List[int]]:
        """ Gets the top ten users with most experience points. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore ORDER BY user_xp DESC LIMIT 10")
        top_ten_members = await mycursor.fetchall()
        await mycursor.close()
        return top_ten_members

    async def get_all_users_by_score_points(self) -> List[List[int]]:
        """ Gets all users from the MembersScore table ordered by score points. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore ORDER BY score_points DESC")
        users = await mycursor.fetchall()
        await mycursor.close()
        return users

    async def get_all_users_by_xp(self) -> List[List[int]]:
        """ Gets all users from the MembersScore table ordered by XP. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM MembersScore ORDER BY user_xp DESC")
        users = await mycursor.fetchall()
        await mycursor.close()
        return users

    # ===== UPDATE =====
    async def clear_user_lvl(self, user_id: int) -> None:
        """ Clears the level and XP of a user.
        :param user_id: The ID of the user to clear. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE MembersScore SET user_xp = 0, user_lvl = 1 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

    async def update_user_xp(self, user_id: int, xp: int) -> None:
        """ Updates the user Xp in the MembersScore table.
        :param user_id: The ID of the user to update.
        :pram xp: The XP incremention value to apply. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE MembersScore SET user_xp = user_xp + %s WHERE user_id = %s", (xp, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_lvl(self, user_id: int) -> None:
        """ Updates the user level in the MembersScore table.
        :param user_id: The ID of the user to update the level. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE MembersScore set user_lvl = user_lvl + 1 WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

    async def update_user_xp_time(self, user_id: int, time: int) -> None:
        """ Updates the user XP time in the MembersScore table.
        :param user_id: The ID of the user to update.
        :param time: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE MembersScore SET user_xp_time = %s WHERE user_id = %s", (time, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_score_points(self, user_id: int, score_points: int) -> None:
        """ Updates the user's score points in the MembersScore table.
        :param user_id: The ID of the user to update.
        :param score_points: The increment value to apply to the score points. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE MembersScore SET score_points = score_points + %s WHERE user_id = %s", (score_points, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_rep_time(self, user_id: int, rep_time: int) -> None:
        """ Updates the user rep time.
        :param user_id: The ID of the user to update.
        :param rep_time: The rep time. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE MembersScore SET rep_time = %s WHERE user_id = %s", (rep_time, user_id))
        await db.commit()
        await mycursor.close()

    # ===== DELETE =====

    async def remove_user(self, user_id: int) -> None:
        """ Removes a user from the MembersScore table.
        :param user_id: The ID of the user to remove. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM MembersScore WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

