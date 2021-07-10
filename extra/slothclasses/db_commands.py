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

    # ======== UserTribe =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_tribe(self, ctx) -> None:
        """ (Owner) Creates the UserTribe table. """

        if await self.table_user_tribe_exists():
            return await ctx.send("**The `UserTribe` table already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE UserTribe (
                user_id BIGINT NOT NULL, tribe_name VARCHAR(50) NOT NULL,
                tribe_description VARCHAR(200) NOT NULL, two_emojis VARCHAR(2) NOT NULL,
                tribe_thumbnail VARCHAR(200) DEFAULT NULL, tribe_form VARCHAR(100) DEFAULT NULL,
                slug VARCHAR(75) NOT NULL,
                PRIMARY KEY (tribe_name),
                CONSTRAINT fk_tribe_owner_id FOREIGN KEY (user_id) REFERENCES UserCurrency (user_id) ON DELETE CASCADE ON UPDATE CASCADE
            ) DEFAULT CHARSET=utf8mb4""")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Created `UserTribe` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_tribe(self, ctx) -> None:
        """ (Owner) Drops the UserTribe table. """

        if not await self.table_user_tribe_exists():
            return await ctx.send("**The `UserTribe` table doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserTribe")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Dropped `UserTribe` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_tribe(self, ctx) -> None:
        """ (Owner) Resets the UserTribe table. """

        if not await self.table_user_tribe_exists():
            return await ctx.send("**The `UserTribe` table doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserTribe")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Reset `UserTribe` table!**")

    async def table_user_tribe_exists(self) -> bool:
        """ Checks whether the UserTribe table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'UserTribe'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

    # ======== TribeMember =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_tribe_member(self, ctx) -> None:
        """ (Owner) Creates the TribeMember table. """

        if await self.table_tribe_member_exists():
            return await ctx.send("**The `TribeMember` table already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE TribeMember (
                owner_id BIGINT NOT NULL,
                tribe_name VARCHAR(50) NOT NULL,
                member_id BIGINT NOT NULL,
                tribe_role VARCHAR(30) DEFAULT NULL,
                PRIMARY KEY (member_id),
                CONSTRAINT fk_tribe_owner FOREIGN KEY (owner_id) REFERENCES UserTribe (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_tribe_name FOREIGN KEY (tribe_name) REFERENCES UserTribe (tribe_name) ON DELETE CASCADE ON UPDATE CASCADE
            ) DEFAULT CHARSET=utf8mb4""")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Created `TribeMember` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_tribe_member(self, ctx) -> None:
        """ (Owner) Drops the TribeMember table. """

        if not await self.table_tribe_member_exists():
            return await ctx.send("**The `TribeMember` table doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE TribeMember")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Dropped `TribeMember` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_tribe_member(self, ctx) -> None:
        """ (Owner) Resets the TribeMember table. """

        if not await self.table_tribe_member_exists():
            return await ctx.send("**The `TribeMember` table doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM TribeMember")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Reset `TribeMember` table!**")

    async def table_tribe_member_exists(self) -> bool:
        """ Checks whether the TribeMember table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'TribeMember'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

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
            sloth_class VARCHAR(30) DEFAULT 'default',
            skills_used INT DEFAULT 0,
            tribe VARCHAR(50) DEFAULT NULL,
            change_class_ts BIGINT DEFAULT 0,

            has_potion TINYINT(1) DEFAULT 0,
            knife_sharpness_stack TINYINT(1) DEFAULT 0,
            rings TINYINT(1) DEFAULT 0,

            hacked TINYINT(1) DEFAULT 0,
            protected TINYINT(1) DEFAULT 0,
            knocked_out TINYINT(1) DEFAULT 0,
            wired TINYINT(1) DEFAULT 0,
            frogged TINYINT(1) DEFAULT 0,

            tribe_user_id BIGINT DEFAULT NULL

            PRIMARY KEY (user_id),
            CONSTRAINT fk_sloth_pfl_user_id FOREIGN KEY (user_id) REFERENCES UserCurrency (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fk_sloth_pfl_tribe_name FOREIGN KEY (tribe_user_id, tribe) REFERENCES TribeMember (member_id, tribe_name) ON DELETE SET NULL ON UPDATE CASCADE
        ) DEFAULT CHARSET=utf8mb4""")
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
