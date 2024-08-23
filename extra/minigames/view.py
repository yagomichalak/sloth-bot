# import.standard
import asyncio
import os
from functools import partial
from random import choice, randint
from typing import Any, Dict, List, Optional, Tuple

# import.thirdparty
import discord
from discord.ext import commands

# import.local
from extra import utils
from .buttons import FlagsGameButton, TicTacToeButton
from .whitejack.enums import ButtonOppositeStyleEnum, ButtonStyleEnum

# variables.id
server_id: int = int(os.getenv('SERVER_ID', 123))

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
        """ Checks whether the person who clicked the button is on their turn. """

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
        """ Class init method. """

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
        """ Checks whether the person who clicked on the button is the one who started the blackjack. """

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

class WhiteJackActionView(discord.ui.View):
    """ View for the WhiteJack game actions. """

    def __init__(self, client: commands.Bot, player: discord.Member, game: Any) -> None:
        """ Class init method. """

        super().__init__(timeout=60)
        self.client = client
        self.player = player
        self.game: Any = game
        self.cog = client.get_cog("Games")
        self.msg: discord.Message = None

    @discord.ui.button(style=discord.ButtonStyle.blurple, custom_id="wj_hit_id", emoji='👊🏻')
    async def white_jack_hit_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for hitting in the Whitejack game. """

        await interaction.response.defer()

        guild_id = interaction.guild.id
        cog = self.cog

        if cog.whitejack_games.get(guild_id) is None:
            cog.whitejack_games[guild_id] = {}

        if interaction.user.id in cog.whitejack_games[guild_id]:
            current_game = cog.whitejack_games[guild_id][interaction.user.id][self.game.session_id]
            await current_game.hit_a_card()
            if current_game.status == 'finished':
                del cog.whitejack_games[guild_id][interaction.user.id][current_game.session_id]
                return await self.end_game(interaction)
            embed = await self.game.create_whitejack_embed()
            await interaction.followup.edit_message(interaction.message.id, embed=embed)
        else:
            await interaction.followup.send("**You must be in a whitejack game!**")

    @discord.ui.button(style=discord.ButtonStyle.blurple, custom_id="wj_stand_id", emoji='✊🏻')
    async def white_jack_stand_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for standing in the Whitejack game. """

        await interaction.response.defer()

        guild_id = interaction.guild.id
        cog = self.cog


        if cog.whitejack_games.get(guild_id) is None:
            cog.whitejack_games[guild_id] = {}

        if interaction.user.id in cog.whitejack_games[guild_id]:
            current_game = cog.whitejack_games[guild_id][interaction.user.id][self.game.session_id]
            await current_game.stand()
            if current_game.status == 'finished':
                del cog.whitejack_games[guild_id][interaction.user.id][current_game.session_id]
                return await self.end_game(interaction)
            embed = await self.game.create_whitejack_embed()
            await interaction.followup.edit_message(interaction.message.id, embed=embed)
        else:
            await interaction.followup.send("**You must be in a whitejack game!**")

    @discord.ui.button(style=discord.ButtonStyle.blurple, custom_id="wj_double_id", emoji='✌🏻')
    async def white_jack_double_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for doubling in the Whitejack game. """

        await interaction.response.defer()

        player_id = interaction.user.id
        guild_id = interaction.guild.id
        cog = self.cog

        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_currency = await SlothCurrency.get_user_currency(player_id)
        player_bal = user_currency[0][1]

        if cog.whitejack_games.get(guild_id) is None:
            cog.whitejack_games[guild_id] = {}

        # Check if player's whitejack game is active
        if interaction.user.id in cog.whitejack_games[guild_id]:
            current_game = cog.whitejack_games[guild_id][interaction.user.id][self.game.session_id]
            # Checks whether the player has more than 4 cards  
            if len(current_game.player_cards) > 4:
                await interaction.followup.send("**You can double only in the first three rounds!**")

            # Checks whether the player has sufficient funds for double

            elif player_bal - current_game.bet < current_game.bet:
                await interaction.followup.send("**You have insufficient funds!**")
            else:
                await current_game.double()
                if current_game.status == 'finished':
                    del cog.whitejack_games[guild_id][interaction.user.id][current_game.session_id]
                    return await self.end_game(interaction)

            embed = await self.game.create_whitejack_embed()
            await interaction.followup.edit_message(interaction.message.id, embed=embed)
        else:
            await interaction.followup.send("**You must be in a whitejack game!**")

    @discord.ui.button(style=discord.ButtonStyle.gray, custom_id="wj_surrender_id", emoji='🏳️')
    async def white_jack_surrender_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for surrendering in the Whitejack game. """

        await interaction.response.defer()

        cog = self.cog

        guild_id = interaction.guild.id
        if cog.whitejack_games.get(guild_id) is None:
            cog.whitejack_games[guild_id] = {}

        # Check whether the player's whitejack game is active
        if interaction.user.id in cog.whitejack_games[guild_id]:
            current_game = cog.whitejack_games[guild_id][interaction.user.id][self.game.session_id]
            await current_game.surrender_event()
            if current_game.status == 'finished':
                del cog.whitejack_games[guild_id][interaction.user.id][current_game.session_id]
                return await self.end_game(interaction)

            embed = current_game.create_whitejack_embed()
            await interaction.followup.edit_message(interaction.message.id, embed=embed)
        else:
            await interaction.followup.send("**You must be in a whitejack game!**")

    async def white_jack_refresh_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for refreshing the game state. """

        await interaction.response.defer()
        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_currency = await SlothCurrency.get_user_currency(self.player.id)
        player_bal = user_currency[0][1]

        if player_bal < self.game.bet:
            return await interaction.followup.send("**You have insufficient funds!**")

        await self.cog.white_jack_callback_before(self.game.bet, self.player, interaction.guild, self.game.current_money, interaction=interaction)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Checks whether the person who clicked on the button is the one who started the whitejack. """

        return self.player.id == interaction.user.id

    async def end_game(self, ctx: discord.PartialMessageable) -> None:
        """ Ends the game.
        :param interaction: The interaction. """

        # Disable buttons
        await utils.disable_buttons(self)
        # Changes button styles
        style: discord.ButtonStyle = getattr(ButtonStyleEnum, self.game.state.lower()).value
        await utils.change_style_buttons(self, style)
        # Adds a refresh button
        await self.add_refresh_button()

        msg: discord.Message
        if isinstance(ctx, commands.Context):
            msg = await ctx.send(view=self)
        else:
            msg = await ctx.followup.edit_message(ctx.message.id, view=self)
        await self.cog.white_jack_callback_after(self, self.game, ctx.guild, msg=msg)

    async def add_refresh_button(self) -> None:
        """ Adds a button to refresh the game. """

        # Gets the button's style
        opposite_style: discord.ButtonStyle = getattr(ButtonOppositeStyleEnum, self.game.state.lower()).value

        # Makes the refresh button
        refresh_button: discord.ui.Button = discord.ui.Button(
            style=opposite_style,
            custom_id="wj_refresh_id",
            emoji="🔃"
        )
        # Attaches the callback to the button
        refresh_button.callback = partial(self.white_jack_refresh_button, refresh_button)

        # Adds the button into the view
        self.add_item(refresh_button)

    async def on_timeout(self) -> None:
        """ Puts the game status as finished when the game timeouts. """

        cog = self.cog
        if player_games := cog.whitejack_games[server_id].get(self.player.id):
            if current_game := player_games.get(self.game.session_id):
                if hasattr(current_game, 'status') and current_game.status == 'finished':
                    del cog.whitejack_games[server_id][self.player.id][current_game.session_id]
                else:
                    SlothCurrency = self.client.get_cog('SlothCurrency')
                    await SlothCurrency.update_user_money(self.player.id, -self.game.bet)
        
        if self.msg:
            await utils.disable_buttons(self)
            await self.msg.edit(view=self)

        return

class MemoryGameView(discord.ui.View):
    """ View for the Memory game. """

    emojis: List[str] = [
        '🤪', '<:Classypepe:532302844657795072>', '<:leoblabla:978481579590570034>',
        '<:peepoGiveloveKing:755691944247689236>', '<:peepoQueen:757105478714130512>'
    ]

    def __init__(self, client: commands.Bot, member: discord.Member, timeout: Optional[float] = 180) -> None:
        """ Class init method. """

        super().__init__(timeout=timeout)

        self.client = client
        self.member = member
        self.cog = client.get_cog("Games")
        self.button_map: Dict[int, List[discord.Button]] = {}
        self.value: bool = False

        # Emoji info
        self.emoji: str = self.get_random_emoji()
        self.emojis_count: int = 4

        # Card info
        self.generated_cards = []
        self.selected_cards = []
        self.generate_cards()

        # Game info
        self.lives: int = 3
        self.right_answers: int = 0
        self.level: int = 1

    async def callback(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Callback for the button. """

        content = None
        custom_id = button.custom_id
        y, x = custom_id.replace('memory:', '').split('x')
        selected_card = (x, y)
        next_level: bool = False

        if selected_card in self.generated_cards:
            self.selected_cards.append(selected_card)
            button.style = discord.ButtonStyle.green
            button.emoji = self.emoji
            self.right_answers += 1
        else:
            self.lives -= 1
            button.style = discord.ButtonStyle.red
        button.disabled = True

        if len(self.selected_cards) == len(self.generated_cards):
            await utils.disable_buttons(self)
            content = f"**Level `{self.level}` passed!** 🎊"
            next_level = True
        else:
            if self.lives == 0:
                content = f"**Level `{self.level}` lost!** ❌"
                await utils.disable_buttons(self)
                await self.update_game_data()
                self.stop()

        if not content:
            content = self.get_content()

        await interaction.response.edit_message(content=content, view=self)
        if next_level:
            await asyncio.sleep(1.5)
            await self.next_level(interaction.message)

    def get_content(self) -> str:
        """ Returns the game's message content. """

        return f"{self.lives}❤ | {self.right_answers}/{len(self.generated_cards)}✅ (`Lvl {self.level}`)"

    def get_random_emoji(self, new: bool = False) -> str:
        """ Gets a random emoji from the emojis list.
        :param new: Whether to get a non-repeated emoji. """

        while True:
            emoji = choice(self.emojis)
            if new and len(self.emojis) > 1:
                if new == self.emoji:
                    continue
            return emoji

    def generate_cards(self) -> None:
        """ Generates random cards """

        # Generates the 5x5
        for i in range(5):
            for ii in range(5):
                button = discord.ui.Button(
                    label="\u200b", style=discord.ButtonStyle.blurple, row=i,
                    custom_id=f"memory:{i}x{ii}", disabled=True
                )
                button.callback = partial(self.callback, button)
                if self.button_map.get(i):
                    self.button_map[i].append(button)
                else:
                    self.button_map[i] = [button]

        # Generates X flagged cards
        self.generated_cards.clear()
        for _ in range(self.emojis_count):
            while True:
                x, y = randint(0, 4), randint(0, 4)
                button = self.button_map[y][x]
                if button.emoji is None:
                    button.emoji = self.emoji
                    self.generated_cards.append((str(x), str(y)))
                    break
                continue

        # Adds all buttons into the view
        self.clear_items()
        for buttons in self.button_map.values():
            for button in buttons:
                self.add_item(button)


    async def next_level(self, message: discord.Message) -> None:
        """ Updates the view's state for the next game level.
        :param message: The original game message. """

        self.level += 1
        # Changes game state every 5 turns
        if self.level % 5 == 0:
            self.emoji = self.get_random_emoji(new=True)
            # Gives 1 life point for each level multiple of 5
            if self.lives != 3:
                self.lives += 1

        if self.level % 10 == 0:
            if self.emojis_count < 10:
                self.emojis_count += 1

        # Reset game state
        self.reset_game_status()
        self.generate_cards()
        content = self.get_content()
        await message.edit(content=content, view=self)
        await asyncio.sleep(2)
        # Enables buttons and removes emojis
        await utils.enable_buttons(self)
        await utils.remove_emoji_buttons(self)
        # Edits message
        await message.edit(view=self)

    async def update_game_data(self) -> None:
        """ Updates the player's data in the database. """

        current_ts = await utils.get_timestamp()
        memory_member = await self.cog.get_memory_member(self.member.id)
        if not memory_member:
            return await self.cog.insert_memory_member(self.member.id, self.level-1, current_ts)

        if self.level - 1 > memory_member[1]:
            await self.cog.update_memory_member(self.member.id, self.level-1, current_ts)

    def reset_game_status(self) -> None:
        """ Resets the game status. """

        self.right_answers = 0
        self.button_map.clear()
        self.selected_cards.clear()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Checks whether the user can interact with the buttons. """

        return interaction.user.id == self.member.id

    async def on_timeout(self) -> None:
        """ Runs when the game timeouts. """

        self.value = None
