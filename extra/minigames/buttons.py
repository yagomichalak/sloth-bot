import discord
from discord.ext import commands

from typing import List, Tuple

class TicTacToeButton(discord.ui.Button):
    """ Button for the TicTacToe game. """


    def __init__(self, custom_id: str, row: int):
        super().__init__(label='\u200b', style=discord.ButtonStyle.blurple, custom_id=custom_id, row=row)

    
    async def callback(self, interaction: discord.Interaction) -> None:
        """ Callback for the button click. """

        user: discord.Member = interaction.user
        await interaction.response.defer()
        i, ii = tuple(self.custom_id.replace('ttt_button:', '').split('_'))
        coords_played: Tuple[int, int, int] = (int(i), int(ii))



        all_coords_played = [
            coord for key in self.view.coords.keys() for coord in self.view.coords[key]
        ]

        if coords_played in list(all_coords_played):
            return

        # Appends play coordinates to the coords played list
        if self.view.coords.get(user.id):
            self.view.coords[user.id].append(coords_played)
        else:
            self.view.coords[user.id] = [coords_played]

        # Changes the turn player
        if self.view.turn_member == self.view.player:
            self.emoji = '❌'
            self.view.turn_member = self.view.opponent

        else:
            self.emoji = '⭕'
            self.view.turn_member = self.view.player

        embed = interaction.message.embeds[0]
        embed.remove_field(1)
        embed.add_field(name="__Turn__:", value=f"Now it's {self.view.turn_member.mention}'s turn!")

        if await self.check_win_state(user):
            
            embed.remove_field(1)
            embed.add_field(name="__We have a Winner!__:", value=f"{user.mention} just won the game!")
            await interaction.followup.send(f"**You won the game, {interaction.user.mention}!**")
            self.view.stop()

        all_coords_played.append(coords_played)
        if len(all_coords_played) >= 9:
            embed.remove_field(1)
            await interaction.followup.send(f"**The game has drawn, {interaction.user.mention}!**")
            self.view.stop()

        await interaction.message.edit(embed=embed, view=self.view)

    async def check_win_state(self, user: discord.Member) -> None:
        """ Checks whether someone won the game. """


        cases: List[List[Tuple[int, int]]] = [
            # Upper horizontal
            [(0, 0), (0, 1), (0, 2)],
            # Middle horizontal
            [(1, 0), (1, 1), (1, 2)],
            # Bottom horizontal
            [(2, 0), (2, 1), (2, 2)],

            # Upper vertical
            [(0, 0), (1, 0), (2, 0)],
            # Middle vertical
            [(1, 0), (1, 1), (1, 2)],
            # Bottom vertical
            [(2, 0), (2, 1), (2, 2)],

            # Right diagonal
            [(0, 0), (1, 1), (2, 2)],
            # Left diagonal
            [(0, 2), (1, 1), (2, 0)],

        ]

        you: List[Tuple[int, int]] = self.view.coords[user.id]

        for case in cases:
            if len(set(you).intersection(set(case))) >= 3:
                return True

        return False