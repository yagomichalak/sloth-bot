import discord
from discord.ext import commands
from mysqldb import *
import asyncio
from extra.useful_variables import list_of_commands
from extra.menu import ConfirmSkill
import time
from typing import List, Dict
import os
from datetime import datetime

reportsupport_channel_id = int(os.getenv('REPORT_CHANNEL_ID'))
dnk_id = int(os.getenv('DNK_ID'))
case_cat_id = int(os.getenv('CASE_CAT_ID'))
moderator_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
lesson_management_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID'))

staff_vc_id = int(os.getenv('STAFF_VC_ID'))

allowed_roles = [
int(os.getenv('OWNER_ROLE_ID')), admin_role_id,
moderator_role_id]


class ReportSupport(commands.Cog):
    '''
    A cog related to the system of reports and some other things.
    '''

    def __init__(self, client) -> None:
        self.client = client
        self.cosmos_id: int = int(os.getenv('COSMOS_ID'))
        self.cache = {}
        self.report_cache = {}
        # Teacher application attributes
        self.teacher_app_channel_id: int = int(os.getenv('TEACHER_APPLICATION_CHANNEL_ID'))
        self.teacher_app_cat_id: int = int(os.getenv('TEACHER_APPLICATION_CAT_ID'))

        self.moderator_app_channel_id: int = int(os.getenv('MODERATOR_APPLICATION_CHANNEL_ID'))
        self.moderator_app_cat_id: int = int(os.getenv('MODERATOR_APPLICATION_CAT_ID'))
        

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print('ReportSupport cog is online!')

    @commands.Cog.listener()
    async def on_raw_interaction_update(self, payload, member, button, response) -> None:
        """ Handles Report-Support related buttons. """
        
        if int(payload['id']) != int(os.getenv('REPORT_SUPPORT_MSG_ID')):
            return

        button.ping(response)

        custom_id = button.custom_id

        if custom_id.startswith('apply_to_teach') or custom_id.startswith('apply_to_moderate'):
            # Apply to be a teacher
            member_ts = self.cache.get(member.id)
            time_now = time.time()
            if member_ts:
                sub = time_now - member_ts
                if sub <= 1800:
                    return await member.send(
                        f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**")

            if custom_id.startswith('apply_to_teach'):
                await self.send_teacher_application(member)
            else:
                await self.send_moderator_application(member)
                

        elif custom_id.startswith('buy_custom_bot'):
            # Order a bot
            dnk = self.client.get_user(dnk_id)
            embed = discord.Embed(title="New possible order!",
                description=f"{member.mention} ({member.id}) might be interested in buying something from you!",
                color=member.color)
            embed.set_thumbnail(url=member.avatar_url)
            await dnk.send(embed=embed)
            await member.send(f"**If you are really interested in **buying** a custom bot, send a private message to {dnk.mention}!**")
            await self.dnk_embed(member)

        elif custom_id.startswith('report_support'):
            member_ts = self.report_cache.get(member.id)
            time_now = time.time()
            if member_ts:
                sub = time_now - member_ts
                if sub <= 240:
                    return await member.send(
                        f"**You are on cooldown to report, try again in {round(240-sub)} seconds**")

            self.report_cache[member.id] = time.time()
            await self.select_report(member, member.guild)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload) -> None:
        # Checks if it wasn't a bot's reaction

        if not payload.guild_id:
            return

        if not payload.member or payload.member.bot:
            return

        guild = self.client.get_guild(payload.guild_id)

        # Checks if it's in the teacher applications channel
        if payload.channel_id == self.teacher_app_channel_id:
            await self.handle_teacher_application(guild, payload)

        # Checks if it's in the moderator applications channel
        elif payload.channel_id == self.moderator_app_channel_id:
            await self.handle_moderator_application(guild, payload)


    async def handle_teacher_application(self, guild, payload) -> None:
        """ Handles teacher application.
        :param guild: The server in which the application is running.
        :param payload: Data about the Staff member who is opening the application. """

        emoji = str(payload.emoji)
        if emoji == '✅':
            # Gets the teacher app and does the magic
            teacher_app = await self.get_teacher_app_by_message(payload.message_id)
            if not teacher_app:
                return

            # Checks if the person has not an open interview channel already
            if teacher_app[0][2] == 'no':
                # Creates an interview room with the teacher and sends their application there (you can z!close there)
                return await self.create_teacher_interview_room(guild, teacher_app)

        elif emoji == '❌':
            # Tries to delete the teacher app from the db, in case it is registered
            teacher_app = await self.get_teacher_app_by_message(payload.message_id)
            if teacher_app and teacher_app[0][2] == 'no':
                await self.delete_teacher_app(payload.message_id)
                teacher_app_channel = self.client.get_channel(self.teacher_app_channel_id)
                app_msg = await teacher_app_channel.fetch_message(payload.message_id)
                await app_msg.add_reaction('🔏')
                teacher = discord.utils.get(guild.members, id=teacher_app[0][1])
                if teacher:
                    msg = "**Teacher Application**\nOur staff has avaluated your teacher application and has come to the conclusion that we are not in need of this lesson."
                    await payload.member.send(embed=discord.Embed(description=msg))
            return

    async def handle_moderator_application(self, guild, payload) -> None:
        """ Handles moderator application.
        :param guild: The server in which the application is running.
        :param payload: Data about the Staff member who is opening the application. """

        emoji = str(payload.emoji)
        if emoji == '✅':
            # Gets the moderator app and does the magic
            moderator_app = await self.get_moderator_app_by_message(payload.message_id)
            if not moderator_app:
                return

            # Checks if the person has not an open interview channel already
            if not moderator_app[0][2]:
                # Creates an interview room with the moderator and sends their application there (you can z!close there)
                return await self.create_moderator_interview_room(guild, moderator_app)

        elif emoji == '❌':
            # Tries to delete the moderator app from the db, in case it is registered
            moderator_app = await self.get_moderator_app_by_message(payload.message_id)
            if moderator_app and not moderator_app[0][2]:
                await self.delete_moderator_app(payload.message_id)
                moderator_app_channel = self.client.get_channel(self.moderator_app_channel_id)
                app_msg = await moderator_app_channel.fetch_message(payload.message_id)
                await app_msg.add_reaction('🔏')
                moderator = discord.utils.get(guild.members, id=moderator_app[0][1])
                if moderator:
                    msg = "**Moderator Application**\nOur staff has avaluated your moderator application and has come to a conclusion, and due to intern and unspecified reasons we are **declining** it. Thank you anyways*"
                    await payload.member.send(embed=discord.Embed(description=msg))
            return


    async def send_teacher_application(self, member):

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
        embed.set_footer(text=f"by {member}", icon_url=member.avatar_url)

        embed.description = '''
        - Hello, there you've reacted to apply to become a teacher.
        To apply please answer to these following questions with One message at a time
        Question one:
        What language are you applying to teach?'''
        q1 = await member.send(embed=embed)
        a1 = await self.get_message(member, msg_check)
        if not a1:
            return

        embed.description = '''
        - Why do you want to teach that language on the language sloth?
        Please answer with one message.'''
        q2 = await member.send(embed=embed)
        a2 = await self.get_message(member, msg_check)
        if not a2:
            return

        embed.description = '''
        - On The Language Sloth, our classes happen once a week at the same time weekly.
        Please let us know when would be the best time for you to teach,
        E.A: Thursdays 3 pm CET, you can specify your timezone.
        Again remember to answer with one message.'''
        q3 = await member.send(embed=embed)
        a3 = await self.get_message(member, msg_check)
        if not a3:
            return

        embed.description = '''
        - Let's talk about your English level, how do you consider your English level?
        Are you able to teach lessons in English?
        Please answer using one message only'''
        q4 = await member.send(embed=embed)
        a4 = await self.get_message(member, msg_check)
        if not a4:
            return

        embed.description = '''- Have you ever taught people before?'''
        q5 = await member.send(embed=embed)
        a5 = await self.get_message(member, msg_check)
        if not a5:
            return

        embed.description = '''- Inform a short description for your class.'''
        q6 = await member.send(embed=embed)
        a6 = await self.get_message(member, msg_check)
        if not a6:
            return

        embed.description = '''- How old are you?'''
        q7 = await member.send(embed=embed)
        a7 = await self.get_message(member, msg_check)
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
            cosmos = discord.utils.get(teacher_app_channel.guild.members, id=self.cosmos_id)
            app = await teacher_app_channel.send(content=f"{cosmos.mention}, {member.mention}\n{app}")
            await app.add_reaction('✅')
            await app.add_reaction('❌')
            # Saves in the database
            await self.save_teacher_app(app.id, member.id)

        else:
            self.cache[member.id] = 0
            return await member.send("**Thank you anyways!**")


    async def send_moderator_application(self, member):

        self.cache[member.id] = time.time()

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
        embed.set_footer(text=f"by {member}", icon_url=member.avatar_url)

        embed.description = "- What's your age?"
        q1 = await member.send(embed=embed)
        a1 = await self.get_message(member, msg_check)
        if not a1:
            return

        embed.description = """
        - Hello, there you've reacted to apply to become a moderator.
To apply please answer to these following questions with One message at a time
Question one:
Do you have any experience moderating Discord servers?"""
        q2 = await member.send(embed=embed)
        a2 = await self.get_message(member, msg_check)
        if not a2:
            return

        embed.description = """
        - What is your gender?
Please answer with one message."""
        q3 = await member.send(embed=embed)
        a3 = await self.get_message(member, msg_check)
        if not a3:
            return

        embed.description = """
        - What's your English level? Are you able to express yourself using English?
Please answer using one message only."""
        q4 = await member.send(embed=embed)
        a4 = await self.get_message(member, msg_check)
        if not a4:
            return

        embed.description = """
        - Why are you applying to be Staff? What is your motivation?
Please answer using one message only."""
        q5 = await member.send(embed=embed)
        a5 = await self.get_message(member, msg_check)
        if not a5:
            return

        embed.description = """- How do you think The Language Sloth could be a better community?
Please answer using one message only."""
        q6 = await member.send(embed=embed)
        a6 = await self.get_message(member, msg_check)
        if not a6:
            return

        embed.description = """- How active are you on Discord in general?
Please answer using one message only."""
        q7 = await member.send(embed=embed)
        a7 = await self.get_message(member, msg_check)
        if not a7:
            return

        embed.description = """- What is your time zone?
Please answer using one message only.."""
        q8 = await member.send(embed=embed)
        a8 = await self.get_message(member, msg_check)
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
            embed.description = "**Application successfully made, please, be patient now!**"
            await member.send(embed=embed)
            moderator_app_channel = await self.client.fetch_channel(self.moderator_app_channel_id)
            cosmos = discord.utils.get(moderator_app_channel.guild.members, id=self.cosmos_id)
            app = await moderator_app_channel.send(content=f"{cosmos.mention}, {member.mention}\n{app}")
            await app.add_reaction('✅')
            await app.add_reaction('❌')
            # Saves in the database
            await self.save_moderator_app(app.id, member.id)

        else:
            self.cache[member.id] = 0
            return await member.send("**Thank you anyway!**")

    # Report methods
    async def select_report(self, member, guild):

        # Ask what they want to do [Report someone, general help, missclick]
        react_list = ['1️⃣', '2️⃣', '3️⃣', '❌']

        report_embed = discord.Embed(
            title="What kind of report would you like to start?")
        report_embed.description = '''
        1️⃣ Report another user for breaking the rules.

        2️⃣ I need help with the server in general.

        3️⃣ I need to change some roles and I can't.

        ❌ Cancel, I missclicked.'''
        msg = await member.send(embed=report_embed)

        for react in react_list:
            await msg.add_reaction(react)

        try:
            r, _ = await self.client.wait_for(
                'reaction_add',
                timeout=240,
                check=lambda r, u: u.id == member.id and r.emoji in react_list and r.message.id == msg.id
            )
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="Timeout",
                description='**Try again!**',
                color=discord.Color.red())
            await member.send(embed=timeout_embed)

        else:
            emoji = str(r.emoji)
            if emoji == '1️⃣':
                # Report another user for breaking the rules
                try:
                    exists = await self.report_someone(member, guild)
                    if exists is False:
                        return
                except:
                    pass

                else:
                    return await self.audio(member, 'case_alert')

            elif emoji == '2️⃣':
                # I need help with the server in general
                message = f"Please, {member.mention}, try to explain what kind of help you want related to the server."
                try:
                    exists = await self.generic_help(member, guild, 'general help', message)
                    if exists is False:
                        return
                except:
                    pass
                else:
                    return await self.audio(member, 'general_help_alert')
            elif emoji == '3️⃣':
                # I need to change some roles and I can't
                message = f"Please, {member.mention}, inform us what roles you want, and if you spotted a specific problem with the reaction-role selection."
                try:
                    exists = await self.generic_help(member, guild, 'role help', message)
                    if exists is False:
                        return
                except:
                    pass
                else:
                    return await self.audio(member, 'role_help_alert')
            elif emoji == '❌':
                # Cancel, I misclicked
                return await member.send("**All right, cya!**")

    # - Report someone
    async def report_someone(self, member, guild):

        if await self.member_has_open_channel(member.id):
            embed = discord.Embed(title="Error!", description="**You already have an open channel!**", color=discord.Color.red())
            await member.send(embed=embed)
            return False

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
            await member.send("**Something went wrong with it, please contact an admin!**")
            raise Exception
        else:
            # print('created!')
            created_embed = discord.Embed(
                title="Report room created!",
                description=f"**Go to {the_channel.mention}!**",
                color=discord.Color.green())
            await member.send(embed=created_embed)
            await self.insert_user_open_channel(member.id, the_channel.id)
            await self.increase_case_number()
            embed = discord.Embed(title="Report Support!", description=f"Please, {member.mention}, try to explain what happened and who you want to report.",
                color=discord.Color.red())
            message = await the_channel.send(content=f"{member.mention}, {moderator.mention}, {cosmos.mention}", embed=embed)
            ctx = await self.client.get_context(message)
            return await self.client.get_cog('Tools').vc(ctx=ctx, member=member)

    # - Report someone
    async def generic_help(self, member, guild, type_help, message):

        if await self.member_has_open_channel(member.id):
            embed = discord.Embed(title="Error!", description="**You already have an open channel!**", color=discord.Color.red())
            await member.send(embed=embed)
            return False

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
            await member.send("**Something went wrong with it, please contact an admin!**")
            raise Exception
        else:
            # print('created!')
            created_embed = discord.Embed(
                title=f"Room for `{type_help}` created!",
                description=f"**Go to {the_channel.mention}!**",
                color=discord.Color.green())
            await member.send(embed=created_embed)
            await self.insert_user_open_channel(member.id, the_channel.id)
            embed = discord.Embed(title=f"{type_help.title()}!",
            description=f"{message}",
                color=discord.Color.red())
            await the_channel.send(content=f"{member.mention}, {moderator.mention}", embed=embed)

    async def get_message(self, member, check):
        try:
            message = await self.client.wait_for('message', timeout=240,
            check=check)
        except asyncio.TimeoutError:
            await member.send("**Timeout! Try again.**")
            return None
        else:
            content = message.content
            return content

    async def get_reaction(self, member, check):
        try:
            reaction, user = await self.client.wait_for('reaction_add',
            timeout=120, check=check)
        except asyncio.TimeoutError:
            await member.send("**Timeout! Try again.**")
            return None
        else:
            return str(reaction.emoji)

    async def member_has_open_channel(self, member_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM OpenChannels WHERE user_id = {member_id}")
        user = await mycursor.fetchall()
        await mycursor.close()
        return user

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_case_counter(self, ctx):
        '''
        (ADM) Creates the CaseCounter table.
        '''
        await ctx.message.delete()
        if await self.table_case_counter_exists():
            return await ctx.send("**Table __CaseCounter__ already exists!**", delete_after=3)

        mycursor, db = await the_database()
        await mycursor.execute("CREATE TABLE CaseCounter (case_number bigint default 0)")
        await mycursor.execute("INSERT INTO CaseCounter (case_number) VALUES (0)")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table __CaseCounter__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_case_counter(self, ctx):
        '''
        (ADM) Drops the CaseCounter table.
        '''
        await ctx.message.delete()
        if not await self.table_case_counter_exists():
            return await ctx.send("**Table __CaseCounter__ doesn't exist!**", delete_after=3)

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE CaseCounter")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __CaseCounter__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_case_counter(self, ctx):
        '''
        (ADM) Resets the CaseCounter table.
        '''
        await ctx.message.delete()
        if not await self.table_case_counter_exists():
            return await ctx.send("**Table __CaseCounter__ doesn't exist yet!**", delete_after=3)

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM CaseCounter")
        await mycursor.execute("INSERT INTO CaseCounter (case_number) VALUES (0)")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __CaseCounter__ reset!**", delete_after=3)

    async def table_case_counter_exists(self) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'CaseCounter'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_open_channels(self, ctx):
        '''
        (ADM) Creates the OpenChannels table.
        '''
        await ctx.message.delete()
        if await self.table_open_channels_exists():
            return await ctx.send("**Table __OpenChannels__ already exists!**", delete_after=3)

        mycursor, db = await the_database()
        await mycursor.execute("CREATE TABLE OpenChannels (user_id bigint, channel_id bigint)")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table __OpenChannels__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_open_channels(self, ctx):
        '''
        (ADM) Drops the OpenChannels table.
        '''
        await ctx.message.delete()
        if not await self.table_open_channels_exists():
            return await ctx.send("**Table __OpenChannels__ doesn't exist!**", delete_after=3)

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE OpenChannels")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __OpenChannels__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_open_channels(self, ctx):
        '''
        (ADM) Resets the OpenChannels table.
        '''
        await ctx.message.delete()
        if not await self.table_open_channels_exists():
            return await ctx.send("**Table __OpenChannels__ doesn't exist yet!**", delete_after=3)

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM OpenChannels")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __OpenChannels__ reset!**", delete_after=3)

    async def table_open_channels_exists(self) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'OpenChannels'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False
        else:
            return True

    async def get_case_number(self):
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM CaseCounter")
        counter = await mycursor.fetchall()
        await mycursor.close()
        return counter

    async def increase_case_number(self):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE CaseCounter SET case_number = case_number + 1")
        await db.commit()
        await mycursor.close()

    async def insert_user_open_channel(self, member_id: int, channel_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"INSERT INTO OpenChannels (user_id, channel_id) VALUES (%s, %s)", (member_id, channel_id))
        await db.commit()
        await mycursor.close()

    async def remove_user_open_channel(self, member_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"DELETE FROM OpenChannels WHERE user_id = {member_id}")
        await db.commit()
        await mycursor.close()

    async def get_case_channel(self, channel_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM OpenChannels WHERE channel_id = {channel_id}")
        channel = await mycursor.fetchall()
        await mycursor.close()
        return channel

    @commands.command(aliases=['permit_case', 'allow_case', 'witness', 'aw'])
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

    @commands.command(aliases=['forbid_case', 'fw'])
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

    @commands.command()
    @commands.has_any_role(*allowed_roles)
    async def close_channel(self, ctx):
        '''
        (MOD) Closes a Case-Channel.
        '''
        user_channel = await self.get_case_channel(ctx.channel.id)
        if user_channel:
            channel = discord.utils.get(ctx.guild.channels, id=user_channel[0][1])
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
        else:
            await ctx.send(f"**What do you think that you are doing? You cannot delete this channel, {ctx.author.mention}!**")

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
        teacher = discord.utils.get(guild.members, id=teacher_app[0][1])

        # moderator = discord.utils.get(guild.roles, id=moderator_role_id)
        cosmos = discord.utils.get(guild.members, id=self.cosmos_id)
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
        await self.update_teacher_application(teacher.id, txt_channel.id, vc_channel.id)

        app_embed = discord.Embed(
            title=f"{teacher.name}'s Interview",
            description=f'''
            Hello, {teacher.mention}, we have received and reviewed your teacher application. In order to set up your lesson and explain how our system works we have to schedule a voice conversation with you.
            When would be the best time to talk to one of our staff?''',
            color=teacher.color)
        await txt_channel.send(content=f"{cosmos.mention}, {lesson_management.mention}, {teacher.mention}", embed=app_embed)

    async def create_moderator_interview_room(self, guild: discord.Guild, moderator_app: List[str]) -> None:
        """ Creates an interview room with the moderator.
        :param guild: The server in which the interview will be.
        :param moderator_app: The moderator application info. """

        moderator_app_cat = discord.utils.get(guild.categories, id=self.moderator_app_cat_id)
        moderator = discord.utils.get(guild.members, id=moderator_app[0][1])

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
        await self.update_moderator_application(moderator.id, txt_channel.id, vc_channel.id)

        app_embed = discord.Embed(
            title=f"{moderator.name}'s Interview",
            description=f"""
            Hello, {moderator.mention}, we have received and reviewed your moderator application. In order to set you up and explain how our moderation works we have to schedule a voice conversation with you.
            When would be the best time to talk to one of our staff?""",
            color=moderator.color)
        await txt_channel.send(content=f"{cosmos.mention}, {admin.mention}, {moderator.mention}", embed=app_embed)

    # In-game commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def close_app(self, ctx) -> None:
        '''
        (ADMIN) Closes an application channel.
        '''

        # Checks if the channel is in the teacher applications category
        if not ctx.channel.category or not ctx.channel.category.id in [self.teacher_app_cat_id, self.moderator_app_cat_id]:
            return await ctx.send(f"**This is not an application channel, {ctx.author.mention}!**")

        application_type = None
        all_apps_channel = None

        if app_channel := await self.get_teacher_app_by_channel(ctx.channel.id):
            application_type = 'teacher'
            all_apps_channel = discord.utils.get(ctx.guild.channels, id=self.teacher_app_channel_id)

        elif app_channel := await self.get_moderator_app_by_channel(ctx.channel.id):
            application_type = 'moderator'
            all_apps_channel = discord.utils.get(ctx.guild.channels, id=self.moderator_app_channel_id)

        if app_channel:
            txt_channel = discord.utils.get(ctx.guild.channels, id=app_channel[0][3])
            vc_channel = discord.utils.get(ctx.guild.channels, id=app_channel[0][4])
            embed = discord.Embed(title="Confirmation",
                description="Are you sure that you want to delete this application channel?",
                color=ctx.author.color,
                timestamp=ctx.message.created_at)
            confirmation = await ctx.send(content=ctx.author.mention, embed=embed)
            await confirmation.add_reaction('✅')
            await confirmation.add_reaction('❌')
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=20,
                    check=lambda r, u: u == ctx.author and r.message.id == confirmation.id and str(r.emoji) in ['✅', '❌'])
            except asyncio.TimeoutError:
                embed = discord.Embed(title="Confirmation",
                description="You took too long to answer the question; not deleting it!",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at)
                return await confirmation.edit(content=ctx.author.mention, embed=embed)
            else:
                if str(reaction.emoji) == '✅':
                    embed.description = f"**Application channel {txt_channel.mention} is being deleted...**"
                    await confirmation.edit(content=ctx.author.mention, embed=embed)
                    await asyncio.sleep(3)
                    await txt_channel.delete()
                    await vc_channel.delete()

                    if application_type == 'teacher':
                        await self.delete_teacher_app(app_channel[0][0])
                    elif application_type == 'moderator':
                        await self.delete_moderator_app(app_channel[0][0])
                    try:
                        msg = await all_apps_channel.fetch_message(app_channel[0][0])
                        # await msg.delete()
                        await msg.add_reaction('🔒')
                    except Exception:
                        pass
                else:
                    embed.description = "Not deleting it!"
                    await confirmation.edit(content='', embed=embed)
        else:
            await ctx.send(f"**What do you think that you are doing? You cannot delete this channel, {ctx.author.mention}!**")

    # Database back-end methods
    async def get_teacher_app_by_message(self, message_id: int) -> List[str]:
        """ Gets a teacher application from the database by providing a message id. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM TeacherApplication WHERE message_id = %s", (message_id,))
        teacher_app = await mycursor.fetchall()
        await mycursor.close()
        return teacher_app

    async def get_teacher_app_by_channel(self, channel_id: int) -> List[str]:
        """ Gets a teacher application from the database by providing a channel id. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM TeacherApplication WHERE txt_id = %s", (channel_id,))
        teacher_app = await mycursor.fetchall()
        await mycursor.close()
        return teacher_app

    async def save_teacher_app(self, message_id: int, teacher_id: int) -> None:
        """ Saves a teacher application into the database. """

        mycursor, db = await the_database()
        await mycursor.execute(
            '''
            INSERT INTO TeacherApplication (message_id, teacher_id)
            VALUES (%s, %s)''', (message_id, teacher_id)
            )
        await db.commit()
        await mycursor.close()

    async def update_teacher_application(self, teacher_id: int, txt_id: int, vc_id: int) -> None:
        """ Updates the teacher's application; adding the txt and vc ids into it. """

        mycursor, db = await the_database()
        await mycursor.execute(
            '''UPDATE TeacherApplication SET
            channel_open = 'yes', txt_id = %s, vc_id = %s
            WHERE teacher_id = %s''', (txt_id, vc_id, teacher_id)
            )
        await db.commit()
        await mycursor.close()

    async def delete_teacher_app(self, message_id: int) -> None:
        """ Deletes a teacher application from the database. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM TeacherApplication WHERE message_id = %s", (message_id,))
        await db.commit()
        await mycursor.close()

    # Database ADM commands
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_teacher_application(self, ctx) -> None:
        """ (ADM) Creates the TeacherApplication table. """

        if await self.table_teacher_application_exists():
            return await ctx.send("**Table `TeacherApplication` already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute('''CREATE TABLE TeacherApplication (
            message_id BIGINT, teacher_id BIGINT, channel_open VARCHAR(3) default 'no',
            txt_id BIGINT default null, vc_id BIGINT default null)''')

        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `TeacherApplication` created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_teacher_application(self, ctx) -> None:
        """ (ADM) Drops the TeacherApplication table. """

        if not await self.table_teacher_application_exists():
            return await ctx.send("**Table `TeacherApplication` doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE TeacherApplication")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `TeacherApplication` dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_teacher_application(self, ctx) -> None:
        """ (ADM) Resets the TeacherApplication table. """

        if not await self.table_teacher_application_exists():
            return await ctx.send("**Table `TeacherApplication` doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM TeacherApplication")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `TeacherApplication` reset!**")

    async def table_teacher_application_exists(self) -> bool:
        """ Checks whether the TeacherApplication table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'TeacherApplication'")
        exists = await mycursor.fetchall()
        await mycursor.close()

        if len(exists):
            return True
        else:
            return False

    # Moderator Applications

    async def get_moderator_app_by_message(self, message_id: int) -> List[str]:
        """ Gets a moderator application from the database by message ID.
        :param message_id: The message ID. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ModeratorApplication WHERE message_id = %s", (message_id,))
        moderator_app = await mycursor.fetchall()
        await mycursor.close()
        return moderator_app

    async def get_moderator_app_by_channel(self, channel_id: int) -> List[str]:
        """ Gets a moderator application from the database by channel ID.
        :param channel_id: The text channel ID. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ModeratorApplication WHERE txt_id = %s", (channel_id,))
        moderator_app = await mycursor.fetchall()
        await mycursor.close()
        return moderator_app

    async def save_moderator_app(self, message_id: int, moderator_id: int) -> None:
        """ Saves a moderator application into the database.
        :param message_id: The ID of the applicaiton message.
        :param moderator_id: The moderator ID. """

        mycursor, db = await the_database()
        await mycursor.execute(
            """
            INSERT INTO ModeratorApplication (message_id, moderator_id)
            VALUES (%s, %s)""", (message_id, moderator_id)
            )
        await db.commit()
        await mycursor.close()

    async def update_moderator_application(self, moderator_id: int, txt_id: int, vc_id: int) -> None:
        """ Updates the moderator's application; adding the txt and vc ids into it.
        :param moderator_id: The moderator ID.
        :param txt_id: The text channel ID.
        :param vc_id: The voice channel ID. """

        mycursor, db = await the_database()
        await mycursor.execute(
            """UPDATE ModeratorApplication SET
            channel_open = 1, txt_id = %s, vc_id = %s
            WHERE moderator_id = %s""", (txt_id, vc_id, moderator_id)
            )
        await db.commit()
        await mycursor.close()

    async def delete_moderator_app(self, message_id: int) -> None:
        """ Deletes a moderator application from the database.
        :param message_id: The application message's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ModeratorApplication WHERE message_id = %s", (message_id,))
        await db.commit()
        await mycursor.close()

    # Database ADM commands
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_moderator_application(self, ctx) -> None:
        """ (ADM) Creates the ModeratorApplication table. """

        if await self.table_moderator_application_exists():
            return await ctx.send("**Table `ModeratorApplication` already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE ModeratorApplication (
            message_id BIGINT, moderator_id BIGINT, channel_open TINYINT(1) default 0,
            txt_id BIGINT default null, vc_id BIGINT default null)""")

        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `ModeratorApplication` created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_moderator_application(self, ctx) -> None:
        """ (ADM) Drops the ModeratorApplication table. """

        if not await self.table_moderator_application_exists():
            return await ctx.send("**Table `ModeratorApplication` doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE ModeratorApplication")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `ModeratorApplication` dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_moderator_application(self, ctx) -> None:
        """ (ADM) Resets the ModeratorApplication table. """

        if not await self.table_moderator_application_exists():
            return await ctx.send("**Table `ModeratorApplication` doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ModeratorApplication")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `ModeratorApplication` reset!**")

    async def table_moderator_application_exists(self) -> bool:
        """ Checks whether the ModeratorApplication table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'ModeratorApplication'")
        exists = await mycursor.fetchall()
        await mycursor.close()

        if len(exists):
            return True
        else:
            return False

    async def audio(self, member: discord.Member, audio_name: str) -> None:
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


def setup(client):
    client.add_cog(ReportSupport(client))
