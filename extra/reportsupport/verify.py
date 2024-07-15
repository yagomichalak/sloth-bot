import discord
from discord.ext import commands
import os


class Verify(commands.Cog):
    """ Cog for user verification commands and methods. """

    verify_reqs_channel_id = int(os.getenv('VERIFY_REQS_CHANNEL_ID', 123))
    verify_reqs_cat_id = int(os.getenv('VERIFY_REQS_CAT_ID', 123))
    verified_role_id = int(os.getenv('VERIFIED_ROLE_ID', 123))

    @commands.Cog.listener(name="on_raw_reaction_add")
    async def on_raw_reaction_add_verify(self, payload) -> None:
        # Checks if it wasn't a bot's reaction

        if not payload.guild_id:
            return

        if not payload.member or payload.member.bot:
            return

        guild = self.client.get_guild(payload.guild_id)
        channel = await self.client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        adm = channel.permissions_for(payload.member).administrator

        # Checks if it's in the teacher applications channel
        if payload.channel_id != self.verify_reqs_channel_id:
            return

        if not adm:
            return await message.remove_reaction(payload.emoji, payload.member)

        await self.handle_verify_request(guild, payload)

    async def handle_verify_request(self, guild, payload) -> None:
        """ Handles teacher applications.
        :param guild: The server in which the application is running.
        :param payload: Data about the Staff member who is opening the application. """

        emoji = str(payload.emoji)
        if emoji not in ['✅', '❌']:
            return

        # Gets the verify request and does the magic
        verify_req = await self.get_application_by_message(payload.message_id)
        if not verify_req:
            return

        verified_user = discord.utils.get(guild.members, id=verify_req[1])

        # Che
        if emoji == '✅':
            verified_role = discord.utils.get(guild.roles, id=self.verified_role_id)
            msg = f"**Verification Request**\nCongratulations, your verification request just got accepted and now you have the `{verified_role.name}` role!"
            try:
                await verified_user.add_roles(verified_role)
            except:
                pass
        else:
            msg = "**Verification Request**\nOur staff has evaluated your verification request and has declined it for internal reasons."

        # Deletes the verify request/application
        await self.delete_application(payload.message_id)
        verify_req_channel = self.client.get_channel(self.verify_reqs_channel_id)
        app_msg = await verify_req_channel.fetch_message(payload.message_id)
        await app_msg.delete()

        if verified_user:
            return await verified_user.send(embed=discord.Embed(description=msg))
