import discord
from discord.ext import commands, menus, tasks
from mysqldb import DatabaseCore

from .player import Player, Skill
from .enums import QuestEnum
from extra.menu import ConfirmSkill, SwitchTribePages
from extra.prompt.menu import Confirm
from extra import utils

import os
from datetime import datetime
from typing import List, Tuple, Union, Dict, Any, Optional, Callable
from random import choice

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID', 123))
approve_thumbnail_channel_id = int(os.getenv('APPROVE_THUMBNAIL_CHANNEL_ID', 123))


class Munk(Player):

    emoji = '<:Munk:839498018712715284>'

    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

    @tasks.loop(minutes=1)
    async def check_mission_one_completion(self) -> None:
        """ Checks whether members completed their mission of number 1. """

        skill_actions = await self.get_skill_actions_by_skill_type_and_int_content(skill_type="quest", int_content=5)
        filtered_skill_actions = [
            skill_action for skill_action in skill_actions
            if skill_action[7] == 1
        ]
        for skill_action in filtered_skill_actions:
            try:
                await self.complete_quest(skill_action[0], 1)
            except:
                pass

    @tasks.loop(minutes=1)
    async def check_mission_six_completion(self) -> None:
        """ Checks whether members completed their mission of number 6. """

        skill_actions = await self.get_skill_actions_by_skill_type_and_int_content(skill_type="quest", int_content=1)
        filtered_skill_actions = [
            skill_action for skill_action in skill_actions
            if skill_action[7] == 6
        ]
        for skill_action in filtered_skill_actions:
            try:
                await self.complete_quest(skill_action[0], 6)
            except:
                pass

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def on_raw_reaction_add_munk(self, payload) -> None:
        """ Checks reactions related to skill actions. """

        # Checks if it wasn't a bot's reaction
        if not payload.guild_id:
            return

        # Checks whether it's a valid member and not a bot
        if not payload.member or payload.member.bot:
            return

        if payload.channel_id != approve_thumbnail_channel_id:
            return

        skill_action = await self.get_skill_action_by_message_id_and_skill_type(message_id=payload.message_id, skill_type='thumbnail_request')
        if skill_action is not None:
            emoji = str(payload.emoji)

            # Checks whether it's a steal
            if emoji == '✅':

                await self.delete_skill_action_by_message_id(payload.message_id)
                channel = self.client.get_channel(skill_action[5])

                message = await channel.fetch_message(skill_action[4])
                if message:
                    tribe = await self.get_tribe_info_by_user_id(user_id=skill_action[0])
                    message_embed = discord.Embed(
                        title="Thumbnail Approved!",
                        description=f"**<@{payload.user_id}>, approved your tribe `{tribe['name']}`'s thumbnail/logo, <@{skill_action[0]}>!**",
                        color=discord.Color.green(),
                        url=tribe['link']
                    )
                    message_embed.set_image(url=skill_action[8])
                    await self.bots_txt.send(content=f"<@{skill_action[0]}>", embed=message_embed)
                    await message.delete()
                    await self.update_tribe_thumbnail(user_id=skill_action[0], tribe_name=tribe['name'], link=skill_action[8])

            elif emoji == '❌':

                await self.delete_skill_action_by_message_id(payload.message_id)
                channel = self.client.get_channel(skill_action[5])
                message = await channel.fetch_message(skill_action[4])
                if message:
                    tribe = await self.get_tribe_info_by_user_id(user_id=skill_action[0])
                    message_embed = discord.Embed(
                        title="Thumbnail Refused!",
                        description=f"**<@{payload.user_id}>, refused your tribe `{tribe['name']}`'s thumbnail/logo, <@{skill_action[0]}>!**",
                        color=discord.Color.red(),
                        url=tribe['link']
                    )
                    message_embed.set_image(url=skill_action[8])
                    await self.bots_txt.send(content=f"<@{skill_action[0]}>", embed=message_embed)
                    await message.delete()

    @commands.command()
    @Player.poisoned()
    @Player.skill_on_cooldown()
    @Player.skills_locked()
    @Player.user_is_class('munk')
    @Player.skill_mark()
    async def munk(self, ctx, target: discord.Member = None) -> None:
        """ Converts a user into a real Munk.
        :param target: The person you want to convert to a Munk. """

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

        attacker = ctx.author

        attacker_fx = await self.get_user_effects(attacker)

        if 'knocked_out' in attacker_fx:
            return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            return await ctx.send(f"**Please, choose a member to use the `Munk` skill, {attacker.mention}!**")

        if target.bot:
            return await ctx.send(f"**You cannot convert a bot into a `Munk`, {attacker.mention}!**")

        if attacker.id == target.id:
            return await ctx.send(f"**You cannot convert yourself, since you are already a `Munk`, {attacker.mention}!**")

        target_fx = await self.get_user_effects(target)

        if 'munk' in target_fx:
            return await ctx.send(f"**{target.mention} is already a `Munk`, {attacker.mention}!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot convert someone who doesn't have an account, {attacker.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot convert someone who has a `default` Sloth class, {attacker.mention}!**")

        if 'protected' in target_fx:
            return await ctx.send(f"**{attacker.mention}, you cannot convert {target.mention} into a `Munk`, because they are protected against attacks!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to convert {target.mention} into a `Munk`?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not converting them, then!**")
        
        if ctx.invoked_with == 'mirror':
            mirrored_skill = await self.get_skill_action_by_user_id_and_skill_type(user_id=attacker.id, skill_type='mirror')
            if not mirrored_skill:
                return await ctx.send(f"**Something went wrong with this, {attacker.mention}!**")
        else:
            _, exists = await Player.skill_on_cooldown(skill=Skill.ONE).predicate(ctx)

        try:
            await target.edit(nick=f"{target.display_name} Munk")
            current_timestamp = await utils.get_timestamp()

            if ctx.invoked_with != 'mirror':
                if exists:
                    await self.update_user_skill_ts(attacker.id, Skill.ONE, current_timestamp)
                else:
                    await self.insert_user_skill_cooldown(attacker.id, Skill.ONE, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)
            munk_embed = await self.get_munk_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
            msg = await ctx.send(embed=munk_embed)
        except Exception as e:
            print(e)
            return await ctx.send(f"**Something went wrong and your `Munk` skill failed, {attacker.mention}!**")

        else:
            await msg.edit(content=f"<@{target.id}>")
            if 'reflect' in target_fx and 'munk' not in attacker_fx:
                await self.reflect_attack(ctx, attacker, target, 'munk')

    async def get_munk_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
        """ Makes an embedded message for a munk action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the munk skill.
        :param target_id: The ID of the target member that is gonna be protected. """

        timestamp = await utils.get_timestamp()

        munk_embed = discord.Embed(
            title="A Munk Convertion has been delightfully performed!",
            description=f"🐿️ <@{perpetrator_id}> converted <@{target_id}> into a `Munk`! 🐿️",
            color = discord.Color.green(),
            timestamp=datetime.fromtimestamp(timestamp)
        )

        munk_embed.set_thumbnail(url="https://languagesloth.com/media/sloth_classes/Munk.png")
        munk_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return munk_embed

    async def get_join_tribe_embed(self, channel, inviter: discord.Member, target: discord.Member, tribe: Dict[str, Union[int, str]]) -> discord.Embed:
        """ Makes an embedded message for a tribe joining.
        :param channel: The context channel.
        :param inviter: The inviter.
        :param target_id: The target member that is gonna be invited to a tribe.
        :param tribe: The tribe and its information. """

        timestamp = await utils.get_timestamp()

        join_tribe_embed = discord.Embed(
            title="Someone just joined a Tribe!",
            description=f"🏕️ {target.mention} just joined `{tribe['name']}`! 🏕️",
            color=discord.Color.green(),
            timestamp=datetime.fromtimestamp(timestamp),
            url=tribe['link']
        )

        join_tribe_embed.set_author(name=inviter, icon_url=inviter.display_avatar)
        if tribe['thumbnail']:
            join_tribe_embed.set_thumbnail(url=tribe['thumbnail'])
        join_tribe_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return join_tribe_embed

    async def get_tribe_info_by_name(self, name: str) -> Dict[str, Union[str, int]]:
        """ Gets information about a specific tribe.
        :param name: The name of the tribe. """

        tribe = await self.db.execute_query("SELECT * FROM UserTribe WHERE tribe_name = %s", (name,), fetch="one")

        tribe_info = {
            'owner_id': None,
            'name': None,
            'description': None,
            'two_emojis': None,
            'thumbnail': None,
            'form': None,
            'link': None
        }

        if tribe:
            tribe_info = {
                'owner_id': tribe[0],
                'name': tribe[1],
                'description': tribe[2],
                'two_emojis': tribe[3],
                'thumbnail': tribe[4],
                'form': tribe[5],
                'link': f"https://languagesloth.com/tribes/{tribe[6]}/"
            }

        return tribe_info

    async def get_tribe_info_by_user_id(self, user_id: int) -> Dict[str, Union[str, int]]:
        """ Gets information about a specific tribe.
        :param user_id: The ID of the user owner of the tribe. """

        tribe = await self.db.execute_query("SELECT * FROM UserTribe WHERE user_id = %s", (user_id,), fetch="one")

        tribe_info = {
            'owner_id': None,
            'name': None,
            'description': None,
            'two_emojis': None,
            'thumbnail': None,
            'form': None,
            'link': None
        }

        if tribe:
            tribe_info = {
                'owner_id': tribe[0],
                'name': tribe[1],
                'description': tribe[2],
                'two_emojis': tribe[3],
                'thumbnail': tribe[4],
                'form': tribe[5],
                'link': f"https://languagesloth.com/tribes/{tribe[6]}/"
            }

        return tribe_info

    async def get_tribe_member(self, user_id: int) -> List[Union[str, int]]:
        """ Gets a Tribe Member.
        :param user_id: The ID of the tribe member to get. """

        return await self.db.execute_query("SELECT * FROM TribeMember WHERE member_id = %s", (user_id,), fetch="one")

    async def get_tribe_members(self, tribe_owner_id: int = None, tribe_name: str = None) -> List[List[Union[int, str]]]:
        """ Gets a list of IDs of members of a particular tribe.
        :param tribe_owner_id: The ID of the owner of the tribe (Optional).
        :param tribe_name: The name of the tribe. (Optional).
        Ps: At least one of the parameters has to be provided. """

        tribe_members: List[int] = []

        if tribe_owner_id:
            tribe = await self.db.execute_query("SELECT tribe_name FROM UserTribe WHERE user_id = %s", (tribe_owner_id,), fetch="one")
            tribe_members = await self.db.execute_query("SELECT member_id, tribe_role FROM TribeMember WHERE tribe_name = %s", (tribe[0],), fetch="all")

        elif tribe_name:
            tribe_members = await self.db.execute_query("SELECT member_id, tribe_role FROM TribeMember WHERE tribe_name = %s", (tribe_name,), fetch="all")

        return tribe_members

    async def get_sloth_class_tribe_members(self, tribe_name: str) -> List[List[Union[int, str]]]:
        """ Gets a list of Sloth Classes with counters from a specific tribe.
        :param tribe_name: The name of the tribe.. """

        return await self.db.execute_query("""
            SELECT sp.sloth_class, COUNT(*)
            FROM TribeMember AS tm
            RIGHT JOIN
                SlothProfile AS sp
            ON
                sp.user_id = tm.member_id
            WHERE tm.tribe_name = %s
            GROUP BY sp.sloth_class
        """, (tribe_name,), fetch="all")

    @commands.group(aliases=['tb'])
    @Player.poisoned()
    @Player.kidnapped()
    async def tribe(self, ctx) -> None:
        """ Command for managing and interacting with a tribe.
        (Use this without a subcommand to see all subcommands available) """
        if ctx.invoked_subcommand:
            return

        cmd = self.client.get_command('tribe')
        prefix = self.client.command_prefix
        subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands
            ]

        subcommands = '\n'.join(subcommands)
        items_embed = discord.Embed(
            title="__Subcommads__:",
            description=f"```apache\n{subcommands}```",
            color=ctx.author.color,
            timestamp=ctx.message.created_at
        )

        await ctx.send(embed=items_embed)

    @tribe.command(aliases=['request_logo', 'ask_thumbnail', 'ask_logo'])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def request_thumbnail(self, ctx, image_url: str = None) -> None:
        """ Request a thumbnail for your tribe.
        :param image_url: The URL link of the thumbnail image. """

        requester = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

        if not image_url:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"You need to inform an image URL, {requester.mention}!**")

        if not image_url.startswith('https://'):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"You need to inform an image URL that has HTTPS in it, {requester.mention}!**")

        if len(image_url) > 200:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"You need to inform an image URL within 200 characters, {requester.mention}!**")

        user_tribe = await self.get_tribe_info_by_user_id(user_id=requester.id)
        if not user_tribe['name']:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You don't even have a tribe, you cannot request it, {requester.mention}!**")

        confirm = await ConfirmSkill(content=requester.mention,
            msg=f"**Are you sure you want to request [this]({image_url}) to be `{user_tribe['name']}`'s thumbnail/logo?**").prompt(ctx)
        if confirm:
            # Sends message to a moderation-clearance room
            room = self.client.get_channel(approve_thumbnail_channel_id)
            request_embed = discord.Embed(
                title="__Thumbnail Request__",
                description=f"{requester.mention} is requesting the image below to be their tribe's (`{user_tribe['name']}`) thumbnail/logo.",
                color=requester.color,
                timestamp=ctx.message.created_at
            )
            request_embed.set_image(url=image_url)
            request_msg = await room.send(embed=request_embed)

            # Don't need to store it, since it is forever
            current_timestamp = await utils.get_timestamp()

            await self.insert_skill_action(
                user_id=requester.id, skill_type="thumbnail_request", skill_timestamp=current_timestamp,
                target_id=requester.id, channel_id=room.id, message_id=request_msg.id,
                content=image_url
            )

            await request_msg.add_reaction('✅')
            await request_msg.add_reaction('❌')

            await ctx.send(f"**Request sent, {ctx.author.mention}!**")

        else:
            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"**Not doing requesting it, then, {requester.mention}!**")

    @tribe.command(aliases=['inv'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def invite(self, ctx, member: discord.Member = None) -> None:
        """ Invites a user to your tribe.
        :param member: The member to invite. """

        inviter = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{inviter.mention}, you can only use this command in {self.bots_txt.mention}!**")

        tribe_member = await self.get_tribe_member(inviter.id)
        if not tribe_member or tribe_member[0] != tribe_member[2]:
            return await ctx.send(f"**You don't have a tribe, {inviter.mention}**!")

        if not member:
            return await ctx.send(f"**Please, inform a member to invite to your tribe, {inviter.mention}!**")

        if inviter.id == member.id:
            return await ctx.send(f"**You cannot invite yourself into your own tribe, {inviter.mention}!**")

        confirm = await ConfirmSkill(f"Are you sure you want to invite, {member.mention} to `{tribe_member[1]}`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not inviting them, then!**")

        # Checks whether user is already in a tribe.
        sloth_profile = await self.get_sloth_profile(member.id)
        if not sloth_profile:
            return await ctx.send(f"**You cannot invite someone that doesn't have an account, {inviter.mention}!**")
        if sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot invite someone that doesn't have a Sloth Class, {inviter.mention}!**")
        if sloth_profile[3]:
            return await ctx.send(f"**You cannot invite someone that is already in a tribe, {inviter.mention}!**")

        custom_ctx = ctx
        custom_ctx.author = member
        invite = await ConfirmSkill(content=f"{member.mention}", msg=f"{inviter.mention} invited you to join their tribe called `{tribe_member[1]}`, do you wanna join?").prompt(custom_ctx)
        if invite:
            user_tribe = await self.get_tribe_info_by_user_id(inviter.id)
            try:
                await self.insert_tribe_member(owner_id=inviter.id, tribe_name=tribe_member[1], user_id=member.id)
                await self.update_someones_tribe(user_id=member.id, tribe_name=tribe_member[1])
                try:
                    await self.update_tribe_name(member=member, two_emojis=user_tribe['two_emojis'], joining=True)
                except:
                    pass

            except Exception as e:
                print(f"Error at inviting {member.id} to tribe: ", e)
                print("Tribe: ", tribe_member[1])
                await ctx.send(f"**Something went wrong with it, {member.mention}, {inviter.mention}!**")
            else:
                join_tribe_embed = await self.get_join_tribe_embed(
                    channel=ctx.channel, inviter=inviter, target=member, tribe=user_tribe)
                await ctx.send(embed=join_tribe_embed)
        else:
            await ctx.send(f"**{member.mention} refused your invitation to join `{tribe_member[1]}`, {inviter.mention}!**")

    @tribe.command(aliases=['view', 'display', 'show'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def see(self, ctx, *, name: str = None) -> None:
        """ Shows some information about a tribe.
        If not provided a tribe name, it will check the one the user is in.
        :param name: The tribe name. """

        member = ctx.author

        tribe = None
        if name:
            tribe = await self.get_tribe_info_by_name(name)
        else:
            sloth_profile = await self.get_sloth_profile(member.id)
            if not sloth_profile or not sloth_profile[3]:
                return await ctx.send(
                    f"**You didn't provide any tribe name and you're not in a tribe either, {member.mention}!**")

            tribe = await self.get_tribe_info_by_name(sloth_profile[3])

        if not tribe['name']:
            return await ctx.send(f"**No tribes with that name were found, {member.mention}!**")

        # Gets all tribe members
        tribe_members = await self.get_tribe_members(tribe_name=tribe['name'])
        all_sloth_class_members = await self.get_sloth_class_tribe_members(tribe_name=tribe['name'])

        all_members = list(map(lambda mid: f"<@{mid[0]}> ({mid[1]})", tribe_members))

        tribe_member_ids: List[int] = list(map(lambda m: m[0], tribe_members))
        currencies = await self.get_users_currency(tribe_member_ids)

        tribe_money: int = sum(list(map(lambda cr: cr[0], filter(lambda cr: cr[0] >= 0, currencies))))
        # Additional data:
        additional = {
            'tribe': tribe,
            'change_embed': self._make_tribe_embed,
            "sloth_class_members": all_sloth_class_members,
            "tribe_money": tribe_money
        }

        pages = menus.MenuPages(source=SwitchTribePages(all_members, **additional), clear_reactions_after=True)
        await pages.start(ctx)

    async def _make_tribe_embed(self, 
        ctx: commands.Context, tribe: Dict[str, Union[str, int]], 
        entries: int, offset: int, lentries: int, kwargs: Dict[str, Any]
    ) -> discord.Embed:
        """ Makes an embed for the Tribe display command. """

        sloth_class_members: List[Tuple[int, str]] = kwargs.get('sloth_class_members')
        tribe_money: str = kwargs.get('tribe_money')

        tribe_owner = self.client.get_user(tribe['owner_id'])
        tribe_embed = discord.Embed(
            title=f"{tribe['name']} ({tribe['two_emojis']})",
            description=tribe['description'],
            timestamp=ctx.message.created_at,
            color=ctx.author.color,
            url=tribe['link']
            )

        if tribe['thumbnail']:
            tribe_embed.set_thumbnail(url=tribe['thumbnail'])
        if tribe_owner:
            tribe_embed.set_author(name=f"Owner: {tribe_owner}", icon_url=tribe_owner.display_avatar, url=tribe_owner.display_avatar)

        tribe_embed.add_field(name="__Total Money:__", value=f"{tribe_money}łł 🍃 ", inline=False)

        formatted_sloth_class_members = await self.format_sloth_class_members(sloth_class_members)
        tribe_embed.add_field(name="__Sloth Class Counter:__", value=' **|** '.join(formatted_sloth_class_members), inline=False)

        tribe_embed.add_field(name="__Members:__", value=', '.join(entries), inline=False)

        for i, v in enumerate(entries, start=offset):
            tribe_embed.set_footer(text=f"({i} of {lentries})")

        return tribe_embed

    async def format_sloth_class_members(self, sloth_class_members: List[Tuple[int, str]]) -> List[str]:
        """ Formats the Sloth Class members by Sloth Class.
        :param sloth_class_members: The list of members to format. """

        return list(
            map(
                lambda scm: f"{'default' if not (sloth_class := self.classes.get(scm[0].lower())) else sloth_class.emoji}: `{scm[1]}`", 
                sloth_class_members
            )
        )

    @tribe.command(aliases=['kick', 'expel', 'kick_out', 'can_i_show_you_the_door?'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def kickout(self, ctx, member: Union[discord.Member, discord.User] = None) -> None:
        """ Exepels someone from your tribe.
        :param member: The member to expel. """

        expeller = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{expeller.mention}, you can only use this command in {self.bots_txt.mention}!**")

        user_tribe = await self.get_tribe_info_by_user_id(user_id=expeller.id)
        if not user_tribe['name']:
            return await ctx.send(f"**You don't have a tribe, {expeller.mention}**!")

        if not member:
            return await ctx.send(f"**Please, inform a member to kick from your tribe, {expeller.mention}!**")

        if expeller.id == member.id:
            return await ctx.send(f"**You cannot kick yourself out of your own tribe, {expeller.mention}!**")

        member_fx = await self.get_user_effects(member)
        if 'kidnapped' in member_fx:
            return await ctx.send(f"**You cannot kick someone from your tribe who is kidnapped, {expeller.mention}!**")

        confirm = await ConfirmSkill(f"Are you sure you want to kick, {member.mention} from `{user_tribe['name']}`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not kicking them, then!**")

        # Checks whether user is already in a tribe.
        sloth_profile = await self.get_sloth_profile(member.id)
        if not sloth_profile:
            return await ctx.send(f"**You cannot kick out someone that doesn't even have an account, {expeller.mention}!**")
        if sloth_profile[3] != user_tribe['name']:
            return await ctx.send(f"**You cannot kick out someone that is not in your tribe, {expeller.mention}!**")

        try:
            # await self.update_someones_tribe(user_id=member.id, tribe_name=None)
            await self.delete_tribe_member(user_id=member.id)
            try:
                await self.update_tribe_name(member=member, two_emojis=user_tribe['two_emojis'], joining=False)
            except:
                pass
        except Exception as e:
            print(e)
            await ctx.send(f"**Something went wrong with it, {expeller.mention}!**")
        else:
            await ctx.send(f"**You successfully kicked {member.mention} out of `{user_tribe['name']}`, {expeller.mention}!**")

    @tribe.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def leave(self, ctx) -> None:
        """ Leaves the tribe the user is in. """

        member = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{member.mention}, you can only use this command in {self.bots_txt.mention}!**")

        tribe_member = await self.get_tribe_member(user_id=member.id)
        if not tribe_member[1]:
            return await ctx.send(f"**You are not in a tribe, {member.mention}**!")

        if member.id == tribe_member[0]:
            return await ctx.send(f"**You cannot leave your own tribe, {member.mention}!**")

        user_tribe = await self.get_tribe_info_by_name(tribe_member[1])

        confirm = await ConfirmSkill(f"Are you sure you want to leave `{user_tribe['name']}`, {member.mention}?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not leaving it, then!**")

        # Updates user tribe status and nickname

        try:
            await self.delete_tribe_member(member.id)
            try:
                await self.update_tribe_name(member=member, two_emojis=user_tribe['two_emojis'], joining=False)
            except Exception as ee:
                print(ee)
                pass
        except Exception as e:
            print(e)
            await ctx.send(f"**Something went wrong with it, {member.mention}!**")
        else:
            await ctx.send(f"**You successfully left `{user_tribe['name']}`, {member.mention}!**")

    async def update_someones_tribe(self, user_id: int, tribe_name: str = None) -> None:
        """ Updates someone's tribe status.
        :param user_id: The ID of the user who's gonna be updated.
        :param tribe_name: The name of the tribe the user is gonna be set to. (default = None) """

        await self.db.execute_query("UPDATE SlothProfile SET tribe = %s, tribe_user_id = %s WHERE user_id = %s", (tribe_name, user_id, user_id))

    async def update_tribe_thumbnail(self, user_id: int, tribe_name: str, link: str = None) -> None:
        """ Updates someone's tribe thumbnail link.
        :param user_id: The ID of the tribe's owner.
        :param tribe_name: The name of the tribe.
        :param link: The link that the tribe's thumbnail will be set to. """

        await self.db.execute_query("""
            UPDATE tribe_tribe SET tribe_thumbnail = %s
            WHERE owner_id = %s AND tribe_name = %s""", (link, user_id, tribe_name), database_name="django")

        await self.db.execute_query("""
            UPDATE UserTribe SET tribe_thumbnail = %s
            WHERE user_id = %s AND tribe_name = %s""", (link, user_id, tribe_name))

    async def update_tribe_name(self, member: discord.Member, two_emojis: str, joining: bool) -> None:
        """ Updates someone's nickname so it has their tribe's two-emoji combination identifier.
        :param member: The member whose nickname is gonna be updated.
        :param two_emojis: The two-emoji combination identifier.
        :param joining: Whether the user is joining the tribe. """

        dname = member.display_name

        if joining:

            # Checks whether member is Munked
            if dname.endswith('Munk'):
                await member.edit(nick=f"{dname.strip()[:-4]} {two_emojis} Munk".strip())
            else:
                await member.edit(nick=f"{dname.strip()} {two_emojis}".strip())

        else:
            nick = ' '.join(map(lambda p: p.strip(), dname.rsplit(two_emojis, 1)))
            if nick != dname:
                await member.edit(nick=nick)

    async def check_tribe_creations(self) -> None:
        """ Check on-going steals and their expiration time. """

        creations = await self.get_skill_actions_by_skill_type('tribe_creation')
        guild = self.client.get_guild(int(os.getenv('SERVER_ID', 123)))
        for creation in creations:
            try:
                # Removes skill action from the database
                await self.delete_skill_action_by_target_id_and_skill_type(target_id=creation[0], skill_type='tribe_creation')
                member = discord.utils.get(guild.members, id=creation[0])
                try:
                    await self.update_tribe_name(member=member, two_emojis=creation[6], joining=True)
                except:
                    pass
            except:
                pass

    @commands.command()
    @Player.poisoned()
    @Player.skills_used(requirement=5)
    @Player.skill_on_cooldown(skill=Skill.TWO)
    @Player.skills_locked()
    @Player.user_is_class('munk')
    @Player.skill_mark()
    async def create_tribe(self, ctx) -> None:
        """ Guides you into the creation of a tribe,
        which is a custom group for people to join and do something. """

        member = ctx.author

        link = 'https://languagesloth.com/tribes'

        tribe_embed = discord.Embed(
            title="__Tribe Creation__",
            description=f"In order to create your tribe, access our website by clicking [here]({link}) or in the button below!",
            color=member.color,
            timestamp=ctx.message.created_at,
            url=link
        )

        tribe_embed.set_author(name=member, url=member.display_avatar, icon_url=member.display_avatar)
        tribe_embed.set_thumbnail(url=member.display_avatar)
        tribe_embed.set_footer(text=member.guild.name, icon_url=member.guild.icon.url)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=5, label="Create Tribe", url=link, emoji="🏕️"))

        await ctx.send(embed=tribe_embed, view=view)

    @commands.command(aliases=['add_tribe_role', 'createtriberole', 'addtriberole'])
    @Player.poisoned()
    @Player.skills_used(requirement=20)
    @Player.skill_on_cooldown(skill=Skill.THREE, seconds=36000)
    @Player.skills_locked()
    @Player.user_is_class('munk')
    @Player.skill_mark()
    async def create_tribe_role(self, ctx, role_name: str = None) -> None:
        """ Creates a tribe role.
    
        With different roles and positions in your tribe, you
        can better administrate and know what each person should do
        or their purpose inside your tribe.

        :param role_name: The name of the tribe role. (MAX = 30 Chars)

        * Cooldown: 1 day
        
        Ps: It is not an actual server role. """

        perpetrator = ctx.author

        # Do the magic here.
        if ctx.channel.id != self.bots_txt.id:
            return await ctx.send(f"**{perpetrator.mention}, you can only use this command in {self.bots_txt.mention}!**")

        perpetrator_fx = await self.get_user_effects(perpetrator)

        if 'knocked_out' in perpetrator_fx:
            return await ctx.send(f"**{perpetrator.mention}, you can't use this skill, because you are knocked-out!**")

        user_tribe = await self.get_tribe_info_by_user_id(perpetrator.id)
        if not user_tribe['name']:
            return await ctx.send(f"**You don't have a tribe, {perpetrator.mention}**!")

        if not role_name:
            return await ctx.send(f"**Please, inform a Tribe Role name, {perpetrator.mention}!**")

        if len(role_name) > 30:
            return await ctx.send(f"**Please, infom a Tribe Role name under or equal to 30 characters, {perpetrator.mention}!**")
        
        if role_name.lower() in ['owner', 'member']:
            return await ctx.send(f"**You cannot use this as your Tribe Role's name, {perpetrator.mention}!**")

        tribe_roles = await self.get_tribe_roles(perpetrator.id)
        if role_name.lower() in [trole[2].lower() for trole in tribe_roles]:
            return await ctx.send(f"**You already have a Tribe Role with that name, {perpetrator.mention}!**")

        confirm = await ConfirmSkill(f"**Are you sure you want to create a Tribe Role named `{role_name}`, {perpetrator.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not making it, then, {perpetrator.mention}!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.THREE, seconds=36000).predicate(ctx)

        try:
            current_timestamp = await utils.get_timestamp()
            await self.insert_tribe_role(perpetrator.id, user_tribe['name'], role_name)
            if exists:
                await self.update_user_skill_ts(perpetrator.id, Skill.THREE, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(perpetrator.id, Skill.THREE, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=perpetrator.id)
            
        except Exception as e:
            print(e)
            return await ctx.send(f"**Something went wrong with your skill and it failed, {perpetrator.mention}!**")

        else:
            tribe_role_embed = await self.get_tribe_role_embed(
                channel=ctx.channel, owner_id=perpetrator.id, tribe_info=user_tribe, role_name=role_name)
            await ctx.send(embed=tribe_role_embed)

    @tribe.command(aliases=['remove_role', 'deleterole', 'removerole'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete_role(self, ctx, role_name: str = None) -> None:
        """ Deletes a specific role from the member's tribe.
        :param role_name: The name of the role to delete. """
        
        member = ctx.author

        if not role_name:
            return await ctx.send(f"**Please, inform a Tribe Role name, {member.mention}!**")

        if len(role_name) > 30:
            return await ctx.send(f"**Tribe Role names have a limit of 30 characters, {member.mention}!**")

        user_tribe = await self.get_tribe_info_by_user_id(user_id=member.id)
        if not user_tribe['name']:
            return await ctx.send(f"**You don't have a tribe, {member.mention}**!")

        tribe_role = await self.get_tribe_role(member.id, role_name)
        if not tribe_role:
            return await ctx.send(f"**You don't have a Tribe Role with that name, {member.mention}!**")

        confirm = await ConfirmSkill(f"**Are you sure you want to delete your tribe's `{tribe_role[2]}` role, {member.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it then, {member.mention}!**")

        try:
            await self.delete_tribe_role(member.id, user_tribe['name'], role_name)
        except Exception as e:
            print(e)
            await ctx.send(f"**Something went wrong with it, {member.mention}!**")
        else:
            await ctx.send(f"**Successfully deleted the `{role_name}` role from your tribe, {member.mention}!**")

    @tribe.command(aliases=['remove_roles', 'deleteroles', 'removeroles'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete_roles(self, ctx) -> None:
        """ Deletes all Tribe Roles from the member's tribe. """
        
        member = ctx.author

        user_tribe = await self.get_tribe_info_by_user_id(user_id=member.id)
        if not user_tribe['name']:
            return await ctx.send(f"**You don't have a tribe, {member.mention}**!")

        tribe_roles = await self.get_tribe_roles(member.id)
        if not tribe_roles:
            return await ctx.send(f"**You don't any Tribe Roles, {member.mention}!**")

        confirm = await ConfirmSkill(f"**Are you sure you want to delete your tribe's roles, {member.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it then, {member.mention}!**")

        try:
            await self.delete_tribe_roles(member.id, user_tribe['name'])
        except Exception as e:
            print(e)
            await ctx.send(f"**Something went wrong with it, {member.mention}!**")
        else:
            await ctx.send(f"**Successfully deleted all roles from your tribe, {member.mention}!**")

    @tribe.command(aliases=['give_role', 'giverole'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def promote(self, ctx, member: discord.Member = None, role_name: str = None) -> None:
        """ Promotes a Tribe Member to a given Tribe Role.
        :param member: The Tribe Member to promote.
        :param role_name: The Tribe Role to promote the member to. """

        owner = ctx.author

        if not member:
            return await ctx.send(f"**Please, inform a Tribe Member to promote, {owner.mention}!**")

        if owner.id == member.id:
            return await ctx.send(f"**You cannot promote yourself, {owner.mention}!**")

        if not role_name:
            return await ctx.send(f"**Please, inform a Tribe Role name, {owner.mention}!**")

        if len(role_name) > 30:
            return await ctx.send(f"**Tribe Role names have a limit of 30 characters, {owner.mention}!**")

        user_tribe = await self.get_tribe_info_by_user_id(user_id=owner.id)
        if not user_tribe['name']:
            return await ctx.send(f"**You don't have a tribe, {owner.mention}**!")

        tribe_member = await self.get_tribe_member(member.id)
        if not tribe_member:
            return await ctx.send(f"**{member.mention} is not even in a tribe, {owner.mention}!**")

        if tribe_member[1] != user_tribe['name']:
            return await ctx.send(f"**{member.mention} is not even from your tribe, {owner.mention}!**")
        
        if str(tribe_member[3]).lower() == role_name.lower():
            return await ctx.send(f"**{member.mention} already has this Tribe Role, {owner.mention}!**")

        tribe_role = await self.get_tribe_role(owner.id, role_name)
        if not tribe_role:
            return await ctx.send(f"**You don't have a Tribe Role with that name, {owner.mention}!**")

        confirm = await ConfirmSkill(f"**Are you sure you want to promote {member.mention} to `{tribe_role[2]}`, {owner.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it then, {owner.mention}!**")

        try:
            await self.update_user_tribe_role(member.id, tribe_role[2])
        except Exception as e:
            print(e)
            await ctx.send(f"**Something went wrong with it, {owner.mention}!**")
        else:
            await ctx.send(f"**Successfully promoted {member.mention} to `{tribe_role[2]}`, {owner.mention}!**")

    @tribe.command(aliases=['take_role', 'takerole'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def demote(self, ctx, member: discord.Member = None) -> None:
        """ Demotes a Tribe Member from their current Tribe Role.
        :param member: The Tribe Member to demote. """

        owner = ctx.author

        if not member:
            return await ctx.send(f"**Please, inform a Tribe Member to promote, {owner.mention}!**")

        if owner.id == member.id:
            return await ctx.send(f"**You cannot demote yourself, {owner.mention}!**")

        user_tribe = await self.get_tribe_info_by_user_id(user_id=owner.id)
        if not user_tribe['name']:
            return await ctx.send(f"**You don't have a tribe, {owner.mention}**!")

        tribe_member = await self.get_tribe_member(member.id)
        if not tribe_member:
            return await ctx.send(f"**{member.mention} is not even in a tribe, {owner.mention}!**")

        if tribe_member[1] != user_tribe['name']:
            return await ctx.send(f"**{member.mention} is not even from your tribe, {owner.mention}!**")

        if tribe_member[3] == 'Member':
            return await ctx.send(f"**{member.mention} already has the default Tribe Role, {owner.mention}!**")

        tribe_role = await self.get_tribe_role(owner.id, tribe_member[3])
        if not tribe_role:
            return await ctx.send(f"**You don't have a Tribe Role with that name, {owner.mention}!**")

        confirm = await ConfirmSkill(f"**Are you sure you want to demote {member.mention} from `{tribe_role[2]}` to `Member`, {owner.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it then, {owner.mention}!**")

        try:
            await self.update_user_tribe_role(member.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**Something went wrong with it, {owner.mention}!**")
        else:
            await ctx.send(f"**Successfully demote {member.mention} from `{tribe_role[2]}` to `Member`, {owner.mention}!**")

    @tribe.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roles(self, ctx, tribe_name: Optional[str] = None) -> None:
        """ Shows the Tribe Roles of a given tribe.
        :param tribe_name: The name of the tribe to show the roles. [Optional]

        PS: If a tribe name is not provided, it will fetch the tribe the user is in. """

        member = ctx.author

        tribe = None
        if tribe_name:
            tribe = await self.get_tribe_info_by_name(tribe_name)
        else:
            sloth_profile = await self.get_sloth_profile(member.id)
            if not sloth_profile or not sloth_profile[3]:
                return await ctx.send(
                    f"**You didn't provide any tribe name and you're not in a tribe either, {member.mention}!**")

            tribe = await self.get_tribe_info_by_name(sloth_profile[3])

        if not tribe['name']:
            return await ctx.send(f"**No tribe with that name was found, {member.mention}**!")

        roles = await self.get_tribe_roles(member.id)
        if not roles:
            return await ctx.send(f"**This tribe doesn't have any internal roles, {member.mention}!**")

        embed = discord.Embed(
            title=f"__{tribe['name']}'s Roles__:",
            description=', '.join([r[2] for r in roles]),
            color=member.color,
            timestamp=ctx.message.created_at,
            url=tribe['link']
        )
        embed.set_author(name=member.display_name, url=member.display_avatar, icon_url=member.display_avatar)
        if tribe['thumbnail']:
            embed.set_thumbnail(url=tribe['thumbnail'])
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    async def get_tribe_role(self, owner_id: int, role_name: str) -> List[Union[int, str]]:
        """ Gets a Tribe Role by name.
        :param owner_id: The ID of the owner of that tribe.
        :param role_name: The name of the role. """

        return await self.db.execute_query("SELECT * FROM TribeRole WHERE owner_id = %s AND LOWER(role_name) =  LOWER(%s)", (owner_id, role_name), fetch="one")

    async def get_tribe_roles(self, owner_id: int) -> List[List[Union[int, str]]]:
        """ Gets all Tribe Roles from tribe owner's tribe.
        :param owner_id: The ID of the owner of that tribe. """

        return await self.db.execute_query("SELECT * FROM TribeRole WHERE owner_id = %s", (owner_id,), fetch="all")

    async def insert_tribe_role(self, owner_id: int, tribe_name: str, role_name: str) -> None:
        """ Inserts a Tribe Role into the database.
        :param owner_id: The ID of the owner of that tribe.
        :param tribe_name: The name of the tribe.
        :param role_name: The name of the role. """

        await self.db.execute_query("""
        INSERT INTO TribeRole (owner_id, tribe_name, role_name) VALUES (%s, %s, %s)
        """, (owner_id, tribe_name, role_name))

    async def delete_tribe_role(self, owner_id: int, tribe_name: str, role_name: str) -> None:
        """ Deletes a Tribe Role from the database.
        :param owner_id: The ID of the owner of that tribe.
        :param tribe_name: The name of the tribe.
        :param role_name: The name of the role. """

        await self.db.execute_query("DELETE FROM TribeRole WHERE owner_id = %s AND LOWER(role_name) = LOWER(%s)", (owner_id, role_name))
        await self.db.execute_query("""
        UPDATE TribeMember SET tribe_role = DEFAULT(tribe_role) WHERE tribe_name = %s AND LOWER(tribe_role) = LOWER(%s)
        """, (tribe_name, role_name))

    async def delete_tribe_roles(self, owner_id: int, tribe_name: str) -> None:
        """ Deletes all Tribe Roles from the database.
        :param owner_id: The ID of the owner of that tribe.
        :param tribe_name: The name of the tribe. """

        await self.db.execute_query("DELETE FROM TribeRole WHERE owner_id = %s", (owner_id,))
        await self.db.execute_query("""
        UPDATE TribeMember SET tribe_role = DEFAULT(tribe_role)
         WHERE tribe_name = %s AND tribe_role <> 'Owner'
        """, (tribe_name,))
        
    async def insert_tribe_member(self, owner_id: int, tribe_name: str, user_id: int, tribe_role: str = 'Member') -> None:
        """ Inserts a Tribe Member.
        :param owner_id: The ID of the owner of the tribe the user is joining.
        :param tribe_name: The tribe name.
        :param user_id: The ID of the user.
        :param tribe_role: The initial role they're gonna have in the tribe. """

        await self.db.execute_query("""
        INSERT INTO TribeMember (owner_id, tribe_name, member_id, tribe_role)
        VALUES (%s, %s, %s, %s)""", (owner_id, tribe_name, user_id, tribe_role))

    async def delete_tribe_member(self, user_id: int) -> None:
        """ Deletes a Tribe Member.
        :param user_id: The ID of the tribe member. """

        await self.db.execute_query("DELETE FROM TribeMember WHERE member_id = %s", (user_id,))

    async def get_tribe_role_embed(self, channel: discord.TextChannel, owner_id: int, tribe_info: Dict[str, Union[str, int]], role_name: str) -> discord.Embed:
        """ Makes an embedded message for a Tribe Role creation.
        :param channel: The context channel.
        :param owner_id: The owner of the tribe.
        :param tribe_info: The tribe info.
        :param role_name: The role created for that tribe. """

        current_ts = await utils.get_timestamp()

        tribe_role_embed = discord.Embed(
            title="__A Tribe Role has been Created__",
            description=f"<@{owner_id}> has just created a Tribe Role named `{role_name}` for their tribe named `{tribe_info['name']}`.",
            color=discord.Color.green(),
            timestamp=datetime.fromtimestamp(current_ts)
        )

        if tribe_info['thumbnail']:
            tribe_role_embed.set_thumbnail(url=tribe_info['thumbnail'])

        tribe_role_embed.set_image(url='https://media1.tenor.com/images/5327c87ecb310a382e891a0ed209357f/tenor.gif?itemid=18799194')
        tribe_role_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return tribe_role_embed

    async def update_user_tribe_owner(self, old_owner_id: int, new_owner_id: int) -> None:
        """ Updates the user's Tribe Role.
        :param old_owner_id: The old Tribe owner's ID.
        :param new_owner_id: The new Tribe owner's ID. """

        await self.db.execute_query("UPDATE UserTribe SET user_id = %s WHERE user_id = %s", (new_owner_id, old_owner_id))
        await self.db.execute_query("""
            UPDATE TribeMember as GL, (
                SELECT owner_id, member_id, tribe_role
                FROM TribeMember
                WHERE member_id = %s
            ) OG, (
                SELECT owner_id, member_id, tribe_role
                FROM TribeMember
                WHERE member_id = %s
            ) T
            SET GL.tribe_role = ( 
                CASE 
                    WHEN GL.member_id = %s THEN T.tribe_role
                    WHEN GL.member_id = %s THEN OG.tribe_role
                END
            )
            WHERE GL.member_id in (%s, %s);
        """, (new_owner_id, old_owner_id, new_owner_id, old_owner_id, new_owner_id, old_owner_id))

        await self.db.execute_query("UPDATE tribe_tribe SET owner_id = %s WHERE owner_id = %s", (new_owner_id, old_owner_id), database_name="django")

    async def update_user_tribe_role(self, user_id: int, role_name: Optional[str] = None) -> None:
        """ Updates the user's Tribe Role.
        :param user_id: The Tribe Member's ID.
        :param role_name: The name of the role. [Optional][Default='Member'] """

        if not role_name:
            await self.db.execute_query("UPDATE TribeMember SET tribe_role = DEFAULT(tribe_role) WHERE member_id = %s", (user_id,))
        else:
            await self.db.execute_query("UPDATE TribeMember SET tribe_role = %s WHERE member_id = %s", (role_name, user_id))

    @tribe.command(aliases=['to', 'transfer'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def transfer_ownership(self, ctx, *, member: discord.Member = None) -> None:
        """ Transfers the ownership of your tribe to someone else. """

        author = ctx.author

        if not member:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

        user_tribe = await self.get_tribe_info_by_user_id(author.id)
        if not user_tribe['name']:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You don't have a tribe, {author.mention}**!")

        if user_tribe['owner_id'] == member.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You can't transfer the tribe to yourself, {author.mention}!**")

        tribe_member = await self.get_tribe_member(member.id)
        if not tribe_member:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{member.mention} is not even in a tribe, you can't transfer the tribe to them, {author.mention}!**")

        if tribe_member[0] != user_tribe['owner_id']:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{member.mention} is in a different tribe, you can't transfer the tribe to them, {author.mention}!**")

        confirm = await ConfirmSkill(
            f"**Are you sure you want to transfer your ownership of `{user_tribe['name']}` to {member.mention}, {author.mention}?**"
            ).prompt(ctx)
        if not confirm:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Not doing it, then, {author.mention}!**")

        await self.update_user_tribe_owner(author.id, member.id)
        await ctx.send(f"**Successfully transferred ownership of `{user_tribe['name']}` from {author.mention} to {member.mention}!**")


    @tribe.command(aliases=["fto", "ftransfer", "force_transfer"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def force_transfer_ownership(self, ctx, tribe_name: str = None, member: discord.Member = None) -> None:
        """ (ADMIN) Force-transfers the ownership of a Tribe to another user.
        :param tribe_name: The name of the tribe from which to transfer ownership.
        :param member: The member to transfer the Tribe to. """

        author = ctx.author

        if not member:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member to transfer the tribe to, {author.mention}!**")

        if not tribe_name:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform the name of the tribe, {author.mention}!**")

        user_tribe = await self.get_tribe_info_by_name(tribe_name)
        if not user_tribe['name']:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**No tribes with that name were found, {author.mention}!**")

        if user_tribe['owner_id'] == member.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You can't transfer the tribe to the same user, {author.mention}!**")

        tribe_member = await self.get_tribe_member(member.id)
        if not tribe_member:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{member.mention} is not even in a tribe, you can't transfer the tribe to them, {author.mention}!**")

        if tribe_member[0] != user_tribe['owner_id']:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**{member.mention} is in a different tribe, you can't transfer the tribe to them, {author.mention}!**")

        confirm = await ConfirmSkill(
            f"**Are you sure you want to transfer ownership of `{user_tribe['name']}` from <@{user_tribe['owner_id']}> to {member.mention}, {author.mention}?**"
            ).prompt(ctx)
        if not confirm:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**Not doing it, then, {author.mention}!**")

        try:
            await self.update_user_tribe_owner(user_tribe['owner_id'], member.id)
        except:
            await ctx.send(f"**Something went wrong with it, {author.mention}!**")
        else:
            await ctx.send(f"**Successfully transferred ownership of `{user_tribe['name']}` from <@{user_tribe['owner_id']}> to {member.mention}!**")

    @commands.command(aliases=['get_mission', 'gq', 'gm'])
    @Player.poisoned()
    @Player.skills_used(requirement=50)
    @Player.skill_on_cooldown(skill=Skill.FOUR, seconds=172800)
    @Player.skills_locked()
    @Player.user_is_class('munk')
    @Player.skill_mark()
    async def get_quest(self, ctx) -> None:
        """ Gets a Quest for you and your Tribe to complete, and if so,
        the involved people will get rewarded.
        
        • Delay = 2 days
        • Cost = Free  """

        perpetrator = ctx.author

        # Do the magic here.
        if ctx.channel.id != self.bots_txt.id:
            return await ctx.send(f"**{perpetrator.mention}, you can only use this command in {self.bots_txt.mention}!**")

        perpetrator_fx = await self.get_user_effects(perpetrator)

        if 'knocked_out' in perpetrator_fx:
            return await ctx.send(f"**{perpetrator.mention}, you can't use this skill, because you are knocked-out!**")

        tribe_member = await self.get_tribe_member(perpetrator.id)
        if not tribe_member:
            return await ctx.send(f"**You are not in a tribe, {perpetrator.mention}**!")

        user_tribe = await self.get_tribe_info_by_user_id(tribe_member[0])

        # Checks whether there's already a max number of 1 open quests in that tribe
        if await self.get_skill_action_by_user_id_and_skill_type(user_id=perpetrator.id, skill_type="quest"):
            return await ctx.send(f"**You cannot have more than 1 on-going Quest at a time, {perpetrator.mention}!**")

        random_quest = await self.generate_random_quest()

        _, exists = await Player.skill_on_cooldown(skill=Skill.FOUR, seconds=172800).predicate(ctx)

        try:
            current_timestamp = await utils.get_timestamp()
            await self.insert_skill_action(
                user_id=perpetrator.id, skill_type="quest", skill_timestamp=current_timestamp,
                target_id=perpetrator.id, channel_id=ctx.channel.id, price=random_quest["enum_value"], content=random_quest["message"]
            )
            if exists:
                await self.update_user_skill_ts(perpetrator.id, Skill.FOUR, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(perpetrator.id, Skill.FOUR, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=perpetrator.id)
            
        except Exception as e:
            print(e)
            return await ctx.send(f"**Something went wrong with your skill and it failed, {perpetrator.mention}!**")

        else:
            tribe_quest_embed = await self.get_tribe_quest_embed(channel=ctx.channel, user_id=perpetrator.id, quest=random_quest, tribe=user_tribe)
            await ctx.send(embed=tribe_quest_embed)


    async def generate_random_quest(self, return_quests: bool = False, return_quests_numbers: bool = False) -> Union[Any, List[Any]]:
        """ Generates a random question.
        :param return_quests: Whether to return the quests as well. """

        quests: List[Dict[str, Union[str, int]]] = [
            {"message": "Complete 5 `TheLanguageJungle` multiplayer games. (zg!mp)", "enum_value": 1, "disabled": True},
            {"message": "Rep someone and get repped back.", "enum_value": 2},
            # {"message": "Win a coinflip betting 50 leaves.", "enum_value": 3},
            {"message": "Get a score 20 in the `Flags` game.", "enum_value": 4},
            {"message": "Spend 4 hours in a Voice Channel.", "enum_value": 5},
            {"message": "Buy any item from the SlothShop, if you have all items you need to get ripped-off first.", "enum_value": 6},
            {"message": "Transfer 25 leaves to two different staff members.", "enum_value": 7},
            # {"message": "Complete a Teacher Class Feedback Prompt", "enum_value": 8},
            # {"message": "Attend a class", "enum_value": 9},
            {"message": "Transfer 25 leaves to two different teachers.", "enum_value": 10},
            # {"message": "Complete 1 `TheLanguageJungle` singleplayer games. (zg!play)", "enum_value": 11},
            {"message": "Feed a pet or a baby", "enum_value": 12},
            # {"message": "Play 3 lottery games", "enum_value": 13},
            {"message": "Perform 2 different RolePlay commands (z!hug, z!kiss, z!boot, etc.).", "enum_value": 14},
        ]

        enabled_quests = [q for q in quests if not q.get("disabled")]

        if return_quests:
            return choice(enabled_quests), enabled_quests
        elif return_quests_numbers:
            return [str(q["enum_value"]) for q in quests]
        else:
            return choice(enabled_quests)

    async def get_tribe_quest_embed(self, 
        channel: Union[discord.TextChannel, discord.Thread], user_id: int, quest: Dict[str, Union[str, int]], tribe: Dict[str, Union[str, int]]
    ) -> discord.Embed:
        """ Makes an embedded message for a Tribe Role creation.
        :param channel: The context channel.
        :param owner_id: The owner of the tribe.
        :param tribe_info: The tribe info.
        :param role_name: The role created for that tribe. """

        current_ts = await utils.get_timestamp()

        tribe_quest_embed = discord.Embed(
            title="__A New Quest has been Started__",
            description=f"<@{user_id}> has just started a Quest for their Tribe named `{tribe['name']}`!",
            color=discord.Color.green(),
            timestamp=datetime.fromtimestamp(current_ts)
        )
        tribe_quest_embed.add_field(name="__Quest__:", value=quest["message"])

        if tribe["thumbnail"]:
            tribe_quest_embed.set_thumbnail(url=tribe["thumbnail"])
        tribe_quest_embed.set_image(url='https://c.tenor.com/MJ8Dxo58AJAAAAAC/muggers-quest.gif')
        tribe_quest_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)
        return tribe_quest_embed

    async def complete_quest(self, user_id: int, quest_number: int, **kwargs) -> None:
        """ Completes an on-going quest for a member.
        :param user_id: The ID of the user who's completing the quest.
        :param quest_number: The quest number. """

        # Gets Quest
        quest = await self.get_skill_action_by_user_id_and_skill_type(user_id=user_id, skill_type="quest")
        if not quest:
            return

        if quest[7] != quest_number:
            return

        # Gets enum value
        enum_name = list(QuestEnum.__annotations__)[quest[7]-1]
        function: Callable = getattr(QuestEnum, enum_name)
        # Runs attached method if there's any
        if function:
            await function(client=self.client, user_id=user_id, quest=quest, **kwargs)

    @tribe.command(aliases=["mission", "task", "chore", "quests"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quest(self, ctx) -> None:
        """ Shows all Quests that the tribe you are in has. """

        member = ctx.author

        tribe_member = await self.get_tribe_member(member.id)
        if not tribe_member:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"**You're not even in a tribe, {member.mention}!**")
        
        user_tribe = await self.get_tribe_info_by_user_id(tribe_member[0])

        tribe_members = await self.get_tribe_members(tribe_member[0], tribe_member[1])
        quests: List[List[Union[str, int]]] = []
        for tribe_member in tribe_members:
            quest = await self.get_skill_action_by_user_id_and_skill_type(user_id=tribe_member[0], skill_type="quest")
            if quest:
                quests.append(quest)

        if not quests:
            return await ctx.send(f"**No quests found in your tribe, {member.mention}!**")

        quests_text: str = await self.make_tribe_quests_text(ctx.guild, quests)
        embed: discord.Embed = discord.Embed(
            title="__Tribe Quests__",
            description=f"Showing all `{len(quests)}` quests from this tribe:\n{quests_text}",
            color=member.color,
            timestamp=ctx.message.created_at

        )
        embed.set_footer(text=f"Requested by: {member}", icon_url=member.display_avatar)
        if user_tribe["thumbnail"]:
            embed.set_thumbnail(url=user_tribe["thumbnail"])

        await ctx.send(embed=embed)
    
    async def make_tribe_quests_text(self, guild: discord.Guild, quests: List[Dict[str, Union[str, int]]], show_target: bool = False) -> str:
        """ Makes a text for the tribe quests.
        :param guild: The server.
        :param quests: The quests to make a text for. """

        texts_list: List[str] = []
        for quest in quests:
            quest_number: int = quest[7]
            quest_owner: discord.Member = guild.get_member(quest[0])

            quest_target_text: str = ""
            quest_target: discord.Member = None
            if show_target:
                quest_target: discord.Member = guild.get_member(quest[3])
                quest_target_text = f"\n[Target]: {quest_target}"

            if quest_number == 1:
                texts_list.append(f"```ini\n[{quest_number}]• {quest[8]}\n[Progress]: {quest[9]} games.\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 2:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Progress]: {quest[9]}/2 reps.\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 3:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 4:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 5:
                m, s = divmod(quest[9], 60)
                h, m = divmod(m, 60)
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Progress]: {h:d}h, {m:02d}m.\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 6:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 7:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Progress]: {1 if quest[9] else 0}/2 transfers.\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 8:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 9:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 10:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Progress]: {1 if quest[9] else 0}/2 transfers.\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 11:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 12:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 13:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Progress]: {quest[9]}/3 lottos.\n[Owner]: {quest_owner}{quest_target_text}```")
            elif quest_number == 14:
                texts_list.append(f"```ini\n[{quest_number}] • {quest[8]}\n[Progress]: {1 if quest[9] else 0}/2 RolePlay commands.\n[Owner]: {quest_owner}{quest_target_text}```")
        
        return ''.join(texts_list)

    async def update_sloth_skill_content(self, user_id: int, content: int, current_ts: int, skill_type: str) -> None:
        """ Updates the skill's integer content.
        :param user_id: The user ID.
        :param content: The integer content.
        :param current_ts: The current timestamp.
        :param skill_type: The skill type. """

        await self.db.execute_query("""
            UPDATE SlothSkills SET edited_timestamp = %s, content = %s 
            WHERE user_id = %s AND skill_type = %s""", (current_ts, content, user_id, skill_type))

    async def update_sloth_skill_int_content(self, user_id: int, int_content: int, current_ts: int, skill_type: str) -> None:
        """ Updates the skill's integer content.
        :param user_id: The user ID.
        :param int_content: The integer content.
        :param current_ts: The current timestamp.
        :param skill_type: The skill type. """

        await self.db.execute_query("""
            UPDATE SlothSkills SET edited_timestamp = %s, int_content = %s 
            WHERE user_id = %s AND skill_type = %s""", (current_ts, int_content, user_id, skill_type))

    async def update_sloth_skill_target_id(self, user_id: int, target_id: int, current_ts: int, skill_type: str) -> None:
        """ Updates the skill's target id.
        :param user_id: The user ID.
        :param target_id: The target ID.
        :param current_ts: The current timestamp.
        :param skill_type: The skill type. """

        await self.db.execute_query("""
            UPDATE SlothSkills SET target_id = %s, edited_timestamp = %s 
            WHERE user_id = %s AND skill_type = %s""", (target_id, current_ts, user_id, skill_type))

    async def update_sloth_skill_user_and_target_id(self, user_id: int, target_id: int, current_ts: int, skill_type: str) -> None:
        """ Updates the skill's user and target id.
        :param user_id: The user ID.
        :param target_id: The target ID.
        :param current_ts: The current timestamp.
        :param skill_type: The skill type. """

        await self.db.execute_query("""
            UPDATE SlothSkills SET user_id = %s, target_id = %s, edited_timestamp = %s 
            WHERE user_id = %s AND skill_type = %s""", (target_id, target_id, current_ts, user_id, skill_type))

    async def update_sloth_skill_user_and_target_id_and_int_content(self, user_id: int, target_id: int, int_content: int, current_ts: int, skill_type: str) -> None:
        """ Updates the skill's user and target id.
        :param user_id: The user ID.
        :param target_id: The target ID.
        :param int_content: The integer content.
        :param current_ts: The current timestamp.
        :param skill_type: The skill type. """

        await self.db.execute_query("""
            UPDATE SlothSkills SET user_id = %s, target_id = %s, int_content = %s, edited_timestamp = %s 
            WHERE user_id = %s AND skill_type = %s""", (target_id, target_id, int_content, current_ts, user_id, skill_type))

    @tribe.command(aliases=["transferquest", "tq"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def transfer_quest(self, ctx, member: discord.Member = None) -> None:
        """ Transfer a quest to someone else.
        :param member: The member to transfer the quest to. """

        author: discord.Member = ctx.author

        if not member:
            return await ctx.send(f"**Please inform a member to transfer your quest to, {author.mention}!**")

        user_profile = await self.get_sloth_profile(author.id)
        if not user_profile:
            return await ctx.send(f"**You don't even have a Sloth Profile, you can't do this, {author.mention}!**")

        quest = await self.get_skill_action_by_user_id_and_skill_type(user_id=author.id, skill_type="quest")
        if not quest:
            return await ctx.send(f"**You don't any Quest to transfer, {author.mention}!**")

        target_profile = await self.get_sloth_profile(member.id)
        if not target_profile:
            return await ctx.send(f"**This person doesn't have a Sloth Profile, {author.mention}!**")

        if user_profile[3] != target_profile[3]:
            return await ctx.send(f"**You can only transfer quest to people from the same tribe as you, {author.mention}!**")

        if target_profile[1] == 'default':
            return await ctx.send(f"**This person has a `default` Sloth Class, you cannot transfer your quest to them, {author.mention}!**")

        quest = await self.get_skill_action_by_user_id_and_skill_type(user_id=author.id, skill_type="quest")
        if not quest:
            return await ctx.send(f"**You don't any Quest to transfer, {author.mention}!**")

        current_ts = await utils.get_timestamp()

        try:
            if quest[9] == member.id:
                await self.update_sloth_skill_user_and_target_id_and_int_content(author.id, member.id, author.id, current_ts, 'quest')
            else:
                await self.update_sloth_skill_user_and_target_id(author.id, member.id, current_ts, 'quest')
        except Exception as e:
            print("Error at transferring quest: ", e)
            await ctx.send(f"**Something went wrong with it, try again later, {author.mention}!**")
        else:
            await ctx.send(f"**Successfully transferred your Quest to {member.mention}, {author.mention}!**")

    async def get_top_ten_tribe_leaves(self) -> List[List[Union[str, int]]]:
        """ Gets the top ten tribes with most leaves. """
        
        return await self.db.execute_query("""
            SELECT SP.tribe, SUM(UC.user_money) AS tm
            FROM UserCurrency AS UC
            INNER JOIN
                SlothProfile AS SP
            ON UC.user_id = SP.user_id
            GROUP BY tribe
            ORDER BY tm DESC
            LIMIT 10
        """, fetch="all")

    async def get_all_tribe_leaves(self) -> List[List[Union[str, int]]]:
        """ Gets all tribe leaves. """
        
        return await self.db.execute_query("""
            SELECT SP.tribe, SUM(UC.user_money) AS tm
            FROM UserCurrency AS UC
            INNER JOIN
                SlothProfile AS SP
            ON UC.user_id = SP.user_id
            GROUP BY tribe
            ORDER BY tm DESC
        """, fetch="all")
    
    @commands.command(aliases=["my_quest", "see_quest", "see_quests", "quest", "quests", "qs"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def my_quests(self, ctx, target: Optional[discord.Member] = None) -> None:
        """ Shows all Quests attached to the you or a user.
        :param target: The member from which to show the quests. [Optional][Default = You] """

        perpetrator = ctx.author

        if not target:
            target = perpetrator
        
        quests = await self.get_skill_action_by_user_id_or_target_id_and_skill_type(user_id=target.id, skill_type="quest", multiple=True)
        if not quests:
            if perpetrator == target:
                return await ctx.send(f"**No quests are attached to you, {perpetrator.mention}!**")
            return await ctx.send(f"**No quests are attached to {target.mention}, {perpetrator.mention}!**")

        quests_text: str = await self.make_tribe_quests_text(ctx.guild, quests, show_target=True)
        embed: discord.Embed = discord.Embed(
            title=f"__{target} Quests__",
            description=f"Showing quests attached to: {target.mention}\n{quests_text}",
            color=target.color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Requested by: {perpetrator}", icon_url=perpetrator.display_avatar)
        embed.set_thumbnail(url=ctx.guild.icon.url)

        await ctx.send(embed=embed)
    
    @commands.command(aliases=["removequest", "detach_quest", "detachquest", "delete_quest", "deletequest", "rmq", "dq"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove_quest(self, ctx, quest_number: str = None) -> None:
        """ Removes q eust by quest number.
        :param quest_number: The quest number. """

        member = ctx.author

        if not quest_number:
            return await ctx.send(f"**Please, inform a quest number, {member.mention}!**")
        
        quest_numbers = await self.generate_random_quest(return_quests_numbers=True)
        if quest_number not in quest_numbers:
            return await ctx.send(f"**Please, inform a valid quest number, {member.mention}!**")

        quests = await self.get_skill_action_by_user_id_or_target_id_and_skill_type(user_id=member.id, skill_type="quest", multiple=True)
        if not quests:
            return await ctx.send(f"**You don't even have any quest attached to you, {member.mention}**")

        if not any(map(lambda q: str(q[7]) == quest_number, quests)):
            return await ctx.send(f"**You don't have any quest with this number!**")

        confirm = await Confirm(f"**Are you sure you wanna remove this quest, {member.mention}?**").prompt(ctx)
        if not confirm:
            return

        await self.delete_skill_action_by_user_id_or_target_id_and_skill_type_and_price(member.id, "quest", quest_number)
        await ctx.send(f"**You successfully removed the quest number `{quest_number}` that was attached to you, {member.mention}!**")
