import discord
from discord.ext import commands
from mysqldb import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

image_calendar_channel_id = 673592568268980244


class Configurations(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Configurations cog is ready!')

    # Shows the image calendar's id
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def showconfigs(self, ctx):
        config = await show_config()
        if len(config) > 0:
            return await ctx.send(f"Calendar configuration:\n**CID: {config[0][0]}\nMID: {config[0][1]}**")
        else:
            return await ctx.send("**There aren't configurations**")

    # Updates the image calendar
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def update(self, ctx):
        await ctx.message.delete()
        copy_channel = self.client.get_channel(image_calendar_channel_id)
        configs = await show_config()
        if len(configs) > 0:
            channel = discord.utils.get(ctx.author.guild.channels, id=configs[0][0])
            msg = await channel.fetch_message(configs[0][1])
        img = Image.open("calendar_template.png")  # Replace name.png with your background image.
        draw = ImageDraw.Draw(img)
        small = ImageFont.truetype("built titling sb.ttf", 45)  # Make sure you insert a valid font from your folder.
        teachers = await show_teachers()
        events = await show_events()
        #    (x,y)::↓ ↓ ↓ (text)::↓ ↓     (r,g,b)::↓ ↓ ↓
        for teacher in teachers:
            x = check_x(teacher)
            y = check_y(teacher)
            clr = check_clr(teacher)

            if x != 0 and y != 0:
                draw.text((x, y), f"{teacher[1]}", clr, font=small)

        for event in events:
            x = check_x(event)
            y = check_y(event)
            clr = check_clr(event)

            if x != 0 and y != 0:
                draw.text((x, y), f"{event[1]}", clr, font=small)

        img.save('calendar_template2.png')  # Change name2.png if needed.
        e = discord.Embed(colour=discord.Colour.dark_green())
        new_message = await copy_channel.send(file=discord.File('calendar_template2.png'))

        for u in new_message.attachments:
            e.set_image(url=u.url)
            if len(configs) > 0:
                return await msg.edit(embed=e)
            else:
                return await ctx.send(embed=e)

    # Adds an image calendar configuration
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def addconfigs(self, ctx, channel_id: str = None, message_id: str = None):
        if not channel_id or not message_id:
            return await ctx.send('**Inform all parameters!**')
        elif not channel_id.isnumeric() or not message_id.isnumeric():
            return await ctx.send('**Inform a numeric values!**')

        await add_cid_id(int(channel_id), int(message_id))
        await ctx.send('**Calendar ids have been configured!**')

    # Deletes an image calendar configuration
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def delconfigs(self, ctx):
        config = await show_config()
        if len(config) != 0:
            await remove_cid_id()
            await ctx.send('**Calendar ids deleted!**')
        else:
            await ctx.send(("**No configurations were set yet!**"))


def setup(client):
    client.add_cog(Configurations(client))
