import discord
from discord.ext import commands, menus
from mysqldb import *
from datetime import datetime
import asyncio
from typing import Dict, List, Union, Any
import time
import os
from pprint import pprint
from extra.useful_variables import different_class_roles
from extra.menu import ConfirmSkill

create_room_vc_id = int(os.getenv('CREATE_SMART_CLASSROOM_VC_ID'))
create_room_cat_id = int(os.getenv('CREATE_ROOM_CAT_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))
cc_channel_id = int(os.getenv('CREATE_CLASSROOM_CHANNEL_ID'))
preference_role_id = int(os.getenv('PREFERENCE_ROLE_ID'))
class_history_channel_id = int(os.getenv('CLASS_HISTORY_CHANNEL_ID'))
bot_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))
reward_channel_id = int(os.getenv('REWARD_CHANNEL_ID'))
mod_role_id = int(os.getenv('MOD_ROLE_ID'))
lesson_management_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
sloth_explorer_role_id = int(os.getenv('SLOTH_EXPLORER_ROLE_ID'))

class CreateClassroom(commands.Cog):
    '''
    Commands related to the class creation system.
    '''

    def __init__(self, client):
        self.client = client
        self.teacher_cache: Dict = {}



    @commands.Cog.listener()
    async def on_ready(self):
        print("CreateClassroom cog is online!")

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
        user, lenactive = await self.get_waiting_reward_student(payload.user_id, payload.message_id)
        if user:
            emoji = str(payload.emoji)
            channel = discord.utils.get(guild.channels, id=reward_channel_id)
            msg = await channel.fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji.name, payload.member)
            if emoji == '✅':
                # Adds user to RewardAcceptedStudents table
                await self.add_student_rewarded(user)
                await self.remove_waiting_reward_student(user[0], user[1], user[4])
                # print('removed1:', user[1])
                await asyncio.sleep(0.5)
                user, lenactive = await self.get_waiting_reward_student(payload.user_id, payload.message_id)
                await self.show_user_feedback(msg=msg, guild=guild, user=user, lenactive=lenactive, teacher=payload.member)
            else:
                await self.remove_waiting_reward_student(msg_id=user[0], user_id=user[1], teacher_id=user[4])
                # print('removed2:', user[1])
                await asyncio.sleep(0.5)
                user, lenactive = await self.get_waiting_reward_student(payload.user_id, payload.message_id)
                return await self.show_user_feedback(msg=msg, guild=guild, user=user, lenactive=lenactive, teacher=payload.member)
            
        else:
            # print('Not in the system anymore, for some reason...')
            pass



    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
            
        mc = message.channel
        mca = message.channel.category
        member = message.author

        if message.author.bot:
            return

        # Checks if channel is in the CreateClassroom category
        if mca and mca.id != create_room_cat_id:
            return

        # Checks if the channel is an active class
        the_class = await self.get_active_class_by_txt(mc.id)
        if the_class and not the_class[0][0] == member.id:
            # Checks if user is an active student
            if await self.check_student_by_vc(member.id, the_class[0][2]):
                await self.update_student_messages(member.id, the_class[0][2])


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        bc = before.channel
        ac = after.channel
        bca = before.channel.category if bc else None
        aca = after.channel.category if ac else None

        #print(f"\033[31mBefore channel\033[m: {bc}")
        #print(f"\033[31mBefore category\033[m: {bca}")
        #print(f"\033[33mAfter channel\033[m: {ac}")
        #print(f"\033[33mAfter category\033[m: {aca}")
        #print('\033[34m=-\033[m'*12)

        # Before voice state
        bsm = before.self_mute
        bsd = before.self_deaf
        bss = before.self_stream
        bsv = before.self_video
        # After voice state
        asm = after.self_mute
        asd = after.self_deaf
        ass = after.self_stream
        asv = after.self_video

        #print(bsm == asm and bsd == asd and bss == ass)

        #Checking if it's in the CreateClassroom category
        if bca and bca.id != create_room_cat_id or aca and aca.id != create_room_cat_id:
            return

        teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)

        # Checks if joining a VC
        if ac and bsm == asm and bsd == asd and bss == ass and bsv == asv:
            # Checks if joining the CreateClassroom vc
            if ac.id == create_room_vc_id:
                # Checks if it's a teacher
                if teacher_role in member.roles:
                    # Checks if it has an active class
                    teacher_class = await self.get_active_class_by_teacher(member.id)
                    if teacher_class:
                        the_vc_channel = discord.utils.get(member.guild.channels, id=teacher_class[0][2])
                        await member.move_to(the_vc_channel)
                        # Update everyone's timestamp
                        epoch = datetime.utcfromtimestamp(0)
                        the_time = (datetime.utcnow() - epoch).total_seconds()
                        await self.update_teacher_ts(member.id, int(the_time))
                        await self.update_all_students_ts(member.id, int(the_time))

                    else:
                        # Checks if user is on cooldown for the questions
                        member_ts = self.teacher_cache.get(member.id)
                        time_now = time.time()
                        if member_ts:
                            sub = time_now - member_ts
                            if sub <= 60:
                                return

                        self.teacher_cache[member.id] = time_now

                        # Checks if the teacher has a saved class
                        saved_classes = await self.get_saved_class(member.id)

                        # If yes
                        if saved_classes:
                            # Load a saved class?
                            create_new = await self.ask_if_saved(member)
                            if not create_new:
                                return

                            if create_new == 'No':
                                # Show saved classes
                                await self.show_saved_classes(member, saved_classes)

                            # Then it'll create a new one
                            else:
                                # Creates a new class
                                class_info = await self.ask_creation_questions(member)
                                if not class_info:
                                    return
                                epoch = datetime.utcfromtimestamp(0)
                                the_time = (datetime.utcnow() - epoch).total_seconds()
                                cc_channel = discord.utils.get(member.guild.channels, id=cc_channel_id)
                                class_ids = await self.create_class(member, cc_channel, class_info[0], class_info[1], class_info[2])
                                await self.insert_active_class(member.id, class_ids[0], class_ids[1], class_info[0],
                                                               class_info[1], int(the_time), class_info[2])

                        # If not
                        else:
                            # Creates a new class
                            class_info = await self.ask_creation_questions(member)
                            if not class_info:
                                return
                            epoch = datetime.utcfromtimestamp(0)
                            the_time = (datetime.utcnow() - epoch).total_seconds()
                            cc_channel = discord.utils.get(member.guild.channels, id=cc_channel_id)
                            class_ids = await self.create_class(member, cc_channel, class_info[0], class_info[1], class_info[2])
                            await self.insert_active_class(member.id, class_ids[0], class_ids[1], class_info[0].title(), class_info[1], int(the_time), class_info[2])


            # Check if teacher is rejoining their class
            elif ac.id != create_room_vc_id and await self.get_active_class_by_teacher_and_vc(member.id, ac.id):
                # Update everyone's timestamp
                epoch = datetime.utcfromtimestamp(0)
                the_time = (datetime.utcnow() - epoch).total_seconds()
                await self.update_teacher_ts(member.id, int(the_time))
                await self.update_all_students_ts(member.id, int(the_time))

            # It's in an active class
            else:
                # Gets the teacher's info
                the_class = await self.get_active_class_by_vc(ac.id)
                # Check if the vc is a class, if not, return
                if not the_class:
                    return

                # Get the current timestamp
                epoch = datetime.utcfromtimestamp(0)
                the_time = (datetime.utcnow() - epoch).total_seconds()

                active_student = await self.get_student(member.id, the_class[0][0])
                # Check if it's an active student
                if active_student:
                    # Check if teacher is in the class
                    the_teacher = discord.utils.get(member.guild.members, id=the_class[0][0])
                    if the_teacher in ac.members:
                        # Update user's ts
                        await self.update_student_ts(member.id, int(the_time), the_teacher.id)

                else:
                    # Check if teacher is in the class
                    the_teacher = discord.utils.get(member.guild.members, id=the_class[0][0])
                    await self.update_teacher_members(the_teacher.id)
                    if the_teacher in ac.members:
                        # Insert user in the class with ts
                        await self.insert_student_w_ts(member.id, int(the_time), the_teacher.id, ac.id)

                    else:
                        # Insert user in the class with None
                        await self.insert_student_w_none(member.id, the_teacher.id, ac.id)

        # Check if leaving a VC
        elif bc and bsm == asm and bsd == asd and bss == ass and bsv == asv:
            # Get the current timestamp
            epoch = datetime.utcfromtimestamp(0)
            the_time = (datetime.utcnow() - epoch).total_seconds()

            # Check if it's an active teacher
            teacher_class = await self.get_active_class_by_teacher(member.id)
            if teacher_class:
                # Updates all users' and the teacher's time and timestamps
                await self.update_teacher_time(member.id, int(the_time))
                await self.update_all_students_time(member.id, int(the_time))
                # Asks the teacher if they wanna end the class
                text_channel = discord.utils.get(member.guild.channels, id=teacher_class[0][1])
                voice_channel = discord.utils.get(member.guild.channels, id=teacher_class[0][2])
                fd_msg = await text_channel.send(
                    f"**{member.mention}, I saw you left your classroom, did you finish your class?**")
                await fd_msg.add_reaction('✅')
                await fd_msg.add_reaction('❌')

                def check(reaction, user):
                    return user == member and str(reaction.emoji) in '✅❌'

                teacher_class = await self.get_active_class_by_teacher(member.id)
                # print(teacher_class[0][6])
                reaction, user = await self.client.wait_for('reaction_add', check=check)
                if str(reaction.emoji) == "✅":
                    await self._end_class(
                        member, text_channel, voice_channel, teacher_class)
                else:
                    await text_channel.send("**Class not ended!**")

            # So it's a student
            else:
                # Check if it was a classroom
                class_room = await self.get_active_class_by_vc(bc.id)
                if class_room:
                    # Check if teacher is in the classroom
                    the_teacher = discord.utils.get(member.guild.members, id=class_room[0][0])
                    if the_teacher in bc.members:
                        # Get student's old timestamp
                        student_info = await self.get_student(member.id, the_teacher.id)
                        # Update the student's time
                        await self.update_student_time(member.id, class_room[0][0], int(the_time), student_info[0][2])

    # General commands

    async def _end_class(self, member, text_channel, voice_channel, teacher_class) -> None:
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
        users_feedback = await self.get_all_students(member.id)
        # print(users_feedback)
        await self.delete_active_class(member.id)
        await self.delete_active_students(member.id)

        # teacher, txt_id, vc_id, language, class_type, vc_timestamp, vc_time, members, class_desc)
        # Makes a class history report
        history_channel = discord.utils.get(member.guild.channels, id=class_history_channel_id)
        m, s = divmod(teacher_class[0][6], 60)
        h, m = divmod(m, 60)
        # print(teacher_class[0][6])
        if int(teacher_class[0][6]) >= 600:
            class_embed = discord.Embed(title=f"__{teacher_class[0][3].title()} Class__",
                                        description=teacher_class[0][8], colour=member.colour,
                                        timestamp=datetime.utcnow())
            class_embed.add_field(name=f"__**Duration:**__",
                                  value=f"{h:d} hours, {m:02d} minutes and {s:02d} seconds", inline=False)
            class_embed.add_field(name=f"__**Joined:**__", value=f"{teacher_class[0][7]} members.",
                                  inline=False)
            class_embed.add_field(name=f"__**Type of class:**__", value=f"{teacher_class[0][4].title()}.",
                                  inline=False)
            class_embed.set_thumbnail(url=member.avatar_url)
            class_embed.set_author(name=member.name, url=member.avatar_url)
            class_embed.set_footer(text='Class Report', icon_url=self.client.user.avatar_url)
            await history_channel.send(embed=class_embed)

            guild = member.guild
            teacher = discord.utils.get(guild.members, id=member.id)
            simple_embed = discord.Embed(title=f"All {teacher.name}'s students", description="**LOADING...**",
                                         colour=discord.Colour.green())
            simple_embed.set_thumbnail(url=guild.icon_url)
            simple_embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            reward_channel = discord.utils.get(guild.channels, id=reward_channel_id)
            simple = await reward_channel.send(content=teacher.mention, embed=simple_embed)
            await simple.add_reaction('✅')
            await simple.add_reaction('❌')
            await self.save_class_feedback(msg=simple,
                teacher=member, users_feedback=users_feedback, 
                class_type=teacher_class[0][4], language=teacher_class[0][3], guild=guild
            )


    async def save_class_feedback(self, msg, teacher, users_feedback, class_type, language, guild) -> None:
        """ Saves all users that filled the class' requirements. """


        # Checks the class' requirements based on the type of the class (Grammar, Pronunciation)
        reward_channel = discord.utils.get(guild.channels, id=reward_channel_id)
        active_users = []
        if users_feedback:
            if class_type.title() == 'Pronunciation':
                active_users = [uf for uf in users_feedback if uf[3] >= 1800]
            elif class_type.title() == 'Grammar':
                active_users = [uf for uf in users_feedback if uf[1] >= 5]


        mycursor, db = await the_database()

        sql = """INSERT INTO RewardStudents (
            reward_message, student_id, student_messages, 
            student_time, teacher_id, class_type, 
            language)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        formated_active_users = [
            (msg.id, u[0], u[1], u[3], teacher.id, class_type, language) for u in active_users
        ]

        # pprint(formated_active_users)

        await mycursor.executemany(sql, formated_active_users)
        await db.commit()
        await mycursor.close()

        user, lenactive = await self.get_waiting_reward_student(teacher.id, msg.id)
        # print('Let us start the first show_user_feedback!!!!!!!!')
        await self.show_user_feedback(msg=msg, guild=guild, user=user, lenactive=lenactive, teacher=teacher)
        # print("**Nice!**")

    
    async def add_student_rewarded(self, user: List[Union[int, str]]):
        """ Saves a user to be rewarded later on.
        :param user: The user to be saved. """

        # print("# - Saving user...")

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO RewardAcceptedStudents (teacher_id, student_id, language, class_type, msg_id)
            VALUES (%s, %s, %s, %s, %s)""", (user[4], user[1], user[6], user[5], user[0]))
        await db.commit()
        await mycursor.close()

    async def delete_rewarded_users(self, msg_id: int) -> None:
        """ Deletes a class rewarding message by message ID:
        :param msg_id: The message ID with which to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM RewardAcceptedStudents WHERE msg_id = %s", (msg_id,))
        await db.commit()
        await mycursor.close()

    async def get_waiting_reward_student(self, user_id: int, msg_id: int) -> List[Union[str, int]]:

        mycursor, db = await the_database()

        await mycursor.execute("SELECT * FROM RewardStudents WHERE reward_message = %s and teacher_id = %s", (msg_id, user_id))
        users = await mycursor.fetchall()
        await mycursor.close()
        if users:
            return users[0], len(users)
        else:
            return users, len(users)

    async def get_reward_accepted_students(self, msg_id: int) -> List[List[Union[int, str]]]:
        """ Gets the reward students for a specific reward message.
        :param msg_id: The ID of the message to look for. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT student_id, language, class_type, msg_id FROM RewardAcceptedStudents WHERE msg_id = %s", (msg_id,))
        users = await mycursor.fetchall()
        await mycursor.close()
        # print("USEEEEERS", users)
        return users

    async def remove_waiting_reward_student(self, msg_id: int, user_id: int, teacher_id: int) -> None:

        mycursor, db = await the_database()

        await mycursor.execute("DELETE FROM RewardStudents WHERE reward_message = %s and teacher_id = %s and student_id = %s", (msg_id, teacher_id, user_id))
        await db.commit()
        await mycursor.close()


    async def show_user_feedback(self, msg, guild, user, lenactive, teacher: discord.Member) -> None:

        if not user:
            # print("The end! Let's reward everyone!1")
            done_embed = discord.Embed(title="__**DONE!**__", colour=discord.Colour.green())
            await msg.edit(embed=done_embed, delete_after=3)
            users = await self.get_reward_accepted_students(msg.id)
            if users:
                return await self.reward_accepted_students(teacher, users)
            else:
                return

        member = discord.utils.get(guild.members, id=user[1])

        if not member:
            await self.remove_waiting_reward_student(msg_id=user[0], user_id=user[1], teacher_id=user[4])
            # print('removed:', user[1])
            await asyncio.sleep(0.5)
            user, lenactive = await self.get_waiting_reward_student(user[4], user[0])
            if user:
                # print('another loop')
                return await self.show_user_feedback(msg=msg, guild=guild, user=user, lenactive=lenactive, teacher=teacher)
            else:
                # print("The end! Let's reward everyone!2")
                # return await self.reward_accepted_students()
                done_embed = discord.Embed(title="__**DONE!**__", colour=discord.Colour.green())
                await msg.edit(embed=done_embed, delete_after=3)
                users = await self,get_reward_accepted_students(msg.id)
                if users:
                    return await self.reward_accepted_students(teacher, users)
                else:
                    return

        # print('USER==========ahahhahahah', user)

        m, s = divmod(user[3], 60)
        h, m = divmod(m, 60)

        reward_embed = discord.Embed(
            title=f"**[{lenactive} to go] Reward __{member}__?**",
            description=f"**Sent:** {user[2]} messages.\n**Have been:** {h:d} hours, {m:02d} minutes and {s:02d} seconds in the voice channel.",
            colour=discord.Colour.green())
        reward_embed.set_thumbnail(url=member.avatar_url)
        reward_embed.set_author(name=f"ID: {member.id}")
        reward_embed.set_footer(text=guild.name, icon_url=guild.icon_url)
        await msg.edit(embed=reward_embed)

    async def reward_accepted_students(self, teacher: discord.Member, users_to_reward: List[int]):
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

            rewarded_members_text = []
            for ru in users_to_reward:
                try:
                    member = discord.utils.get(teacher.guild.members, id=ru[0])
                    rewarded_members_text.append(f"{member.mention}")
                    if await self.user_in_currency(member.id):
                        await self.update_money(member.id, 10)
                        await self.update_user_class_reward(ru[0])
                except:
                    pass

            the_reward_embed.add_field(name="__**Rewarded members**__", value=', '.join(rewarded_members_text), inline=True)

            if await self.user_in_currency(teacher.id):
                try:
                    await self.update_money(teacher.id, 25)
                    await self.update_user_hosted(teacher.id)
                except:
                    pass

            commands_channel = discord.utils.get(teacher.guild.channels, id=bot_commands_channel_id)
            await commands_channel.send(embed=the_reward_embed)
            return await self.delete_rewarded_users(msg_id)

    async def get_custom_role_name(self, custom_roles: Dict[str, List[str]], language: str) -> Union[str, bool]:
        # Loops through the dictionary searching for the custom role name

            try:
                for key, row in custom_roles.items():
                    for alias in row:
                        # print(alias)
                        if language.lower() == alias:
                            return key
                # If not found, returns False
                else:
                    return False
            except Exception as e:
                return False

    async def get_channel_perms(self, member, language):
        teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)
        preference_role = discord.utils.get(member.guild.roles, id=preference_role_id)
        mod_role = discord.utils.get(member.guild.roles, id=mod_role_id)
        lesson_management_role = discord.utils.get(member.guild.roles, id=lesson_management_role_id)
        sloth_explorer_role = discord.utils.get(member.guild.roles, id=sloth_explorer_role_id)

        print(language)
        overwrites = {}
        # Checks whether it is a language that has no native, fluent, studying pattern
        if custom_role_name := await self.get_custom_role_name(different_class_roles, language.lower().strip()):
            custom_role = discord.utils.get(member.guild.roles,
                name=custom_role_name.title())

        if custom_role:
            language = custom_role.name
            overwrites[custom_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, connect=True,
                speak=True, view_channel=True, embed_links=True)
        else:
            language = custom_role_name


        print(language)
        print(custom_role)
        native_role = discord.utils.get(
            member.guild.roles, name=f"Native {language.title()}")

        fluent_role = discord.utils.get(
            member.guild.roles, name=f"Fluent {language.title()}")

        studying_role = discord.utils.get(
            member.guild.roles, name=f"Studying {language.title()}")

        if native_role:
            overwrites[native_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=False, connect=False,
            speak=False, view_channel=True, embed_links=False)

        if fluent_role:
            overwrites[fluent_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, connect=True,
                speak=True, view_channel=True, embed_links=True)

        if studying_role:
            overwrites[studying_role] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, connect=True,
                speak=True, view_channel=True, embed_links=True)

        overwrites[member.guild.default_role] = discord.PermissionOverwrite(
            read_messages=False, send_messages=False, connect=False, 
            speak=False, view_channel=False)

        overwrites[teacher_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True, manage_messages=True, 
            mute_members=True, embed_links=True, connect=True, 
            speak=True, move_members=True, view_channel=True)

        overwrites[mod_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True, manage_messages=True, 
            mute_members=True, embed_links=True, connect=True,
            speak=True, move_members=True, view_channel=True)

        overwrites[lesson_management_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=True, manage_messages=True, 
            mute_members=True, embed_links=True, connect=True,
            speak=True, move_members=True, view_channel=True, manage_channels=True)

        overwrites[preference_role] = discord.PermissionOverwrite(
            read_messages=True, send_messages=False, connect=False, view_channel=True)

        overwrites[sloth_explorer_role] = discord.PermissionOverwrite(
                    read_messages=True, send_messages=True, connect=True,
                    speak=True, view_channel=True, embed_links=True)

        return overwrites

    async def show_saved_classes(self, member, saved_classes):
        cc_channel = discord.utils.get(member.guild.channels, id=cc_channel_id)

        simple_embed = discord.Embed(title=f"All {member.name}'s", description="**LOADING...**",
                                     colour=discord.Colour.green())
        simple_embed.set_thumbnail(url=member.guild.icon_url)
        simple_embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)
        simple = await cc_channel.send(embed=simple_embed)
        class_index = 0

        if len(saved_classes) > 1:
            await simple.add_reaction('⬅️')

        await simple.add_reaction('✅')
        await simple.add_reaction('❌')

        if len(saved_classes) > 1:
            await simple.add_reaction('➡️')

        def check_react(reaction, user):
            if len(saved_classes) > 1:
                if user == member and str(reaction.emoji) in ['⬅️', '✅', '❌', '➡️']:
                    return True
            else:
                if user == member and str(reaction.emoji) in ['✅', '❌']:
                    return True

        while True:
            embed = discord.Embed(
                title=f"__**{saved_classes[class_index][1]} - ({class_index+1}/{len(saved_classes)})**__",
                description=saved_classes[class_index][3], colour=discord.Colour.green())
            embed.add_field(name=f"__**Type:**__", value=saved_classes[class_index][2],
                            inline=True)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=member)
            embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)
            await simple.edit(embed=embed)

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=60,
                                                            check=check_react)
            except asyncio.TimeoutError:
                timeout = discord.Embed(title='Timeout',
                                        description=f"{member}, you took too long to select a class, try again later.",
                                        colour=discord.Colour.dark_red())
                return await cc_channel.send(embed=timeout)

            if str(reaction.emoji) == "✅":
                await simple.remove_reaction(reaction.emoji, member)
                await cc_channel.send(f"**Class (__{saved_classes[class_index][1].title()}__ | __{saved_classes[class_index][2].title()}__) selected!**")
                create_class = await self.create_class(member, cc_channel, saved_classes[class_index][1].title(), saved_classes[class_index][2].title(), saved_classes[class_index][3])
                # teacher_id, txt_id, vc_id, language, class_type, vc_timestamp, vc_time, members, class_desc
                # teacher_id, language, class_type, class_desc
                epoch = datetime.utcfromtimestamp(0)
                the_time = (datetime.utcnow() - epoch).total_seconds()
                return await self.insert_active_class(member.id, create_class[0], create_class[1], saved_classes[class_index][1].title(), saved_classes[class_index][2].title(), int(the_time), saved_classes[class_index][3])

            elif str(reaction.emoji) == '❌':
                await simple.remove_reaction(reaction.emoji, member)
                return await cc_channel.send(f"**{member}, class selection has been cancelled!**")
            elif str(reaction.emoji) == "➡️":
                await simple.remove_reaction(reaction.emoji, member)
                if class_index < (len(saved_classes) - 1):
                    class_index += 1
                continue
            elif str(reaction.emoji) == "⬅️":
                await simple.remove_reaction(reaction.emoji, member)
                if class_index > 0:
                    class_index -= 1
                continue

    async def ask_if_saved(self, member):

        cc_channel = discord.utils.get(member.guild.channels, id=cc_channel_id)

        def check_yes_no(m):
            value = m.content
            author = m.author
            if m.channel == cc_channel:
                if value.title() in ['Yes', 'No'] and author == member:
                    return True
                elif not value.title() in ['Yes', 'No'] and author == member:
                    self.client.loop.create_task(
                        cc_channel.send(f'**{member}, inform a valid answer! (Yes / No)**', delete_after=5))

        await cc_channel.send(
            f"**{member.mention}, create a new class? If not, you will load a saved class.**")

        try:
            class_new = await self.client.wait_for('message', timeout=60.0, check=check_yes_no)
            class_new = class_new.content
        except asyncio.TimeoutError:
            timeout = discord.Embed(title='Timeout',
                                    description=f'{member}, you took too long to answer the questions, try again later.',
                                    colour=discord.Colour.dark_red())
            await cc_channel.send(embed=timeout)
            return False

        if class_new.title() == "Yes":
            return 'Yes'
        else:
            return 'No'

    async def ask_creation_questions(self, member):
        cc_channel = discord.utils.get(member.guild.channels, id=cc_channel_id)

        def check_yes_no(m):
            value = m.content
            author = m.author
            if m.channel == cc_channel:
                if value.title() in ['Yes', 'No'] and author == member:
                    return True
                elif not value.title() in ['Yes', 'No'] and author == member:
                    self.client.loop.create_task(
                        cc_channel.send(f'**{member}, inform a valid answer! (Yes / No)**', delete_after=5))


        # Question 1 - Language
        await cc_channel.send(f"**{member.mention}, type the language that you are gonna teach in the class.\n(None = Don't want to create a class)**")

        def check_language(m):
            value = m.content
            author = m.author
            if m.channel == cc_channel:
                if len(value) <= 20 and author == member:
                    return True
                elif not len(value) <= 20 and author == member:
                    self.client.loop.create_task(
                        cc_channel.send(f"**{member}, inform a shorter name! (Max = 20 characters)**",
                                              delete_after=5))

        try:
            class_language = await self.client.wait_for('message', timeout=60.0, check=check_language)
            class_language = class_language.content
        except asyncio.TimeoutError:
            timeout = discord.Embed(title='Timeout',
                                    description=f"{member}, you took too long to answer the questions, try again later.",
                                    colour=discord.Colour.dark_red())
            await cc_channel.send(embed=timeout)
            return False

        if class_language.title() == 'None':
            await cc_channel.send(f"**{member}, not creating a room then!**")
            return False

        # Question 2 - Type
        await cc_channel.send(f"**{member}, what is the type of your class? (Pronunciation / Grammar)**")

        def check_type(m):
            value = m.content
            author = m.author
            if m.channel == cc_channel:
                if len(value) <= 13 and author == member and value.title() in ['Pronunciation', 'Grammar']:
                    return True
                elif len(value) <= 13 and author == member and not value.title() in ['Pronunciation',
                                                                                     'Grammar']:
                    self.client.loop.create_task(
                        cc_channel.send(f"**{member}, type a valid answer! (Pronunciation / Grammar)**",
                                              delete_after=5))
                elif not len(value) <= 13 and author == member:
                    self.client.loop.create_task(
                        cc_channel.send(f"**{member}, inform a shorter name! (Max = 13 characters)**",
                                              delete_after=5))

        try:
            class_type = await self.client.wait_for('message', timeout=60.0, check=check_type)
            class_type = class_type.content
        except asyncio.TimeoutError:
            timeout = discord.Embed(title='Timeout',
                                    description=f"{member}, you took too long to answer the questions, try again later.",
                                    colour=discord.Colour.dark_red())
            await cc_channel.send(embed=timeout)
            return False

            # Question 3 - Description
        await cc_channel.send(f"**{member}, what's the description of the class?**")

        def check_description(m):
            value = m.content
            author = m.author
            if m.channel == cc_channel:
                if len(value) <= 100 and author == member:
                    return True
                elif len(value) > 100 and author == member:
                    self.client.loop.create_task(
                        cc_channel.send(f"**{member}, inform a shorter description! (Max = 100 characters)**",
                                              delete_after=5))

        try:
            class_desc = await self.client.wait_for('message', timeout=60.0, check=check_description)
            class_desc = class_desc.content
        except asyncio.TimeoutError:
            timeout = discord.Embed(title='Timeout',
                                    description=f"{member}, you took too long to answer the questions, try again later.",
                                    colour=discord.Colour.dark_red())
            await cc_channel.send(embed=timeout)
            return False

        # Question 4 - Description

        await cc_channel.send(
            f"**{member}, do you wanna save the configurations of this class to use them in the next time?**")

        try:
            save_class = await self.client.wait_for('message', timeout=60.0, check=check_yes_no)
            save_class = save_class.content
            if save_class.title() == 'Yes':
                await self.insert_saved_class(member.id, class_language, class_type, class_desc)

        except asyncio.TimeoutError:
            timeout = discord.Embed(title='Timeout',
                                    description=f"{member}, you took too long to answer the questions, try again later.",
                                    colour=discord.Colour.dark_red())
            await cc_channel.send(embed=timeout)
            return False

        else:
            return class_language, class_type, class_desc


    async def create_class(self, member, cc_channel, language, class_type, desc):
        # (Creating rooms)
        the_category_test = discord.utils.get(member.guild.categories, id=create_room_cat_id)
        # Creating text channel
        overwrites = await self.get_channel_perms(member, language)

        cemoji = '🗣️' if class_type == 'Pronunciation' else '📖'
        text_channel = await the_category_test.create_text_channel(
            name=f"{cemoji} {language} Classroom",
            topic=desc,
            overwrites=overwrites)
        # Creating voice channel
        voice_channel = await the_category_test.create_voice_channel(
            name=f"{cemoji} {language.title()} Classroom",
            user_limit=None,
            overwrites=overwrites)
        try:
            await member.move_to(voice_channel)
        except discord.errors.HTTPException:
            await cc_channel.send(
                f"**{member}, you cannot be moved, because you are not in a Voice-Channel, nonetheless the configurations were saved!**")
            await text_channel.delete()
            return await voice_channel.delete()

        await text_channel.send(f"**{member.mention}, this is your text channel!**")
        return text_channel.id, voice_channel.id

    # Database commands

    #Saved classes table
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_saved_classes(self, ctx):
        '''
        (ADM) Creates the SavedClasses table.
        '''
        await ctx.message.delete()
        if await self.check_table_saved_classes_exists():
            return await ctx.send(f"**The table __SavedClasses__ already exists!**", delete_after=5)
        mycursor, db = await the_database()
        await mycursor.execute(
            "CREATE TABLE SavedClasses (teacher_id bigint, language VARCHAR(20), class_type VARCHAR(13), class_desc VARCHAR(100))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __SavedClasses__ created!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_saved_classes(self, ctx):
        '''
        (ADM) Drops the SavedClasses table.
        '''
        await ctx.message.delete()
        if not await self.check_table_saved_classes_exists():
            return await ctx.send(f"**The table __SavedClasses__ does not exist!**", delete_after=5)
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SavedClasses")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table __SavedClasses__ dropped!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_saved_classes(self, ctx=None):
        '''
        (ADM) Resets the SavedClasses table.
        '''
        await ctx.message.delete()
        if not await self.check_table_saved_classes_exists():
            return await ctx.send("**Table __SavedClasses__ doesn't exist yet!**", delete_after=5)
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SavedClasses")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __SavedClasses__ has been reset!**", delete_after=5)

    async def check_table_saved_classes_exists(self) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'SavedClasses'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True

    # Get
    async def get_saved_class(self, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM SavedClasses WHERE teacher_id = {teacher_id}")
        the_classes = await mycursor.fetchall()
        await mycursor.close()
        return the_classes

    # Insert
    async def insert_saved_class(self, teacher_id: int, language: str, class_type: str, class_desc: str):
        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO SavedClasses (teacher_id, language, class_type, class_desc) VALUES (%s, %s, %s, %s)", (teacher_id, language, class_type, class_desc))
        await db.commit()
        await mycursor.close()


    # Active classes table
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_active_classes(self, ctx):
        '''
        (ADM) Creates the ActiveClass table.
        '''
        await ctx.message.delete()
        if await self.check_table_active_classes_exists():
            return await ctx.send(f"**The table __ActiveClasses__ already exists!**", delete_after=5)
        mycursor, db = await the_database()
        await mycursor.execute(
            f"CREATE TABLE ActiveClasses (teacher_id bigint, txt_id bigint, vc_id bigint, language VARCHAR(20), class_type VARCHAR(13), vc_timestamp bigint, vc_time bigint DEFAULT 0, members bigint DEFAULT 1, class_desc VARCHAR(100))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __ActiveClasses__ created!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_active_classes(self, ctx):
        '''
        (ADM) Drops the ActiveClass table.
        '''
        await ctx.message.delete()
        if not await self.check_table_active_classes_exists():
            return await ctx.send(f"**The table __ActiveClasses__ does not exist!**", delete_after=5)
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE ActiveClasses")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table __ActiveClasses__ dropped!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_active_classes(self, ctx=None):
        '''
        (ADM) Resets the ActiveClass table.
        '''
        await ctx.message.delete()
        if not await self.check_table_active_classes_exists():
            return await ctx.send("**Table __ActiveClasses__ doesn't exist yet!**", delete_after=5)
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ActiveClasses")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __ActiveClasses__ has been reset!**", delete_after=5)

    async def check_table_active_classes_exists(self) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'ActiveClasses'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True

    # Get
    async def get_active_class_by_teacher(self, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ActiveClasses WHERE teacher_id = %s", (teacher_id, ))
        the_class = await mycursor.fetchall()
        await mycursor.close()
        return the_class

    async def get_active_class_by_vc(self, vc_id: int):
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ActiveClasses WHERE vc_id = %s", (vc_id,))
        the_class = await mycursor.fetchall()
        await mycursor.close()
        return the_class

    async def get_active_class_by_txt(self, txt_id: int):
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ActiveClasses WHERE txt_id = %s", (txt_id,))
        the_class = await mycursor.fetchall()
        await mycursor.close()
        return the_class

    async def get_active_class_by_teacher_and_vc(self, teacher_id: int, vc_id: int) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ActiveClasses WHERE teacher_id = %s AND vc_id = %s", (teacher_id, vc_id))
        the_class = await mycursor.fetchall()
        await mycursor.close()

        if the_class:
            return True
        else:
            return False

    # Check
    async def check_active_class_by_teacher(self, teacher_id: int) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM ActiveClasses WHERE teacher_id = %s", (teacher_id,))
        the_class = await mycursor.fetchall()
        await mycursor.close()

        if the_class:
            return True
        else:
            return False

    # Insert
    async def insert_active_class(self, teacher_id: int, txt_id: int, vc_id: int, language: str, class_type: str, the_time: int, class_desc: str):
        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO ActiveClasses (teacher_id, txt_id, vc_id, language, class_type, vc_timestamp, class_desc) VALUES (%s, %s, %s, %s, %s, %s, %s)", (teacher_id, txt_id, vc_id, language, class_type, the_time, class_desc))
        await db.commit()
        await mycursor.close()

    # Update
    async def update_teacher_time(self, teacher_id: int, the_time: int):
        mycursor, db = await the_database()
        await mycursor.execute("UPDATE ActiveClasses SET vc_time = vc_time + (%s - vc_timestamp), vc_timestamp = NULL WHERE teacher_id = %s", (the_time, teacher_id))
        await db.commit()
        await mycursor.close()

    async def update_teacher_ts(self, teacher_id: int, the_time: int):
        mycursor, db = await the_database()
        await mycursor.execute("UPDATE ActiveClasses SET vc_timestamp = %s WHERE teacher_id = %s", (the_time, teacher_id))
        await db.commit()
        await mycursor.close()

    async def update_teacher_members(self, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute("UPDATE ActiveClasses SET members = members + 1 WHERE teacher_id = %s", (teacher_id,))
        await db.commit()
        await mycursor.close()


    # Delete
    async def delete_active_class(self, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM ActiveClasses WHERE teacher_id = %s", (teacher_id,))
        await db.commit()
        await mycursor.close()

    # Students table
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_students(self, ctx):
        '''
        (ADM) Creates the Students table.
        '''
        await ctx.message.delete()
        if await self.check_table_students():
            return await ctx.send(f"**The table __Students__ already exists!**", delete_after=5)

        mycursor, db = await the_database()
        await mycursor.execute(
            "CREATE TABLE Students (student_id bigint, student_messages int default 0, student_ts bigint default NULL, student_time bigint default 0, teacher_id bigint, vc_id bigint)")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __Students__ created!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_students(self, ctx):
        '''
        (ADM) Drops the Students table.
        '''
        await ctx.message.delete()
        if not await self.check_table_students():
            return await ctx.send("**The table __Students__ does not exist!**", delete_after=5)
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Students")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table __Students__ dropped!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_students(self, ctx=None):
        '''
        (ADM) Resets the Students table.
        '''
        await ctx.message.delete()
        if not await self.check_table_students():
            return await ctx.send("**Table __Students__ doesn't exist yet!**", delete_after=5)
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Students")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __Students__ has been reset!**", delete_after=5)

    async def check_table_students(self) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Students'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True

    # Get (student)
    async def get_student(self, student_id: int, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM Students WHERE student_id = {student_id} and teacher_id = {teacher_id}")
        the_student = await mycursor.fetchall()
        await mycursor.close()
        return the_student

    async def get_all_students(self, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM Students WHERE teacher_id = {teacher_id}")
        the_students = await mycursor.fetchall()
        await mycursor.close()
        return the_students

    # Insert (student)
    async def insert_student_w_ts(self, student_id: int, the_time: int, teacher_id: int, vc_id: int):
        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO Students (student_id, student_ts, teacher_id, vc_id) VALUES (%s, %s, %s, %s)", (student_id, the_time, teacher_id, vc_id))
        await db.commit()
        await mycursor.close()

    async def insert_student_w_none(self, student_id: int, teacher_id: int, vc_id: int):
        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO Students (student_id, teacher_id, vc_id) VALUES (%s, %s, %s, %s)", (student_id, teacher_id, vc_id))
        await db.commit()
        await mycursor.close()

    # Update (student)
    async def update_student_ts(self, student_id: int, the_time: int, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE Students SET student_ts = {the_time} WHERE student_id = {student_id} and teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    async def update_student_ts_none(self, student_id: int, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE Students SET student_ts = null WHERE student_id = {student_id} and teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    async def update_all_students_ts(self, teacher_id: int, the_time: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE Students SET student_ts = {the_time} WHERE teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()


    async def update_all_students_time(self, teacher_id: int, the_time: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE Students SET student_time = student_time + ({the_time} - student_ts), student_ts = NULL WHERE teacher_id = {teacher_id} and student_ts is not NULL")
        await db.commit()
        await mycursor.close()

    async def update_student_time(self, student_id: int, teacher_id: int, the_time: int, old_ts: int):
        addition = the_time - old_ts
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE Students SET student_time = student_time + {addition}, student_ts = NULL WHERE student_id = {student_id} and teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    async def update_student_messages(self, student_id: int, vc_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE Students SET student_messages = student_messages + 1 WHERE student_id = {student_id} and vc_id = {vc_id}")
        await db.commit()
        await mycursor.close()

    # Check
    async def check_student_by_vc(self, student_id: int, vc_id: int) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM Students WHERE student_id = {student_id} and vc_id = {vc_id}")
        the_student = await mycursor.fetchall()
        await mycursor.close()
        if the_student:
            return True
        else:
            return False

    # Delete
    async def delete_active_students(self, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"DELETE FROM Students WHERE teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    # Other tables

    # General
    async def user_in_currency(self, user_id: int) -> bool:
        mycursor, db = await the_database()
        await mycursor.execute(f"SELECT * FROM UserCurrency WHERE user_id = {user_id}")
        user_currency = await mycursor.fetchall()
        await mycursor.close()
        if user_currency:
            return True
        else:
            return False

    # Update
    async def update_money(self, user_id: int, money: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE UserCurrency SET user_money = user_money + {money} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_classes(self, user_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE UserCurrency SET user_classes = user_classes + 1 WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_class_reward(self, user_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE UserCurrency SET user_class_reward = user_class_reward + 1 WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_hosted(self, teacher_id: int):
        mycursor, db = await the_database()
        await mycursor.execute(f"UPDATE UserCurrency SET user_hosted = user_hosted + 1 WHERE user_id = {teacher_id}")
        await db.commit()
        await mycursor.close()


    # Discord commands
    @commands.command(aliases=['endclass', 'end', 'finishclass', 'finish', 'finish_class'])
    @commands.has_any_role(*[mod_role_id, admin_role_id])
    async def end_class(self, ctx) -> None:
        """ Ends an on-going class. """

        channel = ctx.channel
        member = ctx.author
        teacher_class = await self.get_active_class_by_txt(channel.id)
        if teacher_class:
            confirm = await ConfirmSkill(f"**Do you want to close this class channel, {member.mention}?**").prompt(ctx)
            if confirm:
                text_channel = discord.utils.get(member.guild.channels, id=teacher_class[0][1])
                voice_channel = discord.utils.get(member.guild.channels, id=teacher_class[0][2])
                await self._end_class(member, text_channel, voice_channel, teacher_class)
            else:
                await ctx.send(f"**Not closing it then!**")

        else:
            await ctx.send(f"**This isn't a class channel, {member.mention}!**")

def setup(client):
    client.add_cog(CreateClassroom(client))
