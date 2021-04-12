import discord
from discord.ext import commands, tasks
from extra.native_regions import language_regions
import os

server_id = int(os.getenv('SERVER_ID'))
bot_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class UpdateRegion(commands.Cog):
    '''
    A cog related to the automatic region update feature.
    '''

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("UpdateRegion cog is online!")
        self.change_region.start()

    @tasks.loop(hours=3)
    async def change_region(self):
        guild = self.client.get_guild(server_id)
        everything = []

        for member in guild.members:
            if str(member.status).title() == 'Online':
                for role in member.roles:
                    try:
                        region = language_regions[role.name]
                    except KeyError:
                        pass
                    else:
                        if region:
                            everything.append(region)

        counted_regions = [[x, everything.count(x)] for x in set(everything)]
        counted_regions.sort(key=lambda x: x[1], reverse=True)
        top_region = counted_regions[0][0]
        old_region = guild.region
        await guild.edit(region=top_region)
        channel = discord.utils.get(guild.channels, id=bot_and_commands_channel_id)
        if str(old_region) != str(top_region):
            await channel.send(f"**Region changed from `{old_region}` to `{top_region}`**")
        else:
            await channel.send(f"**Region remained the same; `{old_region}`**")


def setup(client):
    client.add_cog(UpdateRegion(client))
