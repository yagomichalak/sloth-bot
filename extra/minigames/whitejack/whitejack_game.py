import asyncio
import discord
from discord.ext import commands
from extra.minigames.blackjack.blackjack_db import BlackJackDB
from mysqldb import *
import copy
import random
from ..blackjack.blackjack_db import BlackJackDB
from .create_cards_pack import wj_pack
from typing import List, Union, Optional, Dict
from .enums import EmbedColorEnum, EmbedStateEnum
from extra import utils


cogs: List[commands.Cog] = [
	BlackJackDB
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
        self.cog = self.client.get_cog('SlothCurrency')
        self.doubled = False
        self.blackjack = False

        # Player info
        self.player = player
        self.player_total = 0
        self.player_a_number = 0
        self.player_cards: List = []

        # Dealer info
        self.dealer_total_showed = '`?`'
        self.dealer_total = 0
        self.dealer_a_number = 0
        self.dealer_cards: List = []

        self.state = None
        self.title = f"**Bet: {self.bet} leaves 🍃"
        self.status = 'in game'
        self.game_pack: List = copy.deepcopy(wj_pack)
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

        print("haha")
        if self.player_total == self.dealer_total == 21:
            self.draw_event()
        elif self.player_total == 21:
            self.blackjack_event_player()
        elif self.dealer_total == 21:
            self.blackjack_event_dealer()

    # FOR DEALER
    # Verify if exist and change "A" card value if the value of points it's over 21,
    # if "A" card exist and changed value it's less than 22 return True, otherwise return False
    def change_a_value_dealer(self) -> bool:
        for card in self.dealer_cards:
            if card.number == 'A':
                self.dealer_total -= 10
                card.number = '1'
            if self.dealer_total <= 21:
                return True
        return False

    # FOR PLAYER
    # Verify if exist and change "A" card value if the value of points it's over 21,
    # if "A" card exist and changed value it's less than 22 return True, otherwise return False
    def change_a_value_player(self) -> bool:
        for card in self.player_cards:
            if card.number == 'A':
                self.player_total -= 10
                card.number = '1'
            if self.player_total <= 21:
                return True
        return False

    async def create_whitejack_embed(self) -> discord.Embed:
        """ Creates an embed for the WhiteJack game. """

        player_name = self.player.display_name
        current_time = await utils.get_time_now()
        state = self.state
        if state:
            state = state.lower()
            color: discord.Color = getattr(EmbedColorEnum, state).value
        else:
            color = None

        if state:
            title = self.title
        else:
            title: str = f"Bet: {self.bet} leaves 🍃"

        embed: discord.Embed = discord.Embed(
            title=title,
            color=self.player.color if not color else color,
            timestamp=current_time
        )

        embed.add_field(name="__Player__", value=self.player_info())
        embed.add_field(name="__Dealer__", value=self.dealer_info())

        embed.set_author(name=player_name, icon_url=self.player.display_avatar)
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

    # Show dealer's hidden card and total of points
    def dealer_final_show(self):
        secret_card = self.dealer_cards[0]
        if secret_card.number == '1':
            secret_card.number = 'A'
        secret_card.symbol = secret_card.card_type
        
        self.dealer_cards[0] = secret_card
        self.dealer_total_showed = self.dealer_total

    # Action of hit a card in blackjack
    async def hit_a_card(self):
        card = self.game_pack.pop()
        self.player_cards.append(card)
        self.player_total += card.points
        if self.player_total > 21:
            if not self.change_a_value_player():
                await self.lose_event()
        elif self.player_total == 21:
            await self.stand()

    # Action of stand in blackjack
    async def stand(self):
        while self.dealer_total < 17:
            card = self.game_pack.pop()
            self.dealer_cards.append(card)
            self.dealer_total += card.points
            if self.dealer_total > 21:
                self.change_a_value_dealer()

        if self.dealer_total > 21 or self.dealer_total < self.player_total:
            await self.win_event()
        elif self.dealer_total > self.player_total:
            await self.lose_event()
        else:
            self.draw_event()

    # Action of double in blackjack
    async def double(self):

        self.doubled = True
        card = self.game_pack.pop()
        self.player_cards.append(card)
        self.player_total += card.points
        if self.player_total > 21:
            if not self.change_a_value_player():
                await self.lose_event()
                return
        await self.stand()

    # When dealer have blackjack
    def blackjack_event_dealer(self):

        self.title = f"Dealer Whitejack - You lost {int(self.bet * 0.75)} leaves 🍃"
        self.state = 'lose'
        self.blackjack = True
        self.status = 'finished'
        self.dealer_final_show()


    # When player have blackjack
    def blackjack_event_player(self):

        # Change title and end the game
        self.title = f"Player Whitejack - You won {int(self.bet * 1.5)} leaves 🍃"
        self.state = 'win'
        self.blackjack = True
        self.status = 'finished'
        self.dealer_final_show()


    # Classic win in blackjack
    async def win_event(self):
        # Increase player balance with bet * 2 if he win

        if self.doubled:
            bet_var: str = int(self.bet * 2)
        else:
            bet_var: str = int(self.bet)

        # Change title and end the game
        self.title = f"Win - You won {bet_var} leaves 🍃"
        self.state = 'win'
        self.status = 'finished'
        self.dealer_final_show()

    # Surrender in blackjack
    async def surrender_event(self):
        # Change title and end the game
        
        self.title = f"Surrender - You lost {int(self.bet * 0.35)} leaves 🍃"
        self.state = 'surrender'
        self.status = 'finished'
        self.dealer_final_show()
        await self.insert_user_data("surrenders", self.player.id)

    async def lose_event(self):
        await self.insert_user_data(type="losses", user_id=self.player.id)

        # Change title and end the game
        if self.doubled:
            bet_var: str = int(self.bet * 2)
        else:
            bet_var: str = int(self.bet)

        self.title = f"Lose - You lost {bet_var} leaves 🍃"
        self.state = 'lose'
        self.status = 'finished'
        self.dealer_final_show()

    # Draw in blackjack
    def draw_event(self) -> None:
        # Refund player's leaves 🍃 if he draw

        # Change title and end the game
        self.title = f"Draw - You won 0 leaves 🍃"
        self.state = 'draw'
        self.status = 'finished'
        self.dealer_final_show()
