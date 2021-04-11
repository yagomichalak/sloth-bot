import discord
from discord.ext import commands
import os


class Files(commands.Cog):
    '''
    File related commands; showing, sending files.
    '''

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Files cog is ready.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def gif(self, ctx, name: str = None):
        '''
        (ADM) Sends a gif from the bot's gif folder.
        :param name: The name of the gif file.
        '''
        await ctx.message.delete()
        try:
            with open(f'./gif/{name}.gif', 'rb') as pic:
                await ctx.send(file=discord.File(pic))
        except FileNotFoundError:
            return await ctx.send("**File not found!**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def png(self, ctx, name: str = None):
        '''
        (ADM) Sends a png from the bot's png folder.
        :param name: The name of the png file.
        '''
        await ctx.message.delete()
        try:
            await ctx.send(file=discord.File(f'./png/{name}.png'))
        except FileNotFoundError:
            return await ctx.send("**File not found!**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def files(self, ctx, type: str = None):
        '''
        (ADM) Shows all files of a given extension from the bot's folders.
        :param type: The type of file to list.
        '''
        await ctx.message.delete()
        if not type:
            return await ctx.send('**Please, specify an extension!**')
        elif type.lower() != "png" and type.lower() != "gif":
            return await ctx.send('**Extension not supported!**')
        arr = os.listdir(f'./{type}')
        temp = []
        for a in arr:
            if type.lower() == "png":
                temp.append(a[:-4])
            else:
                temp.append(a[:-4])

        temp = ' \n'.join(temp)
        embed = discord.Embed(title=f'{type.title()} files', description=f"__All available files:__\n**{temp}**",
                              colour=discord.Colour.dark_green())
        embed.set_footer(text=ctx.author.guild.name)
        if len(temp) == 0:
            embed.add_field(name='None', value='No files available')

        await ctx.send(content=None, embed=embed)

def setup(client):
    client.add_cog(Files(client))
