import discord
from discord.ext import commands
from mysqldb2 import *
from datetime import datetime

create_room_vc_id = 710506029208698923
create_room_cat_id = 710505892713332757
teacher_role_id = 710526156763299932
cc_channel_id = 710505970601689149
preference_role_id = 711231895744151613
class_history_channel_id = 710505920978747432
bot_commands_channel_id = 710506076277047326
reward_channel_id = 710505943716069437

class CreateClassroom(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_ready(self):
        print("CreateClassroom cog is online!")


    @commands.Cog.listener()
    async def on_message(self, message):
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

        #Checking if it's in the CreateClassroom category
        if bca and bca.id != create_room_cat_id or aca and aca.id != create_room_cat_id:
            return

        teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)

        # Checks if joining a VC
        if ac:
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
                                class_ids = await self.create_class(member, cc_channel, class_info[0], class_info[1])
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
                            class_ids = await self.create_class(member, cc_channel, class_info[0], class_info[1])
                            await self.insert_active_class(member.id, class_ids[0], class_ids[1], class_info[0].title(), class_info[1], int(the_time), class_info[2])

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
                    if the_teacher in ac.members:
                        # Insert user in the class with ts
                        await self.insert_student_w_ts(member.id, int(the_time), the_teacher.id, ac.id)

                    else:
                        # Insert user in the class with None
                        await self.insert_student_w_none(member.id, the_teacher.id, ac.id)

        # Check if leaving a VC
        elif bc:
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
                print(teacher_class[0][6])
                reaction, user = await self.client.wait_for('reaction_add', check=check)
                if str(reaction.emoji) == "✅":
                    await text_channel.send("**Class ended!**")
                    await voice_channel.delete()
                    await text_channel.delete()
                    #await asyncio.sleep(5)
                    # Gets all students and deletes the class from the system
                    users_feedback = await self.get_all_students(member.id)
                    print(users_feedback)
                    await self.delete_active_class(member.id)
                    await self.delete_active_students(member.id)

                    # teacher, txt_id, vc_id, language, class_type, vc_timestamp, vc_time, members, class_desc)
                    # Makes a class history report
                    history_channel = discord.utils.get(member.guild.channels, id=class_history_channel_id)
                    m, s = divmod(teacher_class[0][6], 60)
                    h, m = divmod(m, 60)
                    print(teacher_class[0][6])
                    if teacher_class[0][6] >= 360:
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

                    #teacher_id, users_feedback, guild, language, class_type
                    await self.ask_class_feedback(member.id, users_feedback, member.guild,
                                                  teacher_class[0][3], teacher_class[0][4])
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

    async def ask_class_feedback(self, teacher_id, users_feedback, guild, language, class_type):
        reward_channel = discord.utils.get(guild.channels, id=reward_channel_id)
        active_users = []
        if users_feedback:
            if class_type.title() == 'Pronunciation':
                active_users = [uf for uf in users_feedback if uf[3] >= 1800]
            elif class_type.title() == 'Grammar':
                active_users = [uf for uf in users_feedback if uf[1] >= 10]

        if not active_users:
            return
        print(active_users)
        for uf in active_users:
            if await self.user_in_currency(uf[0]):
                await self.update_user_classes(uf[0])
                #print('\033[33muser classes updated\033[m')

        if reward_channel:
            teacher = discord.utils.get(guild.members, id=teacher_id)
            simple_embed = discord.Embed(title=f"All {teacher.name}'s students", description="**LOADING...**",
                                         colour=discord.Colour.green())
            simple_embed.set_thumbnail(url=teacher.guild.icon_url)
            simple_embed.set_footer(text=teacher.guild.name, icon_url=teacher.guild.icon_url)
            simple = await reward_channel.send(content=teacher.mention, embed=simple_embed)
            class_index = 0
            users_to_reward = []

            await simple.add_reaction('✅')
            await simple.add_reaction('❌')

            def check_reward_react(reaction, user):
                if user == teacher and str(reaction.emoji) in ['✅', '❌']:
                    return True

            while True:
                m, s = divmod(active_users[class_index][3], 60)
                h, m = divmod(m, 60)
                member = discord.utils.get(guild.members, id=active_users[class_index][0])
                reward_embed = discord.Embed(
                    title=f"**[{class_index + 1}/{len(active_users)}] Reward __{member}__?**",
                    description=f"**Sent:** {active_users[class_index][1]} messages.\n**Have been:** {h:d} hours, {m:02d} minutes and {s:02d} seconds in the voice channel.",
                    colour=discord.Colour.green())
                reward_embed.set_thumbnail(url=member.avatar_url)
                reward_embed.set_author(name=member.id)
                reward_embed.set_footer(text=teacher.guild.name, icon_url=teacher.guild.icon_url)
                await simple.edit(embed=reward_embed)

                reaction, user = await self.client.wait_for('reaction_add', check=check_reward_react)

                if str(reaction.emoji) == "✅":
                    await simple.remove_reaction(reaction.emoji, teacher)
                    users_to_reward.append(active_users[class_index][0])
                    # rewards the user
                    if class_index < (len(active_users) - 1):
                        class_index += 1
                        continue
                    else:
                        break
                elif str(reaction.emoji) == '❌':
                    await simple.remove_reaction(reaction.emoji, teacher)
                    if class_index < (len(active_users) - 1):
                        class_index += 1
                        # doesn't reward the user
                        continue
                    else:
                        break

            done_embed = discord.Embed(title="__**DONE!**__", colour=discord.Colour.green())
            await simple.edit(embed=done_embed, delete_after=3)
            if users_to_reward:
                the_reward_embed = discord.Embed(title="__**Class Activity Reward**__",
                                                 description=f"The following people got rewarded for participating and being active in {teacher.mention}'s __{language}__ class!\n__Teacher__ **+25łł**; __students__ **+10łł**",
                                                 colour=discord.Colour.green())
                the_reward_embed.set_footer(text=guild.name, icon_url=guild.icon_url)
                the_reward_embed.set_thumbnail(url=teacher.avatar_url)
                the_reward_embed.set_author(name=teacher, icon_url=teacher.avatar_url)
                the_reward_embed.set_image(
                    url="https://cdn.discordapp.com/attachments/668049600871006208/704406592400916510/emote.png")
                for ru in users_to_reward:
                    member = discord.utils.get(guild.members, id=ru)
                    the_reward_embed.add_field(name="**-**", value=f"**{member.mention};**", inline=True)
                    if await self.user_in_currency(member.id):
                        await self.update_money(member.id, 10)
                        await self.update_user_class_reward(ru)
                        #print('\033[33muser money updated\033[m')
                        #print('\033[33muser rewarded class updated\033[m')

                if await self.user_in_currency(teacher.id):
                    await self.update_money(teacher.id, 25)
                    await self.update_user_hosted(teacher.id)
                    #print('\033[33mteacher money updated\033[m')
                    #print('\033[33mteacher hosted updated\033[m')

                commands_channel = discord.utils.get(guild.channels, id=bot_commands_channel_id)
                return await commands_channel.send(embed=the_reward_embed)

    async def get_channel_perms(self, member, language):
        teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)
        preference_role = discord.utils.get(member.guild.roles, id=preference_role_id)
        native_role = discord.utils.get(member.guild.roles,
                                        name=f"Native {language.title()}")
        fluent_role = discord.utils.get(member.guild.roles,
                                        name=f"Fluent {language.title()}")
        studying_role = discord.utils.get(member.guild.roles,
                                          name=f"Studying {language.title()}")
        overwrites = {}
        overwrites[member.guild.default_role] = discord.PermissionOverwrite(read_messages=False,
                                                                            send_messages=False,
                                                                            connect=False,
                                                                            speak=False,
                                                                            view_channel=False)
        overwrites[teacher_role] = discord.PermissionOverwrite(read_messages=True,
                                                               send_messages=True,
                                                               manage_messages=True,
                                                               mute_members=True,
                                                               embed_links=True, connect=True,
                                                               speak=True,
                                                               view_channel=True)
        overwrites[preference_role] = discord.PermissionOverwrite(read_messages=True,
                                                                  send_messages=False,
                                                                  connect=False,
                                                                  view_channel=True)

        if native_role:
            overwrites[native_role] = discord.PermissionOverwrite(read_messages=True,
                                                                  send_messages=False,
                                                                  connect=False,
                                                                  speak=False,
                                                                  view_channel=True,
                                                                  embed_links=False)

        if fluent_role:
            overwrites[fluent_role] = discord.PermissionOverwrite(read_messages=True,
                                                                  send_messages=True,
                                                                  connect=True,
                                                                  speak=True, view_channel=True,
                                                                  embed_links=True)

        if studying_role:
            overwrites[studying_role] = discord.PermissionOverwrite(read_messages=True,
                                                                    send_messages=True,
                                                                    connect=True,
                                                                    speak=True,
                                                                    view_channel=True,
                                                                    embed_links=True)

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
                create_class = await self.create_class(member, cc_channel, saved_classes[class_index][1].title(), saved_classes[class_index][2].title())
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


    async def create_class(self, member, cc_channel, language, class_type):
        # (Creating rooms)
        the_category_test = discord.utils.get(member.guild.categories, id=create_room_cat_id)
        # Creating text channel
        overwrites = await self.get_channel_perms(member, language)

        cemoji = '🗣️' if class_type == 'Pronunciation' else '📖'

        text_channel = await the_category_test.create_text_channel(
            name=f"{cemoji} {language} Classroom",
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
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_table_saved_classes(self, ctx):
        await ctx.message.delete()
        if await self.check_table_saved_classes_exists():
            return await ctx.send(f"**The table __SavedClasses__ already exists!**", delete_after=5)
        mycursor, db = await the_data_base4()
        await mycursor.execute(
            f"CREATE TABLE SavedClasses (teacher_id bigint, language VARCHAR(20), class_type VARCHAR(13), class_desc VARCHAR(100))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __SavedClasses__ created!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drop_table_saved_classes(self, ctx):
        await ctx.message.delete()
        if not await self.check_table_saved_classes_exists():
            return await ctx.send(f"**The table __SavedClasses__ does not exist!**", delete_after=5)
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"DROP TABLE SavedClasses")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table __SavedClasses__ dropped!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_table_saved_classes(self, ctx=None):
        await ctx.message.delete()
        if not await self.check_table_saved_classes_exists():
            return await ctx.send("**Table __SavedClasses__ doesn't exist yet!**", delete_after=5)
        mycursor, db = await the_data_base4()
        await mycursor.execute('SELECT * FROM SavedClasses')
        teachers = await mycursor.fetchall()
        for teacher in teachers:
            await mycursor.execute(f"DELETE FROM SavedClasses WHERE teacher_id = {teacher[0]}")
            await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __SavedClasses__ has been reset!**", delete_after=5)

    async def check_table_saved_classes_exists(self):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'SavedClasses'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True

    # Get
    async def get_saved_class(self, teacher_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SELECT * FROM SavedClasses WHERE teacher_id = {teacher_id}")
        the_classes = await mycursor.fetchall()
        await mycursor.close()
        return the_classes

    # Insert
    async def insert_saved_class(self, teacher_id: int, language: str, class_type: str, class_desc: str):
        mycursor, db = await the_data_base4()
        await mycursor.execute("INSERT INTO SavedClasses (teacher_id, language, class_type, class_desc) VALUES (%s, %s, %s, %s)", (teacher_id, language, class_type, class_desc))
        await db.commit()
        await mycursor.close()


    # Active classes table
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_table_active_classes(self, ctx):
        await ctx.message.delete()
        if await self.check_table_active_classes_exists():
            return await ctx.send(f"**The table __ActiveClasses__ already exists!**", delete_after=5)
        mycursor, db = await the_data_base4()
        await mycursor.execute(
            f"CREATE TABLE ActiveClasses (teacher_id bigint, txt_id bigint, vc_id bigint, language VARCHAR(20), class_type VARCHAR(13), vc_timestamp bigint, vc_time bigint DEFAULT 0, members bigint DEFAULT 1, class_desc VARCHAR(100))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __ActiveClasses__ created!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drop_table_active_classes(self, ctx):
        await ctx.message.delete()
        if not await self.check_table_active_classes_exists():
            return await ctx.send(f"**The table __ActiveClasses__ does not exist!**", delete_after=5)
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"DROP TABLE ActiveClasses")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table __ActiveClasses__ dropped!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_table_active_classes(self, ctx=None):
        await ctx.message.delete()
        if not await self.check_table_active_classes_exists():
            return await ctx.send("**Table __ActiveClasses__ doesn't exist yet!**", delete_after=5)
        mycursor, db = await the_data_base4()
        await mycursor.execute('SELECT * FROM ActiveClasses')
        teachers = await mycursor.fetchall()
        for teacher in teachers:
            await mycursor.execute(f"DELETE FROM ActiveClasses WHERE teacher_id = {teacher[0]}")
            await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __ActiveClasses__ has been reset!**", delete_after=5)

    async def check_table_active_classes_exists(self):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'ActiveClasses'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True

    # Get
    async def get_active_class_by_teacher(self, teacher_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SELECT * FROM ActiveClasses WHERE teacher_id = {teacher_id}")
        the_class = await mycursor.fetchall()
        await mycursor.close()
        return the_class

    async def get_active_class_by_vc(self, vc_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SELECT * FROM ActiveClasses WHERE vc_id = {vc_id}")
        the_class = await mycursor.fetchall()
        await mycursor.close()
        return the_class

    async def get_active_class_by_txt(self, txt_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SELECT * FROM ActiveClasses WHERE txt_id = {txt_id}")
        the_class = await mycursor.fetchall()
        await mycursor.close()
        return the_class

    # Check
    async def check_active_class_by_teacher(self, teacher_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SELECT * FROM ActiveClasses WHERE teacher_id = {teacher_id}")
        the_class = await mycursor.fetchall()
        await mycursor.close()
        if the_class:
            return True
        else:
            return False

    # Insert
    async def insert_active_class(self, teacher_id: int, txt_id: int, vc_id: int, language: str, class_type: str, the_time: int, class_desc: str):
        mycursor, db = await the_data_base4()
        await mycursor.execute("INSERT INTO ActiveClasses (teacher_id, txt_id, vc_id, language, class_type, vc_timestamp, class_desc) VALUES (%s, %s, %s, %s, %s, %s, %s)", (teacher_id, txt_id, vc_id, language, class_type, the_time, class_desc))
        await db.commit()
        await mycursor.close()

    # Update
    async def update_teacher_time(self, teacher_id: int, the_time: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"UPDATE ActiveClasses SET vc_time = vc_time + ({the_time} - vc_timestamp), vc_timestamp = NULL WHERE teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    async def update_teacher_ts(self, teacher_id: int, the_time: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"UPDATE ActiveClasses SET vc_timestamp = {the_time} WHERE teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()


    # Delete
    async def delete_active_class(self, teacher_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"DELETE FROM ActiveClasses WHERE teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    # Students table
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_table_students(self, ctx):
        await ctx.message.delete()
        if await self.check_table_students():
            return await ctx.send(f"**The table __Students__ already exists!**", delete_after=5)
        mycursor, db = await the_data_base4()
        await mycursor.execute(
            f"CREATE TABLE Students (student_id bigint, student_messages int default 0, student_ts bigint default NULL, student_time bigint default 0, teacher_id bigint, vc_id bigint)")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __Students__ created!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drop_table_students(self, ctx):
        await ctx.message.delete()
        if not await self.check_table_students():
            return await ctx.send(f"**The table __Students__ does not exist!**", delete_after=5)
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"DROP TABLE Students")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table __Students__ dropped!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_table_students(self, ctx=None):
        await ctx.message.delete()
        if not await self.check_table_students():
            return await ctx.send("**Table __Students__ doesn't exist yet!**", delete_after=5)
        mycursor, db = await the_data_base4()
        await mycursor.execute('SELECT * FROM Students')
        teachers = await mycursor.fetchall()
        for teacher in teachers:
            await mycursor.execute(f"DELETE FROM Students WHERE teacher_id = {teacher[0]}")
            await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __Students__ has been reset!**", delete_after=5)

    async def check_table_students(self):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'Students'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True

    # Get (student)
    async def get_student(self, student_id: int, teacher_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SELECT * FROM Students WHERE student_id = {student_id} and teacher_id = {teacher_id}")
        the_student = await mycursor.fetchall()
        await mycursor.close()
        return the_student

    async def get_all_students(self, teacher_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SELECT * FROM Students WHERE teacher_id = {teacher_id}")
        the_students = await mycursor.fetchall()
        await mycursor.close()
        return the_students

    # Insert (student)
    async def insert_student_w_ts(self, student_id: int, the_time: int, teacher_id: int, vc_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute("INSERT INTO Students (student_id, student_ts, teacher_id, vc_id) VALUES (%s, %s, %s, %s)", (student_id, the_time, teacher_id, vc_id))
        await db.commit()
        await mycursor.close()

    async def insert_student_w_none(self, student_id: int, teacher_id: int, vc_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute("INSERT INTO Students (student_id, teacher_id, vc_id) VALUES (%s, %s, %s, %s)", (student_id, teacher_id, vc_id))
        await db.commit()
        await mycursor.close()

    # Update (student)
    async def update_student_ts(self, student_id: int, the_time: int, teacher_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"UPDATE Students SET student_ts = {the_time} WHERE student_id = {student_id} and teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    async def update_student_ts_none(self, student_id: int, teacher_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"UPDATE Students SET student_ts = null WHERE student_id = {student_id} and teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    async def update_all_students_ts(self, teacher_id: int, the_time: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"UPDATE Students SET student_ts = {the_time} WHERE teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()


    async def update_all_students_time(self, teacher_id: int, the_time: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"UPDATE Students SET student_time = student_time + ({the_time} - student_ts), student_ts = NULL WHERE teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    async def update_student_time(self, student_id: int, teacher_id: int, the_time: int, old_ts: int):
        addition = the_time - old_ts
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"UPDATE Students SET students_ts = NULL, student_time = student_time + {addition} WHERE student_id = {student_id} and teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    async def update_student_messages(self, student_id: int, vc_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"UPDATE Students SET student_messages = student_messages + 1 WHERE student_id = {student_id} and vc_id = {vc_id}")
        await db.commit()
        await mycursor.close()

    # Check
    async def check_student_by_vc(self, student_id: int, vc_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"SELECT * FROM Students WHERE student_id = {student_id} and vc_id = {vc_id}")
        the_student = await mycursor.fetchall()
        await mycursor.close()
        if the_student:
            return True
        else:
            return False

    # Delete
    async def delete_active_students(self, teacher_id: int):
        mycursor, db = await the_data_base4()
        await mycursor.execute(f"DELETE FROM Students WHERE teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    # Other tables

    # General
    async def user_in_currency(self, user_id: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"SELECT * FROM UserCurrency WHERE user_id = {user_id}")
        user_currency = await mycursor.fetchall()
        await mycursor.close()
        if user_currency:
            return True
        else:
            return False

    # Update
    async def update_money(self, user_id: int, money: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserCurrency SET user_money = user_money + {money} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_classes(self, user_id: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserCurrency SET user_classes = user_classes + 1 WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_class_reward(self, user_id: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserCurrency SET user_class_reward = user_class_reward + 1 WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_hosted(self, teacher_id: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserCurrency SET user_hosted = user_hosted + 1 WHERE user_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

def setup(client):
    client.add_cog(CreateClassroom(client))