import discord
from discord.ext import commands
from mysqldb import the_database
from typing import Any, List, Dict, Union
from extra import utils
import os

cosmos_role_id: int = int(os.getenv('COSMOS_ROLE_ID', 123))
muffin_id: int = int(os.getenv('MUFFIN_ID', 123))
guibot_id: int = int(os.getenv('GUIBOT_ID', 123))

moderator_role_id: int = int(os.getenv('MOD_ROLE_ID', 123))
senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID', 123))
admin_role_id: int = int(os.getenv('ADMIN_ROLE_ID', 123))
lesson_management_role_id: int = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID', 123))
real_event_manager_role_id: int = int(os.getenv('REAL_EVENT_MANAGER_ROLE_ID', 123))

class ApplicationsTable(commands.Cog):
    """ Cog for managing applications. """

    # Teacher application attributes
    teacher_app_channel_id: int = int(os.getenv('TEACHER_APPLICATION_CHANNEL_ID', 123))
    teacher_app_cat_id: int = int(os.getenv('TEACHER_APPLICATION_CAT_ID', 123))
    teacher_parent_channel_id: int = int(os.getenv('TEACHER_CHANNEL_ID', 123))
    teacher_interview_vc_id: int = int(os.getenv('TEACHER_INTERVIEW_VC_ID', 123))

    moderator_app_channel_id: int = int(os.getenv('MODERATOR_APPLICATION_CHANNEL_ID', 123))
    moderator_app_cat_id: int = int(os.getenv('MODERATOR_APPLICATION_CAT_ID', 123))
    moderator_parent_channel_id: int = int(os.getenv('MODERATOR_CHANNEL_ID', 123))
    moderator_interview_vc_id: int = int(os.getenv('MODERATOR_INTERVIEW_VC_ID', 123))

    event_host_app_channel_id: int = int(os.getenv('EVENT_MANAGER_APPLICATION_CHANNEL_ID', 123))
    event_host_app_cat_id: int = int(os.getenv('EVENT_MANAGER_APPLICATION_CAT_ID', 123))
    event_host_parent_channel_id: int = int(os.getenv('EVENT_MANAGER_CHANNEL_ID', 123))
    event_host_interview_vc_id: int = int(os.getenv('EVENT_MANAGER_INTERVIEW_VC_ID', 123))

    debate_manager_app_channel_id: int = int(os.getenv('DEBATE_MANAGER_APPLICATION_CHANNEL_ID', 123))
    debate_manager_app_cat_id: int = int(os.getenv('DEBATE_MANAGER_APPLICATION_CAT_ID', 123))
    debate_manager_parent_channel_id: int = int(os.getenv('DEBATE_MANAGER_CHANNEL_ID', 123))
    debate_manager_interview_vc_id: int = int(os.getenv('DEBATE_MANAGER_INTERVIEW_VC_ID', 123))

    ban_appeals_channel_id: int = int(os.getenv('BAN_APPEALS_CHANNEL_ID', 123))


    interview_info: Dict[str, Any] = {
        'teacher': {
            "app": teacher_app_channel_id, "interview": teacher_interview_vc_id, "parent": teacher_parent_channel_id, 
            "message": "**Teacher Application**\nOur staff has evaluated your Teacher application and has come to the conclusion that we are not in need of this lesson.",
            "cat": teacher_app_cat_id, 
            "pings": [{"id": lesson_management_role_id, "role": True}]},
        'moderator': {
            "app": moderator_app_channel_id, "interview": moderator_interview_vc_id, "parent": moderator_parent_channel_id,
            "cat": moderator_app_cat_id, 
            "message": "**Moderator Application**\nOur staff has evaluated your Moderator application and has come to a conclusion, and due to internal and unspecified reasons we are **declining** it. Thank you anyways",
            "pings": [{"id": cosmos_role_id, "role": True}, {"id": admin_role_id, "role": True}, {"id": senior_mod_role_id, "role": True}]},
        'event_host': {
            "app": event_host_app_channel_id,  "interview": event_host_interview_vc_id, "parent": event_host_parent_channel_id, 
            "cat": event_host_app_cat_id, 
            "message": "**Event Host Application**\nOur staff has evaluated your Event Host application and has come to the conclusion that we are not in need of this event.",
            "pings": [{"id": real_event_manager_role_id, "role": True}]},
        'debate_manager': {
            "app": debate_manager_app_channel_id,  "interview": debate_manager_interview_vc_id, "parent": debate_manager_parent_channel_id, 
            "cat": debate_manager_app_cat_id, 
            "message": "**Debate Manager Application**\nOur staff has evaluated your Debate Manager application and has come to the conclusion that we are **declining** your application for internal reasons.",
            "pings": [{"id": real_event_manager_role_id, "role": True}]}
    }

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def on_raw_reaction_add_applications(self, payload) -> None:
        # Checks if it wasn't a bot's reaction

        if not payload.guild_id:
            return

        if not payload.member or payload.member.bot:
            return

        guild = self.client.get_guild(payload.guild_id)
        try:
            channel = await self.client.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
        except:
            return

        adm = channel.permissions_for(payload.member).administrator
        # Checks if it's in an applications channel
        if payload.channel_id in [
            self.moderator_app_channel_id, self.event_host_app_channel_id, self.teacher_app_channel_id, 
            self.debate_manager_app_channel_id, self.ban_appeals_channel_id]:

            if payload.channel_id == self.debate_manager_app_channel_id: # User is an admin
                if await utils.is_allowed([admin_role_id]).predicate(channel=channel, member=payload.member):
                    return await self.handle_application(guild, payload)
            elif payload.channel_id == self.teacher_app_channel_id: # User is a mod+
                if await utils.is_allowed([moderator_role_id]).predicate(channel=channel, member=payload.member):
                    return await self.handle_application(guild, payload)
            elif payload.channel_id == self.moderator_app_channel_id: # User is a Staff Manager+
                if await utils.is_allowed([senior_mod_role_id]).predicate(channel=channel, member=payload.member):
                    return await self.handle_application(guild, payload)
            elif payload.channel_id == self.ban_appeals_channel_id: # User is a Staff Manager+
                if await utils.is_allowed([senior_mod_role_id]).predicate(channel=channel, member=payload.member):
                    return await self.handle_ban_appeal(guild, payload)
            elif adm: # User is an adm
                return await self.handle_application(guild, payload)

            await message.remove_reaction(payload.emoji, payload.member)


    async def format_application_pings(self, guild: discord.Guild, pings: List[Dict[str, Union[int, bool]]]) -> str:
        """ Formats pings for a specific application title.
        :param guild: The guild to get the users and roles from.
        :param pings: The pings to format. """

        ping_mentions: List[Union[discord.Member, discord.Role]] = []

        for ping in pings:
            if ping['role']:
                role = discord.utils.get(guild.roles, id=ping['id'])
                ping_mentions.append(role.mention)
            else:
                member = discord.utils.get(guild.members, id=ping['id'])
                ping_mentions.append(member.mention)

        if ping_mentions:
            return ', '.join(ping_mentions)

        return ''

    # Applications

    async def get_application_by_message(self, message_id: int) -> List[str]:
        """ Gets a application application from the database by message ID.
        :param message_id: The message ID. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Applications WHERE message_id = %s", (message_id,))
        application_app = await mycursor.fetchone()
        await mycursor.close()
        return application_app

    async def get_application_by_channel(self, channel_id: int) -> List[str]:
        """ Gets a application application from the database by channel ID.
        :param channel_id: The text channel ID. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Applications WHERE txt_id = %s", (channel_id,))
        application_app = await mycursor.fetchone()
        await mycursor.close()
        return application_app

    async def insert_application(self, message_id: int, applicant_id: int, application_type: str) -> None:
        """ Saves a application application into the database.
        :param message_id: The ID of the applicaiton message.
        :param applicant_id: The application ID.
        :param application_type: The type of the application. """

        mycursor, db = await the_database()
        await mycursor.execute(
            """
            INSERT INTO Applications (message_id, applicant_id, application_type)
            VALUES (%s, %s, %s)""", (message_id, applicant_id, application_type)
            )
        await db.commit()
        await mycursor.close()

    async def update_application(self, applicant_id: int, txt_id: int, vc_id: int, application_type: str) -> None:
        """ Updates the application; adding the txt and vc ids into it.
        :param applicant_id: The application ID.
        :param txt_id: The text channel ID.
        :param vc_id: The voice channel ID.
        :param application_type: The type of application to update. """

        mycursor, db = await the_database()
        await mycursor.execute(
            """UPDATE Applications SET
            channel_open = 1, txt_id = %s, vc_id = %s
            WHERE applicant_id = %s AND application_type = %s""", (txt_id, vc_id, applicant_id, application_type)
            )
        await db.commit()
        await mycursor.close()

    async def delete_application(self, message_id: int) -> None:
        """ Deletes a application application from the database.
        :param message_id: The application message's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Applications WHERE message_id = %s", (message_id,))
        await db.commit()
        await mycursor.close()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_applications(self, ctx) -> None:
        """ (ADM) Creates the Applications table. """

        if await self.table_applications_exists():
            return await ctx.send("**Table `Applications` already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE Applications (
                message_id BIGINT, applicant_id BIGINT,
                application_type VARCHAR(50),
                channel_open TINYINT(1) DEFAULT 0,
                txt_id BIGINT DEFAULT NULL, vc_id BIGINT DEFAULT NULL
            )""")

        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `Applications` created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_application(self, ctx) -> None:
        """ (ADM) Drops the Applications table. """

        if not await self.table_applications_exists():
            return await ctx.send("**Table `Applications` doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Applications")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `Applications` dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_applications(self, ctx) -> None:
        """ (ADM) Resets the Applications table. """

        if not await self.table_applications_exists():
            return await ctx.send("**Table `Applications` doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Applications")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `Applications` reset!**")

    async def table_applications_exists(self) -> bool:
        """ Checks whether the Applications table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Applications'")
        exists = await mycursor.fetchall()
        await mycursor.close()

        if len(exists):
            return True
        else:
            return False
