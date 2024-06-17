import discord
from discord.ext import commands, tasks
from typing import List, Any
import random


class LanguageMatch(commands.Cog):
    """ Class for the language match feature. """
    
    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("LanguageMatch cog is ready!")

    @tasks.loop(seconds=60)
    async def check_end_of_conversation(self) -> None:
        """  """

    async def get_random_member(self, members: List[discord.Member], filter_fnc: Any) -> discord.Member:
        """ Gets a random member from a filter.
        :param members: The list of members from which to choose.
        :param filter_fnc: The filter to apply to the get. """

        filtered_members = list(filter(filter_fnc, members))
        return random.choice(filtered_members)


def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """

    client.add_cog(LanguageMatch(client))
