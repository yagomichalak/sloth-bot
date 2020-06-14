import discord
from discord.ext import commands
import asyncio
from gtts import gTTS
from googletrans import Translator
from mysqldb2 import the_data_base5

allowed_roles = [474774889778380820, 574265899801116673, 497522510212890655, 588752954266222602]
teacher_role_id = 507298235766013981


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
        Countsdown by a given number
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
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx, scrt=None):
        '''
        Makes the bot leave the voice channel.
        '''
        guild = ctx.message.guild
        voice_client = guild.voice_client

        if voice_client:
            await voice_client.disconnect()
            if scrt == 'the bot':
                return
            await ctx.send('**Disconnected!**')
        else:
            await ctx.send("**I'm not even in a channel, lol!**")

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.has_any_role(*allowed_roles)
    async def tts(self, ctx, language: str = None, *, message: str = None):
        '''
        Reproduces a Text-to-Speech message in the voice channel.
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

        tts = gTTS(text=message, lang=language)
        tts.save(f'tts/audio.mp3')
        if voice is None:
            return await ctx.send("**You're not in a voice channel**")
        voicechannel = discord.utils.get(ctx.guild.channels, id=voice.channel.id)
        if voice_client is None:
            vc = await voicechannel.connect()
            vc.play(discord.FFmpegPCMAudio(f"tts/audio.mp3"),
                    after=lambda e: self.client.loop.create_task(self.leave(ctx, 'the bot')))
        else:
            return await ctx.send("**I'm already in a voice channel!**", delete_after=5)

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
    async def create_table_the_teachers(self, ctx):
        await ctx.message.delete()
        if await self.check_table_the_teachers_exists():
            return await ctx.send(f"**The table TheTeachers already exists!**", delete_after=3)
        mycursor, db = await the_data_base5()
        await mycursor.execute(
            "CREATE TABLE TheTeachers (teacher_id bigint default null, teacher_name varchar(50) default null)")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table TheTeachers created!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drop_table_the_teachers(self, ctx):
        await ctx.message.delete()
        if not await self.check_table_the_teachers_exists():
            return await ctx.send(f"\t# - The table TheTeachers does not exist!")
        mycursor, db = await the_data_base5()
        await mycursor.execute("DROP TABLE TheTeachers")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table TheTeachers dropped!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_table_the_teachers(self, ctx=None):
        if ctx:
            await ctx.message.delete()
        if not await self.check_table_the_teachers_exists():
            return await ctx.send("**Table TheTeachers doesn't exist yet!**", delete_after=3)
        mycursor, db = await the_data_base5()
        await mycursor.execute("DELETE FROM TheTeachers")
        await db.commit()
        await mycursor.close()
        if ctx:
            await ctx.send("**Table TheTeachers reset!**", delete_after=3)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def register_teachers(self, ctx):
        await ctx.message.delete()
        if not await self.check_table_the_teachers_exists():
            return await ctx.send("**Table TheTeachers doesn't exist yet!**", delete_after=3)
        await self.reset_table_the_teachers()
        mycursor, db = await the_data_base5()
        teacher_role = discord.utils.get(ctx.guild.roles, id=teacher_role_id)
        teachers = [t for t in ctx.guild.members if teacher_role in t.roles]
        for t in teachers:
            await mycursor.execute("INSERT INTO TheTeachers (teacher_id, teacher_name) VALUES (%s, %s)", (t.id, f"{t.name}#{t.discriminator}"))
        await db.commit()
        await mycursor.close()
        return await ctx.send("**All teachers have been registered!**", delete_after=3)

    async def check_table_the_teachers_exists(self):
        mycursor, db = await the_data_base5()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'TheTeachers'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True

    @commands.command()
    async def help(self, ctx, co: str = None):
        '''Provides a description of all commands and cogs.
        :param co: The cog or the command that you want to see. (Optional)
        '''
        if not co:
            halp = discord.Embed(title="Cog Listing and Uncategorized Commands.",
            description="```Use !help *cog* or !help *command* to find out more about them!\n```",
            color=discord.Color.green(),
            timestamp=ctx.message.created_at)

            cogs_desc = ''
            for x in self.client.cogs:
                cog_doc = self.client.cogs[x].__doc__
                if cog_doc:
                    cogs_desc += (f"{x}\n")
            halp.add_field(name='__Cogs__',value=cogs_desc[0:len(cogs_desc)-1],inline=False)

            cmds_desc = ''
            for y in self.client.walk_commands():
                if not y.cog_name and not y.hidden:
                    if y.help:
                        cmds_desc += (f"{y.name} - `{y.help}`"+'\n')
                    else:
                        cmds_desc += (f"{y.name}"+'\n')
            halp.add_field(name='__Uncatergorized Commands__',value=cmds_desc[0:len(cmds_desc)-1],inline=False)
            return await ctx.send('',embed=halp)


        # Checks if it's a command
        command = self.client.get_command(co)
        if command:
            command_embed = discord.Embed(title=f"__Command:__ {command.name}", description=f"__**Description:**__\n```{command.help}```", color=discord.Color.green(), timestamp=ctx.message.created_at)
            await ctx.send(embed=command_embed)

        # Checks if it's a cog
        cog = self.client.get_cog(co)
        elif cog:
            cog_embed = discord.Embed(title=f"__Cog:__ {cog.qualified_name}", description=f"__**Description:**__\n```{cog.description}```", color=discord.Color.green(), timestamp=ctx.message.created_at)
            for c in cog.get_commands():
                if not c.hidden:
                    cog_embed.add_field(name=c.name,value=c.help,inline=False)

            await ctx.send(embed=cog_embed)

        # Otherwise, it's an invalid parameter (Not found)
        else:
            await ctx.send(f"**Invalid parameter! `{co}` is neither a command nor a cog!**")


def setup(client):
    client.add_cog(Tools(client))
