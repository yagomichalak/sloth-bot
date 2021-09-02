import discord
from discord import member
from discord.ext import commands
from mysqldb import *
import asyncio
from extra.useful_variables import list_of_commands
from extra.menu import ConfirmSkill
from extra.view import ReportSupportView
from typing import List, Dict, Optional
import os

case_cat_id = int(os.getenv('CASE_CAT_ID'))
reportsupport_channel_id = int(os.getenv('REPORT_CHANNEL_ID'))
dnk_id = int(os.getenv('DNK_ID'))
moderator_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
lesson_management_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID'))

staff_vc_id = int(os.getenv('STAFF_VC_ID'))

allowed_roles = [
int(os.getenv('OWNER_ROLE_ID')), admin_role_id,
moderator_role_id]

from extra.reportsupport.applications import ApplicationsTable
from extra.reportsupport.verify import Verify
from extra.reportsupport.openchannels import OpenChannels


report_support_classes: List[commands.Cog] = [
    ApplicationsTable, Verify, OpenChannels
]


class ReportSupport(*report_support_classes):
    """ A cog related to the system of reports and some other things. """

    def __init__(self, client) -> None:

        # super(ReportSupport, self).__init__(client)
        self.client = client
        self.cosmos_id: int = int(os.getenv('COSMOS_ID'))
        self.muffin_id: int = int(os.getenv('MUFFIN_ID'))
        self.pretzel_id: int = int(os.getenv('PRETZEL_ID'))
        self.cache = {}
        self.report_cache = {}
        

    @commands.Cog.listener()
    async def on_ready(self) -> None:

        self.client.add_view(view=ReportSupportView(self.client))
        print(self.client.persistent_views)
        print('ReportSupport cog is online!')


    async def handle_teacher_application(self, guild, payload) -> None:
        """ Handles teacher applications.
        :param guild: The server in which the application is running.
        :param payload: Data about the Staff member who is opening the application. """

        emoji = str(payload.emoji)
        if emoji == '✅':
            # Gets the teacher app and does the magic
            teacher_app = await self.get_application_by_message(payload.message_id, 'teacher')
            if not teacher_app:
                return

            # Checks if the person has not an open interview channel already
            if not teacher_app[3]:
                # Creates an interview room with the teacher and sends their application there (you can z!close there)
                return await self.create_teacher_interview_room(guild, teacher_app)

        elif emoji == '❌':
            # Tries to delete the teacher app from the db, in case it is registered
            teacher_app = await self.get_application_by_message(payload.message_id, 'teacher')
            if teacher_app and not teacher_app[3]:
                await self.delete_application(payload.message_id, 'teacher')
                teacher_app_channel = self.client.get_channel(self.teacher_app_channel_id)
                app_msg = await teacher_app_channel.fetch_message(payload.message_id)
                await app_msg.add_reaction('🔏')
                teacher = discord.utils.get(guild.members, id=teacher_app[1])
                if teacher:
                    msg = "**Teacher Application**\nOur staff has evaluated your teacher application and has come to the conclusion that we are not in need of this lesson."
                    await teacher.send(embed=discord.Embed(description=msg))
            return

    async def handle_moderator_application(self, guild, payload) -> None:
        """ Handles moderator applications.
        :param guild: The server in which the application is running.
        :param payload: Data about the Staff member who is opening the application. """

        emoji = str(payload.emoji)
        if emoji == '✅':
            # Gets the moderator app and does the magic
            moderator_app = await self.get_application_by_message(payload.message_id, 'moderator')
            if not moderator_app:
                return

            # Checks if the person has not an open interview channel already
            if not moderator_app[3]:
                # Creates an interview room with the moderator and sends their application there (you can z!close there)
                return await self.create_moderator_interview_room(guild, moderator_app)

        elif emoji == '❌':
            # Tries to delete the moderator app from the db, in case it is registered
            moderator_app = await self.get_application_by_message(payload.message_id, 'moderator')
            if moderator_app and not moderator_app[3]:
                await self.delete_application(payload.message_id, 'moderator')
                moderator_app_channel = self.client.get_channel(self.moderator_app_channel_id)
                app_msg = await moderator_app_channel.fetch_message(payload.message_id)
                await app_msg.add_reaction('🔏')
                moderator = discord.utils.get(guild.members, id=moderator_app[1])
                if moderator:
                    msg = "**Moderator Application**\nOur staff has avaluated your moderator application and has come to a conclusion, and due to intern and unspecified reasons we are **declining** it. Thank you anyways"
                    await moderator.send(embed=discord.Embed(description=msg))
            return

    async def handle_event_manager_application(self, guild, payload) -> None:
        """ Handles event manager applications.
        :param guild: The server in which the application is running.
        :param payload: Data about the Staff member who is opening the application. """

        emoji = str(payload.emoji)
        if emoji == '✅':
            # Gets the teacher app and does the magic
            event_manager_app = await self.get_application_by_message(payload.message_id, 'event_manager')
            if not event_manager_app:
                return

            # Checks if the person has not an open interview channel already
            if not event_manager_app[3]:
                # Creates an interview room with the event_manager and sends their application there (you can z!close there)
                return await self.create_event_manager_interview_room(guild, event_manager_app)

        elif emoji == '❌':
            # Tries to delete the event_manager app from the db, in case it is registered
            event_manager_app = await self.get_application_by_message(payload.message_id, 'event_manager')
            if event_manager_app and not event_manager_app[3]:
                await self.delete_application(payload.message_id, 'event_manager')
                event_manager_app_channel = self.client.get_channel(self.event_manager_app_channel_id)
                app_msg = await event_manager_app_channel.fetch_message(payload.message_id)
                await app_msg.add_reaction('🔏')
                event_manager = discord.utils.get(guild.members, id=event_manager_app[1])
                if event_manager:
                    msg = "**event_manager Application**\nOur staff has evaluated your event_manager application and has come to the conclusion that we are not in need of this lesson."
                    await event_manager.send(embed=discord.Embed(description=msg))
            return


    async def send_teacher_application(self, member) -> None:
        """ Sends a teacher application form to the user.
        :param member: The member to send the application to. """

        def msg_check(message):
            if message.author == member and not message.guild:
                if len(message.content) <= 100:
                    return True
                else:
                    self.client.loop.create_task(member.send("**Your answer must be within 100 characters**"))
            else:
                return False

        def check_reaction(r, u):
            return u.id == member.id and not r.message.guild and str(r.emoji) in ['✅', '❌']

        terms_embed = discord.Embed(
            title="Terms of Application",
            description="""Hello there!
            Thank you for applying for teaching here,
            Before you can formally start applying to teach in The Language Sloth, there are a couple things we would like you to know. The Language Sloth is a free of charge language learning platform which is meant to be accessible and open for anyone who is interested in languages from any background. We do not charge for any kind of service, nor do we pay for any services for starting teachers. We are a community that shares the same interest: Languages.
            We do not require professional teaching skills, anyone can teach their native language, however, we have a set numbers of requirements for our teachers
            Entry requirements:

            》Must be at least 16 years of age
            》Must have at least a conversational level of English
            》Must have clear microphone audio
            》Must commit 40 minutes per week
            》Must prepare their own material weekly

            ``` ✅ To agree with our terms```""",
            color=member.color
        )

        terms = await member.send(embed=terms_embed)
        await terms.add_reaction('✅')
        await terms.add_reaction('❌')

        # Waits for reaction confirmation to the terms of application
        terms_r = await self.get_reaction(member, check_reaction)

        if terms_r is None:
            self.cache[member.id] = 0
            return

        if terms_r != '✅':
            self.cache[member.id] = 0
            return await member.send(f"**Thank you anyways, bye!**")

        embed = discord.Embed(title=f"__Teacher Application__")
        embed.set_footer(text=f"by {member}", icon_url=member.avatar.url)

        embed.description = '''
        - Hello, there you've reacted to apply to become a teacher.
        To apply please answer to these following questions with One message at a time
        Question one:
        What language are you applying to teach?'''
        q1 = await member.send(embed=embed)
        a1 = await self.get_message_content(member, msg_check)
        if not a1:
            return

        embed.description = '''
        - Why do you want to teach that language on the language sloth?
        Please answer with one message.'''
        q2 = await member.send(embed=embed)
        a2 = await self.get_message_content(member, msg_check)
        if not a2:
            return

        embed.description = '''
        - On The Language Sloth, our classes happen once a week at the same time weekly.
        Please let us know when would be the best time for you to teach,
        E.A: Thursdays 3 pm CET, you can specify your timezone.
        Again remember to answer with one message.'''
        q3 = await member.send(embed=embed)
        a3 = await self.get_message_content(member, msg_check)
        if not a3:
            return

        embed.description = '''
        - Let's talk about your English level, how do you consider your English level?
        Are you able to teach lessons in English?
        Please answer using one message only'''
        q4 = await member.send(embed=embed)
        a4 = await self.get_message_content(member, msg_check)
        if not a4:
            return

        embed.description = '''- Have you ever taught people before?'''
        q5 = await member.send(embed=embed)
        a5 = await self.get_message_content(member, msg_check)
        if not a5:
            return

        embed.description = '''- Inform a short description for your class.'''
        q6 = await member.send(embed=embed)
        a6 = await self.get_message_content(member, msg_check)
        if not a6:
            return

        embed.description = '''- How old are you?'''
        q7 = await member.send(embed=embed)
        a7 = await self.get_message_content(member, msg_check)
        if not a7:
            return

        # Get user's native roles
        user_native_roles = []
        for role in member.roles:
            if str(role.name).lower().startswith('native'):
                user_native_roles.append(role.name.title())

        # Application result
        app = f"""```ini\n[Username]: {member} ({member.id})\n[Joined the server]: {member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC")}\n[Applying to teach]: {a1.title()}\n[Native roles]: {', '.join(user_native_roles)}\n[Motivation for teaching]: {a2.capitalize()}\n[Applying to teach on]: {a3.upper()}\n[English level]: {a4.capitalize()}\n[Experience teaching]: {a5.capitalize()}\n[Description]:{a6.capitalize()}\n[Age]: {a7}```"""
        await member.send(app)
        embed.description = '''
        Are you sure you want to apply this? :white_check_mark: to send and :x: to Cancel
        '''
        app_conf = await member.send(embed=embed)
        await app_conf.add_reaction('✅')
        await app_conf.add_reaction('❌')

        # Waits for reaction confirmation
        r = await self.get_reaction(member, check_reaction)
        if r is None:
            return

        if r == '✅':
            embed.description = "**Application successfully made, please, be patient now!**"
            await member.send(embed=embed)
            teacher_app_channel = await self.client.fetch_channel(self.teacher_app_channel_id)
            muffin = discord.utils.get(teacher_app_channel.guild.members, id=self.muffin_id)
            app = await teacher_app_channel.send(content=f"{muffin.mention}, {member.mention}\n{app}")
            await app.add_reaction('✅')
            await app.add_reaction('❌')
            # Saves in the database
            await self.insert_application(app.id, member.id, 'teacher')

        else:
            self.cache[member.id] = 0
            return await member.send("**Thank you anyways!**")

    async def send_moderator_application(self, member):
        """ Sends a moderator application form to the user.
        :param member: The member to send the application to. """

        def msg_check(message):
            if message.author == member and not message.guild:
                if len(message.content) <= 100:
                    return True
                else:
                    self.client.loop.create_task(member.send("**Your answer must be within 100 characters**"))
            else:
                return False

        def check_reaction(r, u):
            return u.id == member.id and not r.message.guild and str(r.emoji) in ['✅', '❌']

        terms_embed = discord.Embed(
            title="Terms of Application",
            description="""Hello there! 
Before you can formally start applying for Staff in The Language Sloth, there are a couple requirements we would like you to know we feel necessity for:

Entry requirements:

```》Must be at least 16 years of age
》Must have at least a conversational level of English
》Must be an active member
》Must not have any warnings in the past 3 months.```""",
            color=member.color
        )

        terms = await member.send(embed=terms_embed)
        await terms.add_reaction('✅')
        await terms.add_reaction('❌')

        # Waits for reaction confirmation to the terms of application
        terms_r = await self.get_reaction(member, check_reaction)

        if terms_r is None:
            self.cache[member.id] = 0
            return

        if terms_r != '✅':
            self.cache[member.id] = 0
            return await member.send(f"**Thanks anyways, bye!**")
            
        embed = discord.Embed(title=f"__Moderator Application__")
        embed.set_footer(text=f"by {member}", icon_url=member.avatar.url)

        embed.description = "- What's your age?"
        q1 = await member.send(embed=embed)
        a1 = await self.get_message_content(member, msg_check)
        if not a1:
            return

        embed.description = """
        - Hello, there you've reacted to apply to become a moderator.
To apply please answer to these following questions with One message at a time
Question one:
Do you have any experience moderating Discord servers?"""
        q2 = await member.send(embed=embed)
        a2 = await self.get_message_content(member, msg_check)
        if not a2:
            return

        embed.description = """
        - What is your gender?
Please answer with one message."""
        q3 = await member.send(embed=embed)
        a3 = await self.get_message_content(member, msg_check)
        if not a3:
            return

        embed.description = """
        - What's your English level? Are you able to express yourself using English?
Please answer using one message only."""
        q4 = await member.send(embed=embed)
        a4 = await self.get_message_content(member, msg_check)
        if not a4:
            return

        embed.description = """
        - Why are you applying to be Staff? What is your motivation?
Please answer using one message only."""
        q5 = await member.send(embed=embed)
        a5 = await self.get_message_content(member, msg_check)
        if not a5:
            return

        embed.description = """- How do you think The Language Sloth could be a better community?
Please answer using one message only."""
        q6 = await member.send(embed=embed)
        a6 = await self.get_message_content(member, msg_check)
        if not a6:
            return

        embed.description = """- How active are you on Discord in general?
Please answer using one message only."""
        q7 = await member.send(embed=embed)
        a7 = await self.get_message_content(member, msg_check)
        if not a7:
            return

        embed.description = """- What is your time zone?
Please answer using one message only.."""
        q8 = await member.send(embed=embed)
        a8 = await self.get_message_content(member, msg_check)
        if not a8:
            return

        # Get user's native roles
        user_native_roles = []
        for role in member.roles:
            if str(role.name).lower().startswith('native'):
                user_native_roles.append(role.name.title())

        # Application result
        app = f"""```ini\n[Username]: {member} ({member.id})
[Joined the server]: {member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC")}
[Native roles]: {', '.join(user_native_roles)}
[Age]: {a1}
[Experience moderating]: {a2.capitalize()}
[Gender]: {a3.title()}
[English level]: {a4.capitalize()}
[Reason & Motivation]: {a5.capitalize()}
[How we can improve Sloth]: {a6.capitalize()}
[Activity Status]: {a7.capitalize()}
[Timezone]: {a8.title()}```"""
        await member.send(app)
        embed.description = """
        Are you sure you want to apply this? :white_check_mark: to send and :x: to Cancel
        """
        app_conf = await member.send(embed=embed)
        await app_conf.add_reaction('✅')
        await app_conf.add_reaction('❌')

        # Waits for reaction confirmation
        r = await self.get_reaction(member, check_reaction)
        if r is None:
            return

        if r == '✅':
            # ""
            embed.description = """**Application successfully made, please, be patient now.**
            
            We will let you know when we need a new mod. We check apps when we need it!""" 
            await member.send(embed=embed)
            moderator_app_channel = await self.client.fetch_channel(self.moderator_app_channel_id)
            cosmos = discord.utils.get(moderator_app_channel.guild.members, id=self.cosmos_id)
            app = await moderator_app_channel.send(content=f"{cosmos.mention}, {member.mention}\n{app}")
            await app.add_reaction('✅')
            await app.add_reaction('❌')
            # Saves in the database
            await self.insert_application(app.id, member.id, 'moderator')

        else:
            self.cache[member.id] = 0
            return await member.send("**Thank you anyways!**")


    async def send_event_manager_application(self, member):
        """ Sends a event manager application form to the user.
        :param member: The member to send the application to. """

        def msg_check(message):
            if message.author == member and not message.guild:
                if len(message.content) <= 100:
                    return True
                else:
                    self.client.loop.create_task(member.send("**Your answer must be within 100 characters**"))
            else:
                return False

        def check_reaction(r, u):
            return u.id == member.id and not r.message.guild and str(r.emoji) in ['✅', '❌']

        terms_embed = discord.Embed(
            title="Terms of Application",
            description="""Hello there!
            Thank you for applying for hosting events here,
            Before you can formally start applying to host events in The Language Sloth, there are a couple things we would like you to know. The Language Sloth is a free of charge language learning platform which is meant to be accessible and open for anyone who is interested in languages from any background. We do not charge for any kind of service, nor do we pay for any services for hosting events. We are a community that shares the same interest: Languages.
            We do not require professional skills, however, we have a set numbers of requirements for our event managers
            Entry requirements:

            》Must be at least 16 years of age
            》Must have at least a conversational level of English
            》Must have clear microphone audio
            》Must prepare their own material weekly

            ``` ✅ To agree with our terms```""",
            color=member.color
        )

        terms = await member.send(embed=terms_embed)
        await terms.add_reaction('✅')
        await terms.add_reaction('❌')

        # Waits for reaction confirmation to the terms of application
        terms_r = await self.get_reaction(member, check_reaction)

        if terms_r is None:
            self.cache[member.id] = 0
            return

        if terms_r != '✅':
            self.cache[member.id] = 0
            return await member.send(f"**Thank you anyways, bye!**")

        embed = discord.Embed(title=f"__Teacher Application__")
        embed.set_footer(text=f"by {member}", icon_url=member.avatar.url)

        embed.title = "Event manager Application"
        embed.description = '''
        - Hello, there you've reacted to apply to become an event manager.
        To apply please answer to these following questions with One message at a time

        Question one:
        What is your event called?'''
        q1 = await member.send(embed=embed)
        a1 = await self.get_message_content(member, msg_check)
        if not a1:
            return

        embed.description = '''
        - Why do you want to host that event on the language sloth?
        Please answer with one message.'''
        q2 = await member.send(embed=embed)
        a2 = await self.get_message_content(member, msg_check)
        if not a2:
            return

        embed.description = '''
        - Please let us know when would be the best time for you to host events
        E.A: Thursdays 3 pm CET, you can specify your timezone.
        Again remember to answer with one message.'''
        q3 = await member.send(embed=embed)
        a3 = await self.get_message_content(member, msg_check)
        if not a3:
            return

        embed.description = """
        - Let's talk about your English level, how do you consider your English level?
        Are you able to host events in English? If not, in which language would you be hosting?
        Please answer using one message only"""
        q4 = await member.send(embed=embed)
        a4 = await self.get_message_content(member, msg_check)
        if not a4:
            return

        embed.description = "- Have you ever hosted events before? If yes, please describe!"
        q5 = await member.send(embed=embed)
        a5 = await self.get_message_content(member, msg_check)
        if not a5:
            return

        embed.description = "- Inform a short description for your event/events."
        q6 = await member.send(embed=embed)
        a6 = await self.get_message_content(member, msg_check)
        if not a6:
            return

        embed.description = "- How old are you?"
        q7 = await member.send(embed=embed)
        a7 = await self.get_message_content(member, msg_check)
        if not a7:
            return

        # Get user's native roles
        user_native_roles = []
        for role in member.roles:
            if str(role.name).lower().startswith('native'):
                user_native_roles.append(role.name.title())

        # Application result
        app = f"""```ini\n[Username]: {member} ({member.id})\n[Joined the server]: {member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC")}\n[Applying to host]: {a1.title()}\n[Native roles]: {', '.join(user_native_roles)}\n[Motivation for hosting]: {a2.capitalize()}\n[Applying to host on]: {a3.upper()}\n[English level]: {a4.capitalize()}\n[Experience hosting]: {a5.capitalize()}\n[Description]:{a6.capitalize()}\n[Age]: {a7}```"""
        await member.send(app)
        embed.description = '''
        Are you sure you want to apply this? :white_check_mark: to send and :x: to Cancel
        '''
        app_conf = await member.send(embed=embed)
        await app_conf.add_reaction('✅')
        await app_conf.add_reaction('❌')

        # Waits for reaction confirmation
        r = await self.get_reaction(member, check_reaction)
        if r is None:
            return

        if r == '✅':
            embed.description = "**Application successfully made, please, be patient now!**"
            await member.send(embed=embed)
            event_manager_channel = await self.client.fetch_channel(self.event_manager_app_channel_id)
            pretzel = discord.utils.get(event_manager_channel.guild.members, id=self.pretzel_id)
            app = await event_manager_channel.send(content=f"{pretzel.mention}, {member.mention}\n{app}")
            await app.add_reaction('✅')
            await app.add_reaction('❌')
            # Saves in the database
            await self.insert_application(app.id, member.id, 'event_manager')

        else:
            self.cache[member.id] = 0
            return await member.send("**Thank you anyways!**")

    async def send_verified_selfies_verification(self, interaction: discord.Interaction) -> None:
        """ Sends a message to the user asking for them to send a selfie in order for them
        to get the verified selfies role.
        :param interaction: The interaction object. """

        guild = interaction.guild
        member = interaction.user

        def msg_check(message):
            if message.author == member and not message.guild:
                if len(message.content) <= 100:
                    return True
                else:
                    self.client.loop.create_task(member.send("**Your answer must be within 100 characters**"))
            else:
                return False

        embed = discord.Embed(
            title=f"__Verify__",
            description=f"""You have opened a verification request, if you would like to verify:\n
**1.** Take a clear picture of yourself holding a piece of paper with today's date and time of verification, and your Discord server name written on it. Image links won't work, only image uploads!\n(You have 5 minutes to do so)"""
        )
        embed.set_footer(text=f"by {member}", icon_url=member.avatar.url)

        embed.set_image(url="https://cdn.discordapp.com/attachments/562019472257318943/882352621116096542/slothfacepopoo.png")

        await member.send(embed=embed)

        while True:
            msg = await self.get_message(member, msg_check, 300)
            if not msg:
                return await member.send(f"**Timeout, you didn't answer in time, try again later!**")


            attachments = [att for att in msg.attachments if att.content_type.startswith('image')]
            if msg.content.lower() == 'quit':
                return await member.send(f"**Bye!**")

            if not attachments:
                await member.send(f"**No uploaded pic detected, send it again or type `quit` to stop this!**")
                continue

            break

        # Sends verified request to admins
        verify_embed = discord.Embed(
            title=f"__Verification Request__",
            description=f"{member} ({member.id})",
            color=member.color,
            timestamp=interaction.message.created_at
        )

        verify_embed.set_thumbnail(url=member.avatar.url)
        verify_embed.set_image(url=attachments[0])
        verify_req_channel_id = discord.utils.get(guild.text_channels, id=self.verify_reqs_channel_id)
        verify_msg = await verify_req_channel_id.send(content=member.mention, embed=verify_embed)
        await verify_msg.add_reaction('✅')
        await verify_msg.add_reaction('❌')
        # Saves
        await self.insert_application(verify_msg.id, member.id, 'verify')
        return await member.send(f"**Request sent, you will get notified here if you get accepted or declined! ✅**")


    # - Report someone
    async def report_someone(self, interaction: discord.Interaction):

        member = interaction.user
        guild = interaction.guild

        if open_channel := await self.member_has_open_channel(member.id):
            if open_channel := discord.utils.get(guild.text_channels, id=open_channel[1]):
                embed = discord.Embed(title="Error!", description=f"**You already have an open channel! ({open_channel.mention})**", color=discord.Color.red())
                await interaction.followup.send(embed=embed, ephemeral=True)
                return False
            else:
                await self.remove_user_open_channel(member.id)

        # Report someone
        case_cat = discord.utils.get(guild.categories, id=case_cat_id)
        counter = await self.get_case_number()
        moderator = discord.utils.get(guild.roles, id=moderator_role_id)
        cosmos = discord.utils.get(guild.members, id=self.cosmos_id)
        overwrites = {guild.default_role: discord.PermissionOverwrite(
            read_messages=False, send_messages=False, connect=False, view_channel=False),
        member: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=False, view_channel=True),
        moderator: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=False, view_channel=True, manage_messages=True)}
        try:
            the_channel = await guild.create_text_channel(name=f"case-{counter[0][0]}", category=case_cat, overwrites=overwrites)
        except Exception:
            await interaction.followup.send("**Something went wrong with it, please contact an admin!**", ephemeral=True)
            raise Exception
        else:
            created_embed = discord.Embed(
                title="Report room created!",
                description=f"**Go to {the_channel.mention}!**",
                color=discord.Color.green())
            await interaction.followup.send(embed=created_embed, ephemeral=True)
            await self.insert_user_open_channel(member.id, the_channel.id)
            await self.increase_case_number()
            embed = discord.Embed(title="Report Support!", description=f"Please, {member.mention}, try to explain what happened and who you want to report.",
                color=discord.Color.red())
            message = await the_channel.send(content=f"{member.mention}, {moderator.mention}, {cosmos.mention}", embed=embed)
            ctx = await self.client.get_context(message)
            return await self.client.get_cog('Tools').vc(ctx, member=member)

    # - Report someone
    async def generic_help(self, interaction: discord.Interaction, type_help: str, message: str, ping: bool = True) -> None:
        """ Opens a generic help channel.
        :param interaction: The interaction that generated this action.
        :param type_help: The kind of general help.
        :param message: The text message to send in the room.
        :param ping: Whether mods should be pinged for this. """

        member = interaction.user
        guild = interaction.guild

        if open_channel := await self.member_has_open_channel(member.id):
            if open_channel := discord.utils.get(guild.text_channels, id=open_channel[1]):
                embed = discord.Embed(title="Error!", description=f"**You already have an open channel! ({open_channel.mention})**", color=discord.Color.red())
                await interaction.followup.send(embed=embed, ephemeral=True)
                return False
            else:
                await self.remove_user_open_channel(member.id)

        # General help
        case_cat = discord.utils.get(guild.categories, id=case_cat_id)
        moderator = discord.utils.get(guild.roles, id=moderator_role_id)
        overwrites = {guild.default_role: discord.PermissionOverwrite(
            read_messages=False, send_messages=False, connect=False, view_channel=False),
        member: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=False, view_channel=True),
        moderator: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=False, view_channel=True, manage_messages=True)}
        try:
            the_channel = await guild.create_text_channel(name=f"{'-'.join(type_help.split())}", category=case_cat, overwrites=overwrites)
        except:
            await interaction.followup.send("**Something went wrong with it, please contact an admin!**", ephemeral=True)
            raise Exception
        else:
            created_embed = discord.Embed(
                title=f"Room for `{type_help}` created!",
                description=f"**Go to {the_channel.mention}!**",
                color=discord.Color.green())
            await interaction.followup.send(embed=created_embed, ephemeral=True)
            await self.insert_user_open_channel(member.id, the_channel.id)
            embed = discord.Embed(title=f"{type_help.title()}!", description=message, color=discord.Color.red())

            if ping:
                await the_channel.send(content=f"{member.mention}, {moderator.mention}", embed=embed)
            else:
                await the_channel.send(content=member.mention, embed=embed)

    async def get_message_content(self, member, check, timeout: Optional[int] = 300) -> str:
        """ Gets a message content.
        :param member: The member to get the message from.
        :param check: The check for the event.
        :param timeout: Timeout for getting the message. [Optional] """

        try:
            message = await self.client.wait_for('message', timeout=timeout,
            check=check)
        except asyncio.TimeoutError:
            await member.send("**Timeout! Try again.**")
            return None
        else:
            content = message.content
            return content

    async def get_message(self, member, check, timeout: Optional[int] = 300) -> discord.Message:
        """ Gets a message.
        :param member: The member to get the message from.
        :param check: The check for the event.
        :param timeout: Timeout for getting the message. [Optional] """

        try:
            message = await self.client.wait_for('message', timeout=timeout,
            check=check)
        except asyncio.TimeoutError:
            await member.send("**Timeout! Try again.**")
            return None
        else:
            return message

    async def get_reaction(self, member, check, timeout: int = 300):
        try:
            reaction, _ = await self.client.wait_for('reaction_add',
            timeout=timeout, check=check)
        except asyncio.TimeoutError:
            await member.send("**Timeout! Try again.**")
            return None
        else:
            return str(reaction.emoji)


    @commands.command(aliases=['permit_case', 'allow_case', 'add_witness', 'witness', 'aw'])
    @commands.has_any_role(*allowed_roles)
    async def allow_witness(self, ctx, member: discord.Member = None):
        """ Allows a witness to join a case channel.
        :param member: The member to allow. """

        if not member:
            return await ctx.send("**Inform a witness to allow!**")

        user_channel = await self.get_case_channel(ctx.channel.id)
        if user_channel:

            confirm = await ConfirmSkill(f"**Are you sure you want to allow {member.mention} as a witness in this case channel, {ctx.author.mention}?**").prompt(ctx)
            if not confirm:
                return await ctx.send(f"**Not allowing them, then!**")

            channel = discord.utils.get(ctx.guild.channels, id=user_channel[0][1])
            try:
                await channel.set_permissions(
                    member, read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)
            except Exception:
                pass

            return await ctx.send(f"**{member.mention} has been allowed here!**")

        else:
            await ctx.send(f"**This is not a case channel, {ctx.author.mention}!**")

    @commands.command(aliases=['forbid_case', 'delete_witness', 'remve_witness', 'fw'])
    @commands.has_any_role(*allowed_roles)
    async def forbid_witness(self, ctx, member: discord.Member = None):
        """ Forbids a witness from a case channel.
        :param member: The member to forbid. """

        if not member:
            return await ctx.send("**Inform a witness to forbid!**")

        user_channel = await self.get_case_channel(ctx.channel.id)
        if user_channel:

            confirm = await ConfirmSkill(f"**Are you sure you want to forbid {member.mention} from being a witness in this case channel, {ctx.author.mention}?**").prompt(ctx)
            if not confirm:
                return await ctx.send(f"**Not forbidding them, then!**")

            channel = discord.utils.get(ctx.guild.channels, id=user_channel[0][1])
            try:
                await channel.set_permissions(
                    member, read_messages=False, send_messages=False, connect=False, speak=False, view_channel=False)
            except Exception:
                pass

            return await ctx.send(f"**{member.mention} has been forbidden here!**")

        else:
            await ctx.send(f"**This is not a case channel, {ctx.author.mention}!**")

    @commands.command(aliases=['delete_channel', 'archive'])
    @commands.has_any_role(*allowed_roles)
    async def close_channel(self, ctx):
        """ (MOD) Closes a Case-Channel. """

        user_channel = await self.get_case_channel(ctx.channel.id)
        if not user_channel:
            return await ctx.send(f"**What do you think that you are doing? You cannot delete this channel, {ctx.author.mention}!**")
            
        channel = discord.utils.get(ctx.guild.text_channels, id=user_channel[0][1])
        embed = discord.Embed(title="Confirmation",
            description="Are you sure that you want to delete this channel?",
            color=ctx.author.color,
            timestamp=ctx.message.created_at)
        confirmation = await ctx.send(content=ctx.author.mention, embed=embed)
        await confirmation.add_reaction('✅')
        await confirmation.add_reaction('❌')
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=20,
                check=lambda r, u: u == ctx.author and r.message.channel == ctx.channel and str(r.emoji) in ['✅', '❌'])
        except asyncio.TimeoutError:
            embed = discord.Embed(title="Confirmation",
            description="You took too long to answer the question; not deleting it!",
            color=discord.Color.red(),
            timestamp=ctx.message.created_at)
            return await confirmation.edit(content=ctx.author.mention, embed=embed)
        else:
            if str(reaction.emoji) == '✅':
                embed.description = f"**Channel {ctx.channel.mention} is being deleted...**"
                await confirmation.edit(content=ctx.author.mention, embed=embed)
                await asyncio.sleep(3)
                await channel.delete()
                await self.remove_user_open_channel(user_channel[0][0])
            else:
                embed.description = "Not deleting it!"
                await confirmation.edit(content='', embed=embed)
            
            

    async def dnk_embed(self, member):
        def check(r, u):
            return u == member and str(r.message.id) == str(the_msg.id) and str(r.emoji) in ['⬅️', '➡️']

        command_index = 0
        initial_embed = discord.Embed(title="__Table of Commands and their Prices__",
                description="These are a few of commands and features that DNK can do.",
                color=discord.Color.blue())
        the_msg = await member.send(embed=initial_embed)
        await the_msg.add_reaction('⬅️')
        await the_msg.add_reaction('➡️')
        while True:
            embed = discord.Embed(title=f"__Table of Commands and their Prices__ ({command_index+1}/{len(list_of_commands)})",
                description="These are a few of commands and features that DNK can do.",
                color=discord.Color.blue())
            embed.add_field(name=list_of_commands[command_index][0],
                value=list_of_commands[command_index][1])
            await the_msg.edit(embed=embed)

            try:
                pending_tasks = [self.client.wait_for('reaction_add', check=check),
                self.client.wait_for('reaction_remove', check=check)]
                done_tasks, pending_tasks = await asyncio.wait(pending_tasks, timeout=60, return_when=asyncio.FIRST_COMPLETED)
                if not done_tasks:
                    raise asyncio.TimeoutError

                for task in pending_tasks:
                    task.cancel()

            except asyncio.TimeoutError:
                await the_msg.remove_reaction('⬅️', self.client.user)
                await the_msg.remove_reaction('➡️', self.client.user)
                break

            else:
                for task in done_tasks:
                    reaction, user = await task
                if str(reaction.emoji) == "➡️":
                    # await the_msg.remove_reaction(reaction.emoji, member)
                    if command_index < (len(list_of_commands) - 1):
                        command_index += 1
                    continue
                elif str(reaction.emoji) == "⬅️":
                    # await the_msg.remove_reaction(reaction.emoji, member)
                    if command_index > 0:
                        command_index -= 1
                    continue

    # Discord methods
    async def create_teacher_interview_room(self, guild: discord.Guild, teacher_app: List[str]) -> None:
        """ Creates an interview room with the teacher.
        :param guild: The server in which the interview will be.
        :param teacher_app: The teacher application info. """

        teacher_app_cat = discord.utils.get(guild.categories, id=self.teacher_app_cat_id)
        teacher = discord.utils.get(guild.members, id=teacher_app[1])

        # moderator = discord.utils.get(guild.roles, id=moderator_role_id)
        muffin = discord.utils.get(guild.members, id=self.muffin_id)
        lesson_management = discord.utils.get(guild.roles, id=lesson_management_role_id)

        # Creates channels
        overwrites: Dict = {guild.default_role: discord.PermissionOverwrite(
            read_messages=False, send_messages=False, connect=False, view_channel=False),
        teacher: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=True, view_channel=True),
        lesson_management: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=True, view_channel=True),
        }
        # moderator: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=False, view_channel=True, manage_messages=True)
        txt_channel = await guild.create_text_channel(name=f"{teacher.name}'s-interview", category=teacher_app_cat, overwrites=overwrites)
        vc_channel = await teacher_app_cat.create_voice_channel(name=f"{teacher.name}'s Interview", overwrites=overwrites)

        # Updates the teacher's application in the database, adding the channels ids
        await self.update_application(teacher.id, txt_channel.id, vc_channel.id, 'teacher')

        app_embed = discord.Embed(
            title=f"{teacher.name}'s Interview",
            description=f"""
            Hello, {teacher.mention}, we have received and reviewed your teacher application. In order to set up your lesson and explain how our system works we have to schedule a voice conversation with you.
            When would be the best time to talk to one of our staff?""",
            color=teacher.color)
        await txt_channel.send(content=f"{muffin.mention}, {lesson_management.mention}, {teacher.mention}", embed=app_embed)

    async def create_moderator_interview_room(self, guild: discord.Guild, moderator_app: List[str]) -> None:
        """ Creates an interview room with the moderator.
        :param guild: The server in which the interview will be.
        :param moderator_app: The moderator application info. """

        moderator_app_cat = discord.utils.get(guild.categories, id=self.moderator_app_cat_id)
        moderator = discord.utils.get(guild.members, id=moderator_app[1])

        cosmos = discord.utils.get(guild.members, id=self.cosmos_id)
        admin = discord.utils.get(guild.roles, id=admin_role_id)

        # Creates channels
        overwrites: Dict = {guild.default_role: discord.PermissionOverwrite(
            read_messages=False, send_messages=False, connect=False, view_channel=False),
        moderator: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=True, view_channel=True),
        }
        txt_channel = await guild.create_text_channel(name=f"{moderator.name}'s-interview", category=moderator_app_cat, overwrites=overwrites)
        vc_channel = await moderator_app_cat.create_voice_channel(name=f"{moderator.name}'s Interview", overwrites=overwrites)

        # Updates the moderator's application in the database, adding the channels ids
        await self.update_application(moderator.id, txt_channel.id, vc_channel.id, 'moderator')

        app_embed = discord.Embed(
            title=f"{moderator.name}'s Interview",
            description=f"""
            Hello, {moderator.mention}, we have received and reviewed your moderator application. In order to set you up and explain how our moderation works we have to schedule a voice conversation with you.
            When would be the best time to talk to one of our staff?""",
            color=moderator.color)
        await txt_channel.send(content=f"{cosmos.mention}, {admin.mention}, {moderator.mention}", embed=app_embed)


        # Discord methods
    
    async def create_event_manager_interview_room(self, guild: discord.Guild, event_manager_app: List[str]) -> None:
        """ Creates an interview room with the event manager.
        :param guild: The server in which the interview will be.
        :param event_manager_app: The moderator application info. """

        event_manager_app_cat = discord.utils.get(guild.categories, id=self.event_manager_app_cat_id)
        event_manager = discord.utils.get(guild.members, id=event_manager_app[1])

        muffin = discord.utils.get(guild.members, id=self.muffin_id)

        # Creates channels
        overwrites: Dict = {guild.default_role: discord.PermissionOverwrite(
            read_messages=False, send_messages=False, connect=False, view_channel=False),
        event_manager: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=True, view_channel=True),
        }
        txt_channel = await guild.create_text_channel(name=f"{event_manager.name}'s-interview", category=event_manager_app_cat, overwrites=overwrites)
        vc_channel = await event_manager_app_cat.create_voice_channel(name=f"{event_manager.name}'s Interview", overwrites=overwrites)

        # Updates the event_manager's application in the database, adding the channels ids
        await self.update_application(event_manager.id, txt_channel.id, vc_channel.id, 'event_manager')

        app_embed = discord.Embed(
            title=f"{event_manager.name}'s Interview",
            description=f"""
            Hello, {event_manager.mention}, we have received and reviewed your event manager application. In order to set you up and explain how our system works we have to schedule a voice conversation with you.
            When would be the best time to talk to one of our staff?""",
            color=event_manager.color)
        await txt_channel.send(content=f"{muffin.mention}, {event_manager.mention}", embed=app_embed)
    # In-game commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def close_app(self, ctx) -> None:
        """ (ADMIN) Closes an application channel. """

        member = ctx.author
        channel = ctx.channel
        guild = ctx.guild

        # Checks if the channel is in the teacher applications category
        if not channel.category or not channel.category.id in [self.teacher_app_cat_id, self.moderator_app_cat_id, self.event_manager_app_cat_id]:
            return await ctx.send(f"**This is not an application channel, {member.mention}!**")

        all_apps_channel = None

        if app_channel := await self.get_application_by_channel(channel.id, 'teacher'):
            all_apps_channel = discord.utils.get(guild.text_channels, id=self.teacher_app_channel_id)

        elif app_channel := await self.get_application_by_channel(channel.id, 'moderator'):
            all_apps_channel = discord.utils.get(guild.text_channels, id=self.moderator_app_channel_id)

        elif app_channel := await self.get_application_by_channel(channel.id, 'event_manager'):
            all_apps_channel = discord.utils.get(guild.text_channels, id=self.event_manager_app_channel_id)

        if app_channel:
            txt_channel = discord.utils.get(guild.channels, id=app_channel[4])
            vc_channel = discord.utils.get(guild.channels, id=app_channel[5])
            embed = discord.Embed(title="Confirmation",
                description="Are you sure that you want to delete this application channel?",
                color=member.color,
                timestamp=ctx.message.created_at)
            confirmation = await ctx.send(content=member.mention, embed=embed)
            await confirmation.add_reaction('✅')
            await confirmation.add_reaction('❌')
            try:
                reaction, _ = await self.client.wait_for('reaction_add', timeout=20,
                    check=lambda r, u: u == member and r.message.id == confirmation.id and str(r.emoji) in ['✅', '❌'])
            except asyncio.TimeoutError:
                embed = discord.Embed(title="Confirmation",
                description="You took too long to answer the question; not deleting it!",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at)
                return await confirmation.edit(content=member.mention, embed=embed)
            else:
                if str(reaction.emoji) == '✅':
                    embed.description = f"**Application channel {txt_channel.mention} is being deleted...**"
                    await confirmation.edit(content=member.mention, embed=embed)
                    await asyncio.sleep(3)
                    await txt_channel.delete()
                    await vc_channel.delete()
                    await self.delete_application(app_channel[0], app_channel[2])
                    try:
                        msg = await all_apps_channel.fetch_message(app_channel[0])
                        await msg.add_reaction('🔒')
                    except Exception:
                        pass
                else:
                    embed.description = "Not deleting it!"
                    await confirmation.edit(content='', embed=embed)
        else:
            await ctx.send(f"**What do you think that you are doing? You cannot delete this channel, {member.mention}!**")


    async def audio(self, member: discord.Member, audio_name: str) -> None:
        """ Plays an audio.
        :param member: A member to get guild context from.
        :param audio_name: The name of the audio to play. """

        # Resolves bot's channel state
        staff_vc = self.client.get_channel(staff_vc_id)
        bot_state = member.guild.voice_client

        try:
            if bot_state and bot_state.channel and bot_state.channel != staff_vc:
                await bot_state.disconnect()
                await bot_state.move_to(staff_vc)
            elif not bot_state:
                voicechannel = discord.utils.get(member.guild.channels, id=staff_vc.id)
                vc = await voicechannel.connect()

            await asyncio.sleep(2)
            voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=member.guild)
            # Plays / and they don't stop commin' /
            if voice_client and not voice_client.is_playing():
                audio_source = discord.FFmpegPCMAudio(f'tts/{audio_name}.mp3')
                voice_client.play(audio_source, after=lambda e: print("Finished Warning Staff!"))
            else:
                print('couldnt play it!')

        except Exception as e:
            print(e)
            return

    @commands.command(aliases=['make_report_msg', 'reportmsg', 'report_msg', 'supportmsg', 'support_msg'])
    @commands.has_permissions(administrator=True)
    async def make_report_support_message(self, ctx) -> None:
        """ (ADM) Makes a Report-Support message. """
        
        guild = ctx.guild
        embed = discord.Embed(
            title="__Report-Support Section__",
            description="""Welcome to the Report-Support section, here you can easily find your way into things and/or get help with whatever problem you may be experiencing.""",
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
            url="https://thelanguagesloth.com"
        )
        embed.set_author(name=self.client.user.display_name, url=self.client.user.avatar.url, icon_url=self.client.user.avatar.url)
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)
        view = ReportSupportView(self.client)
        await ctx.send(embed=embed, view=view)
        self.client.add_view(view=view)

def setup(client):
    client.add_cog(ReportSupport(client))
