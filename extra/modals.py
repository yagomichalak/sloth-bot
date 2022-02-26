import discord
from discord.ui import InputText, Modal
from discord.ext import commands
from .prompt.menu import ConfirmButton
import asyncio

class ModeratorApplicationModal(Modal):
    """ Class for the moderator application. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        super().__init__("Moderator Application")
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
                label="What's your English level?",
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

        await interaction.response.defer(ephemeral=True)
        member: discord.Member = interaction.user

        embed = discord.Embed(
            title=f"__Moderator Application__",
            color=member.color
        )

        member_native_roles = [
            role.name.title() for role in member.roles
            if str(role.name).lower().startswith('native')
        ]

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Joined the server", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
        embed.add_field(name="Native roles", value=', '.join(member_native_roles), inline=False)
        embed.add_field(name="Age, gender, timezone", value=self.children[0].value, inline=False)
        embed.add_field(name="Discord Activity", value=self.children[1].value, inline=False)
        embed.add_field(name="English level", value=self.children[2].value, inline=False)
        embed.add_field(name="Approach to make Sloth a better community", value=self.children[3].value, inline=False)
        embed.add_field(name="Motivation for application", value=self.children[4].value, inline=False)

        confirm_view = ConfirmButton(member, timeout=60)

        await interaction.followup.send(
            content="Are you sure you want to apply this?",
            embed=embed, view=confirm_view, ephemeral=True)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await confirm_view.interaction.followup.send(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            self.cog.cache[member.id] = 0
            return await confirm_view.interaction.followup.send(f"**Not doing it then, {member.mention}!**", ephemeral=True)

 
        await confirm_view.interaction.followup.send(content="""
        **Application successfully made, please, be patient now.**
    • We will let you know when we need a new mod. We check apps when we need it!""", ephemeral=True)


        moderator_app_channel = await self.client.fetch_channel(self.cog.moderator_app_channel_id)
        cosmos_role = discord.utils.get(moderator_app_channel.guild.roles, id=self.cog.cosmos_role_id)
        app = await moderator_app_channel.send(content=f"{cosmos_role.mention}, {member.mention}", embed=embed)
        await app.add_reaction('✅')
        await app.add_reaction('❌')
        # Saves in the database
        await self.cog.insert_application(app.id, member.id, 'moderator')

class TeacherApplicationModal(Modal):
    """ Class for the teacher application. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        super().__init__("Teacher Application")
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
                label="Are you able to teach lessons in English?",
                style=discord.InputTextStyle.short))

        self.add_item(
            InputText(
                label="Why are you applying to be Staff?",
                placeholder="Explain why you want to be a moderator and why we should add you.",
                style=discord.InputTextStyle.paragraph))

    async def callback(self, interaction: discord.Interaction) -> None:
        """ Callback for the moderation application. """

        await interaction.response.defer(ephemeral=True)
        member: discord.Member = interaction.user

        embed = discord.Embed(
            title=f"__Teacher Application__",
            color=member.color
        )

        member_native_roles = [
            role.name.title() for role in member.roles
            if str(role.name).lower().startswith('native')
        ]

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Joined the server", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
        embed.add_field(name="Native roles", value=', '.join(member_native_roles), inline=False)
        embed.add_field(name="Age, from, resides in, active", value=self.children[0].value, inline=False)
        embed.add_field(name="Applying to teach", value=self.children[1].value.title(), inline=False)
        embed.add_field(name="On what day", value=self.children[2].value.title(), inline=False)
        embed.add_field(name="English Level", value=self.children[3].value.capitalize(), inline=False)
        embed.add_field(name="Motivation for application", value=self.children[4].value.capitalize(), inline=False)

        confirm_view = ConfirmButton(member, timeout=60)

        await interaction.followup.send(
            content="Are you sure you want to apply this?",
            embed=embed, view=confirm_view, ephemeral=True)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await confirm_view.interaction.followup.send(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            self.cog.cache[member.id] = 0
            return await confirm_view.interaction.followup.send(f"**Not doing it then, {member.mention}!**", ephemeral=True)
 
        await confirm_view.interaction.followup.send(content="""
        **Application successfully made, please, be patient now.**
    • We will let you know when we need a new mod. We check apps when we need it!""", ephemeral=True)

        teacher_app_channel = await self.client.fetch_channel(self.cog.teacher_app_channel_id)
        cosmos_role = discord.utils.get(teacher_app_channel.guild.roles, id=self.cog.cosmos_role_id)
        app = await teacher_app_channel.send(content=f"{cosmos_role.mention}, {member.mention}", embed=embed)
        await app.add_reaction('✅')
        await app.add_reaction('❌')
        # Saves in the database
        await self.cog.insert_application(app.id, member.id, 'teacher')

class EventHostApplicationModal(Modal):
    """ Class for the Event Host application. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        super().__init__("Event Host Application")
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

        await interaction.response.defer(ephemeral=True)
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

        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Joined the server", value=member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
        embed.add_field(name="Native roles", value=', '.join(member_native_roles), inline=False)
        embed.add_field(name="Event Name & Description", value=self.children[0].value, inline=False)
        embed.add_field(name="Reason to host", value=self.children[1].value.title(), inline=False)
        embed.add_field(name="On what day", value=self.children[2].value.title(), inline=False)
        embed.add_field(name="Age & Experience", value=self.children[3].value.capitalize(), inline=False)
        embed.add_field(name="Can you host events in English?", value=self.children[4].value.capitalize(), inline=False)

        confirm_view = ConfirmButton(member, timeout=60)

        await interaction.followup.send(
            content="Are you sure you want to apply this?",
            embed=embed, view=confirm_view, ephemeral=True)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await confirm_view.interaction.followup.send(f"**{member.mention}, you took too long to answer...**", ephemeral=True)

        if not confirm_view.value:
            self.cog.cache[member.id] = 0
            return await interaction.followup.send(f"**Not doing it then, {member.mention}!**", ephemeral=True)
 
        await confirm_view.interaction.followup.send(content="""
        **Application successfully made, please, be patient now.**
    • We will let you know when we need a new mod. We check apps when we need it!""", ephemeral=True)

        teacher_app_channel = await self.client.fetch_channel(self.cog.teacher_app_channel_id)
        cosmos_role = discord.utils.get(teacher_app_channel.guild.roles, id=self.cog.cosmos_role_id)
        app = await teacher_app_channel.send(content=f"{cosmos_role.mention}, {member.mention}", embed=embed)
        await app.add_reaction('✅')
        await app.add_reaction('❌')
        # Saves in the database
        await self.cog.insert_application(app.id, member.id, 'event_host')