import discord
from discord.app.commands import slash_command, user_command
from discord.ext import commands, tasks
from random import randint, choice
from datetime import datetime
import aiohttp
from pytz import timezone
from mysqldb import the_database
from typing import List, Union
from extra import utils
import os

allowed_roles = [
    int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')), int(os.getenv('MOD_ROLE_ID')), int(os.getenv('ASTROSLOTH_ROLE_ID')), 
    int(os.getenv('SLOTH_EXPLORER_ROLE_ID')),int(os.getenv('SLOTH_NAPPER_ROLE_ID')), int(os.getenv('SLOTH_NATION_ROLE_ID')),
    int(os.getenv('SLOTH_SUPPORTER_ROLE_ID')), int(os.getenv('SLOTH_LOVERS_ROLE_ID')),
    ]
guild_ids = [int(os.getenv('SERVER_ID'))]

class Misc(commands.Cog):
    """ Miscellaneous related commands. """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.look_for_due_reminders.start()
        print("Misc cog is online!")

    @tasks.loop(minutes=1)
    async def look_for_due_reminders(self) -> None:
        """ Looks for expired tempmutes and unmutes the users. """

        current_ts = await utils.get_timestamp()
        reminders = await self.get_due_reminders(current_ts)
        guild = self.client.get_guild(int(os.getenv('SERVER_ID')))
        for reminder in reminders:
            member = discord.utils.get(guild.members, id=reminder[1])
            if member:
                try:	
                    await member.send(f"**`Reminder:`** {reminder[2]}")
                except:
                    pass
            
            await self.delete_member_reminder(reminder[0])

    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, *, question: str = None):
        """ Ask the 8 ball a question. """

        await ctx.message.delete()
        if not question:
            return await ctx.send("**Inform a question!**", delete_after=3)
        elif not question.endswith('?'):
            return await ctx.send('**Please ask a question.**', delete_after=3)

        responses = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely",
                     "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
                     "Yes", "Signs point to yes", "Reply hazy try again", "Ask again later",
                     "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
                     "Very doubtful"]

        num = randint(0, len(responses) - 1)
        if num < 10:
            em = discord.Embed(color=discord.Color.green())
        elif num < 15:
            em = discord.Embed(color=discord.Color(value=0xffff00))
        else:
            em = discord.Embed(color=discord.Color.red())

        response = responses[num]

        em.title = f"🎱**{question}**"
        em.description = response
        await ctx.send(embed=em)

    @commands.command(aliases=['number'])
    async def numberfact(self, ctx, number: int = None):
        """ Get a fact about a number. """

        if not number:
            await ctx.send(f'**Usage: `{ctx.prefix}numberfact <number>`**', delete_after=3)
            return
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://numbersapi.com/{number}?json') as resp:
                    file = await resp.json()
                    fact = file['text']
                    await ctx.send(f"**Did you know?**\n*{fact}*")
        except KeyError:
            await ctx.send("**No facts are available for that number.**", delete_after=3)

    @commands.command()
    async def justask(self, ctx):
        """ Posts link to "Don't ask to ask, just ask" """
        await ctx.message.delete()
        em = discord.Embed(color=ctx.author.color, title=f"Don't ask to ask, just ask.",
                           timestamp=ctx.message.created_at, url='https://dontasktoask.com/')
        em.set_footer(text=f"With ♥ from {ctx.author}", icon_url=ctx.author.display_avatar)
        await ctx.send(embed=em)  

    # ===========

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_member_reminder(self, ctx) -> None:
        """ (ADM) Creates the MemberReminder table. """

        if await self.check_table_member_reminder():
            return await ctx.send("**Table __MemberReminder__ already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE MemberReminder (
            reminder_id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            text VARCHAR(100) NOT NULL,
            reminder_timestamp BIGINT NOT NULL,
            remind_in BIGINT NOT NULL,
            PRIMARY KEY (reminder_id)
            ) """)
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __MemberReminder__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_member_reminder(self, ctx) -> None:
        """ (ADM) Creates the MemberReminder table """

        if not await self.check_table_member_reminder():
            return await ctx.send("**Table __MemberReminder__ doesn't exist!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE MemberReminder")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __MemberReminder__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_member_reminder(self, ctx) -> None:
        """ (ADM) Creates the MemberReminder table """

        if not await self.check_table_member_reminder():
            return await ctx.send("**Table __MemberReminder__ doesn't exist yet!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM MemberReminder")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __MemberReminder__ reset!**", delete_after=3)

    async def check_table_member_reminder(self) -> bool:
        """ Checks if the MemberReminder table exists """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'MemberReminder'")
        table_info = await mycursor.fetchall()
        await mycursor.close()

        if len(table_info) == 0:
            return False

        else:
            return True

    async def get_due_reminders(self, current_ts: int) -> List[int]:
        """ Gets reminders that are due.. 
        :param current_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM MemberReminder WHERE (%s -  reminder_timestamp) >= remind_in", (current_ts,))
        reminders = [(m[0], m[1], m[2]) for m in await mycursor.fetchall()]
        await mycursor.close()
        return reminders


    async def insert_member_reminder(self, user_id: int, text: str, reminder_timestamp: int, remind_in: int) -> None:
        """ Inserts an entry concerning the user's last seen datetime.
        :param user_id: The ID of the user.
        :param text: The text that has to be reminded.
        :param reminder_timestamp: The current timestamp.
        :param remind_in: The amount of seconds to wait until reminding the user. """

        mycursor, db = await the_database()
        await mycursor.execute("""
        INSERT INTO MemberReminder (user_id, text, reminder_timestamp, remind_in) 
        VALUES (%s, %s, %s, %s)""", (user_id, text, reminder_timestamp, remind_in))
        await db.commit()
        await mycursor.close()

    async def delete_member_reminder(self, reminder_id: int) -> None:
        """ Updates the user's last seen datetime.
        :param reminder_id: The ID of the reminder to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM MemberReminder WHERE reminder_id = %s", (reminder_id,))
        await db.commit()
        await mycursor.close()

    async def get_member_reminders(self, user_id: int) -> List[List[Union[str, int]]]:
        """ Gets the user's reminders.
        :param user_id: The ID of the user. """

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM MemberReminder WHERE user_id = %s", (user_id,))
        reminders = await mycursor.fetchall()
        await mycursor.close()
        return reminders

    async def get_reminder(self, reminder_id: int) -> List[Union[str, int]]:
        """ Gets a reminder by ID.
        :param reminder_id: The reminder ID. """
        
        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM MemberReminder WHERE reminder_id = %s", (reminder_id,))
        reminder = await mycursor.fetchone()
        await mycursor.close()
        return reminder


    @commands.command(aliases=['reminder', 'remind', 'remindme', 'set_reminder'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def setreminder(self, ctx, text: str = None, *, time: str = None):
        """ Sets a reminder for the user.
        :param text: The descriptive text for the bot to remind you about.
        :param time: The amount of time to wait before reminding you.

        - Text Format: If it contains more than 1 word, put everything within " "
        - Time Format: 12s 34m 56h 78d (Order doesn't matter).

        Example:
        z!setreminder "do the dishes" 3m 65s
        = The bot will remind you in 4 minutes and 5 seconds.

        PS: Seconds may not be always reliable, since the bot checks reminders every minute. """

        member = ctx.author

        if not text:
            return await ctx.send(f"**Specify a text to remind you, {member.mention}**")

        if len(text) > 100:
            return await ctx.send(f"**Please, inform a text with a maximum of 100 characters, {member.mention}!**")

        if not time:
            return await ctx.send(f"**Inform a time, {member.mention}!**")

        time_dict, seconds = await utils.get_time_from_text(ctx=ctx, time=time)
        if not seconds:
            return

        reminders = await self.get_member_reminders(member.id)
        if len(reminders) >= 3: # User reached limit of reminders.
            return await ctx.send(
                f"**You reached the limit of reminders, wait for them to finish before trying again, {member.mention}!**")

        current_ts = await utils.get_timestamp()
        await self.insert_member_reminder(member.id, text, current_ts, seconds)

        remind_at = int(current_ts + seconds)
        await ctx.send(f"**Reminding you at <t:{remind_at}>, {member.mention}!**")

    @commands.command(aliases=['show_reminders', 'showreminders', 'rmdrs', 'rs'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reminders(self, ctx) -> None:
        """ Shows reminders that you've set. """

        if not ctx.guild:
            return await ctx.send(f"**You can only see your reminders in the server!**")

        member = ctx.author

        if not (reminders := await self.get_member_reminders(member.id)):
            return await ctx.send(f"**You don't have any reminder set yet, {member.mention}!**")

        embed = discord.Embed(
            title="__Your Reminders__",
            color=member.color,
            timestamp=ctx.message.created_at
        )

        embed.set_author(name=member, url=member.display_avatar, icon_url=member.display_avatar)
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_footer(text="Requested at:", icon_url=member.guild.icon.url)
    

        for reminder in reminders:
            remind_at = int(reminder[3] + reminder[4])

            embed.add_field(
                name=f"ID: {reminder[0]}", 
                value=f"**Text:** {reminder[2]}\n**Set to:** <t:{remind_at}>",
                inline=False)

        await ctx.send(embed=embed)


    @commands.command(aliases=["remove_reminder", "dr", "rr", "dontremind", "dont_remind"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete_reminder(self, ctx, reminder_id: int = None) -> None:
        """ Deletes a member reminder.
        :param reminder_id: The ID of the reminder to delete. """

        member = ctx.author

        if not reminder_id:
            return await ctx.send(f"**Please, provide a reminder ID, {member.mention}!**")

        if not (reminder := await self.get_reminder(reminder_id)):
            return await ctx.send(f"**Reminder with ID `{reminder_id}` doesn't exist, {member.mention}!**")

        if reminder[1] != member.id:
            return await ctx.send(f"**You're not the owner of this reminder, {member.mention}!**")

        await self.delete_member_reminder(reminder_id)
        await ctx.send(f"**Successfully deleted reminder with ID `{reminder_id}`, {member.mention}!**")

    @slash_command(name="dnk", guild_ids=guild_ids)
    async def _dnk(self, ctx) -> None:
        """ Tells you something about DNK. """
        
        await ctx.respond(f"**`Sapristi! C'est qui ? Oui, c'est lui le plus grave et inouï keum qu'on n'a jamais ouï-dire, tandis qu'on était si abasourdi et épris de lui d'être ici affranchi lorsqu'il a pris son joli gui qui ne nie ni être suivi par un souris sur son nid ni être mis ici un beau lundi !`**")

    @slash_command(name="twiks", guild_ids=guild_ids)
    async def _twiks(self, ctx) -> None:
        """ Tells you something about Twiks. """

        await ctx.respond(f"**Twiks est mon frérot !**")

    @user_command(name="Help", guild_ids=guild_ids)
    async def _help(self, ctx, user: discord.Member) -> None:
        await ctx.respond(f"**{ctx.author.mention} needs your help, {user.mention}!**")




def setup(client):
    client.add_cog(Misc(client))
