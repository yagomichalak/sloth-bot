import discord
from discord.ext import commands
from discord import slash_command, Option, OptionChoice, ApplicationContext
import os
from extra import utils
from typing import Dict
import requests

senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID', 123))
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
guild_id = int(os.getenv('SERVER_ID', 123))
bootcamp_api_access_key = os.getenv("BOOTCAMP_API_ACCESS_KEY", "")
guild_ids = [guild_id]


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
    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    async def feedback_user(self,
        interaction: ApplicationContext,
        member: Option(discord.Member, description="The member to give feedback to.", required=True), # type: ignore
        rating: Option(int, name="color", description="The color for the embed.", required=True,
            choices=[   
                OptionChoice(name="0⭐", value=0), OptionChoice(name="1⭐", value=1),
                OptionChoice(name="2⭐", value=2), OptionChoice(name="3⭐", value=3),
                OptionChoice(name="4⭐", value=4), OptionChoice(name="5⭐", value=5),
            ])  # type: ignore
    ) -> None:
        """ Gives feedback to a user for the bootcamp. """
        await interaction.defer(ephemeral=True)
        # Save data
        self.post_user_feedback_data(data={
            "user_id": member.id, "rating": rating, "perpetrator_id": interaction.author.id,
        })
        await interaction.respond(f"Gave {member.mention} a `{rating}⭐` rating for the bootcamp!")

    async def post_user_feedback_data(self, data: Dict[str, int]) -> None:
        """ Posts the user bootcamp feedback data to the API endpoint.
        :param data: The data to send. """

        headers = {"Content-Type": "application/json", "Access-key": bootcamp_api_access_key}
        response = requests.post(
            url=f"{self.BASE_URL}/feedback", data=data, headers=headers, timeout=10
        )
        if response.status_code != 201:
            print(response.status_code)
            print(response.text)


def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(Bootcamp(client))
