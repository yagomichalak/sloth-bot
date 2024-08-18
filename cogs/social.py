import discord
from discord import Option, slash_command
from discord.utils import escape_mentions
from discord.ext import commands
from random import randint
import aiohttp
import os
from typing import List, Optional
from mysqldb import DatabaseCore

from extra import utils, useful_variables
from extra.view import QuickButtons
from extra.prompt.menu import ConfirmButton

from extra.moderation.userinfractions import ModerationUserInfractionsTable
from extra.moderation.fakeaccounts import ModerationFakeAccountsTable
from extra.moderation.moderatednicknames import ModeratedNicknamesTable
from extra.slothclasses.player import Player
from extra.misc.slothboard import SlothboardTable

mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID', 123))
analyst_debugger_role_id: int = int(os.getenv('ANALYST_DEBUGGER_ROLE_ID', 123))
watchlist_channel_id = int(os.getenv('WATCHLIST_CHANNEL_ID', 123))
slothboard_channel_id = int(os.getenv('SLOTHBOARD_CHANNEL_ID', 123))
booster_role_id = int(os.getenv('BOOSTER_ROLE_ID', 123))
guild_ids = [int(os.getenv('SERVER_ID', 123))]

social_cogs: List[commands.Bot] = [SlothboardTable]

class Social(*social_cogs):
    """ Social related commands. """

    def __init__(self, client):
        self.client = client
        self.db = DatabaseCore()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Social cog is ready!')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload) -> None:
        """ Sends messages to the Slothboard channel. """
        
        emoji = str(payload.emoji)
        star = '<:Sloth:686237376510689327>'

        # Checkes whether it's the right emoji
        if emoji != star:
            return

        if payload.channel_id == slothboard_channel_id:
            return

        # Gets message
        guild = self.client.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message is None:
            return

        # Checks whether the message has enough reactions
        for reaction in message.reactions:
            if str(reaction) != emoji:
                continue

            if reaction.count < 10:
                continue

            # Check whether message is already in the Slothboard
            if not (something := await self.get_slothboard_message(message.id, channel.id)):

                # Checks whether message content contains an embedded image
                current_date = await utils.get_time_now()

                embed = discord.Embed(
                    title="__Slothboard__",
                    color=discord.Color.gold(),
                    timestamp=current_date
                )

                # Gets all Discord link attachments
                attachment_root = 'https://cdn.discordapp.com/attachments/'
                content = message.content.split()
                discord_attachments = [att for att in content if att.startswith(attachment_root)]
                for datt in discord_attachments:
                    try:
                        if not embed.image:
                            embed.set_image(url=datt)

                        content.remove(datt)
                    except:
                        pass

                message.content = ' '.join(content).strip() if content else None
                embed.description=f"[**Original Message**]({message.jump_url})\n\n**Content:** {message.content}"

                # Gets all embedded attachments
                if all_attachments := message.attachments:
                    attachments = [att for att in all_attachments if att.content_type.startswith('image')]

                    if attachments:
                        embed.set_image(url=attachments[0])
                    else:
                        return

                embed.set_author(name=message.author, url=message.author.display_avatar, icon_url=message.author.display_avatar)
                # Posts in #slothboard
                await self.insert_slothboard_message(message.id, channel.id)
                slothboard_channel = guild.get_channel(slothboard_channel_id)
                return await slothboard_channel.send(content=f"**From:** {channel.mention}", embed=embed)

    @commands.command(aliases=['si', 'server', 'server_info'])
    async def serverinfo(self, ctx) -> None:
        """ Shows information about the server. """

        guild = ctx.guild

        em = discord.Embed(description=guild.description, color=ctx.author.color)
        online = len({m.id for m in guild.members if m.status is not discord.Status.offline})
        em.add_field(name="Server ID", value=guild.id, inline=True)
        em.add_field(name="Owner", value=guild.owner.mention, inline=False)

        admins_role = discord.utils.get(guild.roles, id=admin_role_id)
        admins = len([m.mention for m in guild.members if admins_role in m.roles])
        em.add_field(name="👑 Admins", value=admins, inline=True)

        mods_role = discord.utils.get(guild.roles, id=mod_role_id)
        mods = len([m.mention for m in guild.members if mods_role in m.roles])
        em.add_field(name="<:zslothmod:737325517077872697> Mods", value=mods, inline=True)

        teachers_role = discord.utils.get(guild.roles, id=teacher_role_id)
        teachers = len([m.mention for m in guild.members if teachers_role in m.roles])
        em.add_field(name="🧑‍🏫 Teachers", value=teachers, inline=True)

        em.add_field(name="Members", value=f"🟢 {online} members ⚫ {len(guild.members)} members", inline=True)
        em.add_field(name="Channels",
            value=f"⌨️ {len(guild.text_channels)} | 🔈 {len(guild.voice_channels)} | 📻 {len(guild.stage_channels)} | 📁 {len(guild.categories)} | **=** {len(guild.channels)}",
            inline=False)
        em.add_field(name="Roles", value=len(guild.roles), inline=True)
        em.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        em.add_field(name="<:ban:593407893248802817> Bans", value=len([1 async for b in guild.bans()]), inline=True)
        em.add_field(name="🌟 Boosts", value=f"{guild.premium_subscription_count} (Level {guild.premium_tier})", inline=True)
        features = ', '.join(list(map(lambda f: f.replace('_', ' ').capitalize(), guild.features)))
        em.add_field(name="Server Features", value=features if features else None, inline=False)

        em.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            em.set_image(url=guild.banner.url)
        em.set_author(name=guild.name, icon_url=guild.icon.url)
        created_at = await utils.sort_time(guild.created_at)
        em.set_footer(text=f"Created: {guild.created_at.strftime('%d/%m/%y')} ({created_at})")
        await ctx.send(embed=em)

    # Shows all the info about a user
    @commands.command(aliases=['user', 'whois', 'who_is', 'ui'])
    async def userinfo(self, ctx, *, message : str = None):
        """ Shows all the information about a member.
        :param member: The member to show the info.
        :return: An embedded message with the user's information """

        try:
            await ctx.message.delete()
        except:
            pass

        if not await utils.is_allowed([mod_role_id, admin_role_id]).predicate(ctx):
            if message and len(message.split()) > 1:
                message = message.split()[0]

        members, _ = await utils.greedy_member_reason(ctx, message)

        members = [ctx.author] if not members else members

        for member in members:
            embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at, description=f"\n<@{member.id}>")

            embed.set_author(name=f"User Info: {member}")
            embed.set_thumbnail(url=member.display_avatar)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)

            embed.add_field(name="ID:", value=member.id, inline=False)

            if hasattr(member, 'guild'):
                embed.add_field(name="Guild name:", value=member.display_name, inline=False)
                sorted_time_create = f"<t:{int(member.created_at.timestamp())}:R>"
                sorted_time_join = f"<t:{int(member.joined_at.timestamp())}:R>"

                embed.add_field(name="Created at:", value=f"{member.created_at.strftime('%d/%m/%y')} ({sorted_time_create}) **GMT**",
                                inline=False)
                embed.add_field(name="Joined at:", value=f"{member.joined_at.strftime('%d/%m/%y')} ({sorted_time_join}) **GMT**", inline=False)

                embed.add_field(name="Top role:", value=member.top_role.mention, inline=False)
                if member.voice:
                        embed.add_field(name="In a vc?", value=member.voice.channel.mention)
                else:
                        embed.add_field(name="In a vc?", value="No")


            """embed.add_field(name="Bot?", value=member.bot)"""

            view = QuickButtons(client=self.client, ctx=ctx, target_member=member)
            if not await utils.is_allowed([analyst_debugger_role_id, mod_role_id, admin_role_id]).predicate(ctx):
                view.children.remove(view.children[4])
                if not await utils.is_subscriber(throw_exc=False).predicate(ctx):
                    view.children.remove(view.infractions_button)
                view.children.remove(view.snipe_button)
                view.children.remove(view.vh_button)
                view.children.remove(view.fake_accounts_button)
                view.children.remove(view.moderated_nickname_button)
            else:
                view.children.remove(view.info_button)
                view.children.remove(view.profile_button)

                moderation_cog = self.client.get_cog("Moderation")
                if not await moderation_cog.get_user_infractions(member.id):
                    view.children[0].disabled = True

                if not await moderation_cog.get_fake_accounts(member.id):
                    view.children.remove(view.fake_accounts_button)

                if not await moderation_cog.get_moderated_nickname(member.id):
                    view.children.remove(view.moderated_nickname_button)
                
            await ctx.send(embed=embed, view=view)


    # Sends a random post from the meme subreddit
    # @commands.command()
    # @commands.cooldown(1, 5, type=commands.BucketType.user)
    # async def meme(self, ctx):
    #     """ Gets a random meme from Reddit.

    #     * Cooldown = 5 secs """

    #     reddit = await the_reddit()
    #     memes_submissions = reddit.subreddit('memes').hot()
    #     post_to_pick = randint(1, 50)
    #     for i in range(0, post_to_pick):
    #         submissions = next(x for x in memes_submissions if not x.stickied)

    #     meme_embed = discord.Embed(title="__**Meme**__", colour=ctx.author.colour, timestamp=ctx.message.created_at)
    #     meme_embed.set_image(url=submissions.url)
    #     meme_embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
    #     await ctx.send(embed=meme_embed)

    @commands.command(aliases=['xkcd', 'comic'])
    @Player.poisoned()
    async def randomcomic(self, ctx):
        """ Get a comic from xkcd. """

        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://xkcd.com/info.0.json') as resp:
                data = await resp.json()
                currentcomic = data['num']
        rand = randint(0, currentcomic)  # max = current comic
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://xkcd.com/{rand}/info.0.json') as resp:
                data = await resp.json()
        em = discord.Embed(color=discord.Color.green())
        em.title = f"XKCD Number {data['num']}- \"{data['title']}\""
        em.set_footer(text=f"Published on {data['month']}/{data['day']}/{data['year']}")
        em.set_image(url=data['img'])
        await ctx.send(embed=em)

    @slash_command(name="youtube_together", guild_ids=guild_ids)
    @Player.poisoned()
    @utils.is_allowed([booster_role_id, *useful_variables.patreon_roles.keys(), mod_role_id, admin_role_id, teacher_role_id], throw_exc=True)
    async def youtube_together(self, ctx,
        voice_channel: Option(discord.VoiceChannel, description="The voice channel in which to create the party.")
    ) -> None:
        """ Creates a YouTube Together session in a VC. """

        member = ctx.author

        if not isinstance(voice_channel, discord.VoiceChannel):
            return await ctx.respond(f"**Please, select a `Voice Channel`, {member.mention}!**")

        link: str = ''
        try:
            link = await voice_channel.create_activity_invite(event='youtube', max_age=600)
        except Exception as e:
            print("Invite creation error: ", e)
            await ctx.respond(f"**For some reason I couldn't create it, {member.mention}!**")
        current_time = await utils.get_time_now()

        view = discord.ui.View()
        view.add_item(discord.ui.Button(url=str(link), label="Start/Join the Party!", emoji="🔴"))
        embed = discord.Embed(
            title="__Youtube Together__",
            color=discord.Color.red(),
            timestamp=current_time,
            url=link
        )
        embed.set_author(name=member, url=member.display_avatar, icon_url=member.display_avatar)
        embed.set_footer(text=f"(Expires in 5 minutes)", icon_url=ctx.guild.icon.url)
        await ctx.respond(embed=embed, view=view)


    @commands.command(name="change_nickname", aliases=["cn", "update_nick", "un", "changenick", "updatenick"])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def _change_nickname_command(self, ctx, *, nickname: Optional[str] = None) -> None:
        """ Changes your nickname.
        :param nickname: The nickname to change to. [Optional]
        
        * Cost: 150łł """

        await self._change_nickname_callack(ctx, nickname)

    @slash_command(name="change_nickname", guild_ids=guild_ids)
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def _change_nickname_slash_command(self, ctx,
        nickname: Option(str, name="nickname", description="The nickname to change to.", required=False)
    ) -> None:
        """ Changes your nickname. (150łł)"""

        await ctx.defer()
        await self._change_nickname_callack(ctx, nickname)


    async def _change_nickname_callack(self, ctx, nickname: Optional[str] = None) -> None:
        """ Callback for the change_nickname command.
        :param ctx: The context of the command.
        :param nickname. The nickname to change to. [Optional] """

        nickname = escape_mentions(nickname)

        answer: discord.PartialMessageable = ctx.reply if isinstance(ctx, commands.Context) else ctx.respond
        member: discord.Member = ctx.author
        cost: int = 150

        if nickname and len(nickname) > 30:
            ctx.command.reset_cooldown(ctx)
            return await answer(f"**Inform a nickname containing less than 31 characters!**")

        if not nickname and not member.nick:
            ctx.command.reset_cooldown(ctx)
            return await answer(f"**Your nickname is already set to default!**")

        if nickname and nickname == member.nick:
            ctx.command.reset_cooldown(ctx)
            return await answer(f"**Your nickname is already like this!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')
        profile = await SlothCurrency.get_user_currency(member.id)
        if not profile:
            ctx.command.reset_cooldown(ctx)
            return await answer(f"**You don't even have a Sloth Profile, you can't pay for this!**")

        if profile[0][1] < cost:
            ctx.command.reset_cooldown(ctx)
            return await answer(f"**You don't have `{cost}łł` to pay for this nickname change!**")

        confirm_view = ConfirmButton(member, timeout=60)
        nickname_to_change: str = "'default'" if not nickname else nickname
        msg =  await answer(f"**Are you sure you wanna change your nickname to `{nickname_to_change}`, {member.mention}?**", view=confirm_view)
        await confirm_view.wait()

        await utils.disable_buttons(confirm_view)
        await msg.edit(view=confirm_view)

        if confirm_view.value is None:
            ctx.command.reset_cooldown(ctx)
            return await answer("**Timeout!**")

        if not confirm_view.value:
            ctx.command.reset_cooldown(ctx)
            return await answer("**Canceled!**")

        SlothClass = self.client.get_cog("SlothClass")
        sloth_profile = await SlothClass.get_sloth_profile(member.id)
        user_tribe = await SlothClass.get_tribe_info_by_name(name=sloth_profile[3])
        tribe_emojis = '' if not user_tribe['two_emojis'] else f" {user_tribe['two_emojis']}"
        munk_label = ' Munk' if 'Munk' in member.display_name else ''
        try:
            if nickname:
                await member.edit(nick=f"{nickname}{munk_label}{tribe_emojis}")
            else:
                await member.edit(nick=f"{member.name}{munk_label}{tribe_emojis}")
            await SlothCurrency.update_user_money(member.id, -cost)
        except:
            ctx.command.reset_cooldown(ctx)
            return await answer(f"**For some reason I couldn't update it! Try again later**")
        else:
            await answer(f"**Successfully updated your nickname, {member.mention}!**")
        

            

def setup(client):
    client.add_cog(Social(client))
