# import.thirdparty
from discord.ext import commands

class SlothClassDatabaseCommands(commands.Cog):
    """ A class for organizing the bot's table creation/drop/delete/check commands. """

    # ======== SlothSkills =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_skills(self, ctx) -> None:
        """ (Owner) Creates the SlothSkills table. """

        if await self.table_sloth_skills_exists():
            return await ctx.send("**The `SlothSkills` table already exists!**")

        await self.db.execute_query("""
            CREATE TABLE SlothSkills (
                user_id BIGINT NOT NULL, skill_type VARCHAR(30) NOT NULL,
                skill_timestamp BIGINT NOT NULL, target_id BIGINT DEFAULT NULL,
                message_id BIGINT DEFAULT NULL, channel_id BIGINT DEFAULT NULL,
                emoji VARCHAR(50) DEFAULT NULL, PRICE INT DEFAULT 0,
                content VARCHAR(200) DEFAULT NULL, int_content BIGINT DEFAULT 0,
                edited_timestamp BIGINT DEFAULT NULL,
                PRIMARY KEY (user_id, target_id, skill_type)
            ) DEFAULT CHARSET=utf8mb4""")
        await ctx.send("**Created `SlothSkills` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_sloth_skills(self, ctx) -> None:
        """ (Owner) Drops the SlothSkills table. """

        if not await self.table_sloth_skills_exists():
            return await ctx.send("**The `SlothSkills` table doesn't exist!**")

        await self.db.execute_query("DROP TABLE SlothSkills")
        await ctx.send("**Dropped `SlothSkills` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_sloth_skills(self, ctx) -> None:
        """ (Owner) Resets the SlothSkills table. """

        if not await self.table_sloth_skills_exists():
            return await ctx.send("**The `SlothSkills` table doesn't exist yet!**")

        await self.db.execute_query("DELETE FROM SlothSkills")
        await ctx.send("**Reset `SlothSkills` table!**")

    async def table_sloth_skills_exists(self) -> bool:
        """ Checks whether the SlothSkills table exists. """

        return await self.db.table_exists("SlothSkills")

    # ======== SkillsCooldown =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_skills_cooldown(self, ctx) -> None:
        """ Creates the SkillsCooldown table. """

        member = ctx.author

        if await self.table_skills_cooldown_exists():
            return await ctx.send(f"**Table `SkillsCooldown` already exists, {member.mention}!**")

        await self.db.execute_query("""
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
        await ctx.send(f"**Table `SkillsCooldown` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_skills_cooldown(self, ctx) -> None:
        """ Drops the SkillsCooldown table. """

        member = ctx.author

        if not await self.table_skills_cooldown_exists():
            return await ctx.send(f"**Table `SkillsCooldown` doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE SkillsCooldown")
        await ctx.send(f"**Table `SkillsCooldown` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_skills_cooldown(self, ctx) -> None:
        """ Resets the SkillsCooldown table. """

        member = ctx.author

        if not await self.table_skills_cooldown_exists():
            return await ctx.send(f"**Table `SkillsCooldown` doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM SkillsCooldown")
        await ctx.send(f"**Table `SkillsCooldown` reset, {member.mention}!**")

    async def table_skills_cooldown_exists(self) -> bool:
        """ Checks whether the SkillsCooldown table exists. """

        return await self.db.table_exists("SkillsCooldown")

    # ======== UserTribe =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_tribe(self, ctx) -> None:
        """ (Owner) Creates the UserTribe table. """

        if await self.table_user_tribe_exists():
            return await ctx.send("**The `UserTribe` table already exists!**")

        await self.db.execute_query("""
            CREATE TABLE UserTribe (
                user_id BIGINT NOT NULL, tribe_name VARCHAR(50) NOT NULL,
                tribe_description VARCHAR(200) NOT NULL, two_emojis VARCHAR(2) NOT NULL,
                tribe_thumbnail VARCHAR(200) DEFAULT NULL, tribe_form VARCHAR(100) DEFAULT NULL,
                slug VARCHAR(75) NOT NULL,
                PRIMARY KEY (tribe_name),
                CONSTRAINT fk_tribe_owner_id FOREIGN KEY (user_id) REFERENCES UserCurrency (user_id) ON DELETE CASCADE ON UPDATE CASCADE
            ) DEFAULT CHARSET=utf8mb4""")
        await ctx.send("**Created `UserTribe` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_tribe(self, ctx) -> None:
        """ (Owner) Drops the UserTribe table. """

        if not await self.table_user_tribe_exists():
            return await ctx.send("**The `UserTribe` table doesn't exist!**")

        await self.db.execute_query("DROP TABLE UserTribe")
        await ctx.send("**Dropped `UserTribe` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_tribe(self, ctx) -> None:
        """ (Owner) Resets the UserTribe table. """

        if not await self.table_user_tribe_exists():
            return await ctx.send("**The `UserTribe` table doesn't exist yet!**")

        await self.db.execute_query("DELETE FROM UserTribe")
        await ctx.send("**Reset `UserTribe` table!**")

    async def table_user_tribe_exists(self) -> bool:
        """ Checks whether the UserTribe table exists. """

        return await self.db.table_exists("UserTribe")

    # ======== TribeMember =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_tribe_member(self, ctx) -> None:
        """ (Owner) Creates the TribeMember table. """

        if await self.table_tribe_member_exists():
            return await ctx.send("**The `TribeMember` table already exists!**")

        await self.db.execute_query("""
            CREATE TABLE TribeMember (
                owner_id BIGINT NOT NULL,
                tribe_name VARCHAR(50) NOT NULL,
                member_id BIGINT NOT NULL,
                tribe_role VARCHAR(30) DEFAULT NULL,
                PRIMARY KEY (member_id),
                CONSTRAINT fk_tribe_owner FOREIGN KEY (owner_id) REFERENCES UserTribe (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_tribe_name FOREIGN KEY (tribe_name) REFERENCES UserTribe (tribe_name) ON DELETE CASCADE ON UPDATE CASCADE
            ) DEFAULT CHARSET=utf8mb4""")
        await ctx.send("**Created `TribeMember` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_tribe_member(self, ctx) -> None:
        """ (Owner) Drops the TribeMember table. """

        if not await self.table_tribe_member_exists():
            return await ctx.send("**The `TribeMember` table doesn't exist!**")

        await self.db.execute_query("DROP TABLE TribeMember")
        await ctx.send("**Dropped `TribeMember` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_tribe_member(self, ctx) -> None:
        """ (Owner) Resets the TribeMember table. """

        if not await self.table_tribe_member_exists():
            return await ctx.send("**The `TribeMember` table doesn't exist yet!**")

        await self.db.execute_query("DELETE FROM TribeMember")
        await ctx.send("**Reset `TribeMember` table!**")

    async def table_tribe_member_exists(self) -> bool:
        """ Checks whether the TribeMember table exists. """

        return await self.db.table_exists("TribeMember")

    # ======== TribeRole =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_tribe_role(self, ctx) -> None:
        """ (Owner) Creates the TribeRole table. """

        if await self.table_tribe_role_exists():
            return await ctx.send("**The `TribeRole` table already exists!**")

        await self.db.execute_query("""
            CREATE TABLE TribeRole (
                owner_id BIGINT NOT NULL,
                tribe_name VARCHAR(50) NOT NULL,
                role_name VARCHAR(30) NOT NULL,
                PRIMARY KEY (tribe_name, role_name),
                CONSTRAINT fk_tr_tribe_owner FOREIGN KEY (owner_id) REFERENCES UserTribe (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_tr_tribe_name FOREIGN KEY (tribe_name) REFERENCES UserTribe (tribe_name) ON DELETE CASCADE ON UPDATE CASCADE
            ) DEFAULT CHARSET=utf8mb4""")#COLLATE=utf8mb4_unicode_ci
        await ctx.send("**Created `TribeRole` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_tribe_role(self, ctx) -> None:
        """ (Owner) Drops the TribeRole table. """

        if not await self.table_tribe_role_exists():
            return await ctx.send("**The `TribeRole` table doesn't exist!**")

        await self.db.execute_query("DROP TABLE TribeRole")
        await ctx.send("**Dropped `TribeRole` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_tribe_role(self, ctx) -> None:
        """ (Owner) Resets the TribeRole table. """

        if not await self.table_tribe_role_exists():
            return await ctx.send("**The `TribeRole` table doesn't exist yet!**")

        await self.db.execute_query("DELETE FROM TribeRole")
        await ctx.send("**Reset `TribeRole` table!**")

    async def table_tribe_role_exists(self) -> bool:
        """ Checks whether the TribeRole table exists. """

        return await self.db.table_exists("TribeRole")

    # ======== SlothProfile =========
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_profile(self, ctx) -> None:
        """ Creates the SlothProfile table. """

        member = ctx.author

        if await self.table_sloth_profile_exists():
            return await ctx.send(f"**Table `SlothProfile` already exists, {member.mention}!**")

        await self.db.execute_query("""
        CREATE TABLE SlothProfile (
            user_id BIGINT NOT NULL,
            sloth_class VARCHAR(30) DEFAULT 'default',
            skills_used INT DEFAULT 0,
            tribe VARCHAR(50) DEFAULT NULL,
            change_class_ts BIGINT DEFAULT 0,

            has_potion TINYINT(1) DEFAULT 0,
            knife_sharpness_stack TINYINT(1) DEFAULT 0,
            rings TINYINT(1) DEFAULT 0,

            tribe_user_id BIGINT DEFAULT NULL,

            PRIMARY KEY (user_id),
            CONSTRAINT fk_sloth_pfl_user_id FOREIGN KEY (user_id) REFERENCES UserCurrency (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fk_sloth_pfl_tribe_name FOREIGN KEY (tribe, tribe_user_id) REFERENCES TribeMember (tribe_name, member_id) ON DELETE SET NULL ON UPDATE CASCADE
        ) DEFAULT CHARSET=utf8mb4""")
        await ctx.send(f"**Table `SlothProfile` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_sloth_profile(self, ctx) -> None:
        """ Drops the SlothProfile table. """

        member = ctx.author

        if not await self.table_sloth_profile_exists():
            return await ctx.send(f"**Table `SlothProfile` doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE SlothProfile")
        await ctx.send(f"**Table `SlothProfile` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_sloth_profile(self, ctx) -> None:
        """ Resets the SlothProfile table. """

        member = ctx.author

        if not await self.table_sloth_profile_exists():
            return await ctx.send(f"**Table `SlothProfile` doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM SlothProfile")
        await ctx.send(f"**Table `SlothProfile` reset, {member.mention}!**")

    async def table_sloth_profile_exists(self) -> bool:
        """ Checks whether the SlothProfile table exists. """

        return await self.db.table_exists("SlothProfile")

    async def update_sloth_profile_class(self, user_id: int, sloth_class: str) -> None:
        """ Updates the user's Sloth Profile's class.
        :param user_id: The ID of the user to update.
        :param sloth_class: The sloth class to update to. """

        await self.db.execute_query("UPDATE SlothProfile SET sloth_class = %s WHERE user_id = %s", (sloth_class, user_id))
