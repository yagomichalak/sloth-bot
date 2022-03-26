import discord
from discord.ext import commands

from mysqldb import the_database
from typing import List, Union, Optional

class VoiceChannelHistoryTable(commands.Cog):
    """ Class for managing the VoiceChannelHistory table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_voice_channel_history_table(self, ctx: commands.Context) -> None:
        """ Creates the VoiceChannelHistory table. """

        member = ctx.author

        if await self.check_voice_channel_history_exists():
            return await ctx.send(f"**Table `VoiceChannelHistory` already exists, {member.mention}!**")
        
        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE VoiceChannelHistory (
                user_id BIGINT NOT NULL,
                action_label VARCHAR(6) NOT NULL,
                action_ts BIGINT NOT NULL,
                vc_id BIGINT NOT NULL,
                vc2_id BIGINT DEFAULT NULL
            )""")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `VoiceChannelHistory` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_voice_channel_history_table(self, ctx: commands.Context) -> None:
        """ Creates the VoiceChannelHistory table. """

        member = ctx.author
        
        if not await self.check_voice_channel_history_exists():
            return await ctx.send(f"**Table `VoiceChannelHistory` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE VoiceChannelHistory")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `VoiceChannelHistory` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_voice_channel_history_table(self, ctx: commands.Context) -> None:
        """ Creates the VoiceChannelHistory table. """

        member = ctx.author
        
        if not await self.check_voice_channel_history_exists():
            return await ctx.send(f"**Table `VoiceChannelHistory` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM VoiceChannelHistory")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `VoiceChannelHistory` reset, {member.mention}!**")

    async def check_voice_channel_history_exists(self) -> bool:
        """ Checks whether the VoiceChannelHistory table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'VoiceChannelHistory'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_voice_channel_history(self, user_id: int, action_label: str, action_ts: int, vc_id: int, vc2_id: Optional[int] = None) -> None:
        """ Inserts a channel into the user's Voice Channel history.
        :param user_id: The user ID.
        :param action_label: The action label.
        :param action_ts: The timestamp of the action.
        :param vc_id: The Voice Channel ID.
        :param vc2_id: The second Voice Channel ID, if any. [Optional] """

        mycursor, db  = await the_database()
        await mycursor.execute("""
            INSERT INTO VoiceChannelHistory (
                user_id, action_label, action_ts, vc_id, vc2_id
            ) VALUES (%s, %s, %s, %s, %s)
        """, (user_id, action_label, action_ts, vc_id, vc2_id))
        await db.commit()
        await mycursor.close()

    async def get_voice_channel_history(self, user_id: int) -> List[List[Union[int, str]]]:
        """ Gets the user's Voice Channel history.
        :param user_id: The user's ID. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM VoiceChannelHistory WHERE user_id = %s", (user_id,))
        history_vcs = await mycursor.fetchall()
        await mycursor.close()
        return history_vcs

    async def delete_voice_channel_history(self, user_id: int, limit: int = 10) -> None:
        """ Deletes Voice Channels from the user's history.
        :param user_id: The user ID.
        :param limit: The limit of channels to delete from the user's history. [Default = 10] """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM VoiceChannelHistory WHERE user_id = %s LIMIT %s", (user_id, limit))
        await db.commit()
        await mycursor.close()