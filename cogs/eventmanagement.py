# import.standard
import os
from typing import Any, Dict

# import.thirdparty
import discord
from discord.ext import commands

# import.local
from extra import utils
from extra.menu import ConfirmSkill
from extra.smartroom.event_rooms import EventRoomsTable
from mysqldb import DatabaseCore

# variables.role
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
senior_mod_role_id = int(os.getenv('SENIOR_MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))
event_host_role_id = int(os.getenv('EVENT_HOST_ROLE_ID', 123))
event_manager_role_id = int(os.getenv('EVENT_MANAGER_ROLE_ID', 123))
debate_organizer_role_id = int(os.getenv('DEBATE_ORGANIZER_ROLE_ID', 123))
preference_role_id = int(os.getenv('PREFERENCE_ROLE_ID', 123))

# variables.channel
promote_demote_log_channel_id = int(os.getenv('PROMOTE_DEMOTE_LOG_ID', 123))


class EventManagement(EventRoomsTable):
    """ A category for event related commands. """

    def __init__(self, client) -> None:
        """ Class initializing method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to use. """

        print("EventManagement cog is online!")

    async def get_event_permissions(self, guild: discord.Guild) -> Dict[Any, Any]:
        """ Gets permissions for event rooms. """

        # Get some roles
        event_host_role = discord.utils.get(guild.roles, id=event_host_role_id)
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
        manage_permissions=True, manage_channels=True)
        
        overwrites[event_host_role] = discord.PermissionOverwrite(
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
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
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
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def movie(self, ctx) -> None:
        """ Creates a Movie Night voice and text channel. """

        member = ctx.author
        guild = ctx.guild
        room = await self.get_event_room_by_user_id(member.id)
        channel = discord.utils.get(guild.text_channels, id=room[2]) if room else None

        if room and channel:
            return await ctx.send(f"**{member.mention}, you already have an event room going on! ({channel.mention})**")
        elif room and not channel:
            await self.delete_event_room_by_txt_id(room[2])

        confirm = await ConfirmSkill("Do you want to create a `Movie Night`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(guild)

        cinema_club_role = discord.utils.get(
            guild.roles, id=int(os.getenv('CINEMA_CLUB_ROLE_ID', 123))
        )
        # Adds some perms to the Cinema Club role
        overwrites[cinema_club_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            guild.categories, id=int(os.getenv('EVENTS_CAT_ID', 123)))

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
                user_id=member.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{member.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{member.mention}, {text_channel.mention} is up and running!**")

    @create_event.command()
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def karaoke(self, ctx) -> None:
        """ Creates a Karaoke Night voice and text channel. """

        member = ctx.author
        guild = ctx.guild
        room = await self.get_event_room_by_user_id(member.id)
        channel = discord.utils.get(guild.text_channels, id=room[2]) if room else None

        if room and channel:
            return await ctx.send(f"**{member.mention}, you already have an event room going on! ({channel.mention})**")
        elif room and not channel:
            await self.delete_event_room_by_txt_id(room[2])

        confirm = await ConfirmSkill("Do you want to create a `Karaoke Night`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(guild)

        karaoke_club_role = discord.utils.get(
            guild.roles, id=int(os.getenv('KARAOKE_CLUB_ROLE_ID', 123))
        )
        # Adds some perms to the Karaoke Club role
        overwrites[karaoke_club_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            guild.categories, id=int(os.getenv('EVENTS_CAT_ID', 123)))

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
                user_id=member.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{member.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{member.mention}, {text_channel.mention} is up and running!**")

    @create_event.command()
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def culture(self, ctx) -> None:
        """ Creates a Culture Event voice and text channel. """

        member = ctx.author
        guild = ctx.guild
        room = await self.get_event_room_by_user_id(member.id)
        channel = discord.utils.get(guild.text_channels, id=room[2]) if room else None

        if room and channel:
            return await ctx.send(f"**{member.mention}, you already have an event room going on! ({channel.mention})**")
        elif room and not channel:
            await self.delete_event_room_by_txt_id(room[2])

        confirm = await ConfirmSkill("Do you want to create a `Culture Event`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(guild)

        culture_club_role = discord.utils.get(
            guild.roles, id=int(os.getenv('CULTURE_CLUB_ROLE_ID', 123))
        )
        # Adds some perms to the Culture Club role
        overwrites[culture_club_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            guild.categories, id=int(os.getenv('EVENTS_CAT_ID', 123)))

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
                user_id=member.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{member.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{member.mention}, {text_channel.mention} is up and running!**")

    @create_event.command()
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def art(self, ctx) -> None:
        """ Creates a Art Event voice and text channel. """

        member = ctx.author
        guild = ctx.guild
        room = await self.get_event_room_by_user_id(member.id)
        channel = discord.utils.get(guild.text_channels, id=room[2]) if room else None

        if room and channel:
            return await ctx.send(f"**{member.mention}, you already have an event room going on! ({channel.mention})**")
        elif room and not channel:
            await self.delete_event_room_by_txt_id(room[2])

        confirm = await ConfirmSkill("Do you want to create a `Art Event`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(guild)

        art_club_role = discord.utils.get(
            guild.roles, id=int(os.getenv('ART_CLUB_ROLE_ID', 123))
        )
        # Adds some perms to the Art Club role
        overwrites[art_club_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            guild.categories, id=int(os.getenv('EVENTS_CAT_ID', 123)))

        try:
            # Creating text channel
            text_channel = await events_category.create_text_channel(
                name=f"🎏 Art Event 🎏",
                overwrites=overwrites)
            # Creating voice channel
            voice_channel = await events_category.create_voice_channel(
                name=f"🎏 Art Event 🎏",
                user_limit=None,
                overwrites=overwrites)
            # Inserts it into the database
            await self.insert_event_room(
                user_id=member.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{member.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{member.mention}, {text_channel.mention} is up and running!**")

    @create_event.command()
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def wellness(self, ctx) -> None:
        """ Creates a Wellness Event voice and text channel. """

        member = ctx.author
        guild = ctx.guild
        room = await self.get_event_room_by_user_id(member.id)
        channel = discord.utils.get(guild.text_channels, id=room[2]) if room else None

        if room and channel:
            return await ctx.send(f"**{member.mention}, you already have an event room going on! ({channel.mention})**")
        elif room and not channel:
            await self.delete_event_room_by_txt_id(room[2])

        confirm = await ConfirmSkill("Do you want to create a `Wellness Event`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(guild)

        wellness_role = discord.utils.get(
            guild.roles, id=int(os.getenv('FITNESS_HEALTH_ROLE_ID', 123))
        )

        overwrites[wellness_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            guild.categories, id=int(os.getenv('EVENTS_CAT_ID', 123)))

        try:
            # Creating text channel
            text_channel = await events_category.create_text_channel(
                name=f"🌺 Wellness Event 🌺",
                overwrites=overwrites)
            # Creating voice channel
            voice_channel = await events_category.create_voice_channel(
                name=f"🌺 Wellness Event 🌺",
                user_limit=None,
                overwrites=overwrites)
            # Inserts it into the database
            await self.insert_event_room(
                user_id=member.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{member.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{member.mention}, {text_channel.mention} is up and running!**")

    @create_event.command()
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def reading(self, ctx) -> None:
        """ Creates a Reading Session voice and text channel. """

        member = ctx.author
        guild = ctx.guild
        room = await self.get_event_room_by_user_id(member.id)
        channel = discord.utils.get(guild.text_channels, id=room[2]) if room else None

        if room and channel:
            return await ctx.send(f"**{member.mention}, you already have an event room going on! ({channel.mention})**")
        elif room and not channel:
            await self.delete_event_room_by_txt_id(room[2])

        confirm = await ConfirmSkill("Do you want to create a `Reading Session`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(guild)

        culture_club_role = discord.utils.get(
            guild.roles, id=int(os.getenv('READING_CLUB_ROLE_ID', 123))
        )
        # Adds some perms to the Reading Club role
        overwrites[culture_club_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            guild.categories, id=int(os.getenv('EVENTS_CAT_ID', 123)))

        try:
            # Creating text channel
            text_channel = await events_category.create_text_channel(
                name=f"🎏 Reading Session 📖",
                overwrites=overwrites)
            # Creating voice channel
            voice_channel = await events_category.create_voice_channel(
                name=f"🎏 Reading Session 📖",
                user_limit=None,
                overwrites=overwrites)
            # Inserts it into the database
            await self.insert_event_room(
                user_id=member.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{member.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{member.mention}, {text_channel.mention} is up and running!**")

    @create_event.command()
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def gaming(self, ctx) -> None:
        """ Creates a Gaming Event voice and text channel. """

        member = ctx.author
        guild = ctx.guild
        room = await self.get_event_room_by_user_id(member.id)
        channel = discord.utils.get(guild.text_channels, id=room[2]) if room else None

        if room and channel:
            return await ctx.send(f"**{member.mention}, you already have an event room going on! ({channel.mention})**")
        elif room and not channel:
            await self.delete_event_room_by_txt_id(room[2])

        confirm = await ConfirmSkill("Do you want to create a `Gaming Event`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(guild)

        gamer_role = discord.utils.get(
            guild.roles, id=int(os.getenv('PARTY_GAMES_ROLE_ID', 123))
        )
        # Adds some perms to the Gamer role
        overwrites[gamer_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            guild.categories, id=int(os.getenv('EVENTS_CAT_ID', 123)))

        try:
            # Creating text channel
            text_channel = await events_category.create_text_channel(
                name=f"🎮 Gaming Event 🎮",
                overwrites=overwrites)
            # Creating voice channel
            voice_channel = await events_category.create_voice_channel(
                name=f"🎮 Gaming Event 🎮",
                user_limit=None,
                overwrites=overwrites)
            # Inserts it into the database
            await self.insert_event_room(
                user_id=member.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{member.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{member.mention}, {text_channel.mention} is up and running!**")

    @create_event.command()
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def sport(self, ctx) -> None:
        """ Creates a Sport Event voice and text channel. """

        member = ctx.author
        guild = ctx.guild
        room = await self.get_event_room_by_user_id(member.id)
        channel = discord.utils.get(guild.text_channels, id=room[2]) if room else None

        if room and channel:
            return await ctx.send(f"**{member.mention}, you already have an event room going on! ({channel.mention})**")
        elif room and not channel:
            await self.delete_event_room_by_txt_id(room[2])

        confirm = await ConfirmSkill("Do you want to create a `Sport Event`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not creating it then!**")

        overwrites = await self.get_event_permissions(guild)

        gamer_role = discord.utils.get(
            guild.roles, id=int(os.getenv('FITNESS_HEALTH_ROLE_ID', 123))
        )
        # Adds some perms to the Sport Club role
        overwrites[gamer_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True,
            connect=True, speak=True, view_channel=True)

        events_category = discord.utils.get(
            guild.categories, id=int(os.getenv('EVENTS_CAT_ID', 123)))

        try:
            # Creating text channel
            text_channel = await events_category.create_text_channel(
                name=f"🏃 Sport Event 🏃",
                overwrites=overwrites)
            # Creating voice channel
            voice_channel = await events_category.create_voice_channel(
                name=f"🏃 Sport Event 🏃",
                user_limit=None,
                overwrites=overwrites)
            # Inserts it into the database
            await self.insert_event_room(
                user_id=member.id, vc_id=voice_channel.id, txt_id=text_channel.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**{member.mention}, something went wrong, try again later!**")

        else:
            await ctx.send(f"**{member.mention}, {text_channel.mention} is up and running!**")

    @commands.command(aliases=['close_event'])
    @commands.has_any_role(*[event_host_role_id, event_manager_role_id, mod_role_id, admin_role_id, owner_role_id])
    async def delete_event(self, ctx) -> None:
        """ Deletes an event room. """
        member = ctx.author
        perms = ctx.channel.permissions_for(member)
        delete = False

        if not (room := await self.get_event_room_by_txt_id(ctx.channel.id)):
            return await ctx.send(f"**{member.mention}, this is not an event room, write this command in the event channel you created!**")

        # Checks whether member can delete room
        if room[0] == member.id:  # If it's the owner of the room
            delete = True

        elif perms.administrator or mod_role_id in [r.id for r in member.roles]:  # If it's a staff member
            delete = True

        if delete:
            confirm = await ConfirmSkill(f"**{member.mention}, are you sure you want to delete the event rooms?**").prompt(ctx)
            if confirm:
                try:
                    await self.delete_event_room_by_txt_id(ctx.channel.id)
                    if (room_one := self.client.get_channel(room[1])): 
                        await room_one.delete()
                    if (room_two := self.client.get_channel(room[2])): 
                        await room_two.delete()
                except Exception as e:
                    print(e)
                    await ctx.send(f"**Something went wrong with it, try again later, {member.mention}!**")
            else:
                await ctx.send(f"**Not deleting them, then, {member.mention}!**")

    @commands.command(aliases=['dh'])
    @utils.is_allowed([owner_role_id, admin_role_id, event_manager_role_id], throw_exc=True)
    async def demote_host(self, ctx, member: discord.Member = None) -> None:
        """ Demotes a host to a regular user.
        :param member: The host that is going to be demoted. """

        if not member:
            return await ctx.send("**Please, inform a member to demote to a regular user!**")

        author: discord.Member = ctx.author

        event_host = discord.utils.get(ctx.guild.roles, id=event_host_role_id)
        if event_host not in member.roles:
            return await ctx.send(f"**{member.mention} is not even an Event Host!**")

        try:
            await member.remove_roles(event_host)
        except:
            pass

        # General log
        demote_embed = discord.Embed(
            title="__Event Host Demotion__",
            description=f"{member.mention} has been demoted from an `Event Host` to `regular user` by {author.mention}",
            color=discord.Color.dark_red(),
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=demote_embed)

        # Moderation log
        if demote_log := discord.utils.get(ctx.guild.text_channels, id=promote_demote_log_channel_id):
            demote_embed.set_author(name=member, icon_url=member.display_avatar)
            demote_embed.set_footer(text=f"Demoted by {author}", icon_url=author.display_avatar)
            await demote_log.send(embed=demote_embed)

        try:
            await member.send(f"**You have been demoted from an `Event Host` to a regular user!**")
        except:
            pass
    
    @commands.command(aliases=['ph'])
    @utils.is_allowed([owner_role_id, admin_role_id, event_manager_role_id], throw_exc=True)
    async def promote_host(self, ctx, member: discord.Member = None) -> None:
        """ Promotes a regular user to a host.
        :param member: The user that is going to be promoted. """

        if not member:
            return await ctx.send("**Please, inform a member to promote to event host!**")

        author: discord.Member = ctx.author

        event_host = discord.utils.get(ctx.guild.roles, id=event_host_role_id)
        if event_host in member.roles:
            return await ctx.send(f"**{member.mention} already is an Event Host!**")

        try:
            await member.add_roles(event_host)
        except:
            pass

        # General log
        promote_embed = discord.Embed(
            title="__Event Host Promotion__",
            description=f"{member.mention} has been promoted to `Event Host` by {author.mention}",
            color=discord.Color.green(),
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=promote_embed)

        # Moderation log
        if promote_log := discord.utils.get(ctx.guild.text_channels, id=promote_demote_log_channel_id):
            promote_embed.set_author(name=member, icon_url=member.display_avatar)
            promote_embed.set_footer(text=f"Promoted by {author}", icon_url=author.display_avatar)
            await promote_log.send(embed=promote_embed)

        try:
            await member.send(f"**You have been promoted to `Event Host`**")
        except:
            pass

    @commands.command(aliases=['ddo'])
    @utils.is_allowed([owner_role_id, admin_role_id, event_manager_role_id], throw_exc=True)
    async def demote_debate_organizer(self, ctx, member: discord.Member = None) -> None:
        """ Demotes a debate organizer to a regular user.
        :param member: The host that is going to be demoted. """

        if not member:
            return await ctx.send("**Please, inform a member to demote to a regular user!**")

        author: discord.Member = ctx.author

        debate_organizer = discord.utils.get(ctx.guild.roles, id=debate_organizer_role_id)
        if debate_organizer not in member.roles:
            return await ctx.send(f"**{member.mention} is not even a `Debate Organizer`!**")

        try:
            await member.remove_roles(debate_organizer)
        except:
            pass

        # General log
        demote_embed = discord.Embed(
            title="__Debate Organizer Demotion__",
            description=f"{member.mention} has been demoted from a `Debate Organizer` to `regular user` by {author.mention}",
            color=discord.Color.dark_red(),
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=demote_embed)

        # Moderation log
        if demote_log := discord.utils.get(ctx.guild.text_channels, id=promote_demote_log_channel_id):
            demote_embed.set_author(name=member, icon_url=member.display_avatar)
            demote_embed.set_footer(text=f"Demoted by {author}", icon_url=author.display_avatar)
            await demote_log.send(embed=demote_embed)

        try:
            await member.send(f"**You have been demoted from a `Debate Organizer` to a regular user!**")
        except:
            pass
    
    @commands.command(aliases=['pdo'])
    @utils.is_allowed([owner_role_id, admin_role_id, event_manager_role_id], throw_exc=True)
    async def promote_debate_organizer(self, ctx, member: discord.Member = None) -> None:
        """ Promotes a regular user to a debate organizer.
        :param member: The user that is going to be promoted. """

        if not member:
            return await ctx.send("**Please, inform a member to promote to debate organizer!**")

        author: discord.Member = ctx.author

        debate_organizer = discord.utils.get(ctx.guild.roles, id=debate_organizer_role_id)
        if debate_organizer in member.roles:
            return await ctx.send(f"**{member.mention} already is a `Debate Organizer`!**")

        try:
            await member.add_roles(debate_organizer)
        except:
            pass

        # General log
        promote_embed = discord.Embed(
            title="__Debate Organizer Promotion__",
            description=f"{member.mention} has been promoted to `Debate Organizer` by {author.mention}",
            color=discord.Color.green(),
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=promote_embed)

        # Moderation log
        if promote_log := discord.utils.get(ctx.guild.text_channels, id=promote_demote_log_channel_id):
            promote_embed.set_author(name=member, icon_url=member.display_avatar)
            promote_embed.set_footer(text=f"Promoted by {author}", icon_url=author.display_avatar)
            await promote_log.send(embed=promote_embed)

        try:
            await member.send(f"**You have been promoted to `Debate Organizer`**")
        except:
            pass


def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(EventManagement(client))
