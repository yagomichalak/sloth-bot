import discord
from discord.ext import commands
from .buttons import TicTacToeButton, FlagsGameButton

from typing import Dict, List, Tuple
from random import randint
from extra import utils
import os

server_id: int = int(os.getenv('SERVER_ID'))

class TicTacToeView(discord.ui.View):
    """ View for the TicTacToe minigame. """

    def __init__(self, client: commands.Bot, player: discord.Member, opponent: discord.Member) -> None:
        """ Class init method. """

        super().__init__(timeout=60)
        self.client = client
        self.player = player
        self.opponent = opponent

        self.state = True

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

    async def on_timeout(self) -> None:
        self.state = False

class MoveObjectGameView(discord.ui.View):
    """ View for the MoveObject minigame. """

    columns, rows = 13, 9
    x, y = 6, 4

    def __init__(self, ctx: commands.Context, player: discord.Member) -> None:
        """ Class init method. """

        super().__init__(timeout=60)
        self.ctx = ctx
        self.player = player
        self.gg: bool = False
        self.inserted: Dict[str, Tuple[int]] = {'player': (self.x, self.y)}
        self.status: str = 'playing'

    @discord.ui.button(label='\u200b', custom_id="mo_game_left_btn", emoji="⬅️")
    async def mo_game_left_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Callback for the game's left button. """

        if self.x - 1 > 0:
            moved, gg = await self.check_player_collision(-1, 0, str(button.emoji))
            if moved is not None:
                self.x -= 1
        await self.update_embed(interaction)
        if gg:
            await self.end_game(interaction)

    @discord.ui.button(label='\u200b', custom_id="mo_game_right_btn", emoji="➡️")
    async def mo_game_right_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Callback for the game's right button. """

        if self.x + 1 < self.columns - 1:
            moved, gg = await self.check_player_collision(1, 0, str(button.emoji))
            if moved is not None:
                self.x += 1
        await self.update_embed(interaction)
        if gg:
            await self.end_game(interaction)

    @discord.ui.button(label='\u200b', custom_id="mo_game_down_btn", emoji="⬇️")
    async def mo_game_down_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Callback for the game's down button. """

        if self.y + 1 < self.rows - 1:
            moved, gg = await self.check_player_collision(0, 1, str(button.emoji))
            if moved is not None:
                self.y += 1
        await self.update_embed(interaction)
        if gg:
            await self.end_game(interaction)

    @discord.ui.button(label='\u200b', custom_id="mo_game_up_btn", emoji="⬆️")
    async def mo_game_up_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Callback for the game's up button. """

        if self.y - 1 > 0:
            moved, gg = await self.check_player_collision(0, -1, str(button.emoji))
            if moved is not None:
                self.y -= 1
        await self.update_embed(interaction)
        if gg:
            await self.end_game(interaction)

    @discord.ui.button(label='\u200b', custom_id="mo_game_surrender_btn", emoji="🏳️")
    async def mo_game_surrender_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Callback for the game's surrender button. """

        embed = interaction.message.embeds[0]

        embed.color = discord.Color.orange()
        await interaction.message.edit(content="**Noob!** 🏳️", embed=embed)
        await self.update_embed(interaction)
        self.status = 'Surrender'
        self.stop()


    async def update_embed(self, interaction: discord.Interaction) -> None:
        """ Updates the embed's state.
        :param interaction: The interaction. """

        embed = interaction.message.embeds[0]

        square = await self.make_game_square()
        square = '\n'.join(map(lambda r: ''.join(r), square))
        embed.description = square
        await interaction.message.edit(embed=embed)

    async def end_game(self, interaction: discord.Interaction) -> None:
        """ Ends the game.
        :param interaction: The interaction. """

        embed = interaction.message.embeds[0]

        embed.title = "__Victory!__"
        embed.color = discord.Color.green()
        await utils.disable_buttons(self)
        await interaction.message.edit(content="**GG, you won!**", embed=embed, view=self)
        self.status = 'Victory'
        self.stop()


    async def make_game_square(self, update: bool = False) -> str:
        """ Makes a game square with emojis.
        :param update: Whether to update the game square by putting objects in it. """

        emoji = '\u2B1B'

        simple_square = [[emoji for __ in range(self.columns)] for _ in range(self.rows)]
        square = await self.make_square_border(simple_square)
        square = await self.put_objects(square, update)
        return square

    
    async def make_square_border(self, square: List[List[str]]) -> List[List[str]]:
        """ Makes a border for the given square.
        :param square: The current state of the game square. """

        blue = ':blue_square:'

        new_list = []
        for i, row in enumerate(square):

            if i == 0 or i == len(square) - 1:
                new_row = []
                for column in row:
                    column = blue
                    new_row.append(column)

                new_list.append(new_row)
            else:
                new_row = row
                new_row[0] = blue
                new_row[-1] = blue
                new_list.append(new_row)

        return new_list

    async def put_objects(self, square: List[List[str]], update: bool) -> List[List[str]]:
        """ Puts all objects into the game square field.
        :param square: The game square field.
        :param update: Whether to update the game square by putting objects in it. """

        # List of inserted items

        # Puts player
        player = '🐸'
        x = self.x
        y = self.y
        self.inserted['player'] = (x, y, player)

        if update:
            # Puts item
            square, item_tuple = await self.insert_item(square)
            self.inserted['item'] = item_tuple

            # Puts destiny
            square, destiny_tuple = await self.insert_destiny(square)
            self.inserted['destiny'] = destiny_tuple

        for values in self.inserted.values():
            x, y, emoji = values
            square[y][x] = emoji

        return square

    async def insert_item(self, square: List[List[str]]) -> Dict[str, Tuple[int]]:
        """ Inserts the Item object.
        :param square: The current state of the game square."""

        item = '🍫'

        while True:
            rand_x = randint(2, self.columns-3)
            rand_y = randint(2, self.rows-3)
            if (rand_x, rand_y) not in self.inserted.values():
                square[rand_y][rand_x] = item
                return square, (rand_x, rand_y, item)

    async def insert_destiny(self, square: List[List[str]]) -> Dict[str, Tuple[int]]:
        """ Inserts the Destiny object.
        :param square: The current state of the game square. """

        destiny = '👩'

        while True:
            rand_x = randint(1, self.columns-2)
            rand_y = randint(1, self.rows-2)
            if (rand_x, rand_y) not in self.inserted.values():
                square[rand_y][rand_x] = destiny
                return square, (rand_x, rand_y, destiny)

    async def check_player_collision(self, xadd: int, yadd: int, emj: str) -> Dict[str, List[bool]]:
        """ Checks collision of the player with items and the destinies.
        :param xadd: The addition to apply to the X axis, in case of collision.
        :param yadd: The addition to apply to the Y axis, in case of collision.
        :param emj: The emoji of the button clicked. """

        moved = False
        gg = False

        item_x, item_y, item_emj = self.inserted['item']
        destiny_x, destiny_y, _ = self.inserted['destiny']
        player_x, player_y, _ = self.inserted['player']

        if (player_x+xadd, player_y+yadd) == (item_x, item_y):
            if emj == '⬅️':
                if item_x - 1 > 0:

                    self.inserted['item'] = (item_x+xadd, item_y+yadd, item_emj)
                    moved = True
                else:
                    moved = None

            elif emj == '➡️':
                if item_x + 1 < self.columns - 1:

                    self.inserted['item'] = (item_x+xadd, item_y+yadd, item_emj)
                    moved = True
                else:
                    moved = None

            elif emj == '⬇️':
                if item_y + 1 < self.rows - 1:

                    self.inserted['item'] = (item_x+xadd, item_y+yadd, item_emj)
                    moved = True
                else:
                    moved = None

            elif emj == '⬆️':
                if item_y - 1 > 0:

                    self.inserted['item'] = (item_x+xadd, item_y+yadd, item_emj)
                    moved = True
                else:
                    moved = None
        elif (player_x+xadd, player_y+yadd) == (destiny_x, destiny_y):
            moved = None

        if moved and (item_x+xadd, item_y+yadd) == (destiny_x, destiny_y):
            moved = True
            gg = True

        return moved, gg

class FlagsGameView(discord.ui.View):
    """ View for the FlagGame. """

    def __init__(self, ctx: commands.Context, client: commands.Bot, countries_names: List[str], flags: list, points: int, round: int, timeout_count: int = 0) -> None:
        super().__init__(timeout=30)
        self.ctx = ctx
        self.client = client
        self.flags = flags
        self.countries_names = countries_names
        self.points = points
        self.round = round
        self.cog = self.client.get_cog('Games')
        self.used = False
        self.timeout_count = timeout_count

        counter: int = 0
        for _ in range(4):
            counter += 1
            button = FlagsGameButton(style=discord.ButtonStyle.secondary, custom_id=self.countries_names[counter-1], label=self.countries_names[counter-1][:-1],  row=1)
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

class BlackJackActionView(discord.ui.View):
    """ View for the BlackJack game actions. """

    def __init__(self, client: commands.Bot, player: discord.Member) -> None:
        """ Class init method. """

        super().__init__(timeout=120)
        self.client = client
        self.player = player

    @discord.ui.button(label="hit", style=discord.ButtonStyle.blurple, custom_id="bj_hit_id")
    async def black_jack_hit_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for hitting in the BlackJack game. """

        await interaction.response.defer()

        guild_id = interaction.guild.id
        cog = self.client.get_cog('Games')

        if cog.blackjack_games.get(guild_id) is None:
            cog.blackjack_games[guild_id] = {}

        if interaction.user.id in cog.blackjack_games[guild_id]:
            current_game = cog.blackjack_games[guild_id].get(interaction.user.id)
            current_game.hit_a_card()
            if current_game.status == 'finished':
                del cog.blackjack_games[guild_id][interaction.user.id]
                await self.end_game(interaction)
            await interaction.followup.edit_message(interaction.message.id, embed=current_game.embed())
        else:
            await interaction.followup.send("**You must be in a blackjack game!**")

    @discord.ui.button(label="stand", style=discord.ButtonStyle.blurple, custom_id="bj_stand_id")
    async def black_jack_stand_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for standing in the BlackJack game. """

        await interaction.response.defer()

        guild_id = interaction.guild.id
        cog = self.client.get_cog('Games')


        if cog.blackjack_games.get(guild_id) is None:
            cog.blackjack_games[guild_id] = {}

        if interaction.user.id in cog.blackjack_games[guild_id]:
            current_game = cog.blackjack_games[guild_id].get(interaction.user.id)
            current_game.stand()
            if current_game.status == 'finished':
                del cog.blackjack_games[guild_id][interaction.user.id]
                await self.end_game(interaction)
            await interaction.followup.edit_message(interaction.message.id, embed=current_game.embed())
        else:
            await interaction.followup.send("**You must be in a blackjack game!**")

    @discord.ui.button(label="double", style=discord.ButtonStyle.blurple, custom_id="bj_double_id")
    async def black_jack_double_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for doubling in the BlackJack game. """

        await interaction.response.defer()


        player_id = interaction.user.id
        guild_id = interaction.guild.id
        cog = self.client.get_cog('Games')

        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_currency = await SlothCurrency.get_user_currency(player_id)
        player_bal = user_currency[0][1]
        print(player_bal)

        if cog.blackjack_games.get(guild_id) is None:
            cog.blackjack_games[guild_id] = {}

        # Check if player's blackjack game is active
        if interaction.user.id in cog.blackjack_games[guild_id]:
            current_game = cog.blackjack_games[guild_id].get(interaction.user.id)
            # Checks whether the player has more than 4 cards  
            if len(current_game.player_cards) > 4:
                await interaction.followup.send("**You can double only in the first three rounds!**")

            # Checks whether the player has sufficient funds for double
            elif player_bal < current_game.bet:
                await interaction.followup.send("**You have insufficient funds!**")
            else:
                current_game.double()
                if current_game.status == 'finished':
                    del cog.blackjack_games[guild_id][interaction.user.id]
                    user_currency = await SlothCurrency.get_user_currency(player_id)
                    print(user_currency[0][1])
                    await self.end_game(interaction)
                    user_currency = await SlothCurrency.get_user_currency(player_id)
                    print(user_currency[0][1])

            await interaction.followup.edit_message(interaction.message.id, embed=current_game.embed())
        else:
            await interaction.followup.send("**You must be in a blackjack game!**")

    @discord.ui.button(label="triple", style=discord.ButtonStyle.blurple, custom_id="bj_triple_id")
    async def black_jack_triple_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for doubling in the BlackJack game. """

        await interaction.response.defer()


        player_id = interaction.user.id
        guild_id = interaction.guild.id
        cog = self.client.get_cog('Games')

        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_currency = await SlothCurrency.get_user_currency(player_id)
        player_bal = user_currency[0][1]

        if cog.blackjack_games.get(guild_id) is None:
            cog.blackjack_games[guild_id] = {}

        # Check if player's blackjack game is active
        if interaction.user.id in cog.blackjack_games[guild_id]:
            current_game = cog.blackjack_games[guild_id].get(interaction.user.id)
            # Checks whether the player has more than 4 cards  
            if len(current_game.player_cards) > 4:
                await interaction.followup.send("**You can triple only in the first three rounds!**")

            # Checks whether the player has sufficient funds for triple
            elif player_bal < current_game.bet:
                await interaction.followup.send("**You have insufficient funds!**")
            else:
                current_game.triple()
                if current_game.status == 'finished':
                    del cog.blackjack_games[guild_id][interaction.user.id]
                    user_currency = await SlothCurrency.get_user_currency(player_id)
                    await self.end_game(interaction)
                    user_currency = await SlothCurrency.get_user_currency(player_id)

            await interaction.followup.edit_message(interaction.message.id, embed=current_game.embed())
        else:
            await interaction.followup.send("**You must be in a blackjack game!**")

    @discord.ui.button(label="surrender", style=discord.ButtonStyle.gray, custom_id="bj_surrender_id")
    async def black_jack_surrender_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for surrendering in the BlackJack game. """

        await interaction.response.defer()

        cog = self.client.get_cog('Games')

        guild_id = interaction.guild.id
        if cog.blackjack_games.get(guild_id) is None:
            cog.blackjack_games[guild_id] = {}

        # Check whether the player's blackjack game is active
        if interaction.user.id in cog.blackjack_games[guild_id]:
            current_game = cog.blackjack_games[guild_id].get(interaction.user.id)
            current_game.surrender_event()
            if current_game.status == 'finished':
                del cog.blackjack_games[guild_id][interaction.user.id]
                await self.end_game(interaction)

            await self.client.get_cog('SlothCurrency').update_user_money(self.player.id, int(current_game.bet * (1 - 0.35)))
            embed = current_game.embed()
            embed.color = int('ffffff', 16)
            await interaction.followup.edit_message(interaction.message.id, embed=embed)
        else:
            await interaction.followup.send("**You must be in a blackjack game!**")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.player.id == interaction.user.id

    async def end_game(self, interaction: discord.Interaction) -> None:
        """ Ends the game.
        :param interaction: The interaction. """

        await utils.disable_buttons(self)
        await interaction.followup.edit_message(interaction.message.id, view=self)
        self.stop()

    async def on_timeout(self) -> None:
        """ Puts the game status as finished when the game timeouts. """

        cog = self.client.get_cog('Games')
        current_game = cog.blackjack_games[server_id].get(self.player.id)
        if hasattr(current_game, 'status') and current_game.status == 'finished':
            del cog.blackjack_games[server_id][self.player.id]
        return
