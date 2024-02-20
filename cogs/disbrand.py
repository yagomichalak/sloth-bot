import discord
from discord.ext import commands, tasks
from mysqldb import the_database
from typing import List, Dict, Any
import os

server_id: int = int(os.getenv("SERVER_ID", 123))
sponsored_by_category_id: int = int(os.getenv("SPONSORED_BY_CATEGORY_ID", 123))

mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
preference_role_id = int(os.getenv('PREFERENCE_ROLE_ID', 123))


class Disbrand(commands.Cog):
    """ A category for the Disbrand features and commands """
    
    def __init__(self, client: commands.Bot) -> None:
        """ The class init method. """
        
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog's ready to be used. """

        await self.create_pending_user_advertisement_channels.start()
        print("Disbrand cog is online!")
        
    @tasks.loop(seconds=60)
    async def create_pending_user_advertisement_channels(self) -> None:
        """ Checks the pending user advertising channels to be created. """
        
        print("[create_pending_user_advertisement_channels]")
        
        pending_channels = await self.get_user_advertisement_channels(status="pending")
        if not pending_channels:
            return

        created_channels: List[Dict[str, Any]] = []
        
        guild = self.client.get_guild(server_id)
        sponsored_by_category = discord.utils.get(guild.categories, id=sponsored_by_category_id)
        # preference_role = discord.utils.get(guild.roles, id=preference_role_id)

        for pending_channel in pending_channels:
            overwrites = {}
            try:
                # Get some roles
                # overwrites[guild.default_role] = discord.PermissionOverwrite(
                #     read_messages=False, send_messages=False, connect=False,
                #     speak=False, view_channel=False)

                # overwrites[preference_role] = discord.PermissionOverwrite(
                #     read_messages=True, send_messages=False, connect=False, view_channel=True)
                
                # Creates the text channel
                text_channel = await sponsored_by_category.create_text_channel(
                    name=pending_channel[1].lower().strip()[:75])
                
            except Exception as e:
                print("Failed to create User Advertisement Channel.")
                print(e)
            
            else:
                created_channels.append({
                    "old_channel_name": pending_channel[1],
                    "new_channel_name": text_channel.name,
                    "channel_id": text_channel.id,
                    "category_id": sponsored_by_category_id,
                    "server_id": server_id,
                    "server_name": guild.name,
                    "status": "created",
                    "user_id": pending_channel[0]
                })

        if created_channels:
            await self.update_user_advertisement_channels(created_channels)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_advertisement_channel(self, ctx) -> None:
        """ (ADM) Creates the UserAdvertisementChannel table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if await self.check_user_advertisement_channel_table_exists():
            return await ctx.send(f"**The `UserAdvertisementChannel` table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE UserAdvertisementChannel (
                user_id BIGINT NOT NULL,
                channel_name VARCHAR(75) NOT NULL,
                channel_id BIGINT DEFAULT NULL,
                server_name VARCHAR(75) DEFAULT NULL,
                server_id BIGINT DEFAULT NULL,
                status VARCHAR(7) DEFAULT "pending",
                selected BOOLEAN DEFAULT 1,
                category_id BIGINT DEFAULT NULL,
                UNIQUE KEY (user_id, server_id))
            """)
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table `UserAdvertisementChannel` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_advertisement_channel(self, ctx) -> None:
        """ (ADM) Drops the UserAdvertisementChannel table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if not await self.check_user_advertisement_channel_table_exists():
            return await ctx.send(f"**The `UserAdvertisementChannel` table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserAdvertisementChannel")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table `UserAdvertisementChannel` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_advertisement_channel(self, ctx) -> None:
        """ (ADM) Resets the UserAdvertisementChannel table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author
        if not await self.check_user_advertisement_channel_table_exists():
            return await ctx.send(f"**The `UserAdvertisementChannel` table doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserAdvertisementChannel")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table `UserAdvertisementChannel` reset, {member.mention}!**")

    # ===== SHOW =====
    async def check_user_advertisement_channel_table_exists(self) -> bool:
        """ Checks whether the UserAdvertisementChannel table exists in the database. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'UserAdvertisementChannel'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False
    
    async def get_user_advertisement_channels(self, status: str) -> List[Dict[str, Any]]:
        """ Get User Advertisement Channels by status.
        :param status: The status. """
        
        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserAdvertisementChannel WHERE status = %s", (status,))
        channels = await mycursor.fetchall()
        await mycursor.close()
        return channels

    async def update_user_advertisement_channels(self, channels: List[Dict[str, Any]]) -> None:
        """ Get User Advertisement Channels by status.
        :param status: The status. """
        
        mycursor, db = await the_database()
        await mycursor.executemany("""
            UPDATE
                UserAdvertisementChannel
            SET
                channel_id = %(channel_id)s,
                channel_name = %(new_channel_name)s,
                category_id = %(category_id)s,
                server_id = %(server_id)s,
                server_name = %(server_name)s,
                status = %(status)s
            WHERE
                user_id = %(user_id)s AND channel_name = %(old_channel_name)s;
        """, channels)
        channels = await db.commit()
        await mycursor.close()

def setup(client: commands.Bot) -> None:
    """ Cog's setup function. """
    
    client.add_cog(Disbrand(client))
