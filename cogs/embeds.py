# import.standard
import os

# import.thirdparty
import discord
from discord import Option, OptionChoice, slash_command
from discord.ext import commands

# import.local
from extra import utils

# variables.id
guild_ids = [int(os.getenv('SERVER_ID', 123))]

# variables.role
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
staff_manager_role_id = int(os.getenv('STAFF_MANAGER_ROLE_ID', 123))
lesson_manager_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID', 123))
allowed_roles = [owner_role_id, admin_role_id, mod_role_id]

class Embeds(commands.Cog):
    """ A cog related to embedded messages. """

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('[.cogs] Embeds cog is ready!')

    # Sends an embedded message
    @commands.command(aliases=['emb'])
    @commands.has_any_role(*allowed_roles, lesson_manager_role_id)
    async def embed(self, ctx):
        """ (MOD) Sends an embedded message. """

        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        msg = ctx.message.content.split(ctx.message.content.split(' ')[0], 1)
        embed = discord.Embed(description=msg[1], colour=discord.Colour.dark_green())
        await ctx.send(embed=embed)

    @slash_command(name="embed", default_permission=False, guild_ids=guild_ids)
    @utils.is_allowed([staff_manager_role_id], throw_exc=True)
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
