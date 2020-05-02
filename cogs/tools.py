import discord
from discord.ext import commands
import asyncio
from gtts import gTTS
allowed_roles = [474774889778380820, 574265899801116673, 497522510212890655, 588752954266222602]

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
    async def leave(self, ctx):
        guild = ctx.message.guild
        voice_client = guild.voice_client

        if voice_client:
            await voice_client.disconnect()
            await ctx.send('**Disconnected!**')
        else:
            await ctx.send("**I'm not even in a channel, lol!**")


    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.has_any_role(*allowed_roles)
    async def tts(self, ctx, language: str = None, *, message: str = None):
        await ctx.message.delete()
        if not language:
            return await ctx.send("**Please, inform a language!**", delete_after=5)
        elif not message:
            return await ctx.send("**Please, inform a message!**", delete_after=5)

        voice = ctx.message.author.voice
        voice_client = ctx.message.guild.voice_client

        tts = gTTS(text=message, lang=language)
        tts.save(f'tts/audio.mp3')
        if voice is None:
            return await ctx.send("**You're not in a voice channel**")
        voicechannel = discord.utils.get(ctx.guild.channels, id=voice.channel.id)
        if voice_client is None:
            vc = await voicechannel.connect()
            #vc.play(discord.FFmpegPCMAudio(f"tts/audio.mp3"), after=lambda e: self.client.loop.create_task(self.leave(ctx)))
            vc.play(discord.FFmpegPCMAudio(f"tts/audio.mp3"))
        else:
            vc = await voicechannel.connect()
            await vc.play(discord.FFmpegPCMAudio(f"tts/audio.mp3"))


def setup(client):
    client.add_cog(Tools(client))
