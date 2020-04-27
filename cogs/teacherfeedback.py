import discord
from discord.ext import commands
from mysqldb import *
from mysqldb2 import *
from datetime import datetime


teacher_role_id = 507298235766013981
create_classroom_id = 704430199298850907
feedback_channel_id = 704429237725167756
create_classroom_category_id = 562019326295670806
class_history_channel_id = 704429055239258153
reward_channel_id = 704428903682408498
bot_commands_channel_id = 562019654017744904

class TeacherFeedback(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_ready(self):
        print('TeacherFeedback cog is online!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.channel.category.id == create_classroom_category_id:
            return

        user_is_student = await self.get_specific_user(message.author.id)
        if user_is_student:
            for user_class in user_is_student:
                if user_class[6] == message.channel.id:
                    return await self.update_student_messages(message.author.id, user_class[1])


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        if after.channel:
            user_get_class = await self.user_get_teacher_class(after.channel.id)
            if user_get_class and user_get_class[0][0] != member.id:
                if user_get_class[0][3]:
                    class_channel = discord.utils.get(member.guild.channels, id=user_get_class[0][3])
                    if class_channel:
                        if len(class_channel.members) > user_get_class[0][8]:
                            await self.update_teacher_members(user_get_class[0][0], user_get_class[0][1], len(class_channel.members))

                        # Check if the teacher is in the voice channel
                        voice_channel = discord.utils.get(member.guild.channels, id=user_get_class[0][3])
                        the_teacher = discord.utils.get(member.guild.members, id=user_get_class[0][0])
                        teacher_in_vc = the_teacher in voice_channel.members

                        member_in_class = await self.is_member_in_class(member.id, user_get_class[0][0], user_get_class[0][1])
                        epoch = datetime.utcfromtimestamp(0)
                        the_time = (datetime.utcnow() - epoch).total_seconds()
                        if member_in_class:
                            if teacher_in_vc:
                                await self.update_specific_student2(member.id, user_get_class[0][0], user_get_class[0][1], the_time)
                            else:
                                await self.update_specific_student(member.id, user_get_class[0][0], user_get_class[0][1], 0)
                        else:
                            if teacher_in_vc:
                                await self.insert_user_into_class(member.id, user_get_class[0][1], user_get_class[0][0], user_get_class[0][2], the_time)
                            else:
                                await self.insert_user_into_class(member.id, user_get_class[0][1], user_get_class[0][0], user_get_class[0][2])

            elif before.channel and await self.user_get_teacher_class(before.channel.id):
                class_info = await self.user_get_teacher_class(before.channel.id)
                if class_info[0][3]:
                    channel = discord.utils.get(member.guild.channels, id=class_info[0][3])
                    if channel:
                        member_in_class = await self.is_member_in_class(member.id, class_info[0][0],
                                                                        class_info[0][1])
                        if member_in_class:
                            epoch = datetime.utcfromtimestamp(0)
                            the_time = (datetime.utcnow() - epoch).total_seconds()
                            student_info = await self.get_specific_student(member.id, class_info[0][0],
                                                                           class_info[0][1])
                            if student_info[0][5]:
                                duration = the_time - student_info[0][5]
                            else:
                                duration = 0
                            await self.update_specific_student(member.id, class_info[0][0], class_info[0][1], duration)

        elif await self.user_get_teacher_class(before.channel.id):
            class_info = await self.user_get_teacher_class(before.channel.id)
            if class_info[0][3]:
                channel = discord.utils.get(member.guild.channels, id=class_info[0][3])
                if channel:
                    member_in_class = await self.is_member_in_class(member.id, class_info[0][0], class_info[0][1])
                    if member_in_class:
                        epoch = datetime.utcfromtimestamp(0)
                        the_time = (datetime.utcnow() - epoch).total_seconds()
                        student_info = await self.get_specific_student(member.id, class_info[0][0], class_info[0][1])
                        if student_info[0][5]:
                            duration = the_time - student_info[0][5]
                        else:
                            duration = 0
                        await self.update_specific_student(member.id, class_info[0][0], class_info[0][1], duration)




        if after.channel and after.channel.category and after.channel.category.id == create_classroom_category_id or before.channel and before.channel.category and before.channel.category.id == create_classroom_category_id:
            the_teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)
            if not the_teacher_role in member.roles:
                return

            teacher_class = None
            if before.channel:
                teacher_class = await self.get_teacher_class_info(member.id, before.channel.id)

            if after.channel:
                teacher_class = await self.get_teacher_class_info(member.id, after.channel.id)
                if teacher_class:
                    epoch = datetime.utcfromtimestamp(0)
                    the_time = (datetime.utcnow() - epoch).total_seconds()
                    await self.update_teacher_times(member.id, teacher_class[0][1], 0, the_time)
                    await self.update_student_times2(teacher_class[0][1], member.id, the_time)


            # Joins a vc
            if after.channel and after.channel.id == create_classroom_id:

                all_teacher_classes = await self.get_teacher_all_classes(member.id)

                def check_yes_no(m):
                    value = m.content
                    author = m.author
                    if m.channel == feedback_channel:
                        if value.title() in ['Yes', 'No'] and author == member:
                            return True
                        elif not value.title() in ['Yes', 'No'] and author == member:
                            self.client.loop.create_task(
                                feedback_channel.send('**Inform a valid answer! (Yes / No)**', delete_after=5))


                feedback_channel = discord.utils.get(member.guild.channels, id=feedback_channel_id)
                # Checks if the teacher has saved classes
                if all_teacher_classes:
                    # Question 1 - New class
                    await feedback_channel.send(f"**{member.mention}, create a new class? If not, you will load a saved class.**")

                    try:
                        class_new = await self.client.wait_for('message', timeout=60.0, check=check_yes_no)
                        class_new = class_new.content
                    except asyncio.TimeoutError:
                        timeout = discord.Embed(title='Timeout',
                                                description='You took too long to answer the questions, try again later.',
                                                colour=discord.Colour.dark_red())
                        return await feedback_channel.send(embed=timeout)

                    if class_new.title() == 'No':
                        simple_embed = discord.Embed(title=f"All {member.name}'s", description="**LOADING...**", colour=discord.Colour.green())
                        simple_embed.set_thumbnail(url=member.guild.icon_url)
                        simple_embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)
                        simple = await feedback_channel.send(embed=simple_embed)
                        class_index = 0

                        if len(all_teacher_classes) > 1:
                            await simple.add_reaction('⬅️')

                        await simple.add_reaction('✅')
                        await simple.add_reaction('❌')

                        if len(all_teacher_classes) > 1:
                            await simple.add_reaction('➡️')

                        def check_react(reaction, user):
                            if len(all_teacher_classes) > 1:
                                if user == member and str(reaction.emoji) in ['⬅️', '✅', '❌', '➡️']:
                                    return True
                            else:
                                if user == member and str(reaction.emoji) in ['✅', '❌']:
                                    return True


                        while True:
                            embed = discord.Embed(title=f"__**{all_teacher_classes[class_index][4]} - #{all_teacher_classes[class_index][1]}**__", description=all_teacher_classes[class_index][9], colour=discord.Colour.green())
                            embed.add_field(name=f"__**Type:**__", value=all_teacher_classes[class_index][5], inline=True)
                            embed.set_thumbnail(url=member.avatar_url)
                            embed.set_author(name=member)
                            embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)
                            await simple.edit(embed=embed)

                            try:
                                reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=check_react)
                            except asyncio.TimeoutError:
                                timeout = discord.Embed(title='Timeout',
                                                        description='You took too long to select a class, try again later.',
                                                        colour=discord.Colour.dark_red())
                                return await feedback_channel.send(embed=timeout)

                            if str(reaction.emoji) == "✅":
                                await simple.remove_reaction(reaction.emoji, member)
                                await feedback_channel.send("**Class selected!**")
                                # (Creating rooms)
                                the_category_test = discord.utils.get(member.guild.categories, id=create_classroom_category_id)
                                # Creating text channel
                                teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)
                                native_role = discord.utils.get(member.guild.roles, name=f"Native {all_teacher_classes[class_index][4].title()}")
                                fluent_role = discord.utils.get(member.guild.roles, name=f"Fluent {all_teacher_classes[class_index][4].title()}")
                                studying_role = discord.utils.get(member.guild.roles, name=f"Studying {all_teacher_classes[class_index][4].title()}")
                                if native_role and fluent_role and studying_role:
                                    overwrites = {
                                        member.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                                        teacher_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, mute_members=True, embed_links=True),
                                        native_role: discord.PermissionOverwrite(read_messages=True, send_messages=False, connect=False),
                                        fluent_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                                        studying_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                                    }
                                else:
                                    overwrites = {
                                        member.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                                        teacher_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, mute_members=True, embed_links=True),
                                    }
                                text_channel = await the_category_test.create_text_channel(
                                    name=f"{all_teacher_classes[class_index][4].title()} Classroom", overwrites=overwrites)
                                # Creating voice channel
                                voice_channel = await the_category_test.create_voice_channel(
                                    name=f"{all_teacher_classes[class_index][4].title()} Classroom", user_limit=None, overwrites=overwrites)
                                try:
                                    await member.move_to(voice_channel)
                                except discord.errors.HTTPException:
                                    await feedback_channel.send(f"**{member.mention}, you cannot be moved, nor finish the configurations because you are not in a Voice-Channel!**")
                                    await text_channel.delete()
                                    return await voice_channel.delete()

                                epoch = datetime.utcfromtimestamp(0)
                                the_time = (datetime.utcnow() - epoch).total_seconds()
                                await self.insert_teacher_class(member.id, text_channel.id, voice_channel.id, all_teacher_classes[class_index][4], all_teacher_classes[class_index][5], the_time, all_teacher_classes[class_index][9], 'No')
                                return await text_channel.send(f"**{member.mention}, this is your text channel!**")

                            elif str(reaction.emoji) == '❌':
                                await simple.remove_reaction(reaction.emoji, member)
                                return await feedback_channel.send("**Class selection has been cancelled!**")
                            elif str(reaction.emoji) == "➡️":
                                await simple.remove_reaction(reaction.emoji, member)
                                if class_index < (len(all_teacher_classes) - 1):
                                    class_index += 1
                                continue
                            elif str(reaction.emoji) == "⬅️":
                                await simple.remove_reaction(reaction.emoji, member)
                                if class_index > 0:
                                    class_index -= 1
                                continue


                # Question 2 - Language
                if not all_teacher_classes:
                    await feedback_channel.send(f"**{member.mention}, type the language that you are gonna teach in the class.\n(None = Don't want to create a class)**")
                else:
                    await feedback_channel.send("**Type the language that you are gonna teach in the class.\n(None = Don't want to create a class)**")

                def check_language(m):
                    value = m.content
                    author = m.author
                    if m.channel == feedback_channel:
                        if len(value) <= 20 and author == member:
                            return True
                        elif not len(value) <= 20 and author == member:
                            self.client.loop.create_task(feedback_channel.send('**Inform a shorter name! (Max = 20 characters)**', delete_after=5))

                try:
                    class_language = await self.client.wait_for('message', timeout=60.0, check=check_language)
                    class_language = class_language.content
                except asyncio.TimeoutError:
                    timeout = discord.Embed(title='Timeout',
                                            description='You took too long to answer the questions, try again later.',
                                            colour=discord.Colour.dark_red())
                    return await feedback_channel.send(embed=timeout)

                if class_language.title() == 'None':
                    return await feedback_channel.send(f"**{member}, not creating a room then!**")

                # Question 3 - Type
                await feedback_channel.send(f"**What is the type of your class? (Pronunciation / Grammar)**")

                def check_type(m):
                    value = m.content
                    author = m.author
                    if m.channel == feedback_channel:
                        if len(value) <= 13 and author == member and value.title() in ['Pronunciation', 'Grammar']:
                            return True
                        elif len(value) <= 13 and author == member and not value.title() in ['Pronunciation', 'Grammar']:
                            self.client.loop.create_task(
                                feedback_channel.send('**Type a valid answer! (Pronunciation / Grammar)**', delete_after=5))
                        elif not len(value) <= 13 and author == member:
                            self.client.loop.create_task(feedback_channel.send('**Inform a shorter name! (Max = 13 characters)**', delete_after=5))

                try:
                    class_type = await self.client.wait_for('message', timeout=60.0, check=check_type)
                    class_type = class_type.content
                except asyncio.TimeoutError:
                    timeout = discord.Embed(title='Timeout',
                                            description='You took too long to answer the questions, try again later.',
                                            colour=discord.Colour.dark_red())
                    return await feedback_channel.send(embed=timeout)

                # Question 4 - Description
                await feedback_channel.send(f"**What's the description of the class?**")
                def check_description(m):
                    value = m.content
                    author = m.author
                    if m.channel == feedback_channel:
                        if len(value) <= 100 and author == member:
                            return True
                        elif len(value) > 100 and author == member:
                            self.client.loop.create_task(feedback_channel.send(f"**Inform a shorter description! (Max = 100 characters)**", delete_after=5))

                try:
                    class_desc = await self.client.wait_for('message', timeout=60.0, check=check_description)
                    class_desc = class_desc.content
                except asyncio.TimeoutError:
                    timeout = discord.Embed(title='Timeout',
                                            description='You took too long to answer the questions, try again later.',
                                            colour=discord.Colour.dark_red())
                    return await feedback_channel.send(embed=timeout)

                # Question 4 - Description

                await feedback_channel.send(f"**Do you wanna save the configurations of this class to use them in the next time?**")

                try:
                    save_class = await self.client.wait_for('message', timeout=60.0, check=check_yes_no)
                    save_class = save_class.content
                except asyncio.TimeoutError:
                    timeout = discord.Embed(title='Timeout',
                                            description='You took too long to answer the questions, try again later.',
                                            colour=discord.Colour.dark_red())
                    return await feedback_channel.send(embed=timeout)



                await feedback_channel.send(f"__**Language:**__ {class_language} | __**Type:**__ {class_type}")

                # (Creating rooms)
                the_category_test = discord.utils.get(member.guild.categories, id=create_classroom_category_id)
                teacher_role = discord.utils.get(member.guild.roles, id=teacher_role_id)
                native_role = discord.utils.get(member.guild.roles,
                                                name=f"Native {class_language.title()}")
                fluent_role = discord.utils.get(member.guild.roles,
                                                name=f"Fluent {class_language.title()}")
                studying_role = discord.utils.get(member.guild.roles,
                                                  name=f"Studying {class_language.title()}")
                if native_role and fluent_role and studying_role:
                    overwrites = {
                        member.guild.default_role: discord.PermissionOverwrite(read_messages=False,
                                                                               send_messages=False),
                        teacher_role: discord.PermissionOverwrite(read_messages=True, send_messages=True,
                                                                  manage_messages=True, mute_members=True,
                                                                  embed_links=True),
                        native_role: discord.PermissionOverwrite(read_messages=True, send_messages=False,
                                                                 connect=False),
                        fluent_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                        studying_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    }
                else:
                    overwrites = {
                        member.guild.default_role: discord.PermissionOverwrite(read_messages=False,
                                                                               send_messages=False),
                        teacher_role: discord.PermissionOverwrite(read_messages=True, send_messages=True,
                                                                  manage_messages=True, mute_members=True,
                                                                  embed_links=True),
                    }
                # Creating text channel
                text_channel = await the_category_test.create_text_channel(name=f"{class_language.title()} Classroom", overwrites=overwrites)
                # Creating voice channel
                voice_channel = await the_category_test.create_voice_channel(name=f"{class_language.title()} Classroom", user_limit=None, overwrites=overwrites)
                try:
                    await member.move_to(voice_channel)
                except discord.errors.HTTPException:
                    await feedback_channel.send(
                        f"**{member.mention}, you cannot be moved, nor finish the configurations because you are not in a Voice-Channel!**")
                    await text_channel.delete()
                    return await voice_channel.delete()

                await text_channel.send(f"**{member.mention}, this is your text channel!**")
                # Saving temporary class info in the database
                epoch = datetime.utcfromtimestamp(0)
                the_time = (datetime.utcnow() - epoch).total_seconds()
                await self.insert_teacher_class(member.id, text_channel.id, voice_channel.id, class_language, class_type, the_time, class_desc, save_class.title())

            # Leaves a vc
            elif not after.channel and teacher_class and before.channel.id == teacher_class[0][3] or after.channel and teacher_class and after.channel.id != teacher_class[0][3] and before.channel and before.channel.id == teacher_class[0][3]:
                text_channel = discord.utils.get(member.guild.channels, id=teacher_class[0][2])
                voice_channel = discord.utils.get(member.guild.channels, id=teacher_class[0][3])
                fd_msg = await text_channel.send(f"**{member.mention}, I saw you left your classroom, did you finish your class?**")
                await fd_msg.add_reaction('✅')
                await fd_msg.add_reaction('❌')

                # Updates the timestamp and the duration of the class as soon as the teacher leaves the voice channel
                epoch = datetime.utcfromtimestamp(0)
                the_time = (datetime.utcnow() - epoch).total_seconds()
                if teacher_class[0][6]:
                    class_duration = the_time - teacher_class[0][6]
                else:
                    class_duration = 0
                await self.update_teacher_times(member.id, teacher_class[0][1], class_duration, teacher_class[0][6])
                await self.update_student_times(teacher_class[0][1], member.id, the_time)

                def check(reaction, user):
                    return user == member and str(reaction.emoji) in '✅❌'

                reaction, user = await self.client.wait_for('reaction_add', check=check)
                if str(reaction.emoji) == "✅":
                    await text_channel.send("**Class ended!**")
                    await voice_channel.delete()
                    await text_channel.delete()
                    users_feedback = await self.get_all_users_feedback(teacher_class[0][0], teacher_class[0][1])
                    await self.clear_specific_class_students(teacher_class[0][1], teacher_class[0][0])
                    history_channel = discord.utils.get(member.guild.channels, id=class_history_channel_id)
                    teacher_class = await self.get_teacher_class_info(member.id, before.channel.id)
                    m, s = divmod(teacher_class[0][7], 60)
                    h, m = divmod(m, 60)
                    class_embed = discord.Embed(title=f"__{teacher_class[0][4].title()} Class__", description=teacher_class[0][9], colour=discord.Colour.green(), timestamp=datetime.utcnow())
                    class_embed.add_field(name=f"__**Duration:**__", value=f"{h:d} hours, {m:02d} minutes and {s:02d} seconds", inline=False)
                    class_embed.add_field(name=f"__**Joined:**__", value=f"{teacher_class[0][8]} members.", inline=False)
                    class_embed.add_field(name=f"__**Type of class:**__", value=f"{teacher_class[0][5].title()}.", inline=False)
                    class_embed.set_thumbnail(url=member.avatar_url)
                    class_embed.set_author(name=member.name, url=member.avatar_url)
                    class_embed.set_footer(text='Class Report', icon_url=self.client.user.avatar_url)
                    await history_channel.send(embed=class_embed)
                    if teacher_class[0][10] == 'Yes':
                        await self.clear_saved_class(teacher_class[0][0], teacher_class[0][1])

                    else:
                        # Deletes the class
                        await self.remove_temp_class(teacher_class[0][0], teacher_class[0][1])

                    if teacher_class[0][3] >= 1800:
                        await self.update_money(teacher_class[0][0], 25)
                    await self.ask_class_feedback(teacher_class[0][0], users_feedback, member.guild, teacher_class[0][4], teacher_class[0][5])
                else:
                    await text_channel.send("**Class not ended!**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_table_teacher_feedback(self, ctx):
        await ctx.message.delete()
        if await self.check_table_exist():
            return await ctx.send(f"**The table __TeacherFeedback__ already exists!**", delete_after=5)
        mycursor, db = await the_data_base()
        await mycursor.execute(f"CREATE TABLE TeacherFeedback (teacher_id bigint, class_id int NOT NULL AUTO_INCREMENT PRIMARY KEY, txt_id bigint, vc_id bigint, language VARCHAR(20), class_type VARCHAR(13), vc_timestamp bigint DEFAULT NULL, vc_time bigint, members bigint, class_desc VARCHAR(100), save_class VARCHAR(3))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __TeacherFeedback__ created!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drop_table_teacher_feedback(self, ctx):
        await ctx.message.delete()
        if not await self.check_table_exist():
            return await ctx.send(f"**The table __TeacherFeedback__ does not exist!**", delete_after=5)
        mycursor, db = await the_data_base()
        await mycursor.execute(f"DROP TABLE TeacherFeedback")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table __TeacherFeedback__ dropped!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_table_teacher_feedback(self, ctx = None):
        await ctx.message.delete()
        if not await self.check_table_exist():
            return await ctx.send("**Table __TeacherFeedback__ doesn't exist yet!**", delete_after=5)
        mycursor, db = await the_data_base()
        await mycursor.execute('SELECT * FROM TeacherFeedback')
        teachers = await mycursor.fetchall()
        for teacher in teachers:
            await mycursor.execute(f"DELETE FROM TeacherFeedback WHERE teacher_id = {teacher[0]}")
            await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __TeacherFeedback__ has been reset!**", delete_after=5)


    async def check_table_exist(self):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'TeacherFeedback'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True

    async def insert_teacher_class(self, teacher_id: int, txt_id: int, vc_id: int, language: str, class_type: str, vc_timestamp: int, class_desc: str, save_class: str):
        mycursor, db = await the_data_base()
        await mycursor.execute(
            f"INSERT INTO TeacherFeedback (teacher_id, txt_id, vc_id, language, class_type, vc_timestamp, vc_time, members, class_desc, save_class) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (teacher_id, txt_id, vc_id, language, class_type, vc_timestamp, 0, 1, class_desc, save_class))
        await db.commit()
        await mycursor.close()


    async def get_teacher_class_info(self, teacher_id: int, vc_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT * FROM TeacherFeedback WHERE teacher_id = {teacher_id} and vc_id = {vc_id}")
        teacher_class = await mycursor.fetchall()
        return teacher_class


    async def user_get_teacher_class(self, vc_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT * FROM TeacherFeedback WHERE vc_id = {vc_id}")
        teacher_class = await mycursor.fetchall()
        return teacher_class


    async def get_specific_student(self, student_id: int, teacher_id: int, class_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT * FROM StudentFeedback WHERE teacher_id = {teacher_id} and class_id = {class_id} and student_id = {student_id}")
        student_info = await mycursor.fetchall()
        return student_info


    async def get_teacher_all_classes(self, teacher_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT * FROM TeacherFeedback WHERE teacher_id = {teacher_id}")
        teacher_classes = await mycursor.fetchall()
        return teacher_classes


    async def get_len_table(self):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT COUNT(*) FROM TeacherFeedback")
        lentable = await mycursor.fetchall()
        await mycursor.close()
        return lentable[0][0]


    async def update_teacher_times(self, teacher_id: int, class_id: int, class_duration: int, new_timestamp = None):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"UPDATE TeacherFeedback SET vc_timestamp = {new_timestamp}, vc_time = vc_time + {class_duration} WHERE teacher_id = {teacher_id} and class_id = {class_id}")
        await db.commit()
        await mycursor.close()


    async def update_teacher_members(self, teacher_id: int, class_id: int, new_members: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"UPDATE TeacherFeedback SET members = {new_members} WHERE teacher_id = {teacher_id} and class_id = {class_id}")
        await db.commit()
        await mycursor.close()

    async def clear_saved_class(self, teacher_id: int, class_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"UPDATE TeacherFeedback SET members = 1, vc_time = 0, vc_timestamp = NULL, txt_id = 0, vc_id = 0 WHERE teacher_id = {teacher_id} and class_id = {class_id}")
        await db.commit()
        await mycursor.close()

    async def remove_temp_class(self, teacher_id: int, class_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"DELETE FROM TeacherFeedback WHERE teacher_id = {teacher_id} and class_id = {class_id}")
        await db.commit()
        await mycursor.close()


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def show_classes(self, ctx):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT * FROM TeacherFeedback")
        all_classes = await mycursor.fetchall()
        return await ctx.send(all_classes)

    # StudentFeedback table
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_table_student_feedback(self, ctx):
        await ctx.message.delete()
        if await self.check_table_student_exist():
            return await ctx.send(f"**The table __StudentFeedback__ already exists!**", delete_after=5)
        mycursor, db = await the_data_base()
        await mycursor.execute(f"CREATE TABLE StudentFeedback (student_id bigint, class_id int, teacher_id bigint, messages bigint, time bigint, vc_timestamp bigint DEFAULT NULL, channel_id bigint)")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __StudentFeedback__ created!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drop_table_student_feedback(self, ctx):
        await ctx.message.delete()
        if not await self.check_table_student_exist():
            return await ctx.send(f"**The table __StudentFeedback__ does not exist!**", delete_after=5)
        mycursor, db = await the_data_base()
        await mycursor.execute(f"DROP TABLE StudentFeedback")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table __StudentFeedback__ dropped!**", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_table_student_feedback(self, ctx = None):
        await ctx.message.delete()
        if not await self.check_table_student_exist():
            return await ctx.send("**The table __StudentFeedback__ doesn't exist yet!**", delete_after=5)
        mycursor, db = await the_data_base()
        await mycursor.execute('SELECT * FROM StudentFeedback')
        teachers = await mycursor.fetchall()
        for teacher in teachers:
            await mycursor.execute(f"DELETE FROM StudentFeedback WHERE student_id = {teacher[0]}")
            await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __StudentFeedback__ has been reset!**", delete_after=5)


    async def get_all_users_feedback(self, teacher_id: int, class_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT * FROM StudentFeedback WHERE teacher_id = {teacher_id} and class_id = {class_id}")
        users_feedback = await mycursor.fetchall()
        await mycursor.close()
        return users_feedback


    async def update_student_times(self, class_id: int, teacher_id: int, time = None):
        mycursor, db = await the_data_base()
        students = await self.get_all_users_feedback(teacher_id, class_id)
        for student in students:
            if student[5]:
                class_duration = time - student[5]
            else:
                class_duration = 0

            await mycursor.execute(f"UPDATE StudentFeedback SET vc_timestamp = NULL, time = time + {class_duration} WHERE teacher_id = {teacher_id} and student_id = {student[0]} and class_id = {class_id}")
            await db.commit()
        await mycursor.close()

    async def update_student_times2(self, class_id: int, teacher_id: int, new_timestamp: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"UPDATE StudentFeedback SET vc_timestamp = {new_timestamp} WHERE teacher_id = {teacher_id} and class_id = {class_id}")
        await db.commit()
        await mycursor.close()

    async def update_specific_student(self, student_id: int, teacher_id: int, class_id: int, duration: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"UPDATE StudentFeedback SET vc_timestamp = NULL, time = time + {duration} WHERE teacher_id = {teacher_id} and class_id = {class_id} and student_id = {student_id}")
        await db.commit()
        await mycursor.close()

    async def update_specific_student2(self, student_id: int, teacher_id: int, class_id: int, new_timestamp):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"UPDATE StudentFeedback SET vc_timestamp = {new_timestamp} WHERE teacher_id = {teacher_id} and class_id = {class_id} and student_id = {student_id}")
        await db.commit()
        await mycursor.close()

    async def insert_user_into_class(self, student_id: int, class_id: int, teacher_id: int, channel_id: int, vc_timestamp: int = None):
        mycursor, db = await the_data_base()
        await mycursor.execute("INSERT INTO StudentFeedback (student_id, class_id, teacher_id, messages, time, vc_timestamp, channel_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (student_id, class_id, teacher_id, 0, 0, vc_timestamp, channel_id))
        await db.commit()
        await mycursor.close()


    async def clear_specific_class_students(self, class_id: int, teacher_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"DELETE FROM StudentFeedback WHERE class_id = {class_id} and teacher_id = {teacher_id}")
        await db.commit()
        await mycursor.close()

    async def is_member_in_class(self, student_id: int, teacher_id: int, class_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT * FROM StudentFeedback WHERE class_id = {class_id} and teacher_id = {teacher_id} and student_id = {student_id}")
        student = await mycursor.fetchall()
        await mycursor.close()
        if student:
            return True
        else:
            return False

    async def check_table_student_exist(self):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'StudentFeedback'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def get_all_users(self, ctx):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT * FROM StudentFeedback")
        users_feedback = await mycursor.fetchall()
        await mycursor.close()
        return await ctx.send(users_feedback)

    async def get_specific_user(self, student_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"SELECT * FROM StudentFeedback WHERE student_id = {student_id}")
        student_info = await mycursor.fetchall()
        await mycursor.close()
        return student_info

    async def update_student_messages(self, student_id: int, class_id: int):
        mycursor, db = await the_data_base()
        await mycursor.execute(f"UPDATE StudentFeedback SET messages = messages + 1 WHERE student_id = {student_id} and class_id = {class_id}")
        await db.commit()
        await mycursor.close()


    async def ask_class_feedback(self, teacher_id, users_feedback, guild, language, class_type):
        reward_channel = discord.utils.get(guild.channels, id=reward_channel_id)
        active_users = []
        if users_feedback:
            if class_type.title() == 'Pronunciation':
                active_users = [uf for uf in users_feedback if uf[4] >= 1800]
            elif class_type.title() == 'Grammar':
                active_users = [uf for uf in users_feedback if uf[3] >= 10]

        if not active_users:
            return
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
                    m, s = divmod(active_users[class_index][4], 60)
                    h, m = divmod(m, 60)
                    member = discord.utils.get(guild.members, id=active_users[class_index][0])
                    reward_embed = discord.Embed(
                        title=f"*[{class_index+1}/{len(active_users)}] Reward __{member}__?**",
                        description=f"**Sent:** {active_users[class_index][3]} messages.\n**Have been:** {h:d} hours, {m:02d} minutes and {s:02d} seconds in the voice channel.", colour=discord.Colour.green())
                    reward_embed.set_thumbnail(url=member.avatar_url)
                    reward_embed.set_author(name=member.id)
                    reward_embed.set_footer(text=teacher.guild.name, icon_url=teacher.guild.icon_url)
                    await simple.edit(embed=reward_embed)

                    reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=check_reward_react)

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
                    the_reward_embed = discord.Embed(title="__**Class Activity Reward**__", description=f"The following people got rewarded for participating and being active in {teacher.mention}'s __{language}__ class", colour=discord.Colour.green())
                    the_reward_embed.set_footer(text=guild.name, icon_url=guild.icon_url)
                    the_reward_embed.set_thumbnail(url=teacher.avatar_url)
                    the_reward_embed.set_author(name=teacher, icon_url=teacher.avatar_url)
                    the_reward_embed.set_image(url="https://cdn.discordapp.com/attachments/668049600871006208/704406592400916510/emote.png")
                    for ru in users_to_reward:
                        member = discord.utils.get(guild.members, id=ru)
                        the_reward_embed.add_field(name="**-**", value=f"**{member.mention};**", inline=True)
                        if await self.user_in_currency(member.id):
                            await self.update_money(member.id, 10)

                    commands_channel = discord.utils.get(guild.channels, id=bot_commands_channel_id)
                    return await commands_channel.send(embed=the_reward_embed)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def change_queries(self, ctx):
        mycursor, db = await the_data_base()
        await mycursor.execute("select user, max_questions from user")
        something = await mycursor.fetchall()
        await mycursor.close()
        return await ctx.send(something)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_teacher_classes(self, ctx, teacher: discord.Member = None):
        await ctx.message.delete()
        if not teacher:
            return await ctx.send("**Inform a teacher to reset!**", delete_after=3)

        if not await self.check_table_exist():
            return await ctx.send("**This command may be on maintenance!**", delete_after=3)

        teacher_role = discord.utils.get(ctx.guild.roles, id=teacher_role_id)
        if not teacher_role in teacher.roles:
            return await ctx.send(f"**{teacher} is not even a teacher!**", delete_after=5)
        mycursor, db = await the_data_base()
        await mycursor.execute(f"DELETE FROM TeacherFeedback WHERE teacher_id = {teacher.id}")
        await db.commit()
        await mycursor.close()
        return await ctx.send(f"**Teacher __{teacher}__ has been successfully reset!**", delete_after=5)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delete_teacher_class(self, ctx, teacher: discord.Member = None, class_id: int = None):
        await ctx.message.delete()
        if not teacher:
            return await ctx.send("**Inform a teacher to reset!**", delete_after=3)

        elif not class_id:
            return await ctx.send("**Inform a class id to delete!**", delete_after=3)

        if not await self.check_table_exist():
            return await ctx.send("**This command may be on maintenance!**", delete_after=3)

        teacher_role = discord.utils.get(ctx.guild.roles, id=teacher_role_id)
        if not teacher_role in teacher.roles:
            return await ctx.send(f"**{teacher} is not even a teacher!**", delete_after=5)

        mycursor, db = await the_data_base()
        await mycursor.execute(f"DELETE FROM TeacherFeedback WHERE teacher_id = {teacher.id} and class_id = {class_id}")
        await db.commit()
        await mycursor.close()
        return await ctx.send(f"**__{teacher}__'s class with the id {class_id}# has been successfully deleted!**", delete_after=5)


    async def update_money(self, user_id: int, money: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserCurrency SET user_money = user_money + {money} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def user_in_currency(self, user_id: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"SELECT * FROM UserCurrency WHERE user_id = {user_id}")
        user_currency = await mycursor.fetchall()
        await mycursor.close()
        if user_currency:
            return True
        else:
            return False

def setup(client):
    client.add_cog(TeacherFeedback(client))
