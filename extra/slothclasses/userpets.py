import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union


class UserPetsTable(commands.Cog):
    """ Class for the UserPets table and its commands and methods. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_pets(self, ctx) -> None: pass
