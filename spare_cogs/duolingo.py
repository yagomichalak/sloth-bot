# import.standard
import json
import os
from typing import Optional

# import.thirdparty
import aiohttp
import discord
from discord.ext import commands
from discord.utils import escape_mentions

# import.local
from extra.misc.duolingo import DuolingoProfileTable
from extra.prompt.menu import Confirm
from extra.slothclasses.player import Player

class Duolingo(DuolingoProfileTable, command_attrs=dict(hidden=True)):
    """ Category for Duolingo related commands. """

    def __init__(self, client) -> None:
        self.client = client
        self.session = aiohttp.ClientSession(loop=client.loop)
        self.root = 'https://www.duolingo.com'
        self.authentication = {
            'identifier': os.getenv('DUOLINGO_NAME'),
            'password': os.getenv('DUOLINGO_PASSWORD'),
        }

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to go. """

        print("Duolingo cog is online!")
    
    @commands.command(aliases=['set_duolingo', 'set_owl', 'setduo', 'setduolingo'])
    @Player.poisoned()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def set_duo(self, ctx, *, duo_name: str = None) -> None:
        """ Sets a Duolingo account to your Discord account.
        :param duo_name: Your Duolingo's username. """

        duo_name = escape_mentions(duo_name)

        member = ctx.author

        if not duo_name:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform your Duolingo's username, {member.mention}!**")

        if len(duo_name) > 100:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Usernames must have a maximum of 100 characters, {member.mention}!**")

        if await self.get_duo_profile(member.id):
            return await ctx.send(f"**You have already set a Duolingo account previously, {member.mention}!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')
        if not await SlothCurrency.get_user_currency(member.id):
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://languagesloth.com/profile/update"))
            return await member.send(
            embed=discord.Embed(description=f"**{member.mention}, you don't have a Sloth Account yet. Click [here](https://languagesloth.com/profile/update) to create one, or in the button below!**"))

        confirm = await Confirm(f"**Are you sure you want to set `{duo_name}` as your Duolingo's username, {member.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it, then, {member.mention}!**")

        await self.insert_duo_profile(member.id, duo_name)
        await ctx.send(f"**Successfully set your Duolingo's account to `{duo_name}`, {member.mention}!**")

    @commands.command(aliases=['update_duolingo', 'update_owl', 'updateduo', 'updateduolingo'])
    @Player.poisoned()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def update_duo(self, ctx, *, duo_name: str = None) -> None:
        """ Updates a Duolingo account to your Discord account.
        :param duo_name: Your new Duolingo's username. """

        duo_name = escape_mentions(duo_name)

        member = ctx.author

        if not duo_name:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform your Duolingo's username, {member.mention}!**")

        if len(duo_name) > 100:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Usernames must have a maximum of 100 characters, {member.mention}!**")

        if not (duo_profile := await self.get_duo_profile(member.id)):
            return await ctx.send(f"**You don't even have a Duolingo account set yet, {member.mention}!**")

        confirm = await Confirm(f"**Are you sure you want to update your Duolingo's username from `{duo_profile[1]}` to `{duo_name}`, {member.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it, then, {member.mention}!**")

        await self.update_duo_profile(member.id, duo_name)
        await ctx.send(f"**Successfully updated your Duolingo's username from `{duo_profile[1]}` to `{duo_name}`, {member.mention}!**")

    @commands.command(aliases=['delete_duolingo', 'delete_owl', 'deleteduo', 'deleteduolingo'])
    @Player.poisoned()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def delete_duo(self, ctx) -> None:
        """ Deletes a Duolingo account from your Discord account. """

        member = ctx.author

        if not (duo_profile := await self.get_duo_profile(member.id)):
            return await ctx.send(f"**You don't even have a Duolingo account set yet, {member.mention}!**")

        confirm = await Confirm(f"**Are you sure you want to delete your Duolingo's account named `{duo_profile[1]}`, {member.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it, then, {member.mention}!**")

        await self.delete_duo_profile(member.id)
        await ctx.send(f"**Successfully deleted your Duolingo's account named `{duo_profile[1]}`, {member.mention}!**")

    @commands.command(aliases=['duo', 'duo_me'])
    @Player.poisoned()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def duome(self, ctx, *, member: Optional[discord.Member] = None) -> None:
        """ Gets the user's Duolingo profile.
        :param member: The member to look for. [Optional]

        PS: If member not informed, it'll look for your profile. """

        author = ctx.author

        if not member:
            member = ctx.author

        if member.bot:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**You use this command on a bot, {author.mention}!**")

        duo_profile = await self.get_duo_profile(member.id)
        if not duo_profile:
            if author.id == member.id:
                return await ctx.send(f"**You don't have a Duolingo profile set to your account, {author.mention}!**")
            else:
                return await ctx.send(f"**{member.mention} doesn't have a Duolingo profile set to their account, {author.mention}!**")

        request  = f"{self.root}/users/{duo_profile[1]}"
        headers = {'content-type': 'application/json'}
        
        url = "https://www.duolingo.com/2017-06-30/login?fields="
        async with ctx.typing():
            async with self.session.post(url, headers=headers, data=json.dumps(self.authentication)) as response:
                if response.status != 200:
                    return await ctx.send(f"**Request failed!**")

            async with self.session.get(request) as response:
                if response.status == 404:
                    return await ctx.send(f"**User not found, {author.mention}!**")

                elif response.status != 200:
                    return await ctx.send(f"**Something went wrong with it, {author.mention}! ({response.status})**")

                data = json.loads(await response.read())
                lang_data = data['language_data'][list(data['language_data'].keys())[0]]

                finished_skills = [s for s in lang_data['skills'] if s['progress_percent'] == 100]
                embed = discord.Embed(
                    title=f"__{duo_profile[1]}__",
                    description=f"""
                    **Streak**: `{data['languages'][0]['streak']} days` 🔥
                    **Indexed language:** `{data['learning_language_string']}`
                    **Finished skills for indexed language:** `{len(finished_skills)}`
                    **Timezone:** `{data.get('timezone')}`""",
                    #**Following:** `{len(lang_data['points_ranking_data']) -1} people`""",
                    # **Skills Learned:**: `{data['num_skills_learned']}k`
                    color=member.color,
                    timestamp=ctx.message.created_at,
                    url=f"{self.root}/profile/{duo_profile[1]}"
                )

                languages = sorted(data['languages'], key=lambda k: k['level'], reverse=True) 

                for language in languages[:6]:
                    
                    flag = await self.get_flag(language['language_string'])

                    embed.add_field(
                        name=f"__{language['language_string']} ({flag})__:",
                        value=f"""
                        **Level:** `{language['level']}`
                        **To next level:** `{language['to_next_level']}xp`
                        **Points:** `{language['points']} pts`
                        **Learning:** `{language['current_learning']}`""",
                        inline=True
                    )

                if properties := data.get('tracking_properties'):
                    creation_ts = int(properties['creation_date_millis']/1000)
                    embed.description += f"\n**Following:** `{properties['num_following']} people`"
                    embed.description += f" **Followers:** `{properties['num_followers']} people`"
                    embed.add_field(
                        name="__Properties__:",
                        value=f"""
                        **Creation Date:** <t:{creation_ts}> (<t:{creation_ts}:R>)
                        **Gems:** `{properties['gems']}` 💎
                        **Achievements:** `{len(properties['achievements'])}`
                        """,
                        inline=False)
                
                unfinished_skills = [
                    unf for unf in lang_data['skills']
                    if 0 < unf['progress_percent'] < 100
                ]

                if unfinished_skills:
                    last = unfinished_skills[-1]
                    embed.add_field(name=f"__Last Lesson__", value=f"""
                    **Language:** `{last['language_string']}`
                    **Title:** `{last['title']}`
                    **Progress Percent:** `{round(last['progress_percent'])}%` `({last['progress_level_session_index']}/{last['num_sessions_for_level']})`
                    """, inline=True)

                
                if next := lang_data.get('next_lesson'):
                    embed.add_field(name=f"__Next Lesson__:", value=f"""
                    **Title:** `{next['skill_title']}`
                    **Modules:** `{next['lesson_number']}`
                    """, inline=True)
                    

                embed.set_thumbnail(url=f"https:{data['avatar']}/xxlarge")

                await ctx.send(embed=embed)

    async def get_flag(self, language: str) -> str:
        """ Gets a language flag emoji.
        :param language: The language to get a flag for. """

        flags = {}
        with open('./extra/random/json/flag_emojis.json', 'r', encoding="utf-8") as f:
            flags = json.loads(f.read())
        
        if emoji := flags.get(language.lower()):
            return emoji
        else:
            return '🏳️'

def setup(client) -> None:
    client.add_cog(Duolingo(client))