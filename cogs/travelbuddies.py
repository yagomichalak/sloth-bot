import discord
from discord import slash_command, Option
from discord.ext import commands

import os
from typing import List

from extra import utils
from extra.prompt.menu import ConfirmButton
from extra.modals import TravelBuddyModal

travel_buddies_channel_id: int = int(os.getenv("TRAVEL_BUDDIES_CHANNEL_ID", 123))
guild_ids: List[int] = [int(os.getenv("SERVER_ID", 123))]


class TravelBuddies(commands.Cog):
    """ Category for the Travel Buddies feature. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.cache = {}
        self.channel_id: int = travel_buddies_channel_id

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to go. """

        print("The TravelBuddies cog is ready!")

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        """ Deletes any normal message sent by normal users
        in the travel-buddies channel. """

        perms = message.channel.permissions_for(message.author)
        if perms.administrator:
            return

        await message.delete()

    @slash_command(guild_ids=guild_ids)
    async def find_travel_buddy(self, ctx: discord.ApplicationContext,
        role: Option(discord.Role, name="country_role", description="Select the target country's language role.", required=True)
    ) -> None:
        """ Stars the process of finding a travel buddy. """

        if ctx.channel.id != self.channel_id:
            return await ctx.respond(f"**You cannot use this command here, only in <#{self.channel_id}>!**", ephemeral=True)

        member_ts = self.cache.get(ctx.author.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await ctx.respond(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**", ephemeral=True)

        modal = discord.ui.Modal = TravelBuddyModal(self.client, role)
        await ctx.response.send_modal(modal=modal)


def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(TravelBuddies(client))