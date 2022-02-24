import discord
from discord.ui import InputText, Modal
from discord.ext import commands
from .prompt.menu import ConfirmButton
import asyncio

class ModeratorApplicationModal(Modal):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__("Moderator Application")
        self.client = client
        self.cog: commands.Cog = client.get_cog('ReportSupport')

        self.add_item(InputText(label="How active are you on Discord"))#, what's your country of origin?"))

        self.add_item(
            InputText(
                label="What is your age, gender and timezone?",
                placeholder="Example: 21 years old, male, Brasília.",
                style=discord.InputTextStyle.multiline,
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
                style=discord.InputTextStyle.singleline)
        )
        self.add_item(
            InputText(
                label="Why are you applying to be Staff?",# What's your motivation? ",
                style=discord.InputTextStyle.paragraph, placeholder="Explain why you want to be a moderator and why we should add you.",
            )
        )

    async def callback(self, interaction: discord.Interaction):

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