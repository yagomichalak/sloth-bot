import asyncio
import discord
from discord.ext import commands
from mysqldb import *
import copy
import random
from .whitejack_db import WhiteJackDB
from .create_cards_pack import cards_pack
from typing import List, Union, Optional, Dict
from .enums import EmbedColorEnum, EmbedStateEnum
from extra import utils


cogs: List[commands.Cog] = [
	WhiteJackDB
]

class WhiteJackGame(*cogs):
    """ Class for the WhiteJack game. """

    def __init__(self, 
        client: commands.Bot, bet: int, player: discord.Member, 
        guild: discord.Guild, current_money: int
    ) -> None:
        """ Class init method. """
        
        self.client = client
        self.guild = guild
        self.bet = bet
        self.current_money = current_money

        # Player info
        self.player = player
        self.player_total = 0
        self.player_cards: List = []

        # Dealer info
        self.dealer_total_showed = '`?`'
        self.dealer_total = 0
        self.dealer_cards: List = []

        self.game_pack: List = copy.deepcopy(cards_pack)
        random.shuffle(self.game_pack)

                # Draw first 2 cards for dealer
        # Draw the hidden card for dealer
        secret_card = self.game_pack.pop()
        secret_card.symbol = '`?`'
        self.dealer_total += secret_card.points
        self.dealer_cards.append(secret_card)
        if secret_card.number == 'A':
            self.dealer_a_number += 1

        # Draw the showed card for dealer
        card = self.game_pack.pop()
        # Change one of 'A' points to 1 if both first cards are 'A'
        if card.number == 'A' and self.dealer_total == 11:
            self.dealer_total += 1
            card.number = '1'
        else:
            self.dealer_total += card.points
        self.dealer_cards.append(card)
        if card.number == 'A':
            self.dealer_a_number += 1

        # Draw first 2 cards for player
        for _ in range(2):
            card = self.game_pack.pop()
            # Change one of 'A' points to 1 if both first cards are 'A'
            if card.number == 'A' and self.player_total == 11:
                self.player_total += 1
                card.number = '1'
            else:
                self.player_total += card.points
            self.player_cards.append(card)
            if card.number == 'A':
                self.player_a_number += 1

        if self.player_total == self.dealer_total == 21:
            self.draw_event()
        elif self.player_total == 21:
            self.blackjack_event_player()
        elif self.dealer_total == 21:
            self.blackjack_event_dealer()


    async def create_whitejack_embed(self, state: Optional[str] = None) -> discord.Embed:
        """ Creates an embed for the WhiteJack game.
        :param state: The current state of the game. [Optional] """

        player_name = self.player.display_name
        current_time = await utils.get_time_now()
        if state:
            state = state.lower()

        title_state: str = EmbedStateEnum.__annotations__.get(state)
        color: discord.Color = EmbedColorEnum.__annotations__.get(state)

        if state:
            title = f"{state.title()} - {player_name} {title_state} ? leaves 🍃"
        else:
            title: str = f"{player_name}'s game ({self.bet} leaves 🍃)"

        embed: discord.Embed = discord.Embed(
            title=title,
            color=self.player.color if not color else color,
            timestamp=current_time
        )

        embed.add_field(name="Player", value=self.player_info())
        embed.add_field(name="Dealer", value=self.dealer_info())

        embed.set_author(name=f"{player_name}", icon_url=self.player.display_avatar)
        embed.set_footer(text=f"Whitejack: {self.current_money}łł")

        return embed


    # Return a string with player's cards and total of points
    def player_info(self):
        var = []
        for i in self.player_cards:
            var.append(i.symbol)
        return ' '.join(var) + '\n' + f'**Total: {self.player_total}**'

    # Return a string with dealer's cards and total of points
    def dealer_info(self):
        var = []
        for i in self.dealer_cards:
            var.append(i.symbol)
        return ' '.join(var) + '\n' + f'**Total: {self.dealer_total_showed}**'


    def draw_event(self) -> None:
        pass
    
    def blackjack_event_player(self) -> None:
        pass

    def blackjack_event_dealer(self) -> None:
        pass