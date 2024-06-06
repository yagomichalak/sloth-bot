import discord
from discord.ext import commands
import os

bumps_channel_id = int(os.getenv("BUMPS_CHANNEL_ID", 123))


class Bumps(commands.Cog):
    """ Miscellaneous related commands. """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Misc cog is online!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """ Looks for expired tempmutes and unmutes the users. """
        
        # Checks whether the message was sent in the right channel
        channel = message.channel
        if not message.channel or message.channel.id != bumps_channel_id:
            return

        # Deletes the one to the last message
        msgs = await channel.history(limit=2).flatten()
        await msgs[1].delete()


def setup(client):
    client.add_cog(Bumps(client))
