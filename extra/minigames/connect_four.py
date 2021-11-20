import asyncio
import random
from functools import partial
from typing import Optional, Union, Tuple, List

import discord
import emojis
from discord.ext import commands
from discord.ext.commands import guild_only

from extra.slothclasses.player import Player

from ..constants import Emojis

NUMBERS = list(Emojis.number_emojis.values())
CROSS_EMOJI = Emojis.incident_unactioned

Coordinate = Optional[Tuple[int, int]]
EMOJI_CHECK = Union[discord.Emoji, str]


class Game:
    """ A class for the sConnect 4 Game."""

    def __init__(
        self,
        client: commands.Bot,
        channel: discord.TextChannel,
        player1: discord.Member,
        player2: Optional[discord.Member],
        tokens: List[str],
        size: int = 7
    ) -> None:
        """ Class init method. """

        self.client = client
        self.channel = channel
        self.player1 = player1
        self.player2 = player2 or AI(self.client, game=self)
        self.tokens = tokens

        self.grid = self.generate_board(size)
        self.grid_size = size

        self.unicode_numbers = NUMBERS[:self.grid_size]

        self.message = None

        self.player_active = None
        self.player_inactive = None
        self.last_move: str = None # Last piece played, the string emoji

    @staticmethod
    def generate_board(size: int) -> List[List[int]]:
        """ Generate the connect 4 game board.
        :param size: The size of the board. """

        return [[0 for _ in range(size)] for _ in range(size)]

    async def print_grid(self) -> None:
        """ Formats and outputs the Connect Four grid to the channel. """

        title = (
            f"__Connect 4__: `{self.player1.display_name}`"
            f" VS `{self.client.user.display_name if isinstance(self.player2, AI) else self.player2.display_name}`"
        )

        rows = [" ".join(self.tokens[s] for s in row) for row in self.grid]
        first_row = " ".join(x for x in NUMBERS[:self.grid_size])
        formatted_grid = "\n".join([first_row] + rows)

        if not self.message or not (embeds := self.message.embeds):
            embed = discord.Embed(title=title, description=formatted_grid)
        else:
            embed = embeds[0]
            embed.title = title
            embed.description = formatted_grid


        if self.message:
            self.message = await self.message.edit(embed=embed)
        else:
            self.message = await self.channel.send(content="**Loading...**")
            for emoji in self.unicode_numbers:
                await self.message.add_reaction(emoji)
            await self.message.add_reaction(CROSS_EMOJI)
            self.message = await self.message.edit(content=None, embed=embed)

    async def game_over(self, action: str, player1: discord.User, player2: discord.User) -> None:
        """ Sends a message when the game is over, telling who won.
        :param action: The action of the game. (win/draw/quit)
        :param player1: The player 1. (always the winner)
        :param player2? The player 2. """

        embed = self.message.embeds[0]

        if action == "win":
            embed.color = discord.Color.green()
            embed.set_field_at(0, name="__Game State__", value=f"{player1.mention} won!")
            await self.message.reply(f"**Game Over! {player1.mention} won against {player2.mention}!**")
        elif action == "draw":
            embed.color = discord.Color.orange()
            embed.set_field_at(0, name="__Game State__", value="The game has drawn!")
            await self.message.reply(f"**Game Over! {player1.mention} {player2.mention} It's A Draw 🎉**")
        elif action == "quit":
            embed.color = int("ffffff", 16)
            embed.set_field_at(0, name="__Game State__", value=f"{player1.mention} surrendered!")

            await self.message.reply(f"**{self.player_active.mention} surrendered. Game over!**")
        await self.message.edit(embed=embed)
        try:
            await self.message.clear_reactions()
        except:
            pass
        await self.print_grid()

    async def start_game(self) -> None:
        """ Begins the game. """

        self.player_active, self.player_inactive = self.player1, self.player2

        while True:
            await self.print_grid()

            if isinstance(self.player_active, AI):
                coords = self.player_active.play()
                if not coords:
                    await self.game_over(
                        "draw",
                        self.client.user if isinstance(self.player_active, AI) else self.player_active,
                        self.client.user if isinstance(self.player_inactive, AI) else self.player_inactive,
                    )
                else:
                    column_num = coords[1]
                    self.last_move = NUMBERS[column_num]
                    
            else:
                coords = await self.player_turn()

            if not coords:
                return

            if self.check_win(coords, 1 if self.player_active == self.player1 else 2):
                await self.game_over(
                    "win",
                    self.client.user if isinstance(self.player_active, AI) else self.player_active,
                    self.client.user if isinstance(self.player_inactive, AI) else self.player_inactive,
                )
                return

            self.player_active, self.player_inactive = self.player_inactive, self.player_active

    def predicate(self, reaction: discord.Reaction, user: discord.Member) -> bool:
        """ The predicate to check for the player's reaction.
        :param reaction: The reaction to check.
        :param user: The user who reacted. """

        return (
            reaction.message.id == self.message.id
            and user.id == self.player_active.id
            and str(reaction.emoji) in (*self.unicode_numbers, CROSS_EMOJI)
        )

    async def player_turn(self) -> Coordinate:
        """ Initiates the player's turn. """

        embed = self.message.embeds[0]
        embed.color = self.player_active.color
        embed.clear_fields()
        embed.add_field(name="__Game State__", value=f"{self.player_active.mention}, it's your turn! React with the column you want to place your token in.")
        if self.last_move:
            embed.add_field(name="__Last Move__", value=f"Last piece played was: {self.last_move}", inline=False)
        self.message = await self.message.edit(embed=embed)

        player_num = 1 if self.player_active == self.player1 else 2
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", check=self.predicate, timeout=120)
            except asyncio.TimeoutError:
                embed.set_field_at(0, name="__Game State__", value=f"{self.player_active.mention}, you took too long. Game over!")
                embed.color = discord.Color.brand_red()
                self.message = await self.message.edit(embed=embed)
                return
            else:
                self.last_move = str(reaction.emoji)
                if str(reaction.emoji) == CROSS_EMOJI:
                    await self.game_over("quit", self.player_active, self.player_inactive)
                    return

                await self.message.remove_reaction(reaction, user)

                column_num = self.unicode_numbers.index(str(reaction.emoji))
                column = [row[column_num] for row in self.grid]

                for row_num, square in reversed(list(enumerate(column))):
                    if not square:
                        self.grid[row_num][column_num] = player_num
                        return row_num, column_num
                message = await self.channel.send(f"Column {column_num + 1} is full. Try again")

    def check_win(self, coords: Coordinate, player_num: int) -> bool:
        """ Checks whether placing a piece in a specific coordinate would make the player win.
        :param coords: The coordinates of the recently put piece.
        :param player_num: The player number. (1/2) """

        vertical = [(-1, 0), (1, 0)]
        horizontal = [(0, 1), (0, -1)]
        forward_diag = [(-1, 1), (1, -1)]
        backward_diag = [(-1, -1), (1, 1)]
        axes = [vertical, horizontal, forward_diag, backward_diag]

        for axis in axes:
            counters_in_a_row = 1  # The initial counter that is compared to
            for (row_incr, column_incr) in axis:
                row, column = coords
                row += row_incr
                column += column_incr

                while 0 <= row < self.grid_size and 0 <= column < self.grid_size:
                    if self.grid[row][column] == player_num:
                        counters_in_a_row += 1
                        row += row_incr
                        column += column_incr
                    else:
                        break
            if counters_in_a_row >= 4:
                return True
        return False


class AI:
    """ The Computer Player class for the Single-Player games. """

    def __init__(self, client: commands.Bot, game: Game) -> None:
        """ Class init method. """

        self.game = game
        self.mention = client.user.mention
        self.color = client.user.color

    def get_possible_places(self) -> List[Coordinate]:
        """ Gets all the coordinates where the AI could possibly place a counter. """

        possible_coords = []
        for column_num in range(self.game.grid_size):
            column = [row[column_num] for row in self.game.grid]
            for row_num, square in reversed(list(enumerate(column))):
                if not square:
                    possible_coords.append((row_num, column_num))
                    break
        return possible_coords

    def check_ai_win(self, coord_list: List[Coordinate]) -> Optional[Coordinate]:
        """ Check AI win.

        Check if placing a counter in any possible coordinate would cause the AI to win
        with 10% chance of not winning and returning None.
        :param coord_list: The list of coordinates. """

        if random.randint(1, 10) == 1:
            return
        for coords in coord_list:
            if self.game.check_win(coords, 2):
                return coords

    def check_player_win(self, coord_list: List[Coordinate]) -> Optional[Coordinate]:
        """ Check Player win.

        Check if placing a counter in possible coordinates would stop the player
        from winning with 25% of not blocking them  and returning None.
        :param coord_list: The list of coordinates. """

        if random.randint(1, 4) == 1:
            return
        for coords in coord_list:
            if self.game.check_win(coords, 1):
                return coords

    @staticmethod
    def random_coords(coord_list: List[Coordinate]) -> Coordinate:
        """ Picks a random coordinate from the possible ones.
        :param coord_list: The list of coordinates. """

        return random.choice(coord_list)

    def play(self) -> Union[Coordinate, bool]:
        """ Plays for the AI.

        Gets all possible coords, and determins the move:
        1. coords where it can win.
        2. coords where the player can win.
        3. Random coord
        The first possible value is choosen. """

        possible_coords = self.get_possible_places()

        if not possible_coords:
            return False

        coords = (
            self.check_ai_win(possible_coords)
            or self.check_player_win(possible_coords)
            or self.random_coords(possible_coords)
        )

        row, column = coords
        self.game.grid[row][column] = 2
        return coords


class ConnectFour(commands.Cog):
    """ Category for the Connect Four game. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.games: List[Game] = []
        self.waiting: List[discord.Member] = []

        self.tokens = [":white_circle:", ":blue_circle:", ":red_circle:"]

        self.max_board_size = 9
        self.min_board_size = 5

    async def check_author(self, ctx: commands.Context, board_size: int) -> bool:
        """ Checks whether the requester is free and the board size is correct.
        :param ctx: The context.
        :param board_size: The size of the game board. """

        if self.already_playing(ctx.author):
            await ctx.send("You're already playing a game!")
            return False

        if ctx.author in self.waiting:
            await ctx.send("You've already sent out a request for a player 2")
            return False

        if not self.min_board_size <= board_size <= self.max_board_size:
            await ctx.send(
                f"{board_size} is not a valid board size. A valid board size is "
                f"between `{self.min_board_size}` and `{self.max_board_size}`."
            )
            return False

        return True

    def get_player(
        self,
        ctx: commands.Context,
        announcement: discord.Message,
        reaction: discord.Reaction,
        user: discord.Member
    ) -> bool:
        """ Predicate checking the criteria for the announcement message.
        :param ctx: The context.
        :param announcement: The message.
        :param reaction: The reaction used.
        :param user: The user to get. """

        if self.already_playing(ctx.author):  # If they've joined a game since requesting a player 2
            return True  # It's dealt with later on

        if (
            user.id not in (ctx.me.id, ctx.author.id)
            and str(reaction.emoji) == Emojis.hand_raised
            and reaction.message.id == announcement.id
        ):
            if self.already_playing(user):
                self.client.loop.create_task(ctx.send(f"{user.mention} You're already playing a game!"))
                self.client.loop.create_task(announcement.remove_reaction(reaction, user))
                return False

            if user in self.waiting:
                self.client.loop.create_task(ctx.send(
                    f"{user.mention} Please cancel your game first before joining another one."
                ))
                self.client.loop.create_task(announcement.remove_reaction(reaction, user))
                return False

            return True

        if (
            user.id == ctx.author.id
            and str(reaction.emoji) == CROSS_EMOJI
            and reaction.message.id == announcement.id
        ):
            return True
        return False

    def already_playing(self, player: discord.Member) -> bool:
        """ Checks whether someone is already in a game.
        :param player: The person to check. """

        return any(player in (game.player1, game.player2) for game in self.games)

    @staticmethod
    def check_emojis(
        e1: EMOJI_CHECK, e2: EMOJI_CHECK
    ) -> Tuple[bool, Optional[str]]:
        """ Validates the emojis the user put.
        :param e1: The first emoji.
        :param e2: The second emoji. """

        if isinstance(e1, str) and emojis.count(e1) != 1:
            return False, e1
        if isinstance(e2, str) and emojis.count(e2) != 1:
            return False, e2
        return True, None

    async def _play_game(
        self,
        ctx: commands.Context,
        user: Optional[discord.Member],
        board_size: int,
        emoji1: str,
        emoji2: str
    ) -> None:
        """ Helpers for playing a game of connect four.
        :param ctx: The context.
        :param user: The user user playing. [Optional]
        :param board_size: The size of the game board.
        :param emoji1: The first emoji.
        :param emoji2: The second emoji. """

        self.tokens = [":white_circle:", str(emoji1), str(emoji2)]
        game = None  # If game fails to intialize in try...except

        try:
            game = Game(self.client, ctx.channel, ctx.author, user, self.tokens, size=board_size)
            self.games.append(game)
            await game.start_game()
            self.games.remove(game)
        except Exception:
            # End the game in the event of an unforeseen error so the players aren't stuck in a game
            await ctx.send(f"{ctx.author.mention} {user.mention if user else ''} An error occurred. Game failed.")
            if game in self.games:
                self.games.remove(game)
            raise

    @guild_only()
    @Player.poisoned()
    @commands.group(
        invoke_without_command=True,
        aliases=("4inarow", "connect4", "connectfour", "c4"),
        case_insensitive=True
    )
    async def connect_four(
        self,
        ctx: commands.Context,
        member: discord.Member = None,
        board_size: int = 7,
        emoji1: EMOJI_CHECK = "\U0001f535",
        emoji2: EMOJI_CHECK = "\U0001f534"
    ) -> None:
        """ Plays the classic game of Connect Four with someone!

        Sets up a message waiting for someone else to react and play along.
        The game will start once someone has reacted.
        All inputs will be through reactions.
        :param ctx: The context.
        :param board_size: The size of the game board.
        :param emoji1: The first emoji.
        :param emoji2: The second emoji. """

        if not member or member.bot:
            return await self.ai(ctx)

        if member.id == ctx.author.id:
            return await ctx.send("**You cannot play against yourself!**")

        check, emoji = self.check_emojis(emoji1, emoji2)
        if not check:
            raise commands.EmojiNotFound(emoji)

        check_author_result = await self.check_author(ctx, board_size)
        if not check_author_result:
            return

        if self.already_playing(ctx.author):
            return

        if self.already_playing(member):
            return await ctx.reply("**This member is already playing!**")

        await self._play_game(ctx, member, board_size, str(emoji1), str(emoji2))

    # @guild_only()
    # @connect_four.command(aliases=("bot", "computer", "cpu"))

    async def ai(
        self,
        ctx: commands.Context,
        board_size: int = 7,
        emoji1: EMOJI_CHECK = "\U0001f535",
        emoji2: EMOJI_CHECK = "\U0001f534"
    ) -> None:
        """ Plays  Connect Four against a computer player.
        :param ctx: The context.
        :param board_size: The size of the game board.
        :param emoji1: The first emoji.
        :param emoji2: The second emoji. """

        check, emoji = self.check_emojis(emoji1, emoji2)
        if not check:
            raise commands.EmojiNotFound(emoji)

        check_author_result = await self.check_author(ctx, board_size)
        if not check_author_result:
            return

        await self._play_game(ctx, None, board_size, str(emoji1), str(emoji2))