import discord
from discord.ext import commands
from mysqldb import the_database

class SlothClassDatabaseCommands(commands.Cog):
    """ A class for organizing the bot's table creation/drop/delete/check commands. """

    # ======== SlothSkills =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_skills(self, ctx) -> None:
        """ (Owner) Creates the SlothSkills table. """

        if await self.table_sloth_skills_exists():
            return await ctx.send("**The `SlothSkills` table already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE SlothSkills (
                user_id BIGINT NOT NULL, skill_type VARCHAR(30) NOT NULL,
                skill_timestamp BIGINT NOT NULL, target_id BIGINT DEFAULT NULL,
                message_id BIGINT DEFAULT NULL, channel_id BIGINT DEFAULT NULL,
                emoji VARCHAR(50) DEFAULT NULL, PRICE INT DEFAULT 0
            ) DEFAULT CHARSET=utf8mb4""")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Created `SlothSkills` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_sloth_skills(self, ctx) -> None:
        """ (Owner) Drops the SlothSkills table. """

        if not await self.table_sloth_skills_exists():
            return await ctx.send("**The `SlothSkills` table doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SlothSkills")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Dropped `SlothSkills` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_sloth_skills(self, ctx) -> None:
        """ (Owner) Resets the SlothSkills table. """

        if not await self.table_sloth_skills_exists():
            return await ctx.send("**The `SlothSkills` table doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SlothSkills")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Reset `SlothSkills` table!**")

    async def table_sloth_skills_exists(self) -> bool:
        """ Checks whether the SlothSkills table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'SlothSkills'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

    # ======== SkillsCooldown =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_skills_cooldown(self, ctx) -> None:
        """ Creates the SkillsCooldown table. """

        member = ctx.author

        if await self.table_skills_cooldown_exists():
            return await ctx.send(f"**Table `SkillsCooldown` already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
        CREATE TABLE SkillsCooldown (
            user_id BIGINT NOT NULL,
            skill_one_ts BIGINT DEFAULT NULL,
            skill_two_ts BIGINT DEFAULT NULL,
            skill_three_ts BIGINT DEFAULT NULL,
            skill_four_ts BIGINT DEFAULT NULL,
            skill_five_ts BIGINT DEFAULT NULL,
            PRIMARY KEY (user_id),
            CONSTRAINT fk_skills_user_id FOREIGN KEY (user_id) REFERENCES UserCurrency (user_id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """)
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `SkillsCooldown` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_skills_cooldown(self, ctx) -> None:
        """ Drops the SkillsCooldown table. """

        member = ctx.author

        if not await self.table_skills_cooldown_exists():
            return await ctx.send(f"**Table `SkillsCooldown` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SkillsCooldown")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `SkillsCooldown` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_skills_cooldown(self, ctx) -> None:
        """ Resets the SkillsCooldown table. """

        member = ctx.author

        if not await self.table_skills_cooldown_exists():
            return await ctx.send(f"**Table `SkillsCooldown` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SkillsCooldown")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `SkillsCooldown` reset, {member.mention}!**")

    async def table_skills_cooldown_exists(self) -> bool:
        """ Checks whether the SkillsCooldown table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'SkillsCooldown'")
        exists = await mycursor.fetchall()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    # ======== SlothProfile =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_profile(self, ctx) -> None:
        """ Creates the SlothProfile table. """

        member = ctx.author

        if await self.table_sloth_profile_exists():
            return await ctx.send(f"**Table `SlothProfile` already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
        CREATE TABLE SlothProfile (
            user_id BIGINT NOT NULL,
            sloth_class VARCHAR(30),
            skills_used INT NOT NULL,
            tribe VARCHAR(50) DEFAULT NULL,

            has_potion tinyint(1) default 0,
            knife_sharpness_stack tinyint(1) default 0,
            rings tinyint(1) default 0,

            hacked tinyint(1) default 0,
            protected tinyint(1) default 0,
            knocked_out tinyint(1) default 0,
            wired tinyint(1) default 0,
            frogged tinyint(1) default 0,


            PRIMARY KEY (user_id),
            CONSTRAINT fk_sloth_pfl_user_id FOREIGN KEY (user_id) REFERENCES UserCurrency (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fk_sloth_pfl_tribe_id FOREIGN KEY (tribe) REFERENCES UserTribe (tribe_name) ON UPDATE CASCADE
        )""")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `SlothProfile` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_sloth_profile(self, ctx) -> None:
        """ Drops the SlothProfile table. """

        member = ctx.author

        if not await self.table_sloth_profile_exists():
            return await ctx.send(f"**Table `SlothProfile` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SlothProfile")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `SlothProfile` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_sloth_profile(self, ctx) -> None:
        """ Resets the SlothProfile table. """

        member = ctx.author

        if not await self.table_sloth_profile_exists():
            return await ctx.send(f"**Table `SlothProfile` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SlothProfile")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `SlothProfile` reset, {member.mention}!**")

    async def table_sloth_profile_exists(self) -> bool:
        """ Checks whether the SlothProfile table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'SlothProfile'")
        exists = await mycursor.fetchall()
        await mycursor.close()
        if exists:
            return True
        else:
            return False
