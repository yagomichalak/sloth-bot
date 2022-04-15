import discord
from discord import Option, OptionChoice, slash_command
from discord.ext import commands
from extra import utils
import os

admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
senior_mod_role_id = int(os.getenv('SENIOR_MOD_ROLE_ID', 123))
allowed_roles = [owner_role_id, admin_role_id, mod_role_id]

guild_ids = [int(os.getenv('SERVER_ID', 123))]

class Embeds(commands.Cog):
    """ A cog related to embedded messages. """

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Embeds cog is ready.')

    # Sends an embedded message
    @commands.command(aliases=['emb'])
    @commands.has_any_role(*allowed_roles)
    async def embed(self, ctx):
        """ (MOD) Sends an embedded message. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        msg = ctx.message.content.split(ctx.message.content.split(' ')[0], 1)
        embed = discord.Embed(description=msg[1], colour=discord.Colour.dark_green())
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def embed_join_us(self, ctx):
        """ (ADM) Sends the join-us embedded message. """

        await ctx.message.delete()
        embed = discord.Embed(title="Join our Staff!",
                              description="```We depend on people like you to keep this community running, and any help is welcome. if you feel like you would like to contribute apply to any of the positions below: ```",
                              url='https://docs.google.com/forms/d/1H-rzl9AKgfH1WuKN7nYAW-xJx411Q4-HxfPXuPUFQXs',
                              colour=2788104, timestamp=ctx.message.created_at)
        embed.add_field(name=":police_officer: Become a Moderator",
                        value='Would you like to help us by mediating conflicts in the voice channels and becoming an official part of our staff? [Click here to apply](https://docs.google.com/forms/d/e/1FAIpQLSfFXh7GrwftdDro6iqtuw9W4-G2dZfhqvCcEB1jQacQMdNJtA/viewform)',
                        inline=False)
        embed.add_field(name=":man_teacher: Become a Teacher",
                        value="Do you want to teach on our server? Since this community is made by people like you, we are always looking for people to join our ranks ! Teach your native language here ! [Click here to apply](https://docs.google.com/forms/d/1H-rzl9AKgfH1WuKN7nYAW-xJx411Q4-HxfPXuPUFQXs)",
                        inline=False)
        embed.add_field(name="All positions are unsalaried, for professional enquiry please get in touch.",
                        value="```Other available positions !```", inline=False)
        embed.add_field(name=":musical_note:  Karaoke Night Organizer",
                        value="We are looking for someone to take over the **Karaoke Night** event, A 40 minute per week event that would unite people in a voice chat to sing karaoke.You would have to organize and screenshare karaoke songs on a given day of the week. To anyone interested in this position please contact <@423829836537135108> privately.",
                        inline=False)
        embed.add_field(name=":speaking_head: Moderator in the Debate Club",
                        value="We are searching for someone willing to moderate debates impartially once a week, Must have command of the English language and over 16 years old.",
                        inline=False)
        embed.add_field(name="Apply now!", value="Or Later?", inline=True)
        embed.add_field(name="Apply Tomorrow!", value="Or after tomorrow?", inline=True)
        embed.set_footer(text='Cosmos',
                         icon_url='https://cdn.discordapp.com/avatars/423829836537135108/da15dea5017edf5567e531fc6b97f935.jpg?size=2048')
        embed.set_thumbnail(url='https://i.imgur.com/bFfenC9.png')
        embed.set_image(url='https://cdn.discordapp.com/attachments/668049600871006208/689196815509094403/unnamed.png')
        embed.set_author(name='The Language Sloth', url='https://discordapp.com',
                         icon_url='https://cdn.discordapp.com/attachments/562019489642709022/676564701399744512/jungle_2.gif')
        await ctx.send(embed=embed)

    @slash_command(name="embed", default_permission=False, guild_ids=guild_ids)
    @utils.is_allowed([senior_mod_role_id], throw_exc=True)
    async def _embed(self, ctx,
        description: Option(str, name="description", description="Description.", required=False),
        title: Option(str, name="title", description="Title.", required=False),
        timestamp: Option(bool, name="timestamp", description="If timestamp is gonna be shown.", required=False),
        url: Option(str, name="url", description="URL for the title.", required=False),
        thumbnail: Option(str, name="thumbnail", description="Thumbnail for the embed.", required=False),
        image: Option(str, name="image", description="Display image.", required=False),
        color: Option(str, name="color", description="The color for the embed.", required=False,
            choices=[
                OptionChoice(name="Blue", value="0011ff"), OptionChoice(name="Red", value="ff0000"),
                OptionChoice(name="Green", value="00ff67"), OptionChoice(name="Yellow", value="fcff00"),
                OptionChoice(name="Black", value="000000"), OptionChoice(name="White", value="ffffff"),
                OptionChoice(name="Orange", value="ff7100"), OptionChoice(name="Brown", value="522400"),
                OptionChoice(name="Purple", value="380058")])) -> None:
        """ (ADM) Makes an improved embedded message """

        # Checks if there's a timestamp and sorts time
        embed = discord.Embed()

        # Adds optional parameters, if informed
        if title: embed.title = title
        if timestamp: embed.timestamp = await utils.parse_time()
        if description: embed.description = description.replace(r'\n', '\n')
        if color: embed.color = int(color, 16)
        if thumbnail: embed.set_thumbnail(url=thumbnail)
        if url: embed.url = url
        if image: embed.set_image(url=image)

        if not description and not image and not thumbnail:
            return await ctx.respond(
                f"**{ctx.author.mention}, you must inform at least one of the following options: `description`, `image`, `thumbnail`**")

        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(Embeds(client))
