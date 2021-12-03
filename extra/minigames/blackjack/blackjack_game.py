import discord
from discord.ext import commands

import copy
import random


class BlackJackGame:
    """ Class for the BlackJack game. """

    def __init__(self, client: commands.Bot, bet: int, player: discord.Member, player_cards: list, dealer_cards: list,
                 game_pack: list, guild_id: int) -> None:
        """ Class init method. """

        self.client = client

        # Initial settings for a blackjack game
        # Player's bet
        self.bet = bet
        self.guild_id = guild_id
        self.doubled = False

        # Player info
        self.player = player
        self.player_name = player.display_name
        self.player_id = player.id
        self.player_cards = player_cards
        self.player_total = 0
        self.player_a_number = 0

        # Dealer info
        self.dealer_cards = dealer_cards
        self.dealer_total_showed = '?'
        self.dealer_total = 0
        self.dealer_a_number = 0

        # Game title and status
        self.title = f"**{self.player_name}**'s game ({self.bet} leaves 🍃)"
        self.status = 'in game'
        self.color = self.player.color

        # Copy and shuffle standard 52 cards deck
        self.game_pack = copy.deepcopy(game_pack)
        random.shuffle(self.game_pack)

        # Draw first 2 cards for player
        for i in range(2):
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

        # Draw first 2 cards for dealer
        # Draw the hidden card for dealer
        secret_card = self.game_pack.pop()
        secret_card.symbol = '`?`'
        self.dealer_total += secret_card.points
        dealer_cards.append(secret_card)
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
        dealer_cards.append(card)
        if card.number == 'A':
            self.dealer_a_number += 1

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

    # Create the representation of blackjack game in a embed
    def embed(self):
        embed = discord.Embed(title=self.title, color=self.color)
        embed.add_field(name='**You**', value=self.player_info(), inline=True)
        embed.add_field(name='**Dealer**', value=self.dealer_info(), inline=True)
        embed.set_author(name=self.player, icon_url=self.player.display_avatar)
        embed.set_footer(text='Game mode: Blackjack')
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
        secret_card.symbol = '`' + secret_card.number + secret_card.card_type + '`'
        
        self.dealer_cards[0] = secret_card
        self.dealer_total_showed = self.dealer_total

    # Action of hit a card in blackjack
    def hit_a_card(self):
        card = self.game_pack.pop()
        self.player_cards.append(card)
        self.player_total += card.points
        if self.player_total > 21:
            if not self.change_a_value_player():
                self.lose_event()
        elif self.player_total == 21:
            self.stand()

    # Action of stand in blackjack
    def stand(self):
        while self.dealer_total < 17:
            card = self.game_pack.pop()
            self.dealer_cards.append(card)
            self.dealer_total += card.points
            if self.dealer_total > 21:
                self.change_a_value_dealer()

        if self.dealer_total > 21 or self.dealer_total < self.player_total:
            self.win_event()
        elif self.dealer_total > self.player_total:
            self.lose_event()
        else:
            self.draw_event()

    # Action of double in blackjack
    def double(self):

        SlothCurrency = self.client.get_cog('SlothCurrency')
        self.client.loop.create_task(SlothCurrency.update_user_money(self.player_id, -self.bet))

        self.doubled = True
        card = self.game_pack.pop()
        self.player_cards.append(card)
        self.player_total += card.points
        if self.player_total > 21:
            if not self.change_a_value_player():
                self.lose_event()
                return
        self.stand()

    # When player have blackjack
    def blackjack_event_dealer(self):
        SlothCurrency = self.client.get_cog('SlothCurrency')
        self.client.loop.create_task(SlothCurrency.update_user_money(self.player_id, int(self.bet * 0.5)))

        self.title = f"Dealer blackjack - **{self.player_name}** lost {int(self.bet * 0.5)} leaves 🍃"
        self.status = 'finished'
        self.color = discord.Color.brand_red()
        self.dealer_final_show()

    # When player have blackjack
    def blackjack_event_player(self):
        # Increase player balance with bet * 2.5 if he hit blackjack
        SlothCurrency = self.client.get_cog('SlothCurrency')
        self.client.loop.create_task(SlothCurrency.update_user_money(self.player_id, int(self.bet * 2.5)))

        # Change title and end the game
        self.title = f"Blackjack - **{self.player_name}** won {int(self.bet * 1.5)} leaves 🍃"
        self.status = 'finished'
        self.color = discord.Color.green()
        self.dealer_final_show()

    # Classic win in blackjack
    def win_event(self):
        # Increase player balance with bet * 2 if he win

        SlothCurrency = self.client.get_cog('SlothCurrency')

        match_bal = self.bet
        # se o player dobrou
        if self.doubled:
            # se ele ganhou com 21
            if self.player_total == 21:
                match_bal += self.bet * 2.5
            else:
                match_bal += self.bet * 2
        else:
            # ganhou normal com 21
            if self.player_total == 21:
                match_bal += self.bet * 1.5
            else:
                match_bal += self.bet

        self.client.loop.create_task(SlothCurrency.update_user_money(self.player_id, int(match_bal)))

        # Change title and end the game
        self.title = f"Win - **{self.player_name}** won {self.bet} leaves 🍃"
        self.status = 'finished'
        self.color = discord.Color.green()
        self.dealer_final_show()

    # Surrender in blackjack
    def surrender_event(self):
        # Change title and end the game
        
        self.title = f"Surrender - **{self.player_name}** lost {int(self.bet * 0.40)} leaves 🍃"
        self.color = int("ffffff", 16)
        self.status = 'finished'
        self.dealer_final_show()

    def lose_event(self):
        # Change title and end the game

        self.title = f"Lose - **{self.player_name}** lost {self.bet} leaves 🍃"
        self.color = discord.Color.brand_red()
        self.status = 'finished'
        self.dealer_final_show()

    # Draw in blackjack
    def draw_event(self):
        # Refund player's leaves 🍃 if he draw

        SlothCurrency = self.client.get_cog('SlothCurrency')
        self.client.loop.create_task(SlothCurrency.update_user_money(self.player_id, int(self.bet)))

        # Change title and end the game
        self.title = f"Draw - **{self.player_name}** won 0 leaves 🍃"
        self.status = 'finished'
        self.color = discord.Color.orange()
        self.dealer_final_show()
