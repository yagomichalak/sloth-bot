import discord
from discord.ext import commands


class UserVoiceChannel(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('UserVoiceChannel cog is ready.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Guild info
        guild = member.guild
        category_test_id = 693180588919750778
        cr_voice_channels_ids = {None: 693180716258689074, 2: 693180763327299704, 3: 693180823817683074}
        the_category_test = discord.utils.get(guild.categories, id=category_test_id)

        if after.channel:
            if after.channel.category:
                if after.channel.category.id == category_test_id:
                    # Creates a voice channel and moves the user into there
                    if after.channel.id in cr_voice_channels_ids.values():
                        for key, value in cr_voice_channels_ids.items():
                            if value == after.channel.id:
                                creation = await the_category_test.create_voice_channel(name=f"{member.name}'s room",
                                                                                        user_limit=key)
                                await member.move_to(creation)
                                break

        # Deletes a voice channel that is no longer being used
        if before.channel:
            if before.channel.category:
                if before.channel.category.id == category_test_id:
                    user_voice_channel = discord.utils.get(guild.channels, id=before.channel.id)
                    len_users = len(user_voice_channel.members)
                    if len_users == 0 and user_voice_channel.id not in cr_voice_channels_ids.values():
                        return await user_voice_channel.delete()


def setup(client):
    client.add_cog(UserVoiceChannel(client))
