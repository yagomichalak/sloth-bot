import discord
from discord.ext import commands
import asyncio
from gtts import gTTS
from googletrans import Translator
import inspect
import io
import textwrap
import traceback
from contextlib import redirect_stdout
import os

allowed_roles = [
int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')),
int(os.getenv('MOD_ROLE_ID')), int(os.getenv('SLOTH_LOVERS_ROLE_ID'))
]
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))


class Tools(commands.Cog):
    '''
    Some useful tool commands.
    '''

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Tools cog is ready!')

    # Countsdown from a given number
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def count(self, ctx, amount=0):
        '''
        (ADM) Countsdown by a given number
        :param amount: The start point.
        '''
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
    @commands.has_permissions(kick_members=True)
    async def leave(self, ctx):
        '''
        (MOD) Makes the bot leave the voice channel.
        '''
        guild = ctx.message.guild
        voice_client = guild.voice_client
        user_voice = ctx.message.author.voice
        #voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice_client:
            if user_voice.channel == voice_client.channel:
                await voice_client.disconnect()
                await ctx.send('**Disconnected!**')
            else:
                await ctx.send("**You're not in the bot's voice channel!**")
        else:
            await ctx.send("**I'm not even in a channel, lol!**")

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.has_any_role(*allowed_roles)
    async def tts(self, ctx, language: str = None, *, message: str = None):
        '''
        (BOOSTER) Reproduces a Text-to-Speech message in the voice channel.
        :param language: The language of the message.
        :param message: The message to reproduce.
        '''
        await ctx.message.delete()
        if not language:
            return await ctx.send("**Please, inform a language!**", delete_after=5)
        elif not message:
            return await ctx.send("**Please, inform a message!**", delete_after=5)

        voice = ctx.message.author.voice
        voice_client = ctx.message.guild.voice_client


        # Checks if the user is in a voice channel
        if voice is None:
            return await ctx.send("**You're not in a voice channel**")
        voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        # Checks if the bot is in a voice channel
        if not voice_client:
            await voice.channel.connect()
            voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        # Checks if the bot is in the same voice channel that the user
        if voice.channel == voice_client.channel:
            # Plays the song
            if not voice_client.is_playing():
                tts = gTTS(text=message, lang=language)
                tts.save(f'tts/audio.mp3')
                audio_source = discord.FFmpegPCMAudio('tts/audio.mp3')
                voice_client.play(audio_source, after=lambda e: print('finished playing the tts!'))
        else:
            await ctx.send("**The bot is in a different voice channel!**")

    @commands.command()
    async def tr(self, ctx, language: str = None, *, message: str = None):
        '''
        Translates a message into another language.
        :param language: The language to translate the message to.
        :param message: The message to translate.
        :return: A translated message.
        '''
        await ctx.message.delete()
        if not language:
            return await ctx.send("**Please, inform a language!**", delete_after=5)
        elif not message:
            return await ctx.send("**Please, inform a message to translate!**", delete_after=5)
        trans = Translator()
        try:
            translation = trans.translate(f'{message}', dest=f'{language}')
        except ValueError:
            return await ctx.send("**Invalid parameter for 'language'!**", delete_after=5)
        embed = discord.Embed(title="__Sloth Translator__",
                              description=f"**Translated from `{translation.src}` to `{translation.dest}`**\n\n{translation.text}",
                              colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        '''
        Show the latency.
        '''
        await ctx.send(f"**:ping_pong: Pong! {round(self.client.latency * 1000)}ms.**")

    @commands.command()
    async def math(self, ctx, v1=None, oper: str = None, v2=None):
        '''
        Calculates something.
        :param v1: The value 1.
        :param oper: The operation/operator.
        :param v2: The value 2.
        '''
        await ctx.message.delete()
        if not v1:
            return await ctx.send("**Inform the values to calculate!**", delete_after=3)
        elif not oper:
            return await ctx.send("**Inform the operator to calculate!**", delete_after=3)
        elif not v2:
            return await ctx.send("**Inform the second value to calculate!**", delete_after=3)

        try:
            v1 = float(v1)
            v2 = float(v2)
        except ValueError:
            return await ctx.send("**Invalid value parameter!**", delete_after=3)

        operators = {'+': (lambda x, y: x + y), "plus": (lambda x, y: x + y), '-': (lambda x, y: x - y),
                     "minus": (lambda x, y: x - y),
                     '*': (lambda x, y: x * y), "times": (lambda x, y: x * y), "x": (lambda x, y: x * y),
                     '/': (lambda x, y: x / y),
                     '//': (lambda x, y: x // y), "%": (lambda x, y: x % y), }
        if not oper.lower() in operators.keys():
            return await ctx.send("**Invalid operator!**", delete_after=3)

        embed = discord.Embed(title="__Math__",
                              description=f"`{v1}` **{oper}** `{v2}` **=** `{operators[oper](v1, v2)}`",
                              colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def eval(self, ctx, *, body = None):
        '''
        (ADM) Executes a given command from Python onto Discord.
        :param body: The body of the command.
        '''
        await ctx.message.delete()
        if not body:
            return await ctx.send("**Please, inform the code body!**")

        """Evaluates python code"""
        env = {
            'ctx': ctx,
            'client': self.client,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'source': inspect.getsource
        }

        def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            # remove ```py\n```
            if content.startswith('```') and content.endswith('```'):
                return '\n'.join(content.split('\n')[1:-1])

            # remove `foo`
            return content.strip('` \n')

        def get_syntax_error(e):
            if e.text is None:
                return f'```py\n{e.__class__.__name__}: {e}\n```'
            return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

        env.update(globals())

        body = cleanup_code(body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        def paginate(text: str):
            '''Simple generator that paginates text.'''
            last = 0
            pages = []
            for curr in range(0, len(text)):
                if curr % 1980 == 0:
                    pages.append(text[last:curr])
                    last = curr
                    appd_index = curr
            if appd_index != len(text)-1:
                pages.append(text[last:curr])
            return list(filter(lambda a: a != '', pages))

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            return await ctx.message.add_reaction('\u2049')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    try:

                        out = await ctx.send(f'```py\n{value}\n```')
                    except:
                        paginated_text = paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await ctx.send(f'```py\n{page}\n```')
                                break
                            await ctx.send(f'```py\n{page}\n```')
            else:
                try:
                    out = await ctx.send(f'```py\n{value}{ret}\n```')
                except:
                    paginated_text = paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')

        if out:
            await ctx.message.add_reaction('\u2705')  # tick
        elif err:
            await ctx.message.add_reaction('\u2049')  # x
        else:
            await ctx.message.add_reaction('\u2705')


def setup(client):
    client.add_cog(Tools(client))
