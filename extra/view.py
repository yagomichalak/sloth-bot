import discord
from discord.components import SelectOption
from extra import utils
from discord.ext import commands
from typing import List, Union, Optional
from .menu import ConfirmSkill
from .select import ReportSupportSelect
import os


mod_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))

class ReportSupportView(discord.ui.View):

    def __init__(self, client: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.client = client
        self.cog = client.get_cog('ReportSupport')
        patreon_button = discord.ui.Button(style=5, label="Support us on Patreon!", url="https://www.patreon.com/Languagesloth", emoji="<:patreon:831401582426980422>", row=2)
        self.children.insert(3, patreon_button)


    @discord.ui.button(label="Apply for Teacher!", style=3, custom_id=f"apply_to_teach", emoji="🧑‍🏫")
    async def apply_to_teach_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        member = interaction.user

        # Apply to be a teacher
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await member.send(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**")

        await interaction.response.defer()
        await self.cog.send_teacher_application(member)

    @discord.ui.button(label="Apply for Moderator!", style=3, custom_id=f"apply_to_moderate", emoji="👮")
    async def apply_to_moderate_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """  """

        member = interaction.user

        # Apply to be a teacher
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await member.send(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**")

        await interaction.response.defer()
        await self.cog.send_moderator_application(member)

    @discord.ui.button(label="Apply for Event Manager!", style=3, custom_id=f"apply_to_manage_events", emoji="🎉")
    async def apply_to_event_manager_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """  """

        member = interaction.user

        # Apply to be a teacher
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await member.send(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**")

        await interaction.response.defer()
        await self.cog.send_event_manager_application(member)


    @discord.ui.button(label="Get your own Custom Bot (not for free)", style=1, custom_id=f"get_custom_bot", emoji="🤖", disabled=True, row=2)
    async def bot_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:

        member = interaction.user

        member_ts = self.cog.report_cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 240:
                return await member.send(
                    f"**You are on cooldown to use this, try again in {round(240-sub)} seconds**")
            
        await interaction.response.defer()

        # Order a bot
        dnk = self.client.get_user(int(os.getenv('DNK_ID')))
        embed = discord.Embed(title="New possible order!",
            description=f"{member.mention} ({member.id}) might be interested in buying something from you!",
            color=member.color)
        embed.set_thumbnail(url=member.avatar.url)
        await dnk.send(embed=embed)
        await member.send(f"**If you are really interested in **buying** a custom bot, send a private message to {dnk.mention}!**")
        await self.cog.dnk_embed(member)

    @discord.ui.button(label="Verify", style=1, custom_id=f"verify_id", emoji="☑️", row=2)
    async def verify_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        member = interaction.user

        member_ts = self.cog.report_cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 240:
                return await interaction.followup.send(
                    f"**You are on cooldown to use this, try again in {round(240-sub)} seconds, {member.mention}!**", ephemeral=True)
            

        message = f"""You have opened a verification request, if you would like to verify:
1.Take a clear picture of yourself holding a piece of paper with today's date and time of verification, and your Discord server name written on it."""
        try:
            exists = await self.cog.generic_help(interaction, 'verify', message, 'https://cdn.discordapp.com/attachments/562019472257318943/882352621116096542/slothfacepopoo.png')
            if exists is False:
                return
        except Exception as e:
            print(e)
        else:
            return await self.cog.audio(member, 'general_help_alert')

    @discord.ui.button(label="Report a User or Get Server/Role Support!", style=4, custom_id=f"report_support", emoji="<:politehammer:608941633454735360>", row=3)
    async def report_support_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        member = interaction.user

        member_ts = self.cog.report_cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 240:
                return await interaction.followup.send(
                    f"**You are on cooldown to report, try again in {round(240-sub)} seconds**", ephemeral=True)

        self.cog.report_cache[member.id] = time_now
        view = discord.ui.View()
        view.add_item(ReportSupportSelect(self.client))
        await interaction.followup.send(content="How can we help you?", view=view, ephemeral=True)


class QuickButtons(discord.ui.View):

    def __init__(self, client: commands.Bot, ctx: commands.Context, target_member: discord.Member) -> None:
        super().__init__(timeout=60)
        self.client = client
        self.ctx = ctx
        self.target_member = target_member

        watchlist_button = discord.ui.Button(
            label="Watchlist", style=discord.ButtonStyle.url, emoji="⚠️", url=f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}"
        )
        self.children.append(watchlist_button)
        

    @discord.ui.button(label="Infractions", style=4, emoji="❗", custom_id=f"user_infractions")
    async def infractions_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's infractions. """

        new_ctx = self.ctx
        new_ctx.author = interaction.user

        if await utils.is_allowed([mod_role_id, admin_role_id]).predicate(new_ctx):
            await interaction.response.defer()
            return await self.client.get_cog("Moderation").infractions(ctx=self.ctx, member=self.target_member)
    
    @discord.ui.button(label="Profile", style=1, emoji="👤", custom_id=f"user_profile")
    async def profile_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's profile. """
        
        await interaction.response.defer()
        await self.client.get_cog("SlothCurrency").profile(ctx=self.ctx, member=self.target_member)

    @discord.ui.button(label="Info", style=2, emoji="ℹ️", custom_id=f"user_info")
    async def info_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's info. """

        await interaction.response.defer()
        await self.client.get_cog("SlothReputation").info(ctx=self.ctx, member=self.target_member)

    @discord.ui.button(label="Fake Accounts", style=2, emoji="🥸", custom_id=f"user_fake_accounts")
    async def fake_accounts_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's fake accounts. """

        await interaction.response.defer()
        await self.client.get_cog("Moderation").fake_accounts(ctx=self.ctx, member=self.target_member)


class Test(discord.ui.View):

    def __init__(self) -> None:
        super().__init__()


    @discord.ui.button(style=discord.ButtonStyle.success, label="test", custom_id="test")
    async def test_btn(self, button: discord.ui.button, interaction: discord.Interaction) -> None:

        self.test_btn.disabled = True

        await interaction.response.edit_message(view=self)

        await interaction.channel.send('button disabled!')

class BasicUserCheckView(discord.ui.View):

    def __init__(self, member: Union[discord.User, discord.Member], timeout: int = 180) -> None:
        super().__init__(timeout=timeout)
        self.member = member

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.member.id == interaction.user.id
        

class ExchangeActivityView(discord.ui.View):

    def __init__(self, client: commands.Bot, user_info: List[Union[int, str]]) -> None:
        super().__init__(timeout=60)
        self.client = client
        self.user_info = user_info


    @discord.ui.button(style=discord.ButtonStyle.success, label="Exchange Activity!", custom_id="exchange_money", emoji="💰")
    async def exchange_activity(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Exchanges the member's activity statuses into leaves (łł). """

        ctx = await self.client.get_context(interaction.message)
        member = interaction.user
        ctx.author = member

        m, s = divmod(self.user_info[2], 60)
        h, m = divmod(m, 60)

        await interaction.response.defer()
        
        confirmed = await ConfirmSkill(f"**{member.mention}, are you sure you want to exchange your {h:d} hours, {m:02d} minutes and {self.user_info[1]} messages?**").prompt(ctx)
        if confirmed:
            SlothCurrency = self.client.get_cog('SlothCurrency')
            await SlothCurrency.exchange(ctx)
        else:
            await interaction.followup.send(f"**{member.mention}, not exchanging, then!**")

        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        return self.user_info[0] == interaction.user.id


class GiveawayView(discord.ui.View):
    """ View for giveaway entries """

    def __init__(self, client: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.client = client


    @discord.ui.button(label="Participate", emoji="🎉", custom_id="giveaway_btn_id", style=discord.ButtonStyle.success)
    async def participate_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Handles clicks on the 'participate' button. """

        await interaction.response.defer()
        user = interaction.user
        message = interaction.message

        cog = self.client.get_cog('Giveaways')

        entry = await cog.get_giveaway_entry(user.id, message.id)
        if entry:
            await cog.delete_giveaway_entry(user.id, message.id)
            await interaction.followup.send(f"**You just removed your entry for this giveaway, {user.mention}!** ❌", ephemeral=True)
        else:
            await cog.insert_giveaway_entry(user.id, message.id)
            await interaction.followup.send(f"**Thank you for participating, {user.mention}!** ✅", ephemeral=True)

