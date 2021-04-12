import discord
from discord.ext import commands, menus
from mysqldb import *
from datetime import datetime
import asyncio
from typing import Dict, List, Union, Any
import time
import os
from extra.useful_variables import different_class_roles
from extra.menu import ConfirmSkill, prompt_message_guild, prompt_number, SwitchSavedClasses, SwitchSavedClassesButtons

# IDs from .env
create_room_vc_id = int(os.getenv('CREATE_SMART_CLASSROOM_VC_ID'))
create_room_txt_id = int(os.getenv('CREATE_CLASSROOM_CHANNEL_ID'))
create_room_cat_id = int(os.getenv('CREATE_ROOM_CAT_ID'))

mod_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))
preference_role_id = int(os.getenv('PREFERENCE_ROLE_ID'))
lesson_management_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID'))
sloth_explorer_role_id = int(os.getenv('SLOTH_EXPLORER_ROLE_ID'))

class_history_channel_id = int(os.getenv('CLASS_HISTORY_CHANNEL_ID'))
reward_channel_id = int(os.getenv('REWARD_CHANNEL_ID'))
bot_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class TeacherFeedback(commands.Cog):
    """ Category for language class creations
    and related commands. """

    def __init__(self, client) -> None:
        """ Class initializing method. """

        self.client = client
        self.db = TeacherFeedbackDatabase()
        self.teacher_cache: Dict[int, int] = {}

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to use. """

        print("TeacherFeedback cog is online!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload) -> None:
        # Checks whether it wasn't a bot's reaction
        if not payload.guild_id:
            return

        # Checks whether it's a DM reaction or bot reaction
        if not payload.member or payload.member.bot:
            return

        # Checks whether it was a reaction in the rewards channel
        if payload.channel_id != reward_channel_id:
            return

        guild = self.client.get_guild(payload.guild_id)

        # Checks if it's a reward message
        user = await self.db.get_waiting_reward_student(payload.user_id, payload.message_id)
        lenactive = user[-1]
        if lenactive:
            emoji = str(payload.emoji)
            channel = discord.utils.get(guild.channels, id=reward_channel_id)
            msg = await channel.fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji.name, payload.member)
            if emoji == '✅':
                # Adds user to RewardAcceptedStudents table
                await self.db.insert_student_rewarded(user)
                await self.db.delete_waiting_reward_student(user[0], user[1], user[4])
                await asyncio.sleep(0.5)
                user = await self.db.get_waiting_reward_student(payload.user_id, payload.message_id)
                lenactive = user[-1]
                await self.show_user_feedback(msg=msg, guild=guild, user=user, lenactive=lenactive, teacher=payload.member)
            else:
                await self.db.delete_waiting_reward_student(msg_id=user[0], user_id=user[1], teacher_id=user[4])
                await asyncio.sleep(0.5)
                user = await self.db.get_waiting_reward_student(payload.user_id, payload.message_id)
                lenactive = user[-1]
                return await self.show_user_feedback(msg=msg, guild=guild, user=user, lenactive=lenactive, teacher=payload.member)

        else:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return

        if message.author.bot:
            return

        mc = message.channel
        mca = message.channel.category
        member = message.author

        # Checks if channel is in the CreateClassroom category
        if mca and mca.id != create_room_cat_id:
            return

        # Checks if the channel is an active class
        the_class = await self.db.get_active_teacher_class_by_txt_id(mc.id)
        if the_class and not the_class[0] == member.id:
            # Checks if user is an active student
            if await self.db.get_student_by_vc_id(member.id, the_class[2]):
                await self.db.update_student_messages(member.id, the_class[2])

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """ For when teachers are creating language class channels
        or for when students are joining the classes. """

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
        if before.self_video != after.self_video:
            return

        # Get before/after channels and their categories
        bc = before.channel
        ac = after.channel
        bca = before.channel.category if bc else None
        aca = after.channel.category if ac else None

        # Join
        if ac and not bc:
            # Joining class category
            if aca and aca.id == create_room_cat_id:
                # print('join class')
                await self.join_channel(member, before, after)

        # Switch
        elif ac and bc:
            # Either BCA or ACA have to be leaving the class category
            if (bca or aca) and (bca.id == create_room_cat_id or aca.id == create_room_cat_id):
                # print('switch class')
                await self.switch_channels(member, before, after)

        # Leave
        elif bc:
            # Leaving class category
            if bca and bca.id == create_room_cat_id:
                # print('leave class')
                await self.leave_class(member, before.channel)

    # ===== Channel Events =====

    async def join_channel(self, member, before, after) -> None:
        """ (Event) User joined a channel. """

        ac = after.channel

        # Joining the class creation room
        if ac.id == create_room_vc_id:
            # Creating class
            await self.create_class(member)
        else:
            # Joining class
            await self.join_class(member, after.channel)

    async def switch_channels(self, member, before, after) -> None:
        """ (Event) User switched channels. """

        bc = before.channel
        ac = after.channel
        bca = before.channel.category if bc else None

        # Switching to the class creation room
        if ac.id == create_room_vc_id:
            # Creating class
            await self.create_class(member)

        elif bca and bca.id == create_room_cat_id:
            # Switching classes
            await self.leave_class(member, before.channel)
            await self.join_class(member, after.channel)

    # ===== Class management =====

    async def create_class(self, member: discord.Member) -> None:
        """ Creates a class.
        :param member: The class host/hostess. """

        # Checks whether the member is a teacher
        teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)
        if teacher_role not in member.roles:
            return

        # Checks whether the teacher has an existing class.
        if teacher_class := await self.db.get_active_teacher_class_by_teacher_id(member.id):
            # Checks whether the class vc still exists
            if class_vc := discord.utils.get(member.guild.channels, id=teacher_class[2]):
                try:
                    await member.move_to(class_vc)
                except:
                    pass
                finally:
                    return
            else:
                await self.db.delete_active_teacher_class_by_teacher_and_vc_id(member.id, teacher_class[2])

        # Checks the teacher's timestamp in the class creation vc, for not sending multiple messages
        if await TeacherFeedback.check_teacher_vc_cooldown(member.id, self.teacher_cache):
            return

        # Adds a new timestamp to the teacher
        self.teacher_cache[member.id] = await TeacherFeedback.get_timestamp()

        # Checks whether the teacher has saved classes
        if saved_classes := await self.db.get_teacher_saved_classes(member.id):
            await self.show_teacher_saved_classes(member, saved_classes)
        else:
            class_info: Dict[str, str] = await self.ask_class_creation_questions(member)
            if class_info.values():
                await self.start_class(member, class_info)

    async def show_teacher_saved_classes(self, member: discord.Member, saved_classes: List[List[Union[str, int]]]) -> None:
        """ Shows the teacher their saved classes.
        :param member: The teacher.
        :param saved_classes: The teacher's saved classes. """

        additional = {'cog': self, 'db': self.db, 'change_embed': self._make_saved_class_embed}

        cc_channel = discord.utils.get(member.guild.channels, id=create_room_txt_id)
        msg = await cc_channel.send(f"**Welcome back, {member.mention}!**")
        ctx = await self.client.get_context(msg)
        ctx.author = member

        teacher_menu = menus.MenuPages(source=SwitchSavedClasses(saved_classes, **additional), clear_reactions_after=True)
        # Gets the custom buttons (select, new, trash)
        select_btn = menus.Button('✅', SwitchSavedClassesButtons.select_btn)
        new_btn = menus.Button('🆕', SwitchSavedClassesButtons.new_btn)
        trash_btn = menus.Button('🗑️', SwitchSavedClassesButtons.trash_btn)
        # Attaches the custom buttons (select, new, trash) to the menu
        teacher_menu.add_button(button=select_btn)
        teacher_menu.add_button(button=new_btn)
        teacher_menu.add_button(button=trash_btn)

        await teacher_menu.start(ctx)

    async def _make_saved_class_embed(self, ctx: commands.Context, entries: List[List[Union[str, int]]], offset: int, lentries: int) -> discord.Embed:
        """ Makes an embedded message for the teacher's saved class.
        :param member: The teacher.
        :param saved_classes: The teacher's saved classes. """

        member = ctx.author

        saved_class = entries

        # create_class = await self.create_class(member, cc_channel, saved_classes[class_index][1].title(), saved_classes[class_index][2].title(), saved_classes[class_index][3])

        embed = discord.Embed(
            title=f"__**{saved_class[1].title()} - ({offset}/{lentries})**__",
            description=saved_class[3], color=discord.Colour.green())
        embed.add_field(name=f"__**Type:**__", value=saved_class[2].title(),
                        inline=True)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=member)
        embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)
        return embed

    async def start_class(self, member: discord.Member, class_info: Dict[str, str]) -> None:
        """ Starts a language class.
        :param class_info: The information about the class. """

        current_ts = await TeacherFeedback.get_timestamp()
        cc_channel = discord.utils.get(member.guild.channels, id=create_room_txt_id)
        txt, vc = await self.create_channels(member, cc_channel, class_info)
        await self.db.insert_active_teacher_class(
            member.id,
            txt.id, vc.id, class_info['language'], class_info['type'],
            int(current_ts), class_info['desc'])

    async def join_class(self, member: discord.Member, class_vc: discord.VoiceChannel) -> None:
        """ Joins a class.
        :param member: The member who's joining the class.
        :param class_vc: The class to join. """

        if not class_vc:
            return

        # Checks whether it's a teacher
        if not (teacher_class := await self.db.get_active_teacher_class_by_vc_id(class_vc.id)):
            return

        current_ts = await TeacherFeedback.get_timestamp()

        # Checks whether it's a teacher
        if teacher_class[0] == member.id:
            # Update everyone's timestamp
            await self.db.update_teacher_class_time(member.id, current_ts)
            await self.db.update_teacher_class_ts(member.id, current_ts)
            await self.db.update_all_students_ts(member.id, current_ts)

        else:  # Otherwise, it's a student
            teacher = discord.utils.get(member.guild.members, id=teacher_class[0])
            teacher_in_class = teacher and teacher in class_vc.members

            # Check whether user is already in the system
            if student := await self.db.get_student_by_vc_id(member.id, class_vc.id):
                # Update user's timestamp
                if teacher_in_class:
                    await self.db.update_student_ts(member.id, current_ts, teacher_class[0])
            else:
                await self.db.update_teacher_class_members(teacher_class[0])
                # Insert user into the class
                if teacher_in_class:
                    await self.db.insert_student(member.id, teacher_class[0], class_vc.id, current_ts)
                else:
                    await self.db.insert_student(member.id, teacher_class[0], class_vc.id)

    async def leave_class(self, member: discord.Member, class_vc: discord.VoiceChannel) -> None:
        """ Leaves a class.
        :param member: The member who's leaving the class.
        :param class_vc: The class to leave. """

        current_ts = await TeacherFeedback.get_timestamp()

        teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)

        # Checks whether member is teacher and has an existing class
        if teacher_class := await self.db.get_active_teacher_class_by_teacher_and_vc_id(member.id, class_vc.id):
            # Updates all students time
            await self.db.update_teacher_class_time(member.id, current_ts)
            await self.db.update_all_students_time(member.id, current_ts)

            class_txt = discord.utils.get(member.guild.channels, id=teacher_class[1])
            try:
                msg = await class_txt.send(f"**I saw you left your room, {member.mention}.**")
            except:
                return
            ctx = await self.client.get_context(msg)
            ctx.author = member
            # Asks the teacher whether they are ending the class
            confirm = await ConfirmSkill(f"**End class, {member.mention}?**").prompt(ctx)
            if confirm:
                teacher_class = await self.db.get_active_teacher_class_by_teacher_and_vc_id(member.id, class_vc.id)
                await self.end_class(member, class_txt, class_vc, teacher_class)
        else:
            # Updates the student's time
            if teacher_class := await self.db.get_active_teacher_class_by_vc_id(class_vc.id):
                await self.db.update_student_time(member.id, teacher_class[0], current_ts)

    async def end_class(self, member: discord.Member, text_channel: discord.TextChannel, voice_channel: discord.VoiceChannel, teacher_class: List[int]) -> None:
        """ Ends the teacher's class.
        :param member: The teacher whose class is gonna be ended.
        :param text_channel: The class' text channel.
        :param voice_channel: The class voice channel.
        :param teacher_class: The teacher's class information from the database. """

        await text_channel.send("**Class ended!**")
        await voice_channel.delete()
        await text_channel.delete()
        await asyncio.sleep(5)
        # Gets all students and deletes the class from the system
        users_feedback = await self.db.get_all_students(member.id)
        await self.db.delete_active_teacher_class_by_teacher_and_vc_id(member.id, teacher_class[2])

        await self.db.delete_active_students(member.id)

        # teacher, txt_id, vc_id, language, class_type, vc_timestamp, vc_time, members, class_desc)

        # Checks whether the class duration was greater or equal than 10 minutes.
        if int(teacher_class[6]) >= 600:

            await self.show_class_history(member, teacher_class)

            await self.ask_class_reward(member, teacher_class, users_feedback)

    async def show_class_history(self, member: discord.Member, teacher_class: List[int]) -> None:
        """ Shows the teacher's class in the class history,
        containing statistics of the class.
        :param member: The teacher.
        :param teacher_class: The teacher's class information. """

        formatted_text = await TeacherFeedback.get_formatted_time_text(teacher_class[6])

        # Makes a class history report
        history_channel = discord.utils.get(member.guild.channels, id=class_history_channel_id)

        class_embed = discord.Embed(title=f"__{teacher_class[3].title()} Class__",
            description=teacher_class[8], colour=member.colour, timestamp=datetime.utcnow())

        class_embed.add_field(name=f"__**Duration:**__", value=formatted_text, inline=False)
        class_embed.add_field(name=f"__**Joined:**__", value=f"{teacher_class[7]} members.", inline=False)
        class_embed.add_field(name=f"__**Type of class:**__", value=f"{teacher_class[4].title()}.", inline=False)

        class_embed.set_thumbnail(url=member.avatar_url)
        class_embed.set_author(name=member.name, url=member.avatar_url)
        class_embed.set_footer(text='Class Report', icon_url=self.client.user.avatar_url)

        await history_channel.send(embed=class_embed)

    async def ask_class_reward(self, member: discord.Member, teacher_class: List[int], users_feedback: List[List[int]]) -> None:
        """ Asks the teacher whether they want to reward the students who have
        enough participation in their class.
        :param member: The teacher.
        :param teacher_class: The teacher's class information.
        :param users_feedback: The students' class participation data. """

        guild = member.guild

        simple_embed = discord.Embed(
            title=f"All {member.display_name}'s students", description="**LOADING...**", colour=discord.Colour.green())
        simple_embed.set_thumbnail(url=guild.icon_url)
        simple_embed.set_footer(text=guild.name, icon_url=guild.icon_url)
        reward_channel = discord.utils.get(guild.channels, id=reward_channel_id)
        simple = await reward_channel.send(content=member.mention, embed=simple_embed)

        await simple.add_reaction('✅')
        await simple.add_reaction('❌')

        await self.save_class_feedback(
            msg=simple, teacher=member, users_feedback=users_feedback,
            class_type=teacher_class[4], language=teacher_class[3], guild=guild
        )

        user = await self.db.get_waiting_reward_student(member.id, simple.id)
        lenactive = user[-1]
        await self.show_user_feedback(msg=simple, guild=guild, user=user, lenactive=lenactive, teacher=member)

    async def save_class_feedback(self, msg: discord.Message, teacher: discord.Member, users_feedback: List[List[int]], class_type: str, language: str, guild: discord.Guild) -> None:
        """ Saves the members data so the teacher can give them a feedback and reward them later.
        :param msg: The message to attach the students' data to.
        :param teacher: The teacher.
        :param users_feedback: The students' class participation data.
        :param class_type: The type of the class (Pronunciation / Grammar / Programming)
        :param language: The language taught in the class.
        :param guild: The server in which the class was hosted in. """

        # Checks the class' requirements based on the type of the class (Grammar, Pronunciation)
        active_users = []
        if users_feedback:
            if class_type.title() == 'Pronunciation':
                active_users = [uf for uf in users_feedback if uf[3] >= 1800]
            elif class_type.title() == 'Grammar':
                active_users = [uf for uf in users_feedback if uf[1] >= 5]
            elif class_type.title() == 'Programming':
                active_users = [uf for uf in users_feedback if uf[3] >= 1800]

        formatted_active_users = [
            (msg.id, u[0], u[1], u[3], teacher.id, class_type, language) for u in active_users
        ]

        await self.db.insert_student_reward(formatted_active_users)

    async def show_user_feedback(self, msg: discord.Message, guild: discord.Guild, user: List[int], lenactive: int, teacher: discord.Member) -> None:
        """ Shows the embedded message containing the rewardable students.
        :param msg: The message attached to the data.
        :param guild: The guild in which the class was hosted.
        :param user: The next user to whom give a feedback.
        :param lenactive: The amount of users waiting for a feedback.
        :param teacher: The teacher. """

        if not user:
            done_embed = discord.Embed(title="__**DONE!**__", color=discord.Color.green())
            await msg.edit(embed=done_embed, delete_after=3)
            users = await self.db.get_reward_accepted_students(msg.id)
            if users:
                return await self.reward_accepted_students(teacher, users)
            else:
                return

        member = discord.utils.get(guild.members, id=user[1])

        if not member:
            await self.db.delete_waiting_reward_student(msg_id=user[0], user_id=user[1], teacher_id=user[4])
            await asyncio.sleep(0.5)
            user = await self.db.get_waiting_reward_student(user[4], user[0])
            lenactive = user[-1]
            if lenactive:
                return await self.show_user_feedback(msg=msg, guild=guild, user=user, lenactive=lenactive, teacher=teacher)
            else:
                done_embed = discord.Embed(title="__**DONE!**__", colour=discord.Colour.green())
                await msg.edit(embed=done_embed, delete_after=3)
                users = await self.db.get_reward_accepted_students(msg.id)
                if users:
                    return await self.reward_accepted_students(teacher, users)
                else:
                    return

        m, s = divmod(int(user[3]), 60)
        h, m = divmod(m, 60)

        # Embedded message for the current user
        reward_embed = discord.Embed(
            title=f"**[{lenactive} to go] Reward __{member}__?**",
            description=f"**Sent:** {user[2]} messages.\n**Have been:** {h:d} hours, {m:02d} minutes and {s:02d} seconds in the voice channel.",
            color=discord.Color.green())

        reward_embed.set_thumbnail(url=member.avatar_url)
        reward_embed.set_author(name=f"ID: {member.id}")
        reward_embed.set_footer(text=guild.name, icon_url=guild.icon_url)
        await msg.edit(embed=reward_embed)

    async def reward_accepted_students(self, teacher: discord.Member, users_to_reward: List[int]) -> None:
        """ Rewards all users that got accepted by the teacher.
        :param teacher:  The teacher of that class
        :param users_to_reward: A list of users who got accepted to be rewarded. """

        language = users_to_reward[0][1]
        class_type = users_to_reward[0][2]
        msg_id = users_to_reward[0][3]

        if users_to_reward:
            the_reward_embed = discord.Embed(
                title="__**Class Activity Reward**__",
                description=f"The following people got rewarded for participating and being active in {teacher.mention}'s __{language}__ {class_type} class!\n__Teacher__ **+25łł**; __students__ **+10łł**",
                colour=discord.Colour.green())
            the_reward_embed.set_footer(text=teacher.guild.name, icon_url=teacher.guild.icon_url)
            the_reward_embed.set_thumbnail(url=teacher.avatar_url)
            the_reward_embed.set_author(name=teacher, icon_url=teacher.avatar_url)
            the_reward_embed.set_image(
                url="https://cdn.discordapp.com/attachments/668049600871006208/704406592400916510/emote.png")

            SlothCurrency = self.client.get_cog('SlothCurrency')

            rewarded_members_text = []
            for ru in users_to_reward:
                try:
                    member = discord.utils.get(teacher.guild.members, id=ru[0])
                    rewarded_members_text.append(f"{member.mention}")
                    if await SlothCurrency.get_user_currency(member.id):
                        await SlothCurrency.update_user_money(member.id, 10)
                        await SlothCurrency.update_user_class_reward(ru[0])
                except:
                    pass

            the_reward_embed.add_field(name="__**Rewarded members**__", value=', '.join(rewarded_members_text), inline=True)

            if await SlothCurrency.get_user_currency(teacher.id):
                try:
                    await SlothCurrency.update_user_money(teacher.id, 25)
                    await SlothCurrency.update_user_hosted(teacher.id)
                except:
                    pass

            commands_channel = discord.utils.get(teacher.guild.channels, id=bot_commands_channel_id)
            await commands_channel.send(embed=the_reward_embed)
            return await self.db.delete_rewarded_users(msg_id)

    # ===== Channel management =====

    async def get_channel_perms(self, member: discord.Member, language: str) -> Dict[str, discord.PermissionOverwrite]:
        """ Gets permissions for the class channels according to the language and its roles.
        :param member: The teacher.
        :param language: The language being taught in the class. """

        # Get some roles
        teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)
        preference_role = discord.utils.get(member.guild.roles, id=preference_role_id)
        mod_role = discord.utils.get(member.guild.roles, id=mod_role_id)
        lesson_management_role = discord.utils.get(member.guild.roles, id=lesson_management_role_id)
        sloth_explorer_role = discord.utils.get(member.guild.roles, id=sloth_explorer_role_id)

        overwrites = {}
        # Checks whether it is a custom language that may or may not have a different role pattern
        if custom_role_name := await TeacherFeedback.get_custom_role_name(different_class_roles, language.lower().strip()):
            custom_role = discord.utils.get(member.guild.roles,
                name=custom_role_name.title())

            # Checks whether the role exists
            if custom_role:
                language = custom_role.name
                overwrites[custom_role] = discord.PermissionOverwrite(
                    read_messages=True, send_messages=True, connect=True,
                    speak=True, view_channel=True, embed_links=True)
            else:
                language = custom_role_name

        # Tries to get role permissions for the Native, Fluent, Studying role pattern
        if native_role := discord.utils.get(member.guild.roles, name=f"Native {language.title()}"):
            overwrites[native_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=False, connect=False, speak=False, view_channel=True, embed_links=False)

        if fluent_role := discord.utils.get(member.guild.roles, name=f"Fluent {language.title()}"):
            overwrites[fluent_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True, embed_links=True)

        if studying_role := discord.utils.get(member.guild.roles, name=f"Studying {language.title()}"):
            overwrites[studying_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True, embed_links=True)

        # Gets permissions for general roles
        overwrites[member.guild.default_role] = discord.PermissionOverwrite(
            read_messages=False, send_messages=False, connect=False, speak=False, view_channel=False)

        overwrites[teacher_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True, manage_messages=True, mute_members=True, embed_links=True, connect=True,
            speak=True, move_members=True, view_channel=True)

        overwrites[mod_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True, manage_messages=True, mute_members=True, embed_links=True, connect=True,
            speak=True, move_members=True, view_channel=True)

        overwrites[lesson_management_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True, manage_messages=True, mute_members=True, embed_links=True, connect=True,
            speak=True, move_members=True, view_channel=True, manage_channels=True)

        overwrites[preference_role] = discord.PermissionOverwrite(read_messages=True, send_messages=False, connect=False, view_channel=True)

        overwrites[sloth_explorer_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True, embed_links=True)

        return overwrites

    async def create_channels(self, member: discord.Member, cc_channel, class_info: Dict[str, str]) -> List[Union[discord.TextChannel, discord.VoiceChannel]]:

        """ Creates both class text and voice channels in the server.
        :param member: The teacher.
        :param cc_channel: The Create-a-Classroom channel.
        :param class_info: The information about the class. """

        class_category = discord.utils.get(member.guild.categories, id=create_room_cat_id)
        # Gets the channels perm for the particular language
        overwrites = await self.get_channel_perms(member, class_info['language'])

        # Gets the emoji relative to the class type.
        cemoji = ''
        if class_info['type'].title() == 'Pronunciation':
            cemoji = '🗣️'

        elif class_info['type'].title() == 'Grammar':
            cemoji = '📖'

        elif class_info['type'].title() == 'Programming':
            cemoji = '💻'

        # Creates the text channel
        text_channel = await class_category.create_text_channel(
            name=f"{cemoji} {class_info['language'].title()} Classroom",
            topic=class_info['desc'],
            overwrites=overwrites)

        # Creates the voice channel
        voice_channel = await class_category.create_voice_channel(
            name=f"{cemoji} {class_info['language'].title()} Classroom",
            user_limit=None,
            overwrites=overwrites)

        # Tries to move the user to the voice channel, otherwise delete the channels.
        try:
            await member.move_to(voice_channel)
        except discord.errors.HTTPException:
            await cc_channel.send(
                f"**{member}, you cannot be moved, because you are not in a Voice-Channel, nonetheless the configurations were saved!**")
            await text_channel.delete()
            return await voice_channel.delete()

        await text_channel.send(f"**{member.mention}, this is your text channel!**")
        return text_channel, voice_channel

    # ===== Interactions =====
    async def ask_class_creation_questions(self, member) -> Union[None, Dict[str, str]]:

        cc_channel = discord.utils.get(member.guild.channels, id=create_room_txt_id)

        initial_msg = await cc_channel.send(f"**Let's start your class creation!**")
        ctx = await self.client.get_context(initial_msg)
        ctx.author = member

        # Question 1 - Language
        await cc_channel.send(f"**{member.mention}, type the language that you are gonna teach in the class.\n(None = Don't want to create a class)**")
        if not (class_language := await prompt_message_guild(client=self.client, member=member, channel=cc_channel, limit=20)):
            return
        if class_language.lower() == 'none':
            return await ctx.send(f"**Bye, {member.mention}!**")

        # Question 2 - Type
        await cc_channel.send(f"**{member}, what is the type of your class? (Pronunciation / Grammar / Programming)**")
        while True:
            if not (class_type := await prompt_message_guild(client=self.client, member=member, channel=cc_channel, limit=13)):
                return
            if class_type.lower() in ['pronunciation', 'grammar', 'programming']:
                break

        # Question 3 - Description
        await cc_channel.send(f"**{member}, what's the description of the class?**")
        if not (class_desc := await prompt_message_guild(client=self.client, member=member, channel=cc_channel, limit=100)):
            return

        # Question 4 - Confirmation
        save_class = await ConfirmSkill(f"**{member}, do you wanna save the configurations of this class to use them in the next time?**").prompt(ctx)
        if save_class:
            # Insert class to saved classes, so the user can easily open the class from it later on
            await self.db.insert_saved_teacher_class(member.id, class_language, class_type, class_desc)

        return {'language': class_language, 'type': class_type, 'desc': class_desc}

    # ===== Tools =====
    @staticmethod
    async def get_timestamp() -> int:
        """ Gets the current timestamp. """

        epoch = datetime.utcfromtimestamp(0)
        the_time = (datetime.utcnow() - epoch).total_seconds()
        return the_time

    @staticmethod
    async def check_teacher_vc_cooldown(teacher_id: int, teacher_cache: Dict[int, int], cooldown: int = 60) -> bool:
        """ Checks whether the teacher is on cooldown for creating a class.
        :param teacher_id: The teacher's ID.
        :param teacher_cache: The cache for the teachers
        :param cooldown: The cooldown for the class creation. (Default = 60s) """

        member_ts = teacher_cache.get(teacher_id)
        current_ts = await TeacherFeedback.get_timestamp()
        if member_ts := teacher_cache.get(teacher_id):
            sub = current_ts - member_ts
            return sub <= cooldown
        else:
            return False

    @staticmethod
    async def get_formatted_time_text(seconds: int = 0) -> str:
        """ Gets a time formatted.
        :param seconds: The seconds to format. """

        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)

        text = ''
        if h > 0:
            text = f"{h:d} hours, {m:02d} minutes and {s:02d} seconds"

        elif m > 0:
            text = f"{m:02d} minutes and {s:02d} seconds"

        elif s > 0:
            text = f"{s:02d} seconds"

        return text

    @staticmethod
    async def get_custom_role_name(custom_roles: Dict[str, List[str]], language: str) -> Union[str, bool]:
        """ Gets the name of a custom role by language alias.
        :param custom_roles: Available custom roles.
        :param language: The language alias for the role. """

        # Loops through the dictionary searching for the custom role name.
        try:
            for key, row in custom_roles.items():
                for alias in row:
                    if language.lower() == alias:
                        return key
            # If not found, returns False
            else:
                return False
        except Exception as e:
            return False

    # ====== In-Discord commands ======
    @commands.command(aliases=['showclass', 'view_class', 'viewclass', 'class_info', 'classinfo', 'class_status', 'classstatus'])
    @commands.has_any_role(*[teacher_role_id, mod_role_id, admin_role_id])
    async def show_class(self, ctx) -> None:
        """ (Teacher) Shows an on-going class. """

        channel = ctx.channel
        member = ctx.author
        guild = ctx.guild

        # Checks whether the channel is a class channel
        if not (teacher_class := await self.db.get_active_teacher_class_by_txt_id(channel.id)):
            await ctx.send(f"**This isn't a class channel, {member.mention}!**")

        text_channel = discord.utils.get(guild.channels, id=teacher_class[1])
        voice_channel = discord.utils.get(guild.channels, id=teacher_class[2])

        teacher = discord.utils.get(guild.members, id=teacher_class[0])
        embed = discord.Embed(title=f"__{teacher}'s Class__", description=teacher_class[8], color=teacher.color, timestamp=ctx.message.created_at)

        # Adds the general information field
        formatted_text = await TeacherFeedback.get_formatted_time_text(teacher_class[6])
        embed.add_field(name="__General__",
            value=f"**Language:** {teacher_class[3].title()}.\n**Type:** {teacher_class[4]}.\n**Time:** {formatted_text}.\n**Total Members:** {teacher_class[7]}.\n**Timestamp:** {teacher_class[5]}.", inline=True)

        # Adds the class status information field.
        total_messages = await self.db.get_teacher_class_messages_by_teacher_and_vc_id(teacher.id, voice_channel.id)
        raw_total_time = await self.db.get_teacher_class_time_by_teacher_and_vc_id(teacher.id, voice_channel.id)
        total_time = await TeacherFeedback.get_formatted_time_text(raw_total_time)

        embed.add_field(name="__Channels__",
            value=f"**Text Channel:** {text_channel.mention}.\n**Messages sent:** {total_messages}.\n**Voice Channel:** {voice_channel}.\n**Members In it:** {len(voice_channel.members)}.\n**Total time in it:** {total_time}", inline=True)
        # Adds the PostScript fields
        embed.add_field(name="PS¹", value="The `time` field updates whenever the teacher leaves the room.", inline=False)
        embed.add_field(name="PS²", value="If the `timestamp` field is **None**, it means the teacher is not in the voice channel, therefore users can't earn status.", inline=False)

        # Adds embelishment fields
        embed.set_thumbnail(url=teacher.avatar_url)
        embed.set_author(name=teacher, icon_url=teacher.avatar_url)
        embed.set_footer(text=guild, icon_url=guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['end_class', 'closeclass', 'endclass', 'end', 'finishclass', 'finish', 'finish_class'])
    @commands.has_any_role(*[mod_role_id, admin_role_id])
    async def close_class(self, ctx) -> None:
        """ (MOD) Ends an on-going class. """

        channel = ctx.channel
        member = ctx.author
        teacher_class = await self.db.get_active_teacher_class_by_txt_id(channel.id)
        if teacher_class:
            confirm = await ConfirmSkill(f"**Do you want to close this class channel, {member.mention}?**").prompt(ctx)
            if confirm:
                text_channel = discord.utils.get(member.guild.channels, id=teacher_class[1])
                voice_channel = discord.utils.get(member.guild.channels, id=teacher_class[2])
                await self.end_class(member, text_channel, voice_channel, teacher_class)
            else:
                await ctx.send(f"**Not closing it, then!**")

        else:
            await ctx.send(f"**This isn't a class channel, {member.mention}!**")


class TeacherFeedbackDatabaseCreate:
    """ [CREATE] A class for creating things in the database. """

    pass


class TeacherFeedbackDatabaseInsert:
    """ [INSERT] A class for inserting things into the database. """

    async def insert_saved_teacher_class(self, teacher_id: int, language: str, class_type: str, class_desc: str) -> None:
        """ Inserts a saved teacher class.
        :param teacher_id: The teacher's ID.
        :param language: The language being taught in the class.
        :param class_type: The class type (pronunciation, grammar, programming)
        :param class_desc: The class description. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO SavedClasses (teacher_id, language, class_type, class_desc)
            VALUES (%s, %s, %s, %s)""", (teacher_id, language, class_type, class_desc))
        await db.commit()
        await mycursor.close()

    async def insert_active_teacher_class(self, teacher_id: int, txt_id: int, vc_id: int, language: str, class_type: str, the_time: int, class_desc: str):
        """ Inserts an active teacher class.
        :param teacher_id: The teacher's ID.
        :param txt_id: The text channel ID.
        :param vc_id: The voice channel ID.
        :param language: The language being taught in the class.
        :param class_type: The class type (pronunciation, grammar, programming)
        :param the_time: The current timestamp.
        :param class_desc: The class description. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO ActiveClasses (teacher_id, txt_id, vc_id, language, class_type, vc_timestamp, class_desc)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", (teacher_id, txt_id, vc_id, language, class_type, the_time, class_desc))
        await db.commit()
        await mycursor.close()

    async def insert_student(self, student_id: int, teacher_id: int, vc_id: int, the_time: int = None) -> None:
        """ Inserts a student into the database.
        :param student_id: The student's ID.
        :param teacher_id: The teacher's ID.
        :param vc_id: The voice channel ID.
        :param the_time: The current timestamp. (Optional) """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO Students (student_id, student_ts, teacher_id, vc_id) VALUES (%s, %s, %s, %s)", (student_id, the_time, teacher_id, vc_id))
        await db.commit()
        await mycursor.close()

    async def insert_student_reward(self, formatted_active_users: List[List[Union[str, int]]]) -> None:
        """ Inserts reward related data into the database.
        :param formatted_active_users: The formatted data for the rewardable students. """

        mycursor, db = await the_database()

        sql = """INSERT INTO RewardStudents (
            reward_message, student_id, student_messages,
            student_time, teacher_id, class_type,
            language)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        await mycursor.executemany("""INSERT INTO RewardStudents (
            reward_message, student_id, student_messages,
            student_time, teacher_id, class_type, language)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", formatted_active_users)
        await db.commit()
        await mycursor.close()

    async def insert_student_rewarded(self, user: List[Union[int, str]]):
        """ Saves a user to be rewarded later on.
        :param user: The user to be saved. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO RewardAcceptedStudents (teacher_id, student_id, language, class_type, msg_id)
            VALUES (%s, %s, %s, %s, %s)""", (user[4], user[1], user[6], user[5], user[0]))
        await db.commit()
        await mycursor.close()


class TeacherFeedbackDatabaseSelect:
    """ [SELECT] A class for selecting things from the database. """

    # ===== Teacher =====
    async def get_active_teacher_class_by_teacher_id(self, teacher_id: int) -> List[Union[str, int]]:
        """ Gets an active teacher class by teacher ID.
        :param teacher_id: The teacher's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ActiveClasses WHERE teacher_id = %s", (teacher_id, ))
        the_class = await mycursor.fetchone()
        await mycursor.close()
        return the_class

    async def get_active_teacher_class_by_vc_id(self, vc_id: int) -> List[Union[str, int]]:
        """ Gets an active teacher class by voice channel ID.
        :param vc_id: The voice channel ID. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ActiveClasses WHERE vc_id = %s", (vc_id,))
        the_class = await mycursor.fetchone()
        await mycursor.close()
        return the_class

    async def get_active_teacher_class_by_txt_id(self, txt_id: int) -> List[Union[str, int]]:
        """ Gets an active teacher class by text channel ID.
        :param txt_id: The text channel ID. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ActiveClasses WHERE txt_id = %s", (txt_id,))
        the_class = await mycursor.fetchone()
        await mycursor.close()
        return the_class

    async def get_active_teacher_class_by_teacher_and_vc_id(self, teacher_id: int, vc_id: int) -> List[Union[str, int]]:
        """ Gets an active teacher class by teacher and voice channel ID.
        :param teacher_id: The teacher's ID.
        :param vc_id: The voice channel ID. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ActiveClasses WHERE teacher_id = %s AND vc_id = %s", (teacher_id, vc_id))
        the_class = await mycursor.fetchone()
        await mycursor.close()
        return the_class

    # ===== Saved Class =====
    async def get_teacher_saved_classes(self, teacher_id: int) -> List[List[Union[str, int]]]:
        """ Gets the teacher's saved classes.
        :param teacher_id: The teacher's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM SavedClasses WHERE teacher_id = %s", (teacher_id,))
        saved_classes = await mycursor.fetchall()
        await mycursor.close()
        return saved_classes

    # ===== Active Class =====

    async def get_teacher_class_messages_by_teacher_and_vc_id(self, teacher_id: int, vc_id: int) -> int:
        """ Gets the total amount of messages sent in an active teacher class.
        :param teacher_id: The teacher's ID.
        :param vc_id: The ID of the voice channel attached to that class. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT SUM(student_messages) FROM Students WHERE teacher_id = %s AND vc_id = %s""", (teacher_id, vc_id))
        total_messages = number[0] if (number := await mycursor.fetchone())[0] else 0
        await mycursor.close()
        return total_messages

    async def get_teacher_class_time_by_teacher_and_vc_id(self, teacher_id: int, vc_id: int) -> int:
        """ Gets the total time spent in an active teacher class.
        :param teacher_id: The teacher's ID.
        :param vc_id: The ID of the voice channel attached to that class. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT SUM(student_time) FROM Students WHERE teacher_id = %s AND vc_id = %s""", (teacher_id, vc_id))
        total_time = number[0] if (number := await mycursor.fetchone())[0] else 0
        await mycursor.close()
        return total_time

    # ===== Student =====
    async def get_student_by_vc_id(self, student_id: int, vc_id: int) -> List[int]:
        """ Gets a student by voice channe ID.
        :param student_id: The student's ID.
        :param vc_id: The voice channel ID. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM Students WHERE student_id = %s AND vc_id = %s", (student_id, vc_id))
        the_student = await mycursor.fetchone()
        await mycursor.close()
        return the_student

    async def get_all_students(self, teacher_id: int) -> List[List[int]]:
        """ Get all students by teacher ID.
        :param teacher_id: The teacher's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM Students WHERE teacher_id = %s", (teacher_id,))
        the_students = await mycursor.fetchall()
        await mycursor.close()
        return the_students

    # ===== Reward =====

    async def get_waiting_reward_student(self, teacher_id: int, msg_id: int) -> List[Union[str, int]]:
        """ Gets reward related data that is waiting to be given reviewed.
        :param teacher_id: The teacher's ID.
        :param msg_id: The ID of the message attached to the data. """

        mycursor, db = await the_database()

        await mycursor.execute("SELECT *, COUNT(*) FROM RewardStudents WHERE reward_message = %s and teacher_id = %s", (msg_id, teacher_id))
        users = await mycursor.fetchone()
        await mycursor.close()

        return users

    async def get_reward_accepted_students(self, msg_id: int) -> List[List[Union[int, str]]]:
        """ Gets reward info for the accepted students by reward message ID.
        :param msg_id: The ID of the message to look for. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT student_id, language, class_type, msg_id FROM RewardAcceptedStudents WHERE msg_id = %s", (msg_id,))
        users = await mycursor.fetchall()
        await mycursor.close()
        return users


class TeacherFeedbackDatabaseUpdate:
    """ [UPDATE] A class for updating things in the database. """

    # ===== Teacher =====
    async def update_teacher_class_time(self, teacher_id: int, the_time: int) -> None:
        """ Updates the teacher's voice channel time.
        :param teacher_id: The teacher's ID.
        :param the_time: The current time. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE ActiveClasses SET vc_time = vc_time + (%s - vc_timestamp), vc_timestamp = NULL
            WHERE teacher_id = %s AND vc_timestamp IS NOT NULL""", (the_time, teacher_id))
        await db.commit()
        await mycursor.close()

    async def update_teacher_class_ts(self, teacher_id: int, the_time: int) -> None:
        """ Updates the teacher's voice channel timestamp.
        :param teacher_id: The teacher's ID.
        :param the_time: The current time. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE ActiveClasses SET vc_timestamp = %s WHERE teacher_id = %s", (the_time, teacher_id))
        await db.commit()
        await mycursor.close()

    async def update_teacher_class_members(self, teacher_id: int) -> None:
        """ Updates the teacher's member counter.
        :param teacher_id: The teacher's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE ActiveClasses SET members = members + 1 WHERE teacher_id = %s", (teacher_id,))
        await db.commit()
        await mycursor.close()

    # ===== Student =====

    async def update_student_ts(self, student_id: int, the_time: int, teacher_id: int):
        """ Updates the student's voice channel timestamp.
        :param student_id: The student's ID.
        :param the_time: The current timestamp.
        :param teacher_id: The teacher's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE Students SET student_ts = %s WHERE student_id = %s AND teacher_id = %s""", (the_time, student_id, teacher_id))
        await db.commit()
        await mycursor.close()

    async def update_all_students_ts(self, teacher_id: int, the_time: int) -> None:
        """ Updates all students' voice channel timestamp.
        :param teacher_id: The teacher's ID.
        :param the_time: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE Students SET student_ts = %s WHERE teacher_id = %s", (the_time, teacher_id))
        await db.commit()
        await mycursor.close()

    async def update_student_time(self, student_id: int, teacher_id: int, the_time: int) -> None:
        """ Updates the student's voice channel time.
        :param student_id: The student's ID.
        :param teacher_id: The teacher's ID.
        :param the_time: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE Students SET student_time = student_time + (%s - student_ts), student_ts = NULL
            WHERE student_id = %s AND teacher_id = %s AND student_ts IS NOT NULL""", (the_time, student_id, teacher_id))

        await db.commit()
        await mycursor.close()

    async def update_all_students_time(self, teacher_id: int, the_time: int) -> None:
        """ Updates all students' voice channel time.
        :param teacher_id: The teacher's ID.
        :param the_time: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE Students SET student_time = student_time + (%s - student_ts), student_ts = NULL
            WHERE teacher_id = %s AND student_ts IS NOT NULL""", (the_time, teacher_id))
        await db.commit()
        await mycursor.close()

    async def update_student_messages(self, student_id: int, vc_id: int) -> None:
        """ Update student's message counter.
        :param student_id: The student's ID.
        :param vc_id: The class' voice channel ID. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE Students SET student_messages = student_messages + 1
            WHERE student_id = %s AND vc_id = %s""", (student_id, vc_id))
        await db.commit()
        await mycursor.close()


class TeacherFeedbackDatabaseDelete:
    """ [DELETE] A class for deleting things from the database. """

    async def delete_active_teacher_class_by_teacher_id(self, teacher_id: int):
        """ Deletes an active teacher class by teacher ID.
        :param teacher_id: The teacher's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ActiveClasses WHERE teacher_id = %s", (teacher_id,))
        await db.commit()
        await mycursor.close()

    async def delete_active_teacher_class_by_teacher_and_vc_id(self, teacher_id: int, vc_id: int) -> None:
        """ Deletes an active teacher class by teacher
        and voice channel ID.
        :param teacher_id: The teacher's ID.
        :param vc_id: The voice channel ID. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ActiveClasses WHERE teacher_id = %s AND vc_id = %s", (teacher_id, vc_id))
        await db.commit()
        await mycursor.close()

    async def delete_active_students(self, teacher_id: int) -> None:
        """ Deletes active students.
        :param teacher_id: The teacher's ID. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Students WHERE teacher_id = %s", (teacher_id,))
        await db.commit()
        await mycursor.close()

    async def delete_waiting_reward_student(self, msg_id: int, user_id: int, teacher_id: int) -> None:
        """ Deletes a student from the rewards table.
        :param msg_id: The ID of the message attached to the user data.
        :param user_id: The user's ID.
        :param teacher_id: The teacher's ID. """

        mycursor, db = await the_database()

        await mycursor.execute("DELETE FROM RewardStudents WHERE reward_message = %s AND teacher_id = %s AND student_id = %s", (msg_id, teacher_id, user_id))
        await db.commit()
        await mycursor.close()

    async def delete_rewarded_users(self, msg_id: int) -> None:
        """ Deletes a class rewarding users by message ID:
        :param msg_id: The message ID with which to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM RewardAcceptedStudents WHERE msg_id = %s", (msg_id,))
        await db.commit()
        await mycursor.close()

    async def delete_teacher_saved_class(self, teacher_id: int, language: str, class_type: str, class_desc: str) -> None:
        """ Deletes a teacher saved class from the system.
        :param teacher_id: The teacher's ID.
        :param language: The language of the class.
        :param class_type: The type of class (Pronunciation / Grammar / Programming)
        :param class_desc: The description of the class. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            DELETE FROM SavedClasses
            WHERE teacher_id = %s AND language = %s AND class_type = %s AND class_desc = %s""",
             (teacher_id, language, class_type, class_desc))
        await db.commit()
        await mycursor.close()


class TeacherFeedbackDatabaseShow:
    """ [SHOW] A class for checking things in the database. """

    pass


db_classes: List[object] = [
    TeacherFeedbackDatabaseCreate, TeacherFeedbackDatabaseInsert, TeacherFeedbackDatabaseSelect,
    TeacherFeedbackDatabaseUpdate, TeacherFeedbackDatabaseDelete, TeacherFeedbackDatabaseShow
    ]


class TeacherFeedbackDatabase(*db_classes):
    pass


def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(TeacherFeedback(client))
