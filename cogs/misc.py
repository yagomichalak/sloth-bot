import discord
from discord import slash_command, user_command
from discord.ext import commands, tasks

from random import randint

import os
import aiohttp

from typing import List
from extra import utils
from extra.slothclasses.player import Player
from extra.misc.reminder import MemberReminderTable

allowed_roles = [
    int(os.getenv('OWNER_ROLE_ID', 123)), int(os.getenv('ADMIN_ROLE_ID', 123)), int(os.getenv('MOD_ROLE_ID', 123)), int(os.getenv('ASTROSLOTH_ROLE_ID', 123)), 
    int(os.getenv('SLOTH_EXPLORER_ROLE_ID', 123)),int(os.getenv('SLOTH_NAPPER_ROLE_ID', 123)), int(os.getenv('SLOTH_NATION_ROLE_ID', 123)),
    int(os.getenv('SLOTH_SUPPORTER_ROLE_ID', 123)), int(os.getenv('SLOTH_LOVERS_ROLE_ID', 123)),
    ]
guild_ids = [int(os.getenv('SERVER_ID', 123))]

misc_cogs: List[commands.Cog] = [MemberReminderTable]

class Misc(*misc_cogs):
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
        guild = self.client.get_guild(int(os.getenv('SERVER_ID', 123)))
        for reminder in reminders:
            member = discord.utils.get(guild.members, id=reminder[1])
            if member:
                try:	
                    await member.send(f"**`Reminder:`** {reminder[2]}")
                except:
                    pass
            
            await self.delete_member_reminder(reminder[0])

    @commands.command(aliases=['8ball'])
    @Player.poisoned()
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
    @Player.poisoned()
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


    @commands.command(aliases=['reminder', 'remind', 'remindme', 'set_reminder'])
    @Player.poisoned()
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
    @Player.poisoned()
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
    @Player.poisoned()
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

    @user_command(name="Help", guild_ids=guild_ids)
    async def _help(self, ctx, user: discord.Member) -> None:
        """ Help! """

        await ctx.respond(f"**{ctx.author.mention} needs your help, {user.mention}!**")

def setup(client):
    client.add_cog(Misc(client))
