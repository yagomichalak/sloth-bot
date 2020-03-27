import discord
from discord.ext import commands
import asyncio
import os


class Tools(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Tools cog is ready!')

    # Countsdown from a given number
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def count(self, ctx, amount=0):
        await ctx.message.delete()
        if amount > 0:
            msg = await ctx.send(f'**{amount}**')
            await asyncio.sleep(1)
            for x in range(int(amount) - 1, -1, -1):
                await msg.edit(content=f'**{x}**')
                await asyncio.sleep(1)
            await msg.edit(content='**Done!**')
        else:
            await ctx.send('Invalid parameters!')
    
    # Bot leaves
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx, bot: str =  None):
        guild = ctx.message.guild
        voice_client = guild.voice_client

        if voice_client:
            await voice_client.disconnect()
            if bot == 'the bot':
                return
            await ctx.send('**Disconnected!**')
        else:
            await ctx.send("**I'm not even in a channel, lol!**")
            
            
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reproduce(self, ctx, audio: str = None):
        await ctx.message.delete()
        voice = ctx.message.author.voice
        voice_client = ctx.message.guild.voice_client
        if not audio:
            return await ctx.send("**Inform an audio to play!**")

        arr = os.listdir(f'tts')
        for a in arr:
            if audio.lower() == a[:-4]:
                temp = a[:-4]
                break
        else:
            return await ctx.send("**No audios with that name were found!**")

        if voice is None:
            return await ctx.send("**You're not in a voice channel**")
        if voice_client is None:
            voicechannel = discord.utils.get(ctx.guild.channels, id=voice.channel.id)
            vc = await voicechannel.connect()
            vc.play(discord.FFmpegPCMAudio(f"tts/{temp}.mp3"), after=lambda e: self.client.loop.create_task(self.leave(ctx, 'the bot')))

        else:
            await ctx.send("**I'm already in a voice channel!**")


def setup(client):
    client.add_cog(Tools(client))
