import discord
from discord.ext import commands
from mysqldb import *
import asyncio
from extra.useful_variables import list_of_commands
from extra.prompt.menu import Confirm
from extra.view import ReportSupportView
from typing import List, Dict, Optional
import os

case_cat_id = int(os.getenv('CASE_CAT_ID'))
reportsupport_channel_id = int(os.getenv('REPORT_CHANNEL_ID'))
dnk_id = int(os.getenv('DNK_ID'))
cent_id = int(os.getenv('CENT_ID'))
moderator_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
lesson_management_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID'))
server_id = int(os.getenv('SERVER_ID'))

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
        self.cosmos_role_id: int = int(os.getenv('COSMOS_ROLE_ID'))
        self.muffin_id: int = int(os.getenv('MUFFIN_ID'))
        self.cache = {}
        self.report_cache = {}
        

    @commands.Cog.listener()
    async def on_ready(self) -> None:

        self.client.add_view(view=ReportSupportView(self.client))
        print('ReportSupport cog is online!')


    async def handle_application(self, guild, payload) -> None:
        """ Handles teacher applications.
        :param guild: The server in which the application is running.
        :param payload: Data about the Staff member who is opening the application. """

        emoji = str(payload.emoji)
        if emoji == '✅':
            # Gets the teacher app and does the magic
            if not (app := await self.get_application_by_message(payload.message_id)):
                return

            # Checks if the person has not an open interview channel already
            if not app[3]:
                # Creates an interview room with the teacher and sends their application there (you can z!close there)
                return await self.create_interview_room(guild, app)

        elif emoji == '❌':
            # Tries to delete the teacher app from the db, in case it is registered
            app = await self.get_application_by_message(payload.message_id)
            if app and not app[3]:
                await self.delete_application(payload.message_id)

                interview_info = self.interview_info[app[2]]
                app_channel = self.client.get_channel(interview_info['app'])
                app_msg = await app_channel.fetch_message(payload.message_id)
                await app_msg.add_reaction('🔏')
                
                if applicant := discord.utils.get(guild.members, id=app[1]):
                    return await applicant.send(embed=discord.Embed(description=interview_info['message']))


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
        embed.set_footer(text=f"by {member}", icon_url=member.display_avatar)

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

        embed.description = "- Where are you from?"
        q8 = await member.send(embed=embed)
        a8 = await self.get_message_content(member, msg_check)
        if not a8:
            return

        embed.description = "- Where are you residing?"
        q9 = await member.send(embed=embed)
        a9 = await self.get_message_content(member, msg_check)
        if not a9:
            return

        # Get user's native roles
        user_native_roles = []
        for role in member.roles:
            if str(role.name).lower().startswith('native'):
                user_native_roles.append(role.name.title())

        # Application result
        app = f"```ini\n"\
            f"[Username]: {member} ({member.id})\n" \
            f"[Joined the server]: {member.joined_at.strftime('%a, %d %B %y, %I %M %p UTC')}\n" \
            f"[Applying to teach]: {a1.title()}\n[Native roles]: {', '.join(user_native_roles)}\n" \
            f"[Motivation for teaching]: {a2.capitalize()}\n" \
            f"[Applying to teach on]: {a3.upper()}\n" \
            f"[English level]: {a4.capitalize()}\n" \
            f"[Experience teaching]: {a5.capitalize()}\n" \
            f"[Description]:{a6.capitalize()}\n" \
            f"[Age]: {a7}\n" \
            f"[Lives in]: {a8.capitalize()}\n" \
            f"[Resides in]: {a9.capitalize()}" \
            f"```"
        await member.send(app)
        embed.description = "Are you sure you want to apply this? :white_check_mark: to send and :x: to Cancel"

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

```》Must be at least 18 years of age
》Must have at least a conversational level of English
》Must be an active member
》Be a member of the server for at least a month
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
        embed.set_footer(text=f"by {member}", icon_url=member.display_avatar)

        embed.description = "- What's your age?"
        await member.send(embed=embed)
        a1 = await self.get_message_content(member, msg_check)
        if not a1: return

        embed.description = """
        - Hello, there you've reacted to apply to become a moderator.
To apply please answer to these following questions with One message at a time
Question one:
Do you have any experience moderating Discord servers?"""
        q2 = await member.send(embed=embed)
        a2 = await self.get_message_content(member, msg_check)
        if not a2: return

        embed.description = """
        - What is your gender?
Please answer with one message."""
        await member.send(embed=embed)
        a3 = await self.get_message_content(member, msg_check)
        if not a3: return

        embed.description = """
        - What's your English level? Are you able to express yourself using English?
Please answer using one message only."""
        await member.send(embed=embed)
        a4 = await self.get_message_content(member, msg_check)
        if not a4: return

        embed.description = """
        - Why are you applying to be Staff? What is your motivation?
Please answer using one message only."""
        await member.send(embed=embed)
        a5 = await self.get_message_content(member, msg_check)
        if not a5: return

        embed.description = """- How do you think The Language Sloth could be a better community?
Please answer using one message only."""
        await member.send(embed=embed)
        a6 = await self.get_message_content(member, msg_check)
        if not a6: return

        embed.description = """- How active are you on Discord in general?
Please answer using one message only."""
        await member.send(embed=embed)
        a7 = await self.get_message_content(member, msg_check)
        if not a7: return

        embed.description = """- What is your time zone?
Please answer using one message only.."""
        await member.send(embed=embed)
        a8 = await self.get_message_content(member, msg_check)
        if not a8: return

        embed.description = "- What is your country of origin?"
        await member.send(embed=embed)
        a9 = await self.get_message_content(member, msg_check)
        if not a9: return

        embed.description = "- Tell us about yourself?"
        await member.send(embed=embed)
        a10 = await self.get_message_content(member, msg_check)
        if not a10: return

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
[Timezone]: {a8.title()}
[Origin Country]: {a9.title()}
[About]: {a10.capitalize()}```"""
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
            cosmos_role = discord.utils.get(moderator_app_channel.guild.roles, id=self.cosmos_role_id)
            app = await moderator_app_channel.send(content=f"{cosmos_role.mention}, {member.mention}\n{app}")
            await app.add_reaction('✅')
            await app.add_reaction('❌')
            # Saves in the database
            await self.insert_application(app.id, member.id, 'moderator')

        else:
            self.cache[member.id] = 0
            return await member.send("**Thank you anyways!**")


    async def send_event_host_application(self, member):
        """ Sends a event host application form to the user.
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
            We do not require professional skills, however, we have a set numbers of requirements for our event hosts.
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
        embed.set_footer(text=f"by {member}", icon_url=member.display_avatar)

        embed.title = "Event Host Application"
        embed.description = '''
        - Hello, there you've reacted to apply to become an Event Host.
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
            event_host_channel = await self.client.fetch_channel(self.event_host_app_channel_id)
            app = await event_host_channel.send(content=f"{member.mention}\n{app}")
            await app.add_reaction('✅')
            await app.add_reaction('❌')
            # Saves in the database
            await self.insert_application(app.id, member.id, 'event_host')

        else:
            self.cache[member.id] = 0
            return await member.send("**Thank you anyways!**")

    async def send_debate_manager_application(self, member):
        """ Sends a Debate Manager application form to the user.
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
Before you can formally start applying for Debate Moderator in The Language Sloth, there are a couple requirements we would like you to know we feel necessity for:

Entry requirements:

》Must be at least 18 years of age.

》Must have at least a conversational level of English.

》Must be able to host a debate once a two week period.

》Must not have any warnings in the past 3 months.

》Must be in the server for at least 2 weeks.
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
        embed.set_footer(text=f"by {member}", icon_url=member.display_avatar)

        embed.title = "Debate Manager Application"
        embed.description = '''
        - Hello, there you've reacted to apply to become a Debate Manager.
        To apply please answer to these following questions with One message at a time

        Question one:
        - How old are you?'''
        q1 = await member.send(embed=embed)
        a1 = await self.get_message_content(member, msg_check)
        if not a1:
            return

        embed.description = "- Do you have any experience moderating debates?"
        q2 = await member.send(embed=embed)
        a2 = await self.get_message_content(member, msg_check)
        if not a2:
            return

        embed.description = "- Do you have any experience organizing events?"
        q3 = await member.send(embed=embed)
        a3 = await self.get_message_content(member, msg_check)
        if not a3:
            return

        embed.description = "- Why are you applying to be a Debate Mod?"
        q4 = await member.send(embed=embed)
        a4 = await self.get_message_content(member, msg_check)
        if not a4:
            return

        embed.description = "- What would you change in the Debate Club?"
        q5 = await member.send(embed=embed)
        a5 = await self.get_message_content(member, msg_check)
        if not a5:
            return

        embed.description = "- How active are you on Discord in general?"
        q6 = await member.send(embed=embed)
        a6 = await self.get_message_content(member, msg_check)
        if not a6:
            return

        embed.description = "- What is your time zone?"
        q7 = await member.send(embed=embed)
        a7 = await self.get_message_content(member, msg_check)
        if not a7:
            return

        embed.description = "- Would you like to host events in your native language other than in English?"
        q8 = await member.send(embed=embed)
        a8 = await self.get_message_content(member, msg_check)
        if not a8:
            return

        embed.description = "- If yes, what’s your native language?"
        q9 = await member.send(embed=embed)
        a9 = await self.get_message_content(member, msg_check)
        if not a9:
            return

        # Get user's native roles
        user_native_roles = []
        for role in member.roles:
            if str(role.name).lower().startswith('native'):
                user_native_roles.append(role.name.title())

        # Application result
        app = f"""```ini\n[Username]: {member} ({member.id})\n[Joined the server]: {member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC")}\n[Age]: {a1}\n[Native roles]: {', '.join(user_native_roles)}\n[Experience moderating]: {a2.capitalize()}\n[Experience organizing]: {a3.capitalize()}\n[Motivation]: {a4}\n[What would you change]:{a5.capitalize()}\n[How active]: {a6}\n[Timezone]: {a7}\n[Host in native language]: {a8.title()}\n[Native language]: {a9}```"""
        await member.send(app)
        embed.description = "Are you sure you want to apply this? :white_check_mark: to send and :x: to Cancel"
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
            debate_manager_channel = await self.client.fetch_channel(self.debate_manager_app_channel_id)
            guild = self.client.get_guild(server_id)
            cent = discord.utils.get(guild.members, id=cent_id)
            app = await debate_manager_channel.send(content=f"{cent.mention}, {member.mention}\n{app}")
            await app.add_reaction('✅')
            await app.add_reaction('❌')
            # Saves in the database
            await self.insert_application(app.id, member.id, 'debate_manager')

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
        embed.set_footer(text=f"by {member}", icon_url=member.display_avatar)

        embed.set_image(url="https://cdn.discordapp.com/attachments/562019472257318943/882352621116096542/slothfacepopoo.png")

        await member.send(embed=embed)

        while True:
            msg = await self.get_message(member, msg_check, 300)
            if msg is None:
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

        verify_embed.set_thumbnail(url=member.display_avatar)
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
        cosmos_role = discord.utils.get(guild.roles, id=self.cosmos_role_id)
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
            message = await the_channel.send(content=f"{member.mention}, {moderator.mention}, {cosmos_role.mention}", embed=embed)
            ctx = await self.client.get_context(message)

            if member.voice:
                channel = member.voice.channel
                members = member.voice.channel.members

                for id, member_in_vc in enumerate(members):
                    if member == member_in_vc:
                        del members[id]

                if not members:
                    await ctx.send(f"**{member.mention} is in the {channel.mention} voice channel alone!**")
                else:
                    await ctx.send(f"**{member.mention} is in the {channel.mention} voice channel with other {len(channel.members) - 1} members:** {', '.join([member_in_vc.mention for member_in_vc in members])}")

            else:
                await ctx.send(f"**{member.mention} is not in a VC!**")

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

            confirm = await Confirm(f"**Are you sure you want to allow {member.mention} as a witness in this case channel, {ctx.author.mention}?**").prompt(ctx)
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

            confirm = await Confirm(f"**Are you sure you want to forbid {member.mention} from being a witness in this case channel, {ctx.author.mention}?**").prompt(ctx)
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
    async def create_interview_room(self, guild: discord.Guild, app: List[str]) -> None:
        """ Creates an interview room for the given application.
        :param guild: The server in which the interview will be.
        :param app: The applicant info. """

        applicant = discord.utils.get(guild.members, id=app[1])

        interview_info = self.interview_info.get(app[2])

        # Create Private Thread for the user
        app_parent = self.client.get_channel(interview_info['parent'])

        #delete this later
        message = None
        # message = await app_parent.send('Uncomment this in your development environment')

        txt_channel = await app_parent.create_thread(name=f"{applicant.display_name}'s-interview", message=message, reason=f"{app[2].title()} Interview Room")

        # Add permissions for the user in the interview room
        parent_channel = self.client.get_channel(interview_info['parent'])
        interview_vc = self.client.get_channel(interview_info['interview'])

        # Updates the applicant's application in the database, adding the channels ids
        await self.update_application(applicant.id, txt_channel.id, interview_vc.id, app[2])

        # Set channel perms for the user.
        await parent_channel.set_permissions(applicant, read_messages=True, send_messages=False, view_channel=True)
        await interview_vc.set_permissions(applicant, speak=True, connect=True, view_channel=True)

        app_embed = discord.Embed(
            title=f"{applicant.name}'s Interview",
            description=f"""
            Hello, {applicant.mention}, we have received and reviewed your `{app[2].title().replace('_', ' ')}` application. In order to explain how our system works we have to schedule a voice conversation with you.
            When would be the best time to talk to one of our staff?""",
            color=applicant.color)

        formatted_pings = await self.format_application_pings(guild, interview_info['pings'])
        await txt_channel.send(content=f"{formatted_pings}, {applicant.mention}", embed=app_embed)


    # In-game commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def close_app(self, ctx) -> None:
        """ (ADMIN) Closes an application channel. """

        member = ctx.author
        channel = ctx.channel
        guild = ctx.guild

        if not (app := await self.get_application_by_channel(channel.id)):
            return await ctx.send(f"**This is not an application channel, {member.mention}!**")

        interview_info = self.interview_info[app[2]]
        all_apps_channel = discord.utils.get(guild.text_channels, id=interview_info['app'])

        confirm = await Confirm(f"**Are you sure that you want to delete this application channel, {member.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not deleting it, then, {member.mention}!**")
    
        applicant = guild.get_member(app[1])
        parent_channel = discord.utils.get(guild.text_channels, id=interview_info['parent'])
        interview_vc = discord.utils.get(guild.voice_channels, id=interview_info['interview'])
        try:
            await parent_channel.set_permissions(applicant, overwrite=None)
            await interview_vc.set_permissions(applicant, overwrite=None)
        except:
            pass
        await channel.delete()
        await self.delete_application(app[0])
        try:
            msg = await all_apps_channel.fetch_message(app[0])
            await msg.add_reaction('🔒')
        except:
            pass
            

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
        embed.set_author(name=self.client.user.display_name, url=self.client.user.display_avatar, icon_url=self.client.user.display_avatar)
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)
        view = ReportSupportView(self.client)
        await ctx.send(embed=embed, view=view)
        self.client.add_view(view=view)

def setup(client):
    client.add_cog(ReportSupport(client))
