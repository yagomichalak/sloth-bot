# import.standard
from typing import Any, Dict

# import.thirdparty
import discord
from discord.ext import commands
from discord.ui import InputText, Modal

# import.local
from . import utils
from .prompt.menu import ConfirmButton

class ModeratorApplicationModal(Modal):
    """ Class for the moderator application. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        super().__init__(title="Moderator Application")
        self.client = client
        self.cog: commands.Cog = client.get_cog('ReportSupport')

        self.add_item(InputText(label="How active are you on Discord"))#, what's your country of origin?"))

        self.add_item(
            InputText(
                label="What is your age, gender and timezone?",
                placeholder="Example: 21 years old, male, Brasília.",
                style=discord.InputTextStyle.short,
            )
        )
        self.add_item(
            InputText(
                label="Languages spoken and proficiency level?",
                style=discord.InputTextStyle.short
            )
        )
        self.add_item(
            InputText(
                label="How could you make a better community?",
                style=discord.InputTextStyle.paragraph)
        )
        self.add_item(
            InputText(
                label="Why are you applying to be Staff?",# What's your motivation? ",
                style=discord.InputTextStyle.paragraph, placeholder="Explain why you want to be a moderator and why we should add you.",
            )
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """ Callback for the moderation application. """

        member: discord.Member = interaction.user

        embed = discord.Embed(
            title=f"__Moderator Application__",
            color=member.color
        )

        member_native_roles = [
            role.name.title() for role in member.roles
            if str(role.name).lower().startswith('native')
        ]
        member_native_roles = ['None.'] if not member_native_roles else member_native_roles

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Joined the server", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
        embed.add_field(name="Native roles", value=', '.join(member_native_roles), inline=False)
        embed.add_field(name="Age, gender, timezone", value=self.children[1].value, inline=False)
        embed.add_field(name="Discord Activity", value=self.children[0].value, inline=False)
        embed.add_field(name="Language Levels", value=self.children[2].value, inline=False)
        embed.add_field(name="Approach to make Sloth a better community", value=self.children[3].value, inline=False)
        embed.add_field(name="Motivation for application", value=self.children[4].value, inline=False)

        confirm_view = ConfirmButton(member, timeout=60)

        await interaction.response.send_message(
            content="Are you sure you want to apply this?",
            embed=embed, view=confirm_view, ephemeral=True)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await confirm_view.interaction.followup.send(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            return await confirm_view.interaction.followup.send(f"**Not doing it then, {member.mention}!**", ephemeral=True)

        self.cog.cache[member.id] = await utils.get_timestamp()
        await confirm_view.interaction.followup.send(content="""
        **Application successfully made, please, be patient now.**
    • We will let you know when we need a new mod. We check apps when we need it!""", ephemeral=True)


        moderator_app_channel = await self.client.fetch_channel(self.cog.moderator_app_channel_id)
        owner_role = discord.utils.get(moderator_app_channel.guild.roles, id=self.cog.owner_role_id)
        app = await moderator_app_channel.send(content=f"{owner_role.mention}, {member.mention}", embed=embed)
        await app.add_reaction('✅')
        await app.add_reaction('❌')
        # Saves in the database
        await self.cog.insert_application(app.id, member.id, 'moderator')

class TeacherApplicationModal(Modal):
    """ Class for the teacher application. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        super().__init__(title="Teacher Application")
        self.client = client
        self.cog: commands.Cog = client.get_cog('ReportSupport')

        self.add_item(
            InputText(
                label="Age, from, resides in, how active on Discord",
                placeholder="Example: 21yo, USA, Canada, very active.",
                style=discord.InputTextStyle.short))

        self.add_item(
            InputText(
                label="What language are you applying to teach?",
                style=discord.InputTextStyle.short))

        self.add_item(
            InputText(
                label="On what day and time you wanna teach?",
                placeholder="Thursdays 5PM CET",
                style=discord.InputTextStyle.short))

        self.add_item(
            InputText(
                label="English Level",
                placeholder="Please explain why you would be a great teacher.",
                style=discord.InputTextStyle.short))

        self.add_item(
            InputText(
                label="Motivation for applying",
                placeholder="Please explain why you would be a great teacher.",
                style=discord.InputTextStyle.paragraph))

    async def callback(self, interaction: discord.Interaction) -> None:
        """ Callback for the moderation application. """

        member: discord.Member = interaction.user

        embed = discord.Embed(
            title=f"__Teacher Application__",
            color=member.color
        )

        member_native_roles = [
            role.name.title() for role in member.roles
            if str(role.name).lower().startswith('native')
        ]
        member_native_roles = ['None.'] if not member_native_roles else member_native_roles

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Joined the server", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
        embed.add_field(name="Native roles", value=', '.join(member_native_roles), inline=False)
        embed.add_field(name="Age, from, resides in, active", value=self.children[0].value, inline=False)
        embed.add_field(name="Applying to teach", value=self.children[1].value.title(), inline=False)
        embed.add_field(name="On what day", value=self.children[2].value.title(), inline=False)
        embed.add_field(name="English Level", value=self.children[3].value.capitalize(), inline=False)
        embed.add_field(name="Motivation for application", value=self.children[4].value.capitalize(), inline=False)

        confirm_view = ConfirmButton(member, timeout=60)

        await interaction.response.send_message(
            "Are you sure you want to apply this?",
            embed=embed, view=confirm_view, ephemeral=True)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await confirm_view.interaction.followup.send(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            return await confirm_view.interaction.followup.send(f"**Not doing it then, {member.mention}!**", ephemeral=True)

        self.cog.cache[member.id] = await utils.get_timestamp()
        await confirm_view.interaction.followup.send(content="""
        **Application successfully made, please, be patient now.**
    • We will let you know when we need a new teacher. We check apps when we need it!""", ephemeral=True)

        teacher_app_channel = await self.client.fetch_channel(self.cog.teacher_app_channel_id)
        mayu = discord.utils.get(teacher_app_channel.guild.members, id=self.cog.mayu_id)
        app = await teacher_app_channel.send(content=f"{mayu.mention}, {member.mention}", embed=embed)
        await app.add_reaction('✅')
        await app.add_reaction('❌')
        # Saves in the database
        await self.cog.insert_application(app.id, member.id, 'teacher')

class EventHostApplicationModal(Modal):
    """ Class for the Event Host application. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        super().__init__(title="Event Host Application")
        self.client = client
        self.cog: commands.Cog = client.get_cog('ReportSupport')

        self.add_item(
            InputText(
                label="Event name and description",
                placeholder="Please, type how your event is gonna be called, and a small description for it.",
                style=discord.InputTextStyle.multiline))

        self.add_item(
            InputText(
                label="Why do you want to host that event?",
                style=discord.InputTextStyle.multiline))

        self.add_item(
            InputText(
                label="When is the best time for you to host events?",
                placeholder="I.E: Thursdays 3 pm CET, you can specify your timezone.",
                style=discord.InputTextStyle.short))

        self.add_item(
            InputText(
                label="Your age? Experience hosting events?",
                style=discord.InputTextStyle.short))

        self.add_item(
            InputText(
                label="Can you host events in English?",
                placeholder="If not, in which language would you be hosting?",
                style=discord.InputTextStyle.short))

    async def callback(self, interaction: discord.Interaction) -> None:
        """ Callback for the moderation application. """

        member: discord.Member = interaction.user

        embed = discord.Embed(
            title=f"__Event Host Application__",
            description=f"{member.mention} ({member.id})",
            color=member.color
        )

        member_native_roles = [
            role.name.title() for role in member.roles
            if str(role.name).lower().startswith('native')
        ]
        member_native_roles = ['None.'] if not member_native_roles else member_native_roles

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Joined the server", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
        embed.add_field(name="Native roles", value=', '.join(member_native_roles), inline=False)
        embed.add_field(name="Event Name & Description", value=self.children[0].value, inline=False)
        embed.add_field(name="Reason to host", value=self.children[1].value.title(), inline=False)
        embed.add_field(name="On what day", value=self.children[2].value.title(), inline=False)
        embed.add_field(name="Age & Experience", value=self.children[3].value.capitalize(), inline=False)
        embed.add_field(name="Can you host events in English?", value=self.children[4].value.capitalize(), inline=False)

        confirm_view = ConfirmButton(member, timeout=60)

        await interaction.response.send_message(
            content="Are you sure you want to apply this?",
            embed=embed, view=confirm_view, ephemeral=True)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await confirm_view.interaction.followup.send(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            return await interaction.followup.send(f"**Not doing it then, {member.mention}!**", ephemeral=True)

        self.cog.cache[member.id] = await utils.get_timestamp()
        await confirm_view.interaction.followup.send(content="""
        **Application successfully made, please, be patient now.**
    • We will let you know when we need a new event host. We check apps when we need it!""", ephemeral=True)

        teacher_app_channel = await self.client.fetch_channel(self.cog.event_host_app_channel_id)
        app = await teacher_app_channel.send(content=member.mention, embed=embed)
        await app.add_reaction('✅')
        await app.add_reaction('❌')
        # Saves in the database
        await self.cog.insert_application(app.id, member.id, 'event_host')

class DebateManagerApplicationModal(Modal):
    """ Class for the Event Host application. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        super().__init__(title="Debate Manager Application")
        self.client = client
        self.cog: commands.Cog = client.get_cog('ReportSupport')

        self.add_item(
            InputText(
                label="Age? Timezone? Active on Discord?",
                style=discord.InputTextStyle.short))

        self.add_item(
            InputText(
                label="In what languages do you wanna host events?",
                style=discord.InputTextStyle.short))

        self.add_item(
            InputText(
                label="Do you have any experience with:",
                placeholder="Moderating events? Organizing events?",
                style=discord.InputTextStyle.multiline))

        self.add_item(
            InputText(
                label="Why are you applying to be a Debate Mod?",
                style=discord.InputTextStyle.paragraph))

        self.add_item(
            InputText(
                label="What would you change in the Debate Club?",
                style=discord.InputTextStyle.paragraph))


    async def callback(self, interaction: discord.Interaction) -> None:
        """ Callback for the moderation application. """

        member: discord.Member = interaction.user

        embed = discord.Embed(
            title=f"__Event Host Application__",
            description=f"{member.mention} ({member.id})",
            color=member.color
        )

        member_native_roles = [
            role.name.title() for role in member.roles
            if str(role.name).lower().startswith('native')
        ]
        member_native_roles = ['None.'] if not member_native_roles else member_native_roles

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Joined the server", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
        embed.add_field(name="Native roles", value=', '.join(member_native_roles), inline=False)
        embed.add_field(name="Age, timezone, active", value=self.children[0].value, inline=False)
        embed.add_field(name="Host debates in", value=self.children[1].value.title(), inline=False)
        embed.add_field(name="Experience with moderating, organizing events", value=self.children[2].value.title(), inline=False)
        embed.add_field(name="Motivation", value=self.children[3].value.capitalize(), inline=False)
        embed.add_field(name="What would you change?", value=self.children[4].value.capitalize(), inline=False)
        confirm_view = ConfirmButton(member, timeout=60)
        await interaction.response.send_message(
            content="Are you sure you want to apply this?",
            embed=embed, view=confirm_view, ephemeral=True)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await confirm_view.interaction.followup.send(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            return await interaction.followup.send(f"**Not doing it then, {member.mention}!**", ephemeral=True)

        self.cog.cache[member.id] = await utils.get_timestamp()
        await confirm_view.interaction.followup.send(content="""
        **Application successfully made, please, be patient now.**
    • We will let you know when we need a new debate manager. We check apps when we need it!""", ephemeral=True)

        debate_app_channel = await self.client.fetch_channel(self.cog.debate_manager_app_channel_id)
        app = await debate_app_channel.send(content=member.mention, embed=embed)
        await app.add_reaction('✅')
        await app.add_reaction('❌')
        # Saves in the database
        await self.cog.insert_application(app.id, member.id, 'debate_manager')

class UserReportSupportDetailModal(Modal):
    """ Class for specifying details for a Report Support request. """

    def __init__(self, client: commands.Bot, option: str) -> None:
        """ Class init method. """

        super().__init__(title="Report-Support")
        self.client = client
        self.cog: commands.Cog = client.get_cog('ReportSupport')
        self.add_item(
            InputText(
                label="Who are you reporting?",
                placeholder="Type the username of the user you are reporting.",
                style=discord.InputTextStyle.singleline
            )
        )
        self.add_item(
            InputText(
                label="Reason of the report/What did this user do?",
                placeholder="Describe the situation as much as you can, so we can help you better and faster.",
                style=discord.InputTextStyle.paragraph
            )
        )
        self.add_item(
            InputText(
                label="Do you possess evidence of what happened?",
                placeholder="Recording, screenshots or witnesses can be considered as evidence ",
                style=discord.InputTextStyle.paragraph,
                min_length=2
            )
        )
        self.option = option

    async def callback(self, interaction) -> None:
        """ Callback for the form modal. """

        await interaction.response.defer()
        reportee = self.children[0].value
        text = self.children[1].value
        evidence=self.children[2].value
        member = interaction.user

        if self.option == 'Report':
            try:
                exists = await self.cog.report_someone(interaction, reportee, text, evidence)
                if exists is False:
                    return
            except Exception as e:
                print(e)

            else:
                return await self.cog.audio(member, 'case_alert')

        elif self.option == 'Support':
            message = f"Please, {member.mention}, try to explain what kind of help you want related to the server."
            try:
                exists = await self.cog.generic_help(interaction, 'general help', message)
                if exists is False:
                    return
            except Exception as e:
                print(e)
            else:
                return #await self.cog.audio(member, 'general_help_alert')

        elif self.option == 'Help':
            message = f"Please, {member.mention}, inform us what roles you want, and if you spotted a specific problem with the reaction-role selection."
            try:
                exists = await self.cog.generic_help(interaction, 'role help', message)
                if exists is False:
                    return
            except Exception as e:
                print(e)
            else:
                return #await self.cog.audio(member, 'role_help_alert')

        elif self.option == 'Oopsie':
            return await interaction.followup.send("**All right, cya!**", ephemeral=True)

class UserReportStaffDetailModal(Modal):
    """ Class for specifying details for a Report Support request. """

    def __init__(self, client: commands.Bot, option: str) -> None:
        """ Class init method. """

        super().__init__(title="Report Staff")
        self.client = client
        self.cog: commands.Cog = client.get_cog('ReportSupport')
        self.add_item(
            InputText(
                label="Who are you reporting?",
                placeholder="Type the username of the Staff member you are reporting.",
                style=discord.InputTextStyle.singleline
            )
        )
        self.add_item(
            InputText(
                label="Reason of the report/What did this user do?",
                placeholder="Describe the situation as much as you can, so we can help you better and faster.",
                style=discord.InputTextStyle.paragraph
            )
        )
        self.add_item(
            InputText(
                label="Do you possess evidence of what happened?",
                placeholder="Recording, screenshots or witnesses can be considered as evidence ",
                style=discord.InputTextStyle.paragraph,
                min_length=2
            )
        )
        self.option = option

    async def callback(self, interaction) -> None:
        """ Callback for the form modal. """

        await interaction.response.defer()
        reportee = self.children[0].value
        text = self.children[1].value
        evidence=self.children[2].value
        member = interaction.user

        if self.option == 'Report':
            try:
                exists = await self.cog.report_staff(interaction, reportee, text, evidence)
                if exists is False:
                    return
            except Exception as e:
                print(e)

            else:
                return await self.cog.audio(member, 'case_alert')

        elif self.option == 'Oopsie':
            return #await interaction.followup.send("**All right, cya!**", ephemeral=True)


class TravelBuddyModal(Modal):
    """ Class for the TravelBuddies feature. """

    def __init__(self, client: commands.Bot, country_role: discord.Role) -> None:
        """ Class init method. """

        super().__init__(title="Travel Buddy Form")
        self.client = client
        self.country_role = country_role
        self.cog: commands.Cog = client.get_cog('TravelBuddies')

        self.add_item(
            InputText(
                label="Where",
                placeholder="Where are you traveling to?",
                style=discord.InputTextStyle.short
            )
        )
        self.add_item(
            InputText(
                label="When",
                placeholder="When are you traveling to that place and for how long?",
                style=discord.InputTextStyle.short,
            )
        )
        self.add_item(
            InputText(
                label="Lookin for a host",
                placeholder="Are you looking for a host there?",
                style=discord.InputTextStyle.short
            )
        )
        self.add_item(
            InputText(
                label="Activities",
                placeholder="What kind of activities are you planning or want to do there?",
                style=discord.InputTextStyle.paragraph
            )
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """ Callback for the moderation application. """

        member: discord.Member = interaction.user
        current_time = await utils.get_time_now()

        embed = discord.Embed(
            title=f"__Travel Buddy__",
            color=member.color,
            timestamp=current_time
        )

        embed.set_thumbnail(url=member.display_avatar)

        embed.add_field(name="Who's traveling:", value=member.mention, inline=False)
        embed.add_field(name="Where", value=self.children[0].value, inline=False)
        embed.add_field(name="When", value=self.children[1].value, inline=False)
        embed.add_field(name="Looking for a host", value=self.children[2].value, inline=False)
        embed.add_field(name="Activities", value=self.children[3].value, inline=False)

        confirm_view = ConfirmButton(member, timeout=60)

        await interaction.response.send_message(
            content=f"Are you sure you want to post this, and ping the `{self.country_role.name}`?",
            embed=embed, view=confirm_view, ephemeral=True)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await confirm_view.interaction.response.send_message(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            return await confirm_view.interaction.response.send_message(f"**Not doing it then, {member.mention}!**", ephemeral=True)

        self.cog.cache[member.id] = await utils.get_timestamp()

        message = await confirm_view.interaction.followup.send(
            content=f"Hello, {self.country_role.mention}!", embed=embed, allowed_mentions=discord.AllowedMentions.all()
        )
        message.guild = interaction.guild

        await message.create_thread(name=f"{member}'s Trip", auto_archive_duration=10080)


class BootcampFeedbackModal(Modal):
    """ Class for the moderator application. """

    def __init__(self, client: commands.Bot,  view: discord.ui.View, questions: Dict[int, Dict[str, Any]], index_question: int = 1) -> None:
        """ Class init method. """

        super().__init__(title="Bootcamp Feedback")
        self.client = client
        self.view = view
        self.questions = questions
        self.index_question = index_question
        self.add_question()

    def add_question(self) -> None:

        question = self.questions.get(self.index_question)
        print(question)
        self.children.clear()  # Clear current inputs

        # Add the question input
        self.add_item(
            InputText(
                label=f"Question {self.index_question}",
                placeholder=question["message"],
                style=question["type"],
                required=True,
                max_length=question["max_length"],
            )
        )

        # Add the rating input
        self.add_item(
            InputText(
                label="Rating",
                placeholder="Rate it from 0-5.",
                style=discord.InputTextStyle.singleline,
                required=True,
                max_length=1,
            )
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """ Callback for the moderation application. """

        self.questions[self.index_question]["answer"] = self.children[0].value
        rating = 0
        try:
            rating = int(self.children[1].value)
        except Exception:
            pass
        self.questions[self.index_question]["rating"] = rating

        self.view.questions = self.questions
        self.view.children[self.index_question-1].disabled = True

        if self.index_question == len(self.questions):
            self.view.children[-1].disabled = False
            self.view.children[-1].style = discord.ButtonStyle.success

        await interaction.response.edit_message(view=self.view)
