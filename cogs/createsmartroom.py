import discord
from discord.ext import commands
from extra.smartrooms.rooms import BasicRoom, PremiumRoom, GalaxyRoom
from extra.smartrooms.database_commands import SmartRoomDatabase

class CreateSnartRoom(commands.Cog):

    def __init__(self, client: commands.Cog) -> None:
        self.client = client
        self.db: SmartRoomDatabase = SmartRoomDatabase()


def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(CreateSnartRoom(client))