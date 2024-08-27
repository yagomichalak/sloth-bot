# import.standard
import enum

# import.thirdparty
import discord

class EmbedColorEnum(enum.Enum):
    """ Class for the WhiteJack's embed's color enum. """

    win: discord.Color = discord.Color.green()
    lose: discord.Color = discord.Color.red()
    draw: discord.Color = discord.Color.yellow()
    surrender: discord.Color = int("ffffff", 16)

class EmbedStateEnum(enum.Enum):
    """ Class for the WhiteJack's embed's title enum. """

    win: str = 'won'
    lose: str = 'lost'
    draw: str = 'draw'
    surrender: str = 'surrendered'

class ButtonStyleEnum(enum.Enum):
    """ Class for the WhiteJack's button style enum. """

    win: discord.ButtonStyle = discord.ButtonStyle.success
    lose: discord.ButtonStyle = discord.ButtonStyle.danger
    draw: discord.ButtonStyle = discord.ButtonStyle.blurple
    surrender: discord.ButtonStyle = discord.ButtonStyle.gray

class ButtonOppositeStyleEnum(enum.Enum):
    """ Class for the WhiteJack's button opposite style enum. """

    win: discord.ButtonStyle = discord.ButtonStyle.danger
    lose: discord.ButtonStyle = discord.ButtonStyle.success
    draw: discord.ButtonStyle = discord.ButtonStyle.gray
    surrender: discord.ButtonStyle = discord.ButtonStyle.blurple