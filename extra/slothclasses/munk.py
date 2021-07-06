import discord
from discord.ext import commands, menus
from .player import Player, Skill
from mysqldb import the_database, the_django_database
from extra.menu import ConfirmSkill, SwitchTribePages
from extra import utils
import os
from datetime import datetime
from typing import List, Union, Dict, Any
import asyncio

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))
approve_thumbnail_channel_id = int(os.getenv('APPROVE_THUMBNAIL_CHANNEL_ID'))


class Munk(Player):

    emoji = '<:Munk:839498018712715284>'

    def __init__(self, client) -> None:
        self.client = client

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
    @Player.skill_on_cooldown()
    @Player.user_is_class('munk')
    @Player.skill_mark()
    async def munk(self, ctx, target: discord.Member = None) -> None:
        """ Converts a user into a real Munk.
        :param target: The person you want to convert to a Munk. """

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

        attacker = ctx.author

        if await self.is_user_knocked_out(attacker.id):
            return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            return await ctx.send(f"**Please, choose a member to use the `Munk` skill, {attacker.mention}!**")

        if attacker.id == target.id:
            return await ctx.send(f"**You cannot convert yourself, since you are already a `Munk`, {attacker.mention}!**")

        if target.display_name.strip().title().endswith('Munk'):
            return await ctx.send(f"**{target.mention} is already a `Munk`, {attacker.mention}!**")

        target_currency = await self.get_user_currency(target.id)
        if not target_currency:
            return await ctx.send(f"**You cannot convert someone who doesn't have an account, {attacker.mention}!**")

        if target_currency[7] == 'default':
            return await ctx.send(f"**You cannot convert someone who has a `default` Sloth class, {attacker.mention}!**")

        if await self.is_user_protected(target.id):
            return await ctx.send(f"**{attacker.mention}, you cannot convert {target.mention} into a `Munk`, because they are protected against attacks!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to convert {target.mention} into a `Munk`?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not converting them, then!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.ONE).predicate(ctx)

        try:
            await target.edit(nick=f"{target.display_name} Munk")
            current_timestamp = await utils.get_timestamp()
            # Don't need to store it, since it is forever
            # await self.insert_skill_action(
            #     user_id=attacker.id, skill_type="munk", skill_timestamp=current_timestamp,
            #     target_id=target.id, channel_id=ctx.channel.id
            # )
            if exists:
                await self.update_user_skill_ts(attacker.id, Skill.ONE, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(ctx.author.id, Skill.ONE, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)
            munk_embed = await self.get_munk_embed(
                channel=ctx.channel, perpetrator_id=ctx.author.id, target_id=target.id)
            msg = await ctx.send(embed=munk_embed)
        except Exception as e:
            print(e)
            return await ctx.send(f"**Something went wrong and your `Munk` skill failed, {attacker.mention}!**")

        else:
            await msg.edit(content=f"<@{target.id}>")

    async def get_munk_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
        """ Makes an embedded message for a munk action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the munk skill.
        :param target_id: The ID of the target member that is gonna be protected. """

        timestamp = await utils.get_timestamp()

        munk_embed = discord.Embed(
            title="A Munk Convertion has been delightfully performed!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        munk_embed.description = f"🐿️ <@{perpetrator_id}> converted <@{target_id}> into a `Munk`! 🐿️"
        munk_embed.color = discord.Color.green()

        munk_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Munk.png")
        munk_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

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

        join_tribe_embed.set_author(name=inviter, icon_url=inviter.avatar_url)
        if tribe['thumbnail']:
            join_tribe_embed.set_thumbnail(url=tribe['thumbnail'])
        join_tribe_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

        return join_tribe_embed

    async def get_tribe_info_by_name(self, name: str) -> Dict[str, Union[str, int]]:
        """ Gets information about a specific tribe.
        :param name: The name of the tribe. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM UserTribe WHERE tribe_name = %s", (name,))
        tribe = await mycursor.fetchone()
        await mycursor.close()

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
                'link': f"https://thelanguagesloth.com/tribes/{tribe[6]}/"
            }

        return tribe_info

    async def get_tribe_info_by_user_id(self, user_id: str) -> Dict[str, Union[str, int]]:
        """ Gets information about a specific tribe.
        :param user_id: The ID of the user owner of the tribe. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM UserTribe WHERE user_id = %s", (user_id,))
        tribe = await mycursor.fetchone()
        await mycursor.close()

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
                'link': f"https://thelanguagesloth.com/tribes/{tribe[6]}/"
            }

        return tribe_info

    async def get_tribe_members(self, tribe_owner_id: int = None, tribe_name: str = None) -> Dict[str, List[int]]:
        """ Gets a list of IDs of members of a particular tribe.
        :param tribe_owner_id: The ID of the owner of the tribe (Optional).
        :param tribe_name: The name of the tribe. (Optional).
        Ps: At least one of the parameters has to be provided. """

        mycursor, db = await the_database()

        tribe_members: Dict[str, List[int]] = {}

        if tribe_owner_id:
            await mycursor.execute("SELECT tribe_name FROM UserTribe WHERE user_id = %s", (tribe_owner_id,))
            tribe = await mycursor.fetchone()
            await mycursor.execute("SELECT user_id FROM UserCurrency WHERE tribe = %s", (tribe[0],))
            tribe_members = await mycursor.fetchall()

        elif tribe_name:
            await mycursor.execute("SELECT user_id FROM UserCurrency WHERE tribe = %s", (tribe_name,))
            tribe_members = list(map(lambda mid: mid[0], await mycursor.fetchall()))

        await mycursor.close()

        return tribe_members

    @commands.command(aliases=['request_logo', 'ask_thumbnail', 'ask_logo'])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def request_thumbnail(self, ctx, image_url: str = None) -> None:
        """ Request a thumbnail for your tribe.
        :param image_url: The URL link of the thumbnail image. """

        requester = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            self.client.get_command('request_thumbnail').reset_cooldown(ctx)
            return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

        if not image_url:
            self.client.get_command('request_thumbnail').reset_cooldown(ctx)
            return await ctx.send(f"You need to inform an image URL, {requester.mention}!**")

        if not image_url.startswith('https://'):
            self.client.get_command('request_thumbnail').reset_cooldown(ctx)
            return await ctx.send(f"You need to inform an image URL that has HTTPS in it, {requester.mention}!**")

        if len(image_url) > 200:
            self.client.get_command('request_thumbnail').reset_cooldown(ctx)
            return await ctx.send(f"You need to inform an image URL within 200 characters, {requester.mention}!**")

        user_tribe = await self.get_tribe_info_by_user_id(user_id=requester.id)
        if not user_tribe['name']:
            self.client.get_command('request_thumbnail').reset_cooldown(ctx)
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
            self.client.get_command('request_thumbnail').reset_cooldown(ctx)
            await ctx.send(f"**Not doing requesting it, then, {requester.mention}!**")

    @commands.command(aliases=['invite'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tribe_invite(self, ctx, member: discord.Member = None) -> None:
        """ Invites a user to your tribe.
        :param member: The member to invite. """

        inviter = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{inviter.mention}, you can only use this command in {self.bots_txt.mention}!**")

        user_tribe = await self.get_tribe_info_by_user_id(user_id=inviter.id)
        if not user_tribe['name']:
            return await ctx.send(f"**You don't have a tribe, {inviter.mention}**!")

        if not member:
            return await ctx.send(f"**Please, inform a member to invite to your tribe, {inviter.mention}!**")

        if inviter.id == member.id:
            return await ctx.send(f"**You cannot invite yourself into your own tribe, {inviter.mention}!**")

        confirm = await ConfirmSkill(f"Are you sure you want to invite, {member.mention} to `{user_tribe['name']}`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not inviting them, then!**")

        # Checks whether user is already in a tribe.
        user_currency = await self.get_user_currency(member.id)
        if not user_currency:
            return await ctx.send(f"**You cannot invite someone that doesn't have an account, {inviter.mention}!**")
        if user_currency[7] == 'default':
            return await ctx.send(f"**You cannot invite someone that doesn't have a Sloth Class, {inviter.mention}!**")
        if user_currency[18]:
            return await ctx.send(f"**You cannot invite someone that is already in a tribe, {inviter.mention}!**")

        custom_ctx = ctx
        custom_ctx.author = member
        invite = await ConfirmSkill(content=f"{member.mention}", msg=f"{inviter.mention} invited you to join their tribe called `{user_tribe['name']}`, do you wanna join?").prompt(custom_ctx)
        if invite:
            if not user_currency[18]:
                try:
                    await self.update_someones_tribe(user_id=member.id, tribe_name=user_tribe['name'])
                    try:
                        await self.update_tribe_name(member=member, two_emojis=user_tribe['two_emojis'], joining=True)
                    except:
                        pass

                except Exception as e:
                    print(e)
                    await ctx.send(f"**Something went wrong with it, {member.mention}, {inviter.mention}!**")
                else:
                    join_tribe_embed = await self.get_join_tribe_embed(
                        channel=ctx.channel, inviter=inviter, target=member, tribe=user_tribe)
                    await ctx.send(embed=join_tribe_embed)
            else:
                await ctx.send(f"**You're already in a tribe, {member.mention}!**")
        else:
            await ctx.send(f"**{member.mention} refused your invitation to join `{user_tribe['name']}`, {inviter.mention}!**")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tribe(self, ctx, *, name: str = None) -> None:
        """ Shows some information about a tribe.
        If not provided a tribe name, it will check the one the user is in.
        :param name: The tribe name. """

        member = ctx.author

        tribe = None
        if name:
            tribe = await self.get_tribe_info_by_name(name)
        else:
            user_currency = await self.get_user_currency(member.id)
            if not user_currency or not user_currency[18]:
                return await ctx.send(
                    f"**You didn't provide any tribe name and you're not in a tribe either, {member.mention}!**")

            tribe = await self.get_tribe_info_by_name(user_currency[18])

        if not tribe['name']:
            return await ctx.send(f"**No tribes with that name were found, {member.mention}!**")

        # Gets all tribe members
        tribe_members = await self.get_tribe_members(tribe_name=tribe['name'])

        all_members = list(map(lambda mid: f"<@{mid}>", tribe_members))

        # Additional data:
        additional = {
            'tribe': tribe,
            'change_embed': self._make_tribe_embed
        }

        pages = menus.MenuPages(source=SwitchTribePages(all_members, **additional), clear_reactions_after=True)
        await pages.start(ctx)

    async def _make_tribe_embed(self, ctx: commands.Context, tribe: Dict[str, Union[str, int]], entries: int, offset: int, lentries: int) -> discord.Embed:


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
            tribe_embed.set_author(name=f"Owner: {tribe_owner}", icon_url=tribe_owner.avatar_url, url=tribe_owner.avatar_url)

        # tribe_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        tribe_embed.add_field(name="__Members:__", value=', '.join(entries), inline=False)

        for i, v in enumerate(entries, start=offset):
            tribe_embed.set_footer(text=f"({i} of {lentries})")

        return tribe_embed

    @commands.command(aliases=['expel', 'kick_out', 'can_i_show_you_the_door?'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def kickout(self, ctx, member: discord.User = None) -> None:
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

        confirm = await ConfirmSkill(f"Are you sure you want to kick, {member.mention} from `{user_tribe['name']}`?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not kicking them, then!**")

        # Checks whether user is already in a tribe.
        user_currency = await self.get_user_currency(member.id)
        if not user_currency:
            return await ctx.send(f"**You cannot kick out someone that doesn't even have an account, {expeller.mention}!**")
        if user_currency[18] != user_tribe['name']:
            return await ctx.send(f"**You cannot kick out someone that is not in your tribe, {expeller.mention}!**")

        try:
            await self.update_someones_tribe(user_id=member.id, tribe_name=None)
            try:
                await self.update_tribe_name(member=member, two_emojis=user_tribe['two_emojis'], joining=False)
            except:
                pass
        except Exception as e:
            print(e)
            await ctx.send(f"**Something went wrong with it, {expeller.mention}!**")
        else:
            await ctx.send(f"**You successfully kicked {member.mention} out of `{user_tribe['name']}`, {expeller.mention}!**")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def leave_tribe(self, ctx) -> None:
        """ Leaves the tribe the user is in. """

        member = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{member.mention}, you can only use this command in {self.bots_txt.mention}!**")

        user_currency = await self.get_user_currency(user_id=member.id)
        if not user_currency[18]:
            return await ctx.send(f"**You are not in a tribe, {member.mention}**!")

        user_tribe = await self.get_tribe_info_by_name(user_currency[18])

        if member.id == user_tribe['owner_id']:
            return await ctx.send(f"**You cannot leave your own tribe, {member.mention}!**")

        confirm = await ConfirmSkill(f"Are you sure you want to leave `{user_tribe['name']}`, {member.mention}?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not leaving it, then!**")

        # Updates user tribe status and nickname

        try:
            await self.update_someones_tribe(user_id=member.id, tribe_name=None)
            try:
                await self.update_tribe_name(member=member, two_emojis=user_tribe['two_emojis'], joining=False)
            except:
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

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET tribe = %s WHERE user_id = %s", (tribe_name, user_id))
        await db.commit()
        await mycursor.close()

    async def update_tribe_thumbnail(self, user_id: int, tribe_name: str, link: str = None) -> None:
        """ Updates someone's tribe thumbnail link.
        :param user_id: The ID of the tribe's owner.
        :param tribe_name: The name of the tribe.
        :param link: The link that the tribe's thumbnail will be set to. """

        mycursor, db = await the_django_database()
        await mycursor.execute("""
            UPDATE tribe_tribe SET tribe_thumbnail = %s
            WHERE owner_id = %s AND tribe_name = %s""", (link, user_id, tribe_name))
        await db.commit()
        await mycursor.close()

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE UserTribe SET tribe_thumbnail = %s
            WHERE user_id = %s AND tribe_name = %s""", (link, user_id, tribe_name))
        await db.commit()
        await mycursor.close()

    async def update_tribe_name(self, member: int, two_emojis: str, joining: bool) -> None:
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
        guild = self.client.get_guild(int(os.getenv('SERVER_ID')))
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

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_tribe(self, ctx) -> None:
        """ (Owner) Creates the UserTribe table. """

        if await self.table_user_tribe_exists():
            return await ctx.send("**The `UserTribe` table already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE UserTribe (
                user_id BIGINT NOT NULL, tribe_name VARCHAR(50) NOT NULL,
                tribe_description VARCHAR(200) NOT NULL, two_emojis VARCHAR(2) NOT NULL,
                tribe_thumbnail VARCHAR(200) DEFAULT NULL, tribe_form VARCHAR(100) DEFAULT NULL,
                slug VARCHAR(75) NOT NULL
            ) DEFAULT CHARSET=utf8mb4""")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Created `UserTribe` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_tribe(self, ctx) -> None:
        """ (Owner) Drops the UserTribe table. """

        if not await self.table_user_tribe_exists():
            return await ctx.send("**The `UserTribe` table doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserTribe")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Dropped `UserTribe` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_tribe(self, ctx) -> None:
        """ (Owner) Resets the UserTribe table. """

        if not await self.table_user_tribe_exists():
            return await ctx.send("**The `UserTribe` table doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserTribe")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Reset `UserTribe` table!**")

    async def table_user_tribe_exists(self) -> bool:
        """ Checks whether the UserTribe table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'UserTribe'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

    @commands.command()
    @Player.skills_used(requirement=5)
    @Player.skill_on_cooldown(skill=Skill.TWO)
    @Player.user_is_class('munk')
    @Player.skill_mark()
    async def create_tribe(self, ctx) -> None:
        """ Guides you into the creation of a tribe,
        which is a custom group for people to join and do something. """

        member = ctx.author

        link = 'https://thelanguagesloth.com/tribes'

        tribe_embed = discord.Embed(
            title="__Tribe Creation__",
            description=f"In order to create your tribe, access our website by clicking [here]({link}) or in the button below!",
            color=member.color,
            timestamp=ctx.message.created_at,
            url=link
        )

        tribe_embed.set_author(name=member, url=member.avatar_url, icon_url=member.avatar_url)
        tribe_embed.set_thumbnail(url=member.avatar_url)
        tribe_embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)

        compo = discord.Component()
        compo.add_button(style=5, label="Create Tribe!", url=link, emoji="🏕️")

        await ctx.send(embed=tribe_embed, components=[compo])


    @commands.command()
    @Player.skills_used(requirement=20)
    @Player.skill_on_cooldown(skill=Skill.THREE)
    @Player.user_is_class('munk')
    @Player.skill_mark()
    @Player.not_ready()
    async def create_tribe_role(self, ctx, role_name: str = None) -> None:
        """ Creates a tribe role.
    
        With different roles and positions in your tribe, you
        can better administrate and know what each person should do
        or their purpose inside your tribe.

        :param role_name: The name of the tribe role. (MAX = 30 Chars)
        
        Ps: It is not an actual server role. """

        member = ctx.author

        if not role_name:
            return await ctx.send(f"**Please, inform a tribe role name, {member.mention}!**")

        # Do the magic here.