# import.standard
import os
from typing import Dict, Union

# import.thirdparty
import discord
from discord.ext import commands, tasks

# import.local
from extra import utils

# variables.id
server_id = int(os.getenv('SERVER_ID', 123))

# variables.role
mod_role_id: int = int(os.getenv("MOD_ROLE_ID", 123))
senior_mod_role_id: int = int(os.getenv("SENIOR_MOD_ROLE_ID", 123))

# variables.textchannel
bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID', 123))

class VoiceManagement(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client
        self.vcc_id: int = int(os.getenv('VOICE_CALLS_CHANNEL_ID', 123))

        # user_id: {'timestamp': 123, 'camera_on': False, 'notified': False}

        self.people: Dict[int, Dict[str, Union[int, bool]]] = {}

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.check_camera_on.start()
        print('VoiceManagement cog is online!')

    @tasks.loop(seconds=60)
    async def check_camera_on(self) -> None:
        """ Checks whether people in the Video Calls channel have their cameras on. """

        current_ts = await utils.get_timestamp()
        guild = self.client.get_guild(server_id)
        bots_and_commands_channel =  guild.get_channel(bots_and_commands_channel_id)

        for user_id in list(self.people.keys()):
            secs = current_ts - self.people[user_id]['timestamp']
            # if secs >= 60 and secs < 180:
            #     if not self.people[user_id]['camera_on'] and not self.people[user_id]['notified']:
            #         # Notifies user to turn on camera
            #         msg = f"**Hey, I saw you are in the `Video Calls` channel and didn't turn on your camera. Please, do it or you will soon get disconnected!**"
            #         try:
            #             member = guild.get_member(user_id)
            #             if not member.voice or not (vc := member.voice.channel):
            #                 continue

            #             if self.vcc_id != vc.id:
            #                 continue

            #             await member.send(msg)
            #             self.people[user_id]['notified'] = True
            #         except:
            #             await bots_and_commands_channel.send(f"{msg}. {member.mention}")

            if secs >= 60:
                if not self.people[user_id]['camera_on']:
                    del self.people[user_id]
                    # Disconnects users with cameras off
                    try:
                        member = guild.get_member(user_id)
                        # Mods+ shouldn't get disconnected from the Camera only channel
                        if await utils.is_allowed([mod_role_id, senior_mod_role_id]).predicate(member=member, channel=bots_and_commands_channel): return

                        if not member.voice or not (vc := member.voice.channel):
                            continue

                        if self.vcc_id != vc.id:
                            continue
                        msg = f"**You got disconnected for not turning on your camera in the `Video Calls` voice channel!**"
                        await member.move_to(None)
                        await member.send(msg)
                    except:
                        await bots_and_commands_channel.send(f"{msg}. {member.mention}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """ Checks whether people have open cameras in the voice channel. """

        if member.bot:
            return

        # Check voice states
        if before.mute != after.mute:
            return
        if before.deaf != before.deaf:
            return
        if before.self_mute != after.self_mute:
            return
        if before.self_deaf != after.self_deaf:
            return
        if before.self_stream != after.self_stream:
            return

        # Get before/after channels and their categories
        bc = before.channel
        ac = after.channel

        current_ts = await utils.get_timestamp()

        # Joining the Video Calls channel
        if ac and ac.id == self.vcc_id:
            self.people[member.id] = {
                'timestamp': current_ts,
                'camera_on': after.self_video,
                'notified': False
            }

        # Leaving the Video Calls channel
        elif not ac or ac.id != self.vcc_id:
            self.people.pop(member.id, None)


def setup(client) -> None:
    client.add_cog(VoiceManagement(client))