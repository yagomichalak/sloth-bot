import discord
from discord.ext import commands
from .buttons import TicTacToeButton

from typing import Dict, List, Tuple

class TicTacToeView(discord.ui.View):
    """ View for the TicTacToe minigame. """

    def __init__(self, client: commands.Bot, player: discord.Member, opponent: discord.Member) -> None:
        """ Class init method. """

        super().__init__(timeout=None)
        self.client = client
        self.player = player
        self.opponent = opponent


        self.coords: Dict[int, List[Tuple[int, int]]] = {}

        self.turn_member: discord.Member = player

        self.create_matrix()

    def create_matrix(self) -> None:
        """ Creates the 3x3 Matrix of the game. """

        for i in range(3):
            for ii in range(3):
                button = TicTacToeButton(custom_id=f"ttt_button:{i}_{ii}", row=i)
                self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.turn_member.id
