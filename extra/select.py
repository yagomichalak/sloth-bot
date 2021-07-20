import discord
from discord.ext import commands
import os

class ReportSupportSelect(discord.ui.Select):
    def __init__(self, client: commands.Bot):
        super().__init__(
            custom_id="report_support_select", placeholder="Select what kind of Help you need", 
            min_values=1, max_values=1, 
            options=[
                discord.SelectOption(label="Report", description="Report another user for breaking the rules.", emoji="<:politehammer:608941633454735360>"),
                discord.SelectOption(label="Support", description="I need help with the server in general.", emoji="<:slothconfused:738579956598046802>"),
                discord.SelectOption(label="Help", description="I need to change some roles and I can't.", emoji="<:irrelevant:673334940632481793>"),
                discord.SelectOption(label="Oopsie", description="Cancel, I missclicked.", emoji="❌"),
            ])
        self.client = client
        self.cog = client.get_cog('ReportSupport')
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        guild = self.client.get_guild(int(os.getenv('SERVER_ID')))
        member = discord.utils.get(guild.members, id=interaction.user.id)

        option = interaction.data['values'][0]

        self.view.stop()
        if option == 'Report':
            try:
                exists = await self.cog.report_someone(member, guild)
                if exists is False:
                    return
            except Exception as e:
                print(e)

            else:
                return await self.cog.audio(member, 'case_alert')

        elif option == 'Support':
            message = f"Please, {member.mention}, try to explain what kind of help you want related to the server."
            try:
                exists = await self.cog.generic_help(member, guild, 'general help', message)
                if exists is False:
                    return
            except Exception as e:
                print(e)
            else:
                return await self.cog.audio(member, 'general_help_alert')
                
        elif option == 'Help':
            message = f"Please, {member.mention}, inform us what roles you want, and if you spotted a specific problem with the reaction-role selection."
            try:
                exists = await self.cog.generic_help(member, guild, 'role help', message)
                if exists is False:
                    return
            except Exception as e:
                print(e)
            else:
                return await self.cog.audio(member, 'role_help_alert')

        elif option == 'Oopsie':
            return await member.send("**All right, cya!**")