import discord
from discord.ext import commands
from .player import Player


class SlothClassGeneralCommands(commands.Cog):

    def __init__(self, client) -> None:
        self.client  = client


    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @Player.not_ready()
    async def hug(self, ctx, *, member: discord.Member = None) -> None:
        """ Hugs someone. """
        
        pass
    
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @Player.not_ready()
    async def kiss(self, ctx, *, member: discord.Member = None) -> None:
        """ Kisses someone. """

        pass

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @Player.not_ready()
    async def slap(self, ctx, *, member: discord.Member = None) -> None:
        """ Slaps someone. """

        pass

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @Player.not_ready()
    async def honeymoon(self, ctx, *, member: discord.Member = None) -> None:
        """ Celebrates a honey moon with your partner. """

        pass