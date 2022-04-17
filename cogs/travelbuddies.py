import discord
from discord import slash_command, Option
from discord.ext import commands

import os
from typing import List

from extra import utils
from extra.prompt.menu import ConfirmButton
from extra.modals import TravelBuddyModal

guild_ids: List[int] = [int(os.getenv("SERVER_ID", 123))]


class TravelBuddies(commands.Cog):
    """ Category for the Travel Buddies feature. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tell when the cog is ready to go. """

        print("The TravelBuddies cog is ready!")

    @slash_command(guild_ids=guild_ids)
    async def find_travel_buddy(self, ctx: discord.ApplicationContext,
        role: Option(discord.Role, name="country_role", description="Select the target country's language role.", required=True)
    ) -> None:
        """ Stars the process of finding a travel buddy. """

        print('oi')
        modal = discord.ui.Modal = TravelBuddyModal(self.client, role)
        await ctx.send_modal(modal)



        




def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(TravelBuddies(client))