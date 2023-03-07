import discord
from discord.ext import commands
import os
from typing import List, Union, Dict
from .modals import UserReportSupportDetailModal

class ReportSupportSelect(discord.ui.Select):
    """ Select for the Report-Support options. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

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
    
    async def callback(self, interaction: discord.Interaction):
        """ Callback for the ReportSupport's selected option. """

        if interaction.data["values"][0] == "Report":
            modal = UserReportSupportDetailModal(self.client, interaction.data['values'][0])
            await interaction.response.send_modal(modal)
        else:
            modal = UserReportSupportDetailModal(self.client, interaction.data['values'][0])
            await modal.callback(interaction)

        self.view.stop()


class WarriorUserItemSelect(discord.ui.Select):
    def __init__(self, items: List[Union[int, str]]) -> None:
        super().__init__(
            custom_id="warrior_select_user_item", placeholder="Select the item that you wanna rip off.", 
            min_values=1, max_values=1, 
            options=[
                discord.SelectOption(
                    label=item[4], description=f"Type: {item[5]} | Rip Off Cost: {int(item[6]/2)}🍃",
                    value=item[4],
                    emoji="<:warrior_scratch:869221184925995079>") for item in items])
        self.items = items

    
    async def callback(self, interaction: discord.Interaction) -> None:
        self.view.selected_item = [item for item in self.items if interaction.data['values'][0] == item[4]][0]
        self.view.stop()

class LanguageRoomSelect(discord.ui.Select):
    def __init__(self, client: commands.Bot, custom_id: str, row: int, select_options=[], placeholder="Select language room from list"):
        super().__init__(
            custom_id=custom_id, placeholder=placeholder, 
            min_values=1, max_values=1, 
            options=select_options, row=row)
        self.client = client
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        option = interaction.data['values'][0]

        self.view.chosen_option = option

        self.view.stop()


class SoundBoardSelect(discord.ui.Select):
    """ Select for selecting different soundboard settings. """

    def __init__(self, ctx: commands.Context, client: commands.Bot, sb_view: discord.ui.View, settings: List[Union[int, str]]) -> None:
        super().__init__(
            custom_id="select_soundboard_id", placeholder="Select the soundboard you wanna use.", 
            min_values=1, max_values=1, row=4, 
            options=[
                discord.SelectOption(label=item[0], value=item[1], emoji="⚙️") for item in settings])
        self.ctx = ctx
        self.client = client
        self.sb_view = sb_view
        self.settings = settings

    
    async def callback(self, interaction: discord.Interaction) -> None:
        setting = [setting for setting in self.settings if interaction.data['values'][0] == setting[1]][0]
        self.view.stop()

        # Updates view
        view = self.sb_view(ctx=self.ctx, client=self.client, setting=setting[1])
        view.add_item(self)

        # Updates embed

        embed = interaction.message.embeds[0]
        embed.remove_field(1)
        embed.add_field(name="__Current Setting:__", value=setting[0], inline=False)

        await interaction.response.edit_message(embed=embed, view=view)
