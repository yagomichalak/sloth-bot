# import.standard
import os
from typing import Dict

# import.thirdparty
import discord
import requests
from discord import ApplicationContext, Option, OptionChoice, slash_command
from discord.ext import commands

# import.local
from extra import utils
from extra.view import BootcampFeedbackView

# variables.api
bootcamp_api_access_key = os.getenv("BOOTCAMP_API_ACCESS_KEY", "")
bootcamp_role_id = int(os.getenv("BOOTCAMP_ROLE_ID", 123))

# variables.id
guild_id = int(os.getenv('SERVER_ID', 123))
guild_ids = [guild_id]

# variables.role
senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID', 123))
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))

class Bootcamp(commands.Cog):
    """ A cog related to the Bootcamp event. """

    def __init__(self, client):
        self.client = client
        self.BASE_URL = "https://backend.lovelang.app/api/v1"

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to run. """

        print('Bootcamp cog is ready!')

    @slash_command(name="feedback_user", guild_ids=guild_ids)
    @utils.is_allowed([bootcamp_role_id], throw_exc=True)
    async def feedback_user(self,
        interaction: ApplicationContext,
        member: Option(discord.Member, description="The member to give feedback to.", required=True), # type: ignore
    ) -> None:
        """ Gives feedback to a user for the bootcamp. """

        await interaction.response.defer(ephemeral=True)
        current_ts = await utils.get_timestamp()
        view = BootcampFeedbackView(self.client, member=member, perpetrator=interaction.user, current_ts=current_ts)
        await interaction.followup.send(view=view, ephemeral=True)

    async def post_user_feedback_data(self, data: Dict[str, int]) -> None:
        """ Posts the user bootcamp feedback data to the API endpoint.
        :param data: The data to send. """

        headers = {"Content-Type": "application/json", "Access-key": bootcamp_api_access_key}
        response = requests.post(
            url=f"{self.BASE_URL}/feedback", json=data, headers=headers, timeout=10
        )
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)


def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(Bootcamp(client))
