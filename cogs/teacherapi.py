# import.standard
import asyncio
import json
import os
import shutil
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Tuple, Union
from zipfile import ZipFile

# import.thirdparty
import aiohttp
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

# import.local
from extra import utils
from extra.menu import ConfirmSkill
from mysqldb import DatabaseCore

# variables.role
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
lesson_manager_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID', 123))
allowed_roles = [owner_role_id, admin_role_id, mod_role_id]

# variables.channel
promote_demote_log_channel_id = int(os.getenv('PROMOTE_DEMOTE_LOG_ID', 123))


class TeacherAPI(commands.Cog):
    """ (WIP) A category for using The Language Sloth's teacher's API,
    and some other useful commands related to it. """

    def __init__(self, client) -> None:
        """ Cog initializer """

        self.client = client
        self.teacher_role_id: int = int(os.getenv('TEACHER_ROLE_ID', 123))
        self.session = aiohttp.ClientSession(loop=client.loop)
        self.website_link: str = 'https://languagesloth.com'
        self.django_website_root = os.getenv('DJANGO_WEBSITE_ROOT')
        self.db = DatabaseCore()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ For when the bot starts up """

        print('[.cogs] TeacherAPI cog is ready!')

    async def get_flag(self, language: str) -> str:
        """ Gets a flag from the media files.
        :param language: The language related to the flag.
        :returns: The path of the requested flag, or of the default one.
        """

        path = f"./media/flags/{language.lower()}.png"
        if os.path.isfile(path):
            return path
        else:
            return f"./media/flags/default.png"

    async def paste_text(self, draw, coords: Tuple[int], text: str, color: Tuple[int], font, stroke: Tuple[int]) -> None:
        """ Pastes the given text making a nifty stroke around it.
        :param draw: The draw object to paste on.
        :param coords: The image coordinates to paste on.
        :param text: The text to write in the image.
        :param color: The text color.
        :param stroke: The stroke color.
        """

        draw.text((coords[0]-1, coords[1]), text, stroke, font=font)  # Left
        draw.text((coords[0]+1, coords[1]), text, stroke, font=font)  # Right
        draw.text((coords[0], coords[1]-1), text, stroke, font=font)  # Top
        draw.text((coords[0], coords[1]+1), text, stroke, font=font)  # Bottom
        draw.text((coords[0], coords[1]), text, color, font=font)  # Center

    async def make_description(self, description: str) -> str:
        """ Rearranges the given text by adding \\n tags every 29 characters
        to fit properly in the image.
        :param description: The description rearrange.
        :returns: The rearranged description.
        """

        new_description = ''
        i = 0
        for l in description:
            i += 1
            if i == 29:
                new_description += '\n'
                i = 0
            if i == 0 and l == ' ':
                continue
            new_description += l

        return new_description

    async def get_teacher_pfp(self, teacher: discord.Member) -> Image:
        """ Gets the given teacher's profile picture and returns it.
        :param teacher: The teacher from whom to get the profile picture.
        :returns: The teacher's profile picture in a Pillow Image object.
        """

        async with self.session.get(str(teacher.display_avatar)) as response:
            image_bytes = await response.content.read()
            with BytesIO(image_bytes) as pfp:
                image = Image.open(pfp)
                image = image.resize((128, 128))
                im = image.convert('RGBA')
                return im

    # @commands.command(aliases=['mc', 'card'])
    # @commands.has_any_role(*allowed_roles)
    async def make_card(self, ctx, teacher: discord.Member = None, language: str = None, description: str = None, weekday: str = None, time: str = None) -> None:
        """ Makes a teacher card with their class information.
        :param teacher: The teacher for whom to make the card.
        :param language: The teacher's class language.
        :param description: The teacher's class description.
        :param weekday: The day of the teacher's class.
        :param time: The time of the teacher's class.
        """

        # Checks if the command was given all the required information to make the card.

        author = ctx.author
        try:
            assert teacher, await ctx.send(f"**Please, {author.mention}, inform the `teacher`!**")
            assert description, await ctx.send(f"**Please, {author.mention}, inform the `description`!**")
            assert len(description) < 75, await ctx.send(f"**Please, {author.mention}, the `description` must be under 76 characters!**")
            assert language, await ctx.send(f"**Please, {author.mention}, inform the `language`!**")
            assert len(language) < 80, await ctx.send(f"**Please, {author.mention}, the `language` must be under 31 characters!**")
            assert weekday, await ctx.send(f"**Please, {author.mention}, inform the `weekday`!**")
            assert len(weekday) < 9, await ctx.send(f"**Please, {author.mention}, the `weekday` must be under 10 characters!**")
            assert time, await ctx.send(f"**Please, {author.mention}, inform the `time`!**")
            assert len(weekday) < 25, await ctx.send(f"**Please, {author.mention}, the `time` must be under 25 characters!**")
        except AssertionError as e:
            return

        # Card template path
        path = './media/templates/empty_template.png'

        # Teacher info
        teacher_name = teacher.name
        language = language.lower()
        description = await self.make_description(description)
        weekday = weekday.capitalize()
        time = time.upper()

        # Image info
        small = ImageFont.truetype('./media/fonts/Nougat-ExtraBlack.ttf', 28)

        # Opening images
        background = Image.open(path).resize((685, 485))
        template = Image.open('./media/templates/card_template.png').resize((685, 485))
        icon = await self.get_teacher_pfp(teacher)
        flag = Image.open(await self.get_flag(language)).resize((690, 490))

        # Pasting images
        background.paste(flag, (0, -2), flag)
        background.paste(icon, (438, 102), icon)
        background.paste(template, (0, 0), template)

        # Writing the text  (0 196, 187) | (5, 66, 39)
        draw = ImageDraw.Draw(background)
        await self.paste_text(draw, (230, 100), teacher_name, (0, 196, 187), small, (5, 66, 39))
        await self.paste_text(draw, (230, 136), language.title(), (0, 196, 187), small, (5, 66, 39))
        await self.paste_text(draw, (230, 172), weekday, (0, 196, 187), small, (5, 66, 39))
        await self.paste_text(draw, (230, 208), time, (0, 196, 187), small, (5, 66, 39))
        await self.paste_text(draw, (170, 280), description, (0, 196, 187), small, (5, 66, 39))

        # Get current timestamp
        epoch = datetime.utcfromtimestamp(0)
        the_time = (datetime.utcnow() - epoch).total_seconds()

        # Saving the image
        saved_path = f'./media/temporary/card-{the_time}.png'
        background.save(saved_path, 'png', quality=90)
        await ctx.send(file=discord.File(saved_path))
        os.remove(saved_path)

    @commands.command(aliases=['epfp'])
    @commands.has_permissions(administrator=True)
    @utils.not_ready()
    async def export_profile_pictures(self, ctx) -> None:
        """ Exports a zip file with all of the teachers' profile picture. """

        path = 'media/icons/'
        guild = ctx.guild
        teacher_role = discord.utils.get(guild.roles, id=self.teacher_role_id)
        teachers = [m for m in guild.members if teacher_role in m.roles]
        teacher_names = []

        # Creates the icons folder
        try:
            os.makedirs(f'./media/icons/')
            os.makedirs(f'./media/temporary/')
        except FileExistsError:
            pass

        for teacher in teachers:
            pfp = await self.get_teacher_pfp(teacher)
            pfp.save(f"{path}{teacher.name}.png", 'png', quality=90)
            teacher_names.append(teacher.name)

        # Makes a temporary text file containing all teacher names
        with open('media/icons/teacher_names.txt', 'w+') as f:
            for name in teacher_names:
                f.write(f"{name}\n")

        # Compresses all files in the /icons folder and puts it into the temporary folder
        with ZipFile('media/temporary/teacher_icons.zip', 'w') as zip:
            for file in os.listdir(path):
                full_path = os.path.join(path, file)
                zip.write(full_path, file)

        await ctx.send(file=discord.File('media/temporary/teacher_icons.zip'))

        # Deletes the icons folder
        try:
            shutil.rmtree('./media/icons')
            shutil.rmtree('./media/temporary')
        except Exception as e:
            pass

    async def get_flag(self, language: str) -> str:
        """ Gets the flag for the given language if there is one, otherwise returns the default flag.

        :param language: The language from which to get the flag.
        :returns: The flag path.
        """

        # Gets and Converts the JSON that contains the flag paths to a dictionary
        with open('./media/flags/flags.json', 'r') as f:
            flags = json.load(f)

        # Loops through the dictionary searching for the flag
        for row in flags.values():
            for path, aliases in row.items():
                if language.lower() in aliases:
                    return f"media/flags/{path}"
        # If not found, returns the default one
        else:
            return './media/flags/default.png'

    async def sort_weekdays(self, data: List[Dict[str, Union[int, str]]]) -> Dict[str, List[str]]:
        """ Sorts the given data by the days of the week. """

        weekdays: Dict[str, List[str]] = {
            'Sunday': [],
            'Monday': [],
            'Tuesday': [],
            'Wednesday': [],
            'Thursday': [],
            'Friday': [],
            'Saturday': [],
        }

        for teacher_class in data:
            weekdays[teacher_class['weekday']].append(teacher_class['image'])

        return weekdays

    # @commands.command(aliases=['schedule', 'scheduled', 'scheduled classes', 'cls'])
    # @commands.cooldown(1, 5, commands.BucketType.user)
    async def classes(self, ctx) -> None:
        """ Tells how many classes are scheduled in the website/server. """

        req = f"{self.website_link}/api/teachers/?format=json"
        async with self.session.get(req) as response:
            if response.status != 200:
                return await ctx.send("**Something went wrong with it, try again later!**")

            data = json.loads(await response.read())
            embed = discord.Embed(
                title="Scheduled Classes",
                description=f"**We currently have `{len(data)}` scheduled classes!**",
                url=f"{self.website_link}/class")

            await ctx.send(embed=embed)

    @commands.command(aliases=['pt'])
    @utils.is_allowed([owner_role_id, admin_role_id, lesson_manager_role_id], throw_exc=True)
    async def promote_teacher(self, ctx, member: discord.Member = None) -> None:
        """ Promotes a member to a teacher.
        :param member: The member that is gonna be promoted. """

        author = ctx.author

        if not member:
            return await ctx.send("**Please, inform a member to promote to a teacher!**")

        teacher_role = discord.utils.get(ctx.guild.roles, id=self.teacher_role_id)
        if teacher_role not in member.roles:
            try:
                await member.add_roles(teacher_role)
            except:
                pass

        teacher_state = await self._get_teacher_state(member.id)
        if teacher_state is None:
            return await ctx.send(f"**{member.mention} hasn't logged-in on the website yet!**")
        elif teacher_state:
            return await ctx.send(f"**{member.mention} is already a teacher on the website!**")

        await self._change_teacher_state(member.id, 1)

        # Chat embed
        teacher_embed = discord.Embed(
            title=f"__Promoted!__",
            description=(
                f"{member.mention} has been **promoted** to a `Teacher`! "
                f"Click [here]({self.website_link}/profile) to access your profile or in the button below."
                ),
            color=member.color,
            timestamp=ctx.message.created_at,
            url=self.website_link
            )
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=5, label="Access Profile!", url=f"{self.website_link}/profile", emoji="🧑‍🏫"))
        await ctx.send(embed=teacher_embed, view=view)

        # Log embed
        demote_embed = discord.Embed(
            title="__Teacher Promotion__",
            description=f"{member.mention} has been promoted to a `Teacher` by {author.mention}",
            color=discord.Color.green(),
            timestamp=ctx.message.created_at
        )

        # Moderation log
        if promote_log := discord.utils.get(ctx.guild.text_channels, id=promote_demote_log_channel_id):
            demote_embed.set_author(name=member, icon_url=member.display_avatar)
            demote_embed.set_footer(text=f"Promoted by {author}", icon_url=author.display_avatar)
            await promote_log.send(embed=demote_embed)

        # User message
        try:
            await member.send(f"**You have been promoted to a `Teacher`!**")
        except:
            pass

    @commands.command(aliases=['dt'])
    @utils.is_allowed([owner_role_id, admin_role_id, lesson_manager_role_id], throw_exc=True)
    async def demote_teacher(self, ctx, member: discord.Member = None) -> None:
        """ Demotes a teacher to a regular user.
        :param member: The teacher that is gonna be demoted. """

        if not member:
            return await ctx.send("**Please, inform a member to demote to a regular user!**")

        author: discord.Member = ctx.author

        teacher_role = discord.utils.get(ctx.guild.roles, id=self.teacher_role_id)
        if teacher_role in member.roles:
            try:
                await member.remove_roles(teacher_role)
            except:
                pass

        teacher_state = await self._get_teacher_state(member.id)
        if teacher_state is None:
            return await ctx.send(f"**{member.mention} hasn't logged-in on the website yet!**")
        elif not teacher_state:
            return await ctx.send(f"**{member.mention} is not even a teacher on the website!**")

        await self._change_teacher_state(member.id, 0)
        # General log
        demote_embed = discord.Embed(
            title="__Teacher Demotion__",
            description=f"{member.mention} has been demoted from a `Teacher` to `regular user` by {author.mention}",
            color=discord.Color.dark_red(),
            timestamp=ctx.message.created_at
        )

        await ctx.send(embed=demote_embed)

        # Moderation log
        if demote_log := discord.utils.get(ctx.guild.text_channels, id=promote_demote_log_channel_id):
            demote_embed.set_author(name=member, icon_url=member.display_avatar)
            demote_embed.set_footer(text=f"Demoted by {author}", icon_url=author.display_avatar)
            await demote_log.send(embed=demote_embed)

        # User message
        try:
            await member.send(f"**You have been demoted from a `Teacher` to a regular user!**")
        except:
            pass

    async def _change_teacher_state(self, member_id: int, state: int) -> None:
        """ Changes the current state of a given member in the website.
        :param member_id: The ID of the member that you are changing it.
        :param state: The state to which you are gonna set the to (0=False/1=True). """

        await self.db.execute_query("UPDATE discordlogin_discorduser SET teacher = %s WHERE id = %s", (state, member_id), database_name="django")

    async def _get_teacher_state(self, member_id: int) -> bool:
        """ Gets the member current state from the website.
        :param member_id: The ID of the member that you are checking it. """

        teacher = await self.db.execute_query("SELECT teacher FROM discordlogin_discorduser WHERE id = %s", (member_id,), fetch="one", database_name="django")
        if teacher is None:
            return None
        elif teacher[0] == 1:
            return True
        else:
            return False

    @commands.command(aliases=['check_teacher', 'teacher', 'it'])
    @commands.has_any_role(*allowed_roles, lesson_manager_role_id)
    async def is_teacher(self, ctx, member: discord.Member = None) -> None:
        """ Checks whether the given member is a teacher.
        :param member: The member that you wanna check it. """

        if not member:
            return await ctx.send("**Inform the the member to check whether they're a teacher!**")

        teacher_role = discord.utils.get(ctx.guild.roles, id=self.teacher_role_id)
        teacher_state = await self._get_teacher_state(member.id)
        teacher_embed = discord.Embed(
            title=f"__Is {member} a teacher__",
            description=f"**In the server:** `{teacher_role in member.roles}`!\n**On the website:** `{teacher_state is True}`!",
            color=member.color,
            timestamp=ctx.message.created_at
        )

        await ctx.send(embed=teacher_embed)

    async def get_teacher_cards(self, user_id: int) -> List[List[Union[int, str]]]:
        """ Gets all cards from a given teacher.
        :param user_id: The ID of the teacher. """

        return await self.db.execute_query("SELECT * FROM teacherclass_teacherclass WHERE owner_id = %s", (user_id,), fetch="all", database_name="django")

    # @commands.command(aliases=['see_cards', 'stc'])
    # @commands.cooldown(1, 10, commands.BucketType.user)
    async def see_teacher_cards(self, ctx, teacher: discord.Member = None):
        """ Shows cards for a given user.
        :param teacher: The teacher from whom you want to see the cards. """

        if not teacher:
            return await ctx.send("**Please, inform a teacher!**")

        data = await self.get_teacher_cards(teacher.id)
        if not data:
            return await ctx.send("**No cards found for the given user!**")

        embed = discord.Embed()

        index = 0
        msg = await ctx.send(embed=discord.Embed(title="loading..."))
        await asyncio.sleep(0.5)
        await msg.add_reaction('⬅️')
        await msg.add_reaction('➡️')
        await msg.add_reaction('🛑')

        while True:
            current = data[index]
            embed.clear_fields()
            embed.title = f"Showing cards ({index+1}/{len(data)})"
            embed.description = f"**User:** {teacher.mention}"
            embed.color = ctx.author.color

            embed.add_field(
                name="__Class Info__",
                value=(
                    f"**ID:** {current[0]}\n**Language:** {current[1]}\n**Description:** {current[2]}\n"
                    f"**Day:** {current[5]} at {current[6]}\n**Type:** {current[7]}"
                    ),
                inline=True
            )
            image_path = f"{self.website_link}/{current[3].replace('../', '').replace(' ', '%20')}"
            try:
                embed.set_image(url=image_path)
            except:
                pass

            await msg.edit(embed=embed)
            try:
                r, u = await self.client.wait_for(
                    'reaction_add', timeout=60,
                    check=lambda r, u: u.id == ctx.author.id and msg.id == r.message.id and str(r.emoji) in ['⬅️', '➡️', '🛑']
                    )
            except asyncio.TimeoutError:
                await msg.remove_reaction('⬅️', self.client.user)
                await msg.remove_reaction('➡️', self.client.user)
                await msg.remove_reaction('🛑', self.client.user)
                return

            else:
                if str(r.emoji) == '➡️':
                    await msg.remove_reaction(r, u)
                    if index + 1 < len(data):
                        index += 1
                    continue
                elif str(r.emoji) == '⬅️':
                    await msg.remove_reaction(r, u)
                    if index > 0:
                        index -= 1
                    continue
                elif str(r.emoji) == '🛑':
                    await msg.remove_reaction('⬅️', self.client.user)
                    await msg.remove_reaction('➡️', self.client.user)
                    await msg.remove_reaction('🛑', self.client.user)
                    await msg.remove_reaction('🛑', u)

    async def _delete_teacher_cards(self, user_id: int) -> None:
        """ Deletes all cards from a given teacher.
        :param user_id: The ID of the teacher from which to delete the cards. """

        await self.db.execute_query("DELETE FROM teacherclass_teacherclass WHERE owner_id = %s", (user_id,), database_name="django")

    # @commands.command(aliases=['delete_cards', 'dtc'])
    # @utils.is_allowed([*allowed_roles, lesson_manager_role_id], throw_exc=True)
    async def delete_teacher_cards(self, ctx, user: discord.User = None) -> None:
        """ Deletes all cards from a given teacher from the database.
        :param user: The user from whom to get the cards. """

        if not user:
            return await ctx.send("**Please, inform a user!**")

        cards = await self.get_teacher_cards(user.id)
        if not cards:
            return await ctx.send("**No cards found for the given user!**")

        member = self.client.get_user(user.id)
        teacher = member if member else user

        confirm = await ConfirmSkill(f"The teacher {teacher.mention} has `{len(cards)}` cards, do you want to delete them, {ctx.author.mention}?").prompt(ctx)
        if not confirm:
            return await ctx.send("**Not deleting them then!**")

        
        await self._delete_teacher_cards(user.id)
        for card in cards:
            card_path = f"{self.django_website_root}/{card[3].replace('../', '')}"
            if os.path.exists(card_path):
                try:
                    os.remove(card_path)
                except:
                    pass

        await ctx.send(f"**Cards successfully deleted for `{teacher}`!**")


def setup(client) -> None:
    client.add_cog(TeacherAPI(client))
