import discord
from discord.ext import commands

from typing import Dict, List, Tuple, Optional

import asyncio


class TicTacToeButton(discord.ui.Button):
    """ Button for the TicTacToe game. """


    def __init__(self, custom_id: str, row: int) -> None:
        """ Class init method. """

        super().__init__(label='\u200b', style=discord.ButtonStyle.secondary, custom_id=custom_id, row=row)

    
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

        if win_case := await self.check_win_state(user):
            await self.update_win_case_colors(interaction, win_case)
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
        """ Checks whether someone won the game.
        :param user: The user. """

        #  ___    ___    ___
        # |   |  |   |  |   |
        # |___|  |___|  |___|
        #  ___    ___    ___
        # |   |  |   |  |   |
        # |___|  |___|  |___|
        #  ___    ___    ___
        # |   |  |   |  |   |
        # |___|  |___|  |___|
        #

        cases: List[List[Tuple[int, int]]] = [
            # Upper horizontal
            [(0, 0), (0, 1), (0, 2)],
            # Middle horizontal
            [(1, 0), (1, 1), (1, 2)],
            # Bottom horizontal
            [(2, 0), (2, 1), (2, 2)],

            # Left vertical
            [(0, 0), (1, 0), (2, 0)],
            # Middle vertical
            [(0, 1), (1, 1), (2, 1)],
            # Right vertical
            [(0, 2), (1, 2), (2, 2)],

            # Right diagonal
            [(0, 0), (1, 1), (2, 2)],
            # Left diagonal
            [(0, 2), (1, 1), (2, 0)],

        ]

        you: List[Tuple[int, int]] = self.view.coords[user.id]

        for case in cases:
            if len(set(you).intersection(set(case))) >= 3:
                return case

        return False

    async def update_win_case_colors(self, interaction: discord.Interaction, win_case: List[Tuple[int, int, int]]) -> None:
        """ Updates the colors of the buttons that made the user win the game.
        :param interaction: The interaction.
        :param win_case: The list of tuples containing the coordinates of the win case. """

        rows: List[Tuple[discord.Button]] = [
            tuple(btn for btn in self.view.children if btn.row == 0),
            tuple(btn for btn in self.view.children if btn.row == 1),
            tuple(btn for btn in self.view.children if btn.row == 2),
        ]

        for cord in win_case:
            rows[cord[0]][cord[1]].style = discord.ButtonStyle.green

        await interaction.message.edit(view=self.view)

class FlagsGameButton(discord.ui.Button):
    """ Button of the FlagGame. """

    def __init__(self, style: discord.ButtonStyle = discord.ButtonStyle.secondary, custom_id: Optional[str] = None, label: Optional[str]=None, row: Optional[int] = None) -> None:
        """ Class init method. """

        super().__init__(style=style, label=label, custom_id=custom_id, row=row)
    

    async def callback(self, interaction: discord.Interaction) -> None:
        """ FlagGame's button callback. """

        await interaction.response.defer()
        await self.check_answer(interaction, self.custom_id)


    async def check_answer(self, interaction: discord.Interaction, custom_id: str) -> None:
        """ Checks the user answer. """

        self.view.used = True
        self.view.stop()
        embed = interaction.message.embeds[0]

        # Correct answer
        if custom_id[-1] == '1':
            self.view.points += 1
            if self.view.round >= 19:
                return await self.view.cog.end_flag_game(self.view.ctx, interaction.message, interaction.user, self.view.points)

            await self.view_correct_answer(interaction=interaction, embed=embed)

        # Wrong answer
        if custom_id[-1] == '0':
            if self.view.round >= 19:
                return await self.view.cog.end_flag_game(self.view.ctx, interaction.message, interaction.user, self.view.points)

            await self.view_wrong_answer(interaction=interaction, embed=embed)


    async def view_correct_answer(self, interaction: discord.Interaction, embed: discord.Embed):
        # Changes the clicked button to green
        self.style = discord.ButtonStyle.success
        await interaction.message.edit('\u200b', embed=embed, view=self.view)    

        await asyncio.sleep(0.8)

        # Generates a new guess
        await self.view.cog.generate_flag_game(self.view.ctx, message=interaction.message, points=self.view.points, round=self.view.round + 1, flags=self.view.flags)
    

    async def view_wrong_answer(self, interaction: discord.interactions, embed: discord.Embed):
        # Changes the wrong button to red
        self.style = discord.ButtonStyle.danger

        # Changes the correct button to green
        correct_button = [button for button in self.view.children if button.label == self.view.flags[self.view.round]['name']]
        correct_button[0].style = discord.ButtonStyle.success
        await interaction.message.edit(embed=embed, view=self.view)
        
        await asyncio.sleep(0.8)

        # Generates a new guess
        await self.view.cog.generate_flag_game(self.view.ctx, message=interaction.message, points=self.view.points, round=self.view.round + 1, flags=self.view.flags)

