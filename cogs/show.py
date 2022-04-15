import discord
from discord import Option, SlashCommandGroup, slash_command
from discord.ext import commands

from extra.useful_variables import rules
from extra import utils
from extra.slothclasses.player import Player
from extra.analytics import DataBumpsTable

from typing import Dict
import os
import subprocess
import sys
import json
import wikipedia

allowed_roles = [int(os.getenv('OWNER_ROLE_ID', 123)), int(os.getenv('ADMIN_ROLE_ID', 123)), int(os.getenv('MOD_ROLE_ID', 123))]
guild_ids = [int(os.getenv('SERVER_ID', 123))]

class Show(commands.Cog):
    """ Commands involving showing some information related to the server. """

    def __init__(self, client) -> None:
        """ Class init method. """

        self.client = client

    _cnp = SlashCommandGroup("cnp", "For copy and pasting stuff.", guild_ids=guild_ids)
    

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print('Show cog is ready!')

    # Shows how many members there are in the server
    @commands.command()
    async def members(self, ctx) -> None:
        """ Shows how many members there are in the server (including bots). """

        await ctx.message.delete()
        all_users = ctx.guild.members
        await ctx.send(f'{len(all_users)} members!')

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def about(self, ctx) -> None:
        """ Shows some information about the bot itself. """

        embed = discord.Embed(
            title=f"__About ({self.client.user})__",
            description=(
                f"The {self.client.user} bot is an all-in-one bot designed specially for `The Language Sloth` server. "
                "It has many different commands and features to best satisfy our needs in this server, and it's continuously being improved and updated."
                ),
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
            url='https://thelanguagesloth.com/bots/sloth/'
        )

        lines = subprocess.getstatusoutput('find . -name "*.py" -not -path "./venv*" | xargs wc -l')
        lines = lines[1].split()[-2] if lines else 0

        commits = subprocess.getstatusoutput('git rev-list --count HEAD')[1]
        github_link = "https://github.com/yagomichalak/sloth-bot"

        embed.add_field(
            name="__Lines and Commits__",
            value=f"```apache\n{lines} lines of Python code. It currently has {commits} commits on GitHub```",
            inline=True)
        embed.add_field(
            name="__Commands and Categories__",
            value=f"```apache\n{len([_ for _ in self.client.walk_commands()])} commands in {len(self.client.cogs)} different categories.```",
            inline=True)
        embed.add_field(name="__Operating System__",
            value=f'```apache\nThe bot is running and being hosted on a "{sys.platform}" machine.```',
            inline=True)

        embed.add_field(
            name="__Contribute__",
            value=f"If you want to contribute to the bot by improving its code or by adding an additional feature, you can find its GitHub repo [here]({github_link})!",
            inline=False
        )

        embed.set_author(name='DNK#6725', url='https://discord.gg/languages',
            icon_url='https://cdn.discordapp.com/attachments/719020754858934294/720289112040669284/DNK_icon.png')
        embed.set_thumbnail(url=self.client.user.display_avatar)
        embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon.url)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=5, label='GitHub', emoji="🔗", url=github_link))
        view.add_item(discord.ui.Button(style=5, label="Patreon", emoji="<:patreon:831401582426980422>", url="https://www.patreon.com/Languagesloth"))
        await ctx.send(embed=embed, view=view)

    # Shows the specific rule

    @slash_command(name="rules", guild_ids=guild_ids)
    @utils.is_allowed(allowed_roles)
    async def _rules_slash(self, ctx, 
        rule_number: Option(int, name="rule_number", description="The number of the rule you wanna show.", choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], required=False), 
        reply_message: Option(bool, name="reply_message", description="Whether the slash command should reply to your original message.", required=False, default=True)) -> None:
        """ (MOD) Sends an embedded message containing all rules in it, or a specific rule. """

        if rule_number:
            await self._rule(ctx, rule_number, reply_message)
        else:
            await self._rules(ctx, reply_message)

    @commands.command(name="rule")
    @utils.is_allowed(allowed_roles)
    async def _rule_command(self, ctx, numb: int = None) -> None:
        """ Shows a specific server rule.
        :param numb: The number of the rule to show. """

        await self._rule(ctx, numb)


    async def _rule(self, ctx, numb: int = None, reply: bool = True) -> None:
        """ Shows a specific server rule.
        :param numb: The number of the rule to show. """

        answer: discord.PartialMessageable = None
        if isinstance(ctx, commands.Context):
            await ctx.message.delete()
            answer = ctx.send
        else:
            answer = ctx.respond

        if numb is None:
            return await answer('**Invalid parameter!**')

        if numb > len(rules) or numb <= 0:
            return await answer(f'**Inform a rule from `1-{len(rules)}` rules!**')

        rule_index = list(rules)[numb - 1]
        embed = discord.Embed(title=f'Rule - {numb}# {rule_index}', description=rules[rule_index], color=discord.Color.green())
        embed.set_footer(text=ctx.author.guild.name)

        if reply:
            await answer(embed=embed)
        else:
            await ctx.delete()
            await ctx.channel.send(embed=embed)

    @commands.command(name="rules")
    @utils.is_allowed(allowed_roles)
    async def _rules_command(self, ctx) -> None:
        """ (MOD) Sends an embedded message containing all rules in it. """

        await self._rules(ctx)

    async def _rules(self, ctx, reply: bool = True):
        """ (MOD) Sends an embedded message containing all rules in it. """

        answer: discord.PartialMessageable = None
        if isinstance(ctx, commands.Context):
            await ctx.message.delete()
            answer = ctx.send
        else:
            answer = ctx.respond


        current_time = await utils.get_time_now()

        guild = ctx.guild
        embed = discord.Embed(
            title="__Rules of the Server__", 
            description="You must always abide by the rules and follow [Discord's Terms of Service](https://discord.com/terms) and [Community Guidelines](https://discordapp.com/guidelines)\n```Hello, The Language Sloth public discord server is meant for people all across the globe to meet, learn and share their love for languages. Here are our rules of conduct:```",
            url='https://thelanguagesloth.com', color=discord.Color.green(), timestamp=current_time)
        i = 1
        for rule, rule_value in rules.items():
            embed.add_field(name=f"{i} - __{rule}__:", value=rule_value, inline=False)
            i += 1

        embed.set_footer(text=guild.owner, icon_url=guild.owner.avatar.url)
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_author(name='The Language Sloth', url='https://discordapp.com', icon_url=guild.icon.url)
        if reply:
            await answer(embed=embed)
        else:
            await ctx.delete()
            await ctx.channel.send(embed=embed)

    @commands.command(aliases=['ss'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def server_status(self, ctx) -> None:
        """ Shows some server statuses. """

        member = ctx.author
        months = await DataBumpsTable.get_month_statuses(self)

        embed = discord.Embed(
            title="__Server's Monthly Statuses__",
            description=(
                "**N**: Month counting;\n"
                "**Date**: Months respective to the data;\n"
                "**Joins**: New members;\n"
                "**First**: Total members in the first day of the month;\n"
                "**Last**: Total members in the last day of the month."
                ),
            color=member.color,
            timestamp=ctx.message.created_at,
            url="http://thelanguagesloth.com"
        )

        temp_text1 = f"{'N':>2} | {'Date':<4} | {'Joins':^5} | {'First':>5} | {'Last':>5}"

        embed.add_field(
            name=f"{'='*35}",
            value=f"```apache\n{temp_text1}```",
            inline=False
        )

        temp_text2 = ''
        for i, month in enumerate(months):
            the_month = month[0].strftime('%b')
            temp_text2 += f"{i+1:>2} | {the_month:<4} | {month[1]:^5} | {month[2]:>5} | {month[3]:>5}\n"

        embed.add_field(
            name=f"{'='*35}",
            value=f"```apache\n{temp_text2}```",
            inline=False
        )

        embed.set_author(name=member, icon_url=member.display_avatar)
        embed.set_footer(text=member.guild, icon_url=member.guild.icon.url)
        await ctx.send(embed=embed)


    @_cnp.command(name="specific")
    @utils.is_allowed(allowed_roles, throw_exc=True)
    async def _specific(self, ctx, 
        text: Option(str, name="text", description="Pastes a text for specific purposes", required=True,
            choices=['Muted/Purge', 'Nickname', 'Classes', 'Interview', 'Resources', 'Global', 'Searching Teachers', 'Not An Emotional Support Server'])):
        """ Posts a specific test of your choice """
        
        
        member = ctx.author

        available_texts: Dict[str, str] = {}
        with open(f"./extra/random/json/special_texts.json", 'r', encoding="utf-8") as file:
            available_texts = json.loads(file.read())

        if not (selected_text := available_texts.get(text.lower())):
            return await ctx.respond(f"**Please, inform a supported language, {member.mention}!**\n{', '.join(available_texts)}")

        if selected_text['embed']:
            embed = discord.Embed(
                title=f"__{text.title()}__",
                description=selected_text['text'],
                color=member.color
            )
            if selected_text["image"]:
                embed.set_image(url=selected_text["image"])
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(selected_text['text'])


    @_cnp.command(name="speak")
    @utils.is_allowed(allowed_roles, throw_exc=True)
    async def _speak(self, ctx, language: Option(str, name="language", description="The language they should speak.", required=True)) -> None:
        """ Pastes a 'speak in X language' text in different languages. """

        member = ctx.author

        available_languages: Dict[str, str] = {}
        with open(f"./extra/random/json/speak_in.json", 'r', encoding="utf-8") as file:
            available_languages = json.loads(file.read())

        if not (language_text := available_languages.get(language.lower())):
            return await ctx.respond(f"**Please, inform a supported language, {member.mention}!**\n{', '.join(available_languages)}")

        embed = discord.Embed(
            title=f"__{language.title()}__",
            description=language_text,
            color=member.color
        )
        await ctx.respond(embed=embed)

    @_cnp.command(name="club_speak")
    @utils.is_allowed(allowed_roles, throw_exc=True)
    async def _club_speak(self, ctx) -> None:
        """ Tells people that they must speak in English in club channels. """

        embed = discord.Embed(
            title="__Speak English__",
            description="**This is an English-only channel. Please do not use other languages in the club channels.**",
            color=ctx.author.color
        )
        await ctx.respond(embed=embed)
        
    @commands.command(aliases=['wk','w', 'wiki'])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def wikipedia(self, ctx, *, topic: str = None):
        '''
        Searches something on Wikipedia.
        :param topic: The topic to search.
        '''
        if not topic:
            return await ctx.send(f"**{ctx.author.mention}, please, inform a topic to search!**")
        try:
            result = wikipedia.summary(topic)
        except Exception as error:
            await ctx.send("**I couldn't find anything for this topic!**")
        else:
            if (len(result) <= 2048):
                embed = discord.Embed(title=f"(Wikipedia) - __{topic.title()}__:", description=result, color=discord.Color.green())
                await ctx.send(embed=embed)
            else:
                embedList = []
                n = 2048
                embedList = [result[i:i + n] for i in range(0, len(result), n)]
                for num, item in enumerate(embedList, start=1):
                    if (num == 1):
                        embed = discord.Embed(title=f"(Wikipedia) - __{topic.title()}__:", description=item, color=discord.Color.green())
                        embed.set_footer(text="Page {}".format(num))
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(description=item, color=discord.Color.green())
                        embed.set_footer(text="Page {}".format(num))
                        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Show(client))
