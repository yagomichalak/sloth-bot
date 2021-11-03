import discord
from discord.ext import commands

from typing import List, Dict, Union
from extra.prompt.menu import Confirm
from extra import utils

from datetime import datetime

from extra.smartrooms.rooms import SmartRoom

class GalaxyRoomCommands(commands.Cog):
    """ Class for GalaxyRoom management related commands. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.group(aliases=['gr', 'galaxy_room', 'galaxyroom'])
    async def galaxy(self, ctx) -> None:
        """ Command for managing Galaxy Rooms. """

        if ctx.invoked_subcommand:
            return

        cmd = ctx.command
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

    @galaxy.command(name="allow", aliases=['permit'])
    async def _galaxy_allow(self, ctx) -> None:
        """ Allows one or more members to join your channels.
        :param members: The members to allow. """

        members = await utils.get_mentions(message=ctx.message)
        member = ctx.author

        if member in members:
            members.remove(member)

        if not members:
            return await ctx.send(f"**Inform one or more members to allow, {member.mention}!**")

        smart_room = await self.get_smartroom(txt_id=ctx.channel.id)
        if not smart_room or smart_room.room_type != 'galaxy':
            return await ctx.send(f"**This is not a `Galaxy Room`, {member.mention}!**")

        if smart_room.owner.id != member.id:
            return await ctx.send(f"**This is not your `Galaxy Room`, {member.mention}!**")


        allowed = await smart_room.handle_permissions(members)
    
        if not allowed:
            return await ctx.send(f"**For some reason, I couldn't allow any of those members, {member.mention}!**")

        allowed_members = ', '.join(allowed)
        await ctx.send(f"**{allowed_members} {'have' if len(allowed) > 1 else 'has'} been allowed, {member.mention}!**")

    @galaxy.command(name="forbid", aliases=['prohibit'])
    async def _galaxy_forbid(self, ctx) -> None:
        """ Forbids one or more members from joining your channels.
        :param members: The members to forbid. """

        members = await utils.get_mentions(message=ctx.message)
        member = ctx.author

        if member in members:
            members.remove(member)

        if not members:
            return await ctx.send(f"**Inform one or more members to forbid, {member.mention}!**")

        smart_room = await self.get_smartroom(txt_id=ctx.channel.id)
        if not smart_room or smart_room.room_type != 'galaxy':
            return await ctx.send(f"**This is not a `Galaxy Room`, {member.mention}!**")

        if smart_room.owner.id != member.id:
            return await ctx.send(f"**This is not your `Galaxy Room`, {member.mention}!**")

        forbid = await smart_room.handle_permissions(members, allow=False)

        if not forbid:
            return await ctx.send(f"**For some reason, I couldn't forbid any of those members, {member.mention}!**")

        forbidden_members = ', '.join(forbid)

        await ctx.send(f"**{forbidden_members} {'have' if len(forbid) > 1 else 'has'} been forbidden, {member.mention}!**")


    # Other useful commands
    @galaxy.command(name="info", aliases=['creation', 'expiration'])
    async def _galaxy_info(self, ctx) -> None:
        """ Shows the creation and expiration time of the user's Galaxy Rooms. """

        member: discord.Member = ctx.author

        smart_room = await self.get_smartroom(txt_id=ctx.channel.id)
        if not smart_room or smart_room.room_type != 'galaxy':
            return await ctx.send(f"**This is not a `Galaxy Room`, {member.mention}!**")

        if smart_room.owner.id != member.id:
            return await ctx.send(f"**This is not your `Galaxy Room`, {member.mention}!**")

        user_ts = smart_room.creation_ts if not smart_room.edited_ts else smart_room.edited_ts
        the_time = await utils.get_timestamp()
        deadline = user_ts + 1209600

        embed = discord.Embed(
            title=f"__{ctx.author.name}'s Rooms' Info__",
            description=f'''**Created at:** {datetime.fromtimestamp(user_ts)}
            **Expected expiration:** {datetime.fromtimestamp(deadline)}\n''',
            color=ctx.author.color,
            timestamp=ctx.message.created_at)

        embed.set_thumbnail(url=ctx.author.display_avatar)
        embed.set_footer(text="Requested")

        seconds_left = deadline - the_time
        if seconds_left >= 86400:
            embed.description += f"**Time left:** {round(seconds_left/3600/24)} days left"
        elif seconds_left >= 3600:
            embed.description += f"**Time left:** {round(seconds_left/3600)} hours left"
        elif seconds_left >= 60:
            embed.description += f"**Time left:** {round(seconds_left/60)} minutes left"
        else:
            embed.description += f"**Time left:** {round(seconds_left)} seconds left"

        await ctx.send(embed=embed)

    @galaxy.command(name="pay_rent", aliases=['pr', 'payrent', 'rent', 'renew'])
    async def _galaxy_pay_rent(self, ctx) -> None:
        """ Delays the user's Galaxy Rooms deletion by 14 days.
        
        * Price:
        - +250 for each Thread
        - +500 for the additional Voice Channel, if there is one.
        
        Max Rent Possible: 2500łł
        
        PS: You can either have an extra Voice Channel or up to 4 Threads. """

        if not ctx.guild:
            return await ctx.send("**Don't use it here!**")

        member: discord.Member = ctx.author

        smart_room = await self.get_smartroom(txt_id=ctx.channel.id)
        if not smart_room or smart_room.room_type != 'galaxy':
            return await ctx.send(f"**This is not a `Galaxy Room`, {member.mention}!**")

        if smart_room.owner.id != member.id:
            return await ctx.send(f"**This is not your `Galaxy Room`, {member.mention}!**")

        the_time = await utils.get_timestamp()
        user_ts = smart_room.creation_ts if not smart_room.edited_ts else smart_room.edited_ts
        seconds_left = (user_ts + 1209600) - the_time

        # # Checks rooms deletion time
        if seconds_left > 172800:
            return await ctx.send(f"**You can only renew your rooms at least 2 days before their deletion time, {member.mention}!**")

        money: int = await smart_room.get_rent_price()

        confirm = await Confirm(f"Are you sure you want to renew your Galaxy Room for `{money}łł`, {member.mention}?").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it then, {member.mention}!**")

        # Checks if the user has money for it (1500-2000łł)
        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_currency = await SlothCurrency.get_user_currency(member.id)
        if user_currency[0][1] < money:
            return await ctx.send(f"**You don't have enough money to renew your rooms, {member.mention}!** `({money}łł)`")

        await smart_room.update(self, edited_ts=the_time, notified=0)
        await SlothCurrency.update_user_money(member.id, -money)

        await ctx.send(f"**{member.mention}, Galaxy Rooms renewed! `(-{money}łł)`**")

    
    @galaxy.command(name="transfer_ownership", aliases=['transfer', 'to', 'transferownership'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def _galaxy_transfer_ownership(self, ctx, member: discord.Member = None) -> None:
        """ Transfer the Galaxy Room's ownership  to someone else.
        :param member: The member to transfer the Galaxy Room to.
        
        PS: Only the owner of the Galaxy Room and admins can use this. """

        if not ctx.guild:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("**Don't use it here!**")

        author = ctx.author
        channel = ctx.channel

        if not member:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

        if not (cat := channel.category):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is definitely not a Galaxy Room, {author.mention}!**")

        if not (galaxy_room := await self.get_smartroom(cat_id=cat.id)):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is not a Galaxy Room, {author.mention}!**")

        perms = channel.permissions_for(author)
        if author.id != galaxy_room.owner.id and not perms.administrator:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You don't have permission to do this, {author.mention}!**")
        
        if member.id == galaxy_room.owner.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You cannot transfer the Galaxy Room to the same owner, {author.mention}!**")

        if await self.get_smartroom(user_id=member.id):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You cannot transfer the Galaxy Room to {member.mention} because they have one already, {author.mention}!**")

        confirm = await Confirm(
            f"**Are you sure you want to transfer the ownership of this Galaxy Room from {galaxy_room.owner.mention} to {member.mention}, {author.mention}?**"
            ).prompt(ctx)
        if not confirm:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Not deleting it then, {author.mention}!**")

        try:
            await galaxy_room.update(self, user_id=member.id)
            await galaxy_room.handle_permissions([member])
        except:
            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"**Something went wrong with it, please contact an admin, {author.mention}!**")
        else:
            await ctx.send(f"**Successfully transferred the ownership of this Galaxy Room from {galaxy_room.owner.mention} to {member.mention}!**")


    @galaxy.command(name="close", aliases=['close_room', 'closeroom', 'kill', 'terminate', 'delete', 'del'])
    async def _galaxy_close(self, ctx) -> None:
        """ Deletes a Galaxy Room. """

        if not ctx.guild:
            return await ctx.send("**Don't use it here!**")

        member = ctx.author
        channel = ctx.channel

        if not (cat := channel.category):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is definitely not a Galaxy Room, {member.mention}!**")

        if not (galaxy_room := await self.get_smartroom(cat_id=cat.id)):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is not a Galaxy Room, {member.mention}!**")

        perms = channel.permissions_for(member)
        if member.id != galaxy_room.owner.id and not perms.administrator:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You don't have permission to do this, {member.mention}!**")

        confirm = await Confirm(f"**Are you sure you want to close this Galaxy Room, {member.mention}!**").prompt(ctx)
        if not confirm:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Not deleting it then, {member.mention}!**")

        member = self.client.get_user(galaxy_room.owner.id)
        rooms = galaxy_room.channels
        try:
            await self.delete_things(rooms)
            await member.send(f"**Hey! Your rooms got deleted!**")
        except Exception:
            pass
        finally:
            await galaxy_room.delete()


    @galaxy.group(name="add_channel", aliases=['ac'])
    async def _galaxy_add_channel(self, ctx) -> None:
        """ Adds either a Text or a Voice Channel to
        the user's Galaxy Room. """

        if ctx.invoked_subcommand:
            return

        cmd = ctx.command
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

    @_galaxy_add_channel.command(name='thread', aliases=['th', 'thread_channel', 'text', 'txt', 'text_channel'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def _galaxy_add_channel_thread(self, ctx, *, name: str = None) -> None:
        """ Adds a Text Channel.
        :param name: The name of the Text Channel. """

        member = ctx.author

        if not name:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a channel name, {member.mention}!**")

        if len(name) > 20:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("**Please inform a name having 1-20 characters!**")

        if not (category := ctx.channel.category):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is definitely not a GalaxyRoom, {member.mention}!**")

        smart_room = await self.get_smartroom(cat_id=category.id)
        if not smart_room or smart_room.room_type != 'galaxy':
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is not a GalaxyRoom, {member.mention} !**")

        if smart_room.owner.id != member.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is not your GalaxyRoom, {member.mention}!**")

        vcs, txts = smart_room.voice_channels, smart_room.text_channels

        if len(vcs) == 2:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You cannot add threads because you chose to have a second Voice Channel instead, {member.mention}!**")

        if len(txts) >= 5:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You cannot add more thread channels, {member.mention}!**")

        if len(vcs) + len(txts) >= 6:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You reached your maximum amount of channels in your Galaxy Rooms, {member.mention}!**")

        money: int = await smart_room.get_rent_price()
        confirm = await Confirm(
            f"**Do you want to add an extra `Thread` channel for `250łł`, {member.mention}?**\n\n||From now on, you're gonna be charged `{money}łł` in your next fortnight rents||"
            ).prompt(ctx)
        if not confirm:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Not doing it then, {member.mention}!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')
        if not (user_currency := await SlothCurrency.get_user_currency(member.id)):
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))
            return await member.send( 
                embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                view=view)

        if user_currency[0][1] < 250:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("**You don't have enough money to buy this service!**")

        channel = smart_room.txt
            
        #, auto_archive_duration=10080
        if not (thread := await smart_room.try_to_create(kind='thread', channel=channel, owner=member, name=name)):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

        threads = {'th_id': smart_room.th, 'th2_id': smart_room.th2, 'th3_id': smart_room.th3, 'th4_id': smart_room.th4}
        available_thread: str = list(th[0] for th in threads.items() if not th[1])[0]
        formatted_keyword: Dict[str, int] = {available_thread:thread.id}

        await smart_room.update(self, **formatted_keyword)
        await SlothCurrency.update_user_money(member.id, -250)
        await ctx.send(f"**Thread Channel created, {member.mention}!** ({thread.mention})")


    @_galaxy_add_channel.command(name='voice', aliases=['vc', 'voice_channel'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def _galaxy_add_channel_voice(self, ctx, limit: int = None, *, name: str = None) -> None:
        """ Adds a Voice Channel.
        :param limit: The user limit of the Voice Cchannel.
        :param name: The name of the Voice Channel. """

        member = ctx.author

        if limit is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a user limit for your vc, {member.mention}!** `(0 for limitless)`")
        
        if limit < 0 or limit > 99:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a user limit between `0-99`, {member.mention}!**")

        if not name:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a channel name, {member.mention}!**")

        if len(name) > 20:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("**Please inform a name having 1-20 characters!**")

        if not (category := ctx.channel.category):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is definitely not a GalaxyRoom, {member.mention}!**")

        smart_room = await self.get_smartroom(cat_id=category.id)
        if not smart_room or smart_room.room_type != 'galaxy':
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is not a GalaxyRoom, {member.mention} !**")

        if smart_room.owner.id != member.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is not your GalaxyRoom, {member.mention}!**")

        vcs, txts = smart_room.voice_channels, smart_room.text_channels
        money: int = await smart_room.get_rent_price()

        if len(vcs) == 2:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You cannot add more voice channels, {member.mention}!**")
            
        if len(vcs) + len(txts) >= 3:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You reached your maximum amount of channels in your Galaxy Room, {member.mention}!**")

        confirm = await Confirm(
            f"**Do you want to add an extra `Voice Channel` for `500łł`, {member.mention}?**\n\n||From now on, you're gonna be charged `{money}łł` in your next fortnight rents||"
            ).prompt(ctx)
        if not confirm:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Not doing it then, {member.mention}!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')
        if not (user_currency := await SlothCurrency.get_user_currency(member.id)):
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))
            return await member.send( 
                embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                view=view)

        if user_currency[0][1] < 500:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("**You don't have enough money to buy this service!**")


        cat = smart_room.cat
            
        if not (vc := await self.try_to_create(kind='voice', category=cat, name=name, user_limit=limit)):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Channels limit reached, creation cannot be completed, try again later!**")

        await smart_room.update(self, vc2_id=vc.id)
        await SlothCurrency.update_user_money(member.id, -500)
        await ctx.send(f"**Voice Channel created, {member.mention}!** ({vc.mention})")

    @galaxy.group(name="delete_channel", aliases=['dc', 'deletechannel', 'remove_channel', 'removechannel', 'rc'])
    async def _galaxy_delete_channel(self, ctx) -> None:
        """ Deletes either a Text or a Voice Channel from
        the user's Galaxy Room. """

        if ctx.invoked_subcommand:
            return

        cmd = ctx.command
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

    @_galaxy_delete_channel.command(name='thread', aliases=['thread_channel', 'th', 'text', 'txt', 'text_channel'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def _galaxy_delete_channel_thread(self, ctx) -> None:
        """ Deletes the user's second Text Channel from their Galaxy Room. """

        member = ctx.author

        if not (category := ctx.channel.category):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is definitely not a GalaxyRoom, {member.mention}!**")

        smart_room = await self.get_smartroom(cat_id=category.id)
        if not smart_room or smart_room.room_type != 'galaxy':
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is not a GalaxyRoom, {member.mention} !**")

        if smart_room.owner.id != member.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**This is not your GalaxyRoom, {member.mention}!**")


        txts = smart_room.text_channels
        money: int = await smart_room.get_rent_price()

        if len(txts) <= 1:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You don't have a Thread to delete, {member.mention}!**")

        threads = {'th_id': smart_room.th, 'th2_id': smart_room.th2, 'th3_id': smart_room.th3, 'th4_id': smart_room.th4}
        selected_thread: str = list(filter(lambda th: th[1].id == ctx.channel.id, threads.items()))[0]
        confirm = await Confirm(
            f"**Are you sure you want to delete {selected_thread[1].mention}, {member.mention}?**\n\n||From now on, you're gonna be charged `{money}łł` in your next fortnight rents||"
            ).prompt(ctx)

        if not confirm:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Not doing it then, {member.mention}!**")

        try:
            thread_keyword = {selected_thread[0]: 'NULL'}
            print(thread_keyword)
            await smart_room.update(self, **thread_keyword)
        except Exception as e:
            print(e)
            await ctx.send(f"**For some reason I couldn't delete it, try again, {member.mention}!**")
        else:
            await selected_thread[1].delete()
        


    @_galaxy_delete_channel.command(name='voice', aliases=['vc', 'voice_channel'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def _galaxy_delete_channel_voice(self, ctx) -> None:
        """ Deletes the user's second Voice Channel from their Galaxy Room. """

        member = ctx.author

        if not (user_rooms := await self.get_user_all_galaxy_rooms(member.id)):
            return await ctx.send(f"**You don't have any Galaxy Rooms!**")

        if ctx.channel.id not in user_rooms:
            return await ctx.send(f"**You can only use this command in your Galaxy Rooms, {member.mention}!**")

        vcs, txts = await self.order_rooms(user_rooms)
        money: int = await self.get_rent_price(len(txts), len(vcs)-1)

        if len(vcs) != 2:
            return await ctx.send(f"**You don't have a second Voice Channel to delete, {member.mention}!**")

        confirm = await Confirm(
            f"**Are you sure you want to delete <#{vcs[1]}>, {member.mention}?**\n\n||From now on, you're gonna be charged `{money}łł` in your next fortnight rents||"
            ).prompt(ctx)
        
        if not confirm:
            return await ctx.send(f"**Not doing it then, {member.mention}!**")

        try:
            await self.update_vc_2(member.id)
        except:
            await ctx.send(f"**For some reason I couldn't delete it, try again, {member.mention}!**")
        else:
            if vc := discord.utils.get(ctx.guild.channels, id=vcs[1]):
                await self.delete_things([vc])

            await ctx.send(f"**Voice Channel deleted, {member.mention}!**")



    # @galaxy.command(name="allow_tribe", aliases=['at', 'permit_tribe', 'add_tribe', 'allowtribe', 'permittribe', 'addtribe'])
    # @commands.cooldown(1, 60, commands.BucketType.user)
    # async def _galaxy_allow_tribe(self, ctx) -> None:
    #     """ Allows your Tribe members into your Galaxy Room.  """

    #     member = ctx.author

    #     user_galaxy = await self.get_galaxy_txt(member.id, ctx.channel.category.id)
    #     if not user_galaxy:
    #         return await ctx.send(f"**This is not your room, so you cannot allow people in it, {member.mention}!**")

    #     SlothClass = self.client.get_cog('SlothClass')
    #     user_tribe = await SlothClass.get_tribe_info_by_user_id(member.id)
    #     if not user_tribe['name']:
    #         return await ctx.send(f"**You don't even have a tribe, you cannot do this, {member.mention}!**")

    #     members: List[List[Union[int, str]]] = await SlothClass.get_tribe_members(tribe_name=user_tribe['name'])
    #     members: List[discord.Member] = [m for m_id in members if (m := discord.utils.get(ctx.guild.members, id=m_id[0]))]

    #     if member in members:
    #         members.remove(member)

    #     if not members:
    #         return await ctx.send(f"**You don't have members in your tribe, {member.mention}!**")

    #     async with ctx.typing():
    #         allowed = await self.handle_permissions(members, user_galaxy, ctx.guild)

    #         if not allowed:
    #             return await ctx.send(f"**For some reason, I couldn't allow any of those members, {member.mention}!**")

    #         text: str = "**{lendisa} {subjplural} from {tribe_name} {verbplural} been allowed, {mention}!**".format(
    #             lendisa=len(allowed),
    #             subjplural='people' if len(allowed) > 1 else 'person',
    #             tribe_name=user_tribe['name'],
    #             verbplural='have' if len(allowed) > 1 else 'has',
    #             mention=member.mention)

    #         await ctx.send(text)

    # @galaxy.command(name="forbid_tribe", aliases=[
    #     'dt', 'disallow_tribe', 'delete_tribe', 'removetribe', 'disallowtribe', 'deletetribe', 'deltribe',
    #     'forbidtribe', 'remove_tribe', 'ft'])
    # @commands.cooldown(1, 60, commands.BucketType.user)
    # async def _galaxy_remove_tribe(self, ctx) -> None:
    #     """ Removes your Tribe members from your Galaxy Room.. """

    #     member = ctx.author

    #     user_galaxy = await self.get_galaxy_txt(member.id, ctx.channel.category.id)
    #     if not user_galaxy:
    #         return await ctx.send(f"**This is not your room, so you cannot allow people in it, {member.mention}!**")

    #     SlothClass = self.client.get_cog('SlothClass')
    #     user_tribe = await SlothClass.get_tribe_info_by_user_id(member.id)
    #     if not user_tribe['name']:
    #         return await ctx.send(f"**You don't even have a tribe, you cannot do this, {member.mention}!**")

    #     members: List[List[Union[int, str]]]  = await SlothClass.get_tribe_members(tribe_name=user_tribe['name'])
    #     members: List[discord.Member] = [m for m_id in members if (m := discord.utils.get(ctx.guild.members, id=m_id[0]))]

    #     if member in members:
    #         members.remove(member)

    #     if not members:
    #         return await ctx.send(f"**You don't have members in your tribe, {member.mention}!**")

    #     async with ctx.typing():
    #         disallowed = await self.handle_permissions(members, user_galaxy, ctx.guild, allow=False)
        
    #         if not disallowed:
    #             return await ctx.send(f"**For some reason, I couldn't allow any of those members, {member.mention}!**")

    #         text: str = "**{lendisa} {subjplural} from {tribe_name} {verbplural} been disallowed, {mention}!**".format(
    #             lendisa=len(disallowed),
    #             subjplural='people' if len(disallowed) > 1 else 'person',
    #             tribe_name=user_tribe['name'],
    #             verbplural='have' if len(disallowed) > 1 else 'has',
    #             mention=member.mention)

    #         await ctx.send(text)