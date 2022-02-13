import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union
from extra import utils
import os

afk_channel_id = int(os.getenv('AFK_CHANNEL_ID'))

class UserVoiceSystem(commands.Cog):
    """ Cog for the inner systems of UserVoice events. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client


    @commands.Cog.listener(name="on_voice_state_update")
    async def on_voice_state_update_join_leave(self, member, before, after) -> None:
        """ For when users join or leave the Voice Channel. """

        if member.bot:
            return

        current_ts: int = await utils.get_timestamp()

        # Get before/after channels and their categories
        bc = before.channel
        ac = after.channel

        # # Check voice states
        # if before.mute != after.mute:
        #     return
        # if before.deaf != before.deaf:
        #     return
        if before.self_stream != after.self_stream:
            if not before.self_stream and after.self_stream:
                return
            if bc == ac:
                return

        if before.self_video != after.self_video:
            if not before.self_video and after.self_video:
                return
            if bc == ac:
                return

        # Get before/after channels and their categories
        bc = before.channel
        ac = after.channel

        user_info = await self.get_user_activity_info(member.id)
        if not user_info and not after.self_mute:
            if ac:
                return await self.insert_user_server_activity(member.id, 0, current_ts)
            else:
                return await self.insert_user_server_activity(member.id, 0)

        if not user_info:
            return

        SlothClass: commands.Cog = self.client.get_cog('SlothClass')
        Moderation: commands.Cog = self.client.get_cog('Moderation')

        # Join
        if ac and not bc:
            if not after.self_mute and not after.self_deaf and not after.mute and not after.deaf and after.channel.id != afk_channel_id:
                await self.update_user_server_timestamp(member.id, current_ts)

        # Switch
        elif (ac and bc) and (bc.id != ac.id) and not after.self_mute and not after.mute and not after.deaf:
            alts = await Moderation.get_fake_accounts(member.id)

            alts_list: List[int] = []
            for alt in alts:
                alts_list.append(alt[0])
                alts_list.append(alt[1])

            alts = list(set(alts_list))
            try:
                alts.remove(member.id)
            except ValueError:
                pass

            people_in_vc: int = len([m for m in bc.members if not m.bot and m.id not in alts]) +1

            if people_in_vc < 2 or after.self_mute or after.mute or after.deaf or after.channel.id == afk_channel_id:
                return await self.update_user_server_time(member.id, 0, current_ts)

            if not user_info[0][3]: return
            increment: int = current_ts - user_info[0][3]

            effects = await SlothClass.get_user_effects(member)
            if 'sabotaged' in effects:
                increment = 0

            await self.update_user_server_time(member.id, increment, current_ts)

        # Muted/unmuted
        elif (ac and bc) and (bc.id == ac.id) and before.self_mute != after.self_mute:

            if not after.self_mute and not after.self_deaf and not after.mute and not after.deaf and after.channel.id != afk_channel_id:
                return await self.update_user_server_timestamp(member.id, current_ts)

            alts = await Moderation.get_fake_accounts(member.id)
            alts_list: List[int] = []
            for alt in alts:
                alts_list.append(alt[0])
                alts_list.append(alt[1])

            alts = list(set(alts_list))
            try:
                alts.remove(member.id)
            except ValueError:
                pass

            people_in_vc: int = len([m for m in bc.members if not m.bot and m.id not in alts])
            if people_in_vc < 2 or after.self_mute or after.self_deaf:
                return await self.update_user_server_time(member.id, 0, None)

            if not user_info[0][3]: return
            increment: int = current_ts - user_info[0][3]

            effects = await SlothClass.get_user_effects(member)
            if 'sabotaged' in effects:
                increment = 0

            await self.update_user_server_time(member.id, increment, current_ts)

        # Deafened/undeafened
        elif (ac and bc) and (bc.id == ac.id) and before.self_deaf != after.self_deaf:

            if not after.self_mute and not after.self_deaf and not after.mute and not after.deaf and after.channel.id != afk_channel_id:
                return await self.update_user_server_timestamp(member.id, current_ts)

            alts = await Moderation.get_fake_accounts(member.id)
            alts_list: List[int] = []
            for alt in alts:
                alts_list.append(alt[0])
                alts_list.append(alt[1])

            alts = list(set(alts_list))
            try:
                alts.remove(member.id)
            except ValueError:
                pass

            people_in_vc: int = len([m for m in bc.members if not m.bot and m.id not in alts])
            if people_in_vc < 2 or after.self_mute or after.self_deaf:
                return await self.update_user_server_time(member.id, 0, None)

            if not user_info[0][3]: return
            increment: int = current_ts - user_info[0][3]

            effects = await SlothClass.get_user_effects(member)
            if 'sabotaged' in effects:
                increment = 0

            await self.update_user_server_time(member.id, increment, current_ts)

        # Server Muted/unmuted
        elif (ac and bc) and (bc.id == ac.id) and before.mute != after.mute:

            if not after.self_mute and not after.self_deaf and not after.mute and not after.deaf and after.channel.id != afk_channel_id:
                return await self.update_user_server_timestamp(member.id, current_ts)

            alts = await Moderation.get_fake_accounts(member.id)
            alts_list: List[int] = []
            for alt in alts:
                alts_list.append(alt[0])
                alts_list.append(alt[1])

            alts = list(set(alts_list))
            try:
                alts.remove(member.id)
            except ValueError:
                pass

            people_in_vc: int = len([m for m in bc.members if not m.bot and m.id not in alts])
            if people_in_vc < 2 or after.mute or after.deaf:
                return await self.update_user_server_time(member.id, 0, None)

            if not user_info[0][3]: return
            increment: int = current_ts - user_info[0][3]

            effects = await SlothClass.get_user_effects(member)
            if 'sabotaged' in effects:
                increment = 0

            await self.update_user_server_time(member.id, increment, current_ts)

        # Server Deafened/undeafened
        elif (ac and bc) and (bc.id == ac.id) and before.deaf != after.deaf:

            if not after.self_mute and not after.self_deaf and not after.mute and not after.deaf and after.channel.id != afk_channel_id:
                return await self.update_user_server_timestamp(member.id, current_ts)

            alts = await Moderation.get_fake_accounts(member.id)
            alts_list: List[int] = []
            for alt in alts:
                alts_list.append(alt[0])
                alts_list.append(alt[1])

            alts = list(set(alts_list))
            try:
                alts.remove(member.id)
            except ValueError:
                pass

            people_in_vc: int = len([m for m in bc.members if not m.bot and m.id not in alts])
            if people_in_vc < 2 or after.mute or after.deaf:
                return await self.update_user_server_time(member.id, 0, None)

            if not user_info[0][3]: return
            increment: int = current_ts - user_info[0][3]

            effects = await SlothClass.get_user_effects(member)
            if 'sabotaged' in effects:
                increment = 0

            await self.update_user_server_time(member.id, increment, current_ts)
        
        # Leave
        elif bc and not ac:
            alts = await Moderation.get_fake_accounts(member.id)
            alts_list: List[int] = []
            for alt in alts:
                alts_list.append(alt[0])
                alts_list.append(alt[1])

            alts = list(set(alts_list))
            try:
                alts.remove(member.id)
            except ValueError:
                pass

            people_in_vc: int = len([m for m in bc.members if not m.bot and m.id not in alts])
            if people_in_vc < 2 or before.self_mute or before.mute or before.deaf or before.channel.id == afk_channel_id:
                return await self.update_user_server_timestamp(member.id, None)
            
            if not user_info[0][3]: return
            increment: int = current_ts - user_info[0][3]
            
            effects = await SlothClass.get_user_effects(member)
            if 'sabotaged' in effects:
                increment = 0

            await self.update_user_server_time(member.id, increment)


class UserServerActivityTable(commands.Cog):
    """ Class for the UserServerActivity table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    # ===== Discord commands =====
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_server_activity(self, ctx):
        """ (ADM) Creates the UserServerActivity table. """

        await ctx.message.delete()
        if await self.check_user_server_activity_table_exists():
            return await ctx.send("The `UserServerActivity` already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("CREATE TABLE UserServerActivity (user_id BIGINT, user_messages BIGINT, user_time BIGINT, user_timestamp BIGINT DEFAULT NULL)")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table `UserServerActivity` created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_server_activity(self, ctx):
        """ (ADM) Drops the UserServerActivity table. """

        await ctx.message.delete()

        if not await self.check_user_server_activity_table_exists():
            return await ctx.send("The `UserServerActivity` doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserServerActivity")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table `UserServerActivity` dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_server_activity(self, ctx):
        """ (ADM) Resets the UserServerActivity table. """

        await ctx.message.delete()
        if not await self.check_user_server_activity_table_exists():
            return await ctx.send("The `UserServerActivity` doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserServerActivity")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table `UserServerActivity` reset!**")

    # ===== SHOW =====

    async def check_user_server_activity_table_exists(self) -> bool:
        """ Checks whether the UserServerActivity table exists. """
        
        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'UserServerActivity'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    # ===== INSERT =====
    async def insert_user_server_activity(self, user_id: int, add_msg: int, new_ts: int = None) -> None:
        """ Inserts a user into the UserServerActivity table.
        :param user_id: The ID of the user to insert.
        :param add_msg: The initial message counter for the user to have.
        :param new_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute(
            "INSERT INTO UserServerActivity (user_id, user_messages, user_time, user_timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, add_msg, 0, new_ts))
        await db.commit()
        await mycursor.close()

    # ===== SELECT =====

    async def get_user_activity_info(self, user_id: int) -> List[List[int]]:
        """ Gets a user from the UserServerActivity table.
        :param user_id: The ID of the user to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserServerActivity WHERE user_id = %s", (user_id,))
        user_info = await mycursor.fetchall()
        await mycursor.close()
        return user_info

    # ===== UPDATE =====
    async def update_user_server_messages(self, user_id: int, add_msg: int) -> None:
        """ Updates the user's message counter.
        :param user_id: The ID of the user to update.
        :param add_msg: The increment to apply to their current message counter. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserServerActivity SET user_messages = user_messages + %s WHERE user_id = %s", (add_msg, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_server_time(self, user_id: int, increment: int, current_ts: int = None) -> None:
        """ Updates the user's voice time information.
        :param user_id: The ID of the user to update.
        :param increment: The increment value in seconds to apply.
        :param current_ts: The current timestamp. [Optional] """

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE UserServerActivity SET user_time = user_time + %s, user_timestamp = %s WHERE user_id = %s
            """, (increment, current_ts, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_server_timestamp(self, user_id: int, new_ts: int) -> None:
        """ Updates the user's Server Activity timestamp.
        :param user_id: The ID of the user to update.
        :param new_ts: The new timestamp to set to. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserServerActivity SET user_timestamp = %s WHERE user_id = %s", (new_ts, user_id))
        await db.commit()
        await mycursor.close()

