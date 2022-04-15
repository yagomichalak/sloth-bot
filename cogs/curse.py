import discord
from discord.ext import commands
from mysqldb import *
import os
from extra.misc.curse import CurseTable

server_id = int(os.getenv('SERVER_ID', 123))


class CurseMember(CurseTable):
    """ A cog related to the 'curse a member' feature. """

    def __init__(self, client) -> None:
        """ Class initializing method. """

        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog's ready to be used. """

        print('CurseMember cog is online!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after) -> None:
        """ Event for checking whether the user who joined any voice channel
        is the cursed member, if so, the bot joins the voice channel and plays
        an earrape song. """

        # Checks whether it is the cursed member
        cursed_member = await self.get_cursed_member(member.id)
        if not cursed_member:
            return

        voice = member.voice
        voice_client = member.guild.voice_client
        if not after.channel:
            if voice_client.channel == before.channel:
                await voice_client.disconnect()

        if after.channel:
            if voice_client and after.channel:
                await voice_client.move_to(after.channel)

            else:
                voicechannel = discord.utils.get(member.guild.channels, id=voice.channel.id)
                vc = await voicechannel.connect()
                await self.play_earrape(member.id, vc)

    async def play_earrape(self, mid, vc) -> None:
        """ Plays an earrape song.
        :param mid: The member ID.
        :param vc: The voice channel that the member's currently in. """

        guild = self.client.get_guild(server_id)
        member = discord.utils.get(guild.members, id=mid)
        voice = member.voice
        if voice:
            voicechannel = discord.utils.get(guild.channels, id=voice.channel.id)
            if member in voicechannel.members:
                try:
                    vc.play(discord.FFmpegPCMAudio("earrape.mp3"), after=lambda e: self.client.loop.create_task(self.play_earrape(mid, vc)))
                except Exception:
                    pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def curse(self, ctx, member: discord.Member = None) -> None:
        """ (ADM) Curses someone by playing an earrape song in a loop whenever they join a voice channel.
        :param member: The member to curse. """

        await ctx.message.delete()
        if not member:
            return await ctx.send("**Inform a member to curse!**", delete_after=3)

        if member.voice:
            await self.is_connected(ctx)
            voicechannel = discord.utils.get(member.guild.channels, id=member.voice.channel.id)
            vc = await voicechannel.connect()
            await self.play_earrape(member.id, vc)

        await self.delete_cursed_member()
        await self.insert_cursed_member(member.id)
        await ctx.send(f"**{member} has been cursed!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def uncurse(self, ctx) -> None:
        """ (ADM) Unurses someone.
        :param member: The member to uncurse. """

        await ctx.message.delete()

        await self.is_connected(ctx)
        curse = await self.delete_cursed_member()
        if curse:
            await ctx.send(f"**The curse has been undone!**", delete_after=3)
        else:
            await ctx.send(f"**No one had been cursed!**", delete_after=3)

    async def is_connected(self, ctx) -> None:
        """ Checks whether the bot is currently connect into a voice channel,
        if so, it gets disconnected.
        :param ctx: The context. """

        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()

def setup(client):
    """ Cog's setup function. """

    client.add_cog(CurseMember(client))
