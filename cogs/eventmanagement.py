import discord
from discord.ext import commands, menus
from extra.menu import ConfirmSkill
import os
from typing import Dict, Any, List
from mysqldb import the_database

mod_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
owner_role_id = int(os.getenv('OWNER_ROLE_ID'))
event_manager_role_id = int(os.getenv('EVENT_MANAGER_ROLE_ID'))
preference_role_id = int(os.getenv('PREFERENCE_ROLE_ID'))


class EventManagement(commands.Cog):
    """ A category for event related commands. """

    def __init__(self, client) -> None:
        """ Class initializing method. """

        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to use. """

        print("EventManagement cog is online!")

    async def get_event_permissions(self, guild: discord.Guild) -> Dict[Any, Any]:
        """ Gets permissions for event rooms. """

        # Get some roles
        event_manager_role = discord.utils.get(guild.roles, id=event_manager_role_id)
        preference_role = discord.utils.get(guild.roles, id=preference_role_id)
        mod_role = discord.utils.get(guild.roles, id=mod_role_id)

        overwrites = {}

        overwrites[guild.default_role] = discord.PermissionOverwrite(
        read_messages=False, send_messages=False, connect=False,
        speak=False, view_channel=False)

        overwrites[preference_role] = discord.PermissionOverwrite(
        read_messages=True, send_messages=False, connect=False, view_channel=True)

        overwrites[event_manager_role] = discord.PermissionOverwrite(
        read_messages=True, send_messages=True, manage_messages=True,
        mute_members=True, embed_links=True, connect=True,
        speak=True, move_members=True, view_channel=True,
        manage_permissions=True)

        overwrites[mod_role] = discord.PermissionOverwrite(
        read_messages=True, send_messages=True, manage_messages=True,
        mute_members=True, embed_links=True, connect=True,
        speak=True, move_members=True, view_channel=True)

        return overwrites

    # CREATE EVENT

    @commands.group()
    async def create_event(self, ctx) -> None:
        """ Creates an event. """

        if ctx.invoked_subcommand:
            return

        cmd = self.client.get_command('create_event')
        prefix = self.client.command_prefix
        subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands]

        subcommands = '\n'.join(subcommands)
        embed = discord.Embed(
          title="Subcommads",
          description=f"```apache\n{subcommands}```",
          color=ctx.author.color,
          timestamp=ctx.message.created_at
        )
        await ctx.send(embed=embed)

    @create_event.command()
    @commands.has_any_role(*[event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def movie(self, ctx) -> None:
        """ Creates a Movie Night voice and text channel. """

        if await self.get_event_room_by_user_id(ctx.author.id):
            return await ctx.send(f"**{ctx.author.mention}, you already have an event room going on!**")

        confirm = await ConfirmSkill("Do you want to create a `Movie Night`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(ctx.guild)

        tv_club_role = discord.utils.get(
            ctx.guild.roles, id=int(os.getenv('TV_CLUB_ROLE_ID'))
        )
        # Adds some perms to the Movie Club role
        overwrites[tv_club_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            ctx.author.guild.categories, id=int(os.getenv('EVENTS_CAT_ID')))

        try:
            # Creating text channel
            text_channel = await events_category.create_text_channel(
                name=f"🎥 Movie Night 🎥",
                overwrites=overwrites)
            # Creating voice channel
            voice_channel = await events_category.create_voice_channel(
                name=f"🎥 Movie Night 🎥",
                user_limit=None,
                overwrites=overwrites)
            # Inserts it into the database
            await self.insert_event_room(
                user_id=ctx.author.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{ctx.author.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{ctx.author.mention}, {text_channel.mention} is up and running!**")

    @create_event.command()
    @commands.has_any_role(*[event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def karaoke(self, ctx) -> None:
        """ Creates a Karaoke Night voice and text channel. """

        if await self.get_event_room_by_user_id(ctx.author.id):
            return await ctx.send(f"**{ctx.author.mention}, you already have an event room going on!**")

        confirm = await ConfirmSkill("Do you want to create a `Karaoke Night`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(ctx.guild)

        karaoke_club_role = discord.utils.get(
            ctx.guild.roles, id=int(os.getenv('KARAOKE_CLUB_ROLE_ID'))
        )
        # Adds some perms to the Karaoke Club role
        overwrites[karaoke_club_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            ctx.author.guild.categories, id=int(os.getenv('EVENTS_CAT_ID')))

        try:
            # Creating text channel
            text_channel = await events_category.create_text_channel(
                name=f"🎤 Karaoke Night 🎤",
                overwrites=overwrites)
            # Creating voice channel
            voice_channel = await events_category.create_voice_channel(
                name=f"🎤 Karaoke Night 🎤",
                user_limit=None,
                overwrites=overwrites)
            # Inserts it into the database
            await self.insert_event_room(
                user_id=ctx.author.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{ctx.author.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{ctx.author.mention}, {text_channel.mention} is up and running!**")

    @create_event.command()
    @commands.has_any_role(*[event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def culture(self, ctx) -> None:
        """ Creates a Culture Event voice and text channel. """

        if await self.get_event_room_by_user_id(ctx.author.id):
            return await ctx.send(f"**{ctx.author.mention}, you already have an event room going on!**")

        confirm = await ConfirmSkill("Do you want to create a `Culture Night`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(ctx.guild)

        culture_club_role = discord.utils.get(
            ctx.guild.roles, id=int(os.getenv('CULTURE_CLUB_ROLE_ID'))
        )
        # Adds some perms to the Culture Club role
        overwrites[culture_club_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            ctx.author.guild.categories, id=int(os.getenv('EVENTS_CAT_ID')))

        try:
            # Creating text channel
            text_channel = await events_category.create_text_channel(
                name=f"🎏 Culture Event 🎏",
                overwrites=overwrites)
            # Creating voice channel
            voice_channel = await events_category.create_voice_channel(
                name=f"🎏 Culture Event 🎏",
                user_limit=None,
                overwrites=overwrites)
            # Inserts it into the database
            await self.insert_event_room(
                user_id=ctx.author.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{ctx.author.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{ctx.author.mention}, {text_channel.mention} is up and running!**")

    # DELETE EVENT

    @commands.command()
    @commands.has_any_role(*[event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    async def delete_event(self, ctx) -> None:
        """ Deletes an event room. """
        member = ctx.author
        perms = ctx.channel.permissions_for(member)
        delete = False

        if not (room := await self.get_event_room_by_txt_id(ctx.channel.id)):
            return await ctx.send(f"**{member.mention}, this is not an event room**")

        # Checks whether member can delete room
        if room[0] == member.id:  # If it's the owner of the room
            delete = True

        elif perms.administrator or mod_role_id in [r.id for r in member.roles]:  # If it's a staff member
            delete = True

        if delete:
            confirm = await ConfirmSkill(f"**{member.mention}, are you sure you want to delete the event rooms?**").prompt(ctx)
            if confirm:
                try:
                    await self.client.get_channel(room[1]).delete()
                    await self.client.get_channel(room[2]).delete()
                    await self.delete_event_room_by_txt_id(ctx.channel.id)
                except Exception as e:
                    print(e)
                    await ctx.send(f"**Something went wrong with it, try again later, {member.mention}!**")
            else:
                await ctx.send(f"**Not deleting them, then, {member.mention}!**")

    # ======

    # INSERT

    async def insert_event_room(self, user_id: int, vc_id: int = None, txt_id: int = None) -> None:
        """ Inserts an Event Room by VC ID.
        :param user_id: The ID of the user who's gonna be attached to the rooms.
        :param vc_id: The ID of the VC.
        :param txt_id: The ID of the txt. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO EventRooms (user_id, vc_id, txt_id)
            VALUES (%s, %s, %s)""", (user_id, vc_id, txt_id))
        await db.commit()
        await mycursor.close()

    # GET

    async def get_event_room_by_user_id(self, user_id: int) -> List[int]:
        """ Gets an Event Room by VC ID.
        :param user_id: The ID of the user that you are looking for. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM EventRooms WHERE user_id = %s", (user_id,))
        event_room = await mycursor.fetchone()
        await mycursor.close()
        return event_room

    async def get_event_room_by_vc_id(self, vc_id: int) -> List[int]:
        """ Gets an Event Room by VC ID.
        :param vc_id: The ID of the VC that you are looking for. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM EventRooms WHERE vc_id = %s", (vc_id,))
        event_room = await mycursor.fetchone()
        await mycursor.close()
        return event_room

    async def get_event_room_by_txt_id(self, txt_id: int) -> List[int]:
        """ Gets an Event Room by VC ID.
        :param txt_id: The ID of the txt that you are looking for. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM EventRooms WHERE txt_id = %s", (txt_id,))
        event_room = await mycursor.fetchone()
        await mycursor.close()
        return event_room

    # DELETE

    async def delete_event_room_by_user_id(self, user_id: int) -> None:
        """ Deletes an Event Room by VC ID.
        :param user_id: The ID of the user that you want to delete event rooms from. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM EventRooms WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

    async def delete_event_room_by_vc_id(self, vc_id: int) -> None:
        """ Deletes an Event Room by VC ID.
        :param vc_id: The ID of the txt that you want to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM EventRooms WHERE vc_id = %s", (vc_id,))
        await db.commit()
        await mycursor.close()

    async def delete_event_room_by_txt_id(self, txt_id: int) -> None:
        """ Deletes an Event Room by VC ID.
        :param txt_id: The ID of the txt that you want to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM EventRooms WHERE txt_id = %s", (txt_id,))
        await db.commit()
        await mycursor.close()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_event_rooms(self, ctx) -> None:
        """ (ADM) Creates the EventRooms table. """

        if await self.table_event_rooms_exists():
            return await ctx.send("**The `EventRooms` table already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE EventRooms (
                user_id BIGINT NOT NULL, vc_id BIGINT DEFAULT NULL,
                txt_id BIGINT DEFAULT NULL
            )""")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Created `EventRooms` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_event_rooms(self, ctx) -> None:
        """ (ADM) Drops the EventRooms table. """

        if not await self.table_event_rooms_exists():
            return await ctx.send("**The `EventRooms` table doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE EventRooms")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Dropped `EventRooms` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_event_rooms(self, ctx) -> None:
        """ (ADM) Resets the EventRooms table. """

        if not await self.table_event_rooms_exists():
            return await ctx.send("**The `EventRooms` table doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM EventRooms")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Reset `EventRooms` table!**")

    async def table_event_rooms_exists(self) -> bool:
        """ Checks whether the EventRooms table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'EventRooms'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True


def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(EventManagement(client))
