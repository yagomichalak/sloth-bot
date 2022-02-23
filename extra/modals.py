import discord
from discord.ui import InputText, Modal
from discord.ext import commands

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


        user: discord.Member = interaction.user

        def check_reaction(r, u):
            return u.id == user.id and not r.message.guild and str(r.emoji) in ['✅', '❌']

        embed = discord.Embed(
            title=f"__Moderator Application__",
            color=user.color
        )

        user_native_roles = [
            role.name.title() for role in user.roles
            if str(role.name).lower().startswith('native')
        ]

        embed.set_thumbnail(url=user.display_avatar)
        embed.add_field(name="Joined the server", value=user.joined_at.strftime("%a, %d %B %y, %I %M %p UTC"), inline=False)
        embed.add_field(name="Native roles", value=', '.join(user_native_roles), inline=False)
        embed.add_field(name="Age, gender, timezone", value=self.children[0].value, inline=False)
        embed.add_field(name="Discord Activity", value=self.children[1].value, inline=False)
        embed.add_field(name="English level", value=self.children[2].value, inline=False)
        embed.add_field(name="Approach to make Sloth a better community", value=self.children[3].value, inline=False)
        embed.add_field(name="Motivation for application", value=self.children[4].value, inline=False)
        await interaction.response.send_message(embeds=[embed])

        await user.send(embed=embed)
        embed.description = """
        Are you sure you want to apply this? :white_check_mark: to send and :x: to Cancel
        """
        app_conf = await user.send(embed=embed)
        await app_conf.add_reaction('✅')
        await app_conf.add_reaction('❌')

        # Waits for reaction confirmation
        r = await self.get_reaction(user, check_reaction)
        if r is None:
            return

        if r == '✅':
            # ""
            embed.description = """**Application successfully made, please, be patient now.**
            
            We will let you know when we need a new mod. We check apps when we need it!""" 
            await user.send(embed=embed)
            moderator_app_channel = await self.client.fetch_channel(self.moderator_app_channel_id)
            cosmos_role = discord.utils.get(moderator_app_channel.guild.roles, id=self.cosmos_role_id)
            app = await moderator_app_channel.send(content=f"{cosmos_role.mention}, {user.mention}\n{app}")
            await app.add_reaction('✅')
            await app.add_reaction('❌')
            # Saves in the database
            await self.cog.insert_application(app.id, user.id, 'moderator')

        else:
            self.cache[user.id] = 0
            return await user.send("**Thank you anyways!**")