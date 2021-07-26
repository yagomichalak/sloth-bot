import discord
from discord.components import SelectOption
from extra import utils
from discord.ext import commands
from typing import List, Dict, Union, Any
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
        patreon_button = discord.ui.Button(style=5, label="Support us on Patreon!", url="https://www.patreon.com/Languagesloth", emoji="<:patreon:831401582426980422>")
        self.children.insert(2, patreon_button)


    @discord.ui.button(label="Apply to be a Teacher!", style=3, custom_id=f"apply_to_teach", emoji="🧑‍🏫")
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

    @discord.ui.button(label="Apply to be a Moderator!", style=3, custom_id=f"apply_to_moderate", emoji="👮")
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


    @discord.ui.button(label="Get your own Custom Bot (not for free)", style=1, custom_id=f"get_custom_bot", emoji="🤖")
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

    @discord.ui.button(label="Report a User or Get Server/Role Support!", style=4, custom_id=f"report_support", emoji="<:politehammer:608941633454735360>")
    async def report_support_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:

        member = interaction.user

        member_ts = self.cog.report_cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 240:
                return await member.send(
                    f"**You are on cooldown to report, try again in {round(240-sub)} seconds**")

        self.cog.report_cache[member.id] = time_now
        await interaction.response.defer()
        view = discord.ui.View()
        view.add_item(ReportSupportSelect(self.client))
        await member.send(content="How can we help you?", view=view)
        # await self.cog.select_report(member, member.guild)


class QuickButtons(discord.ui.View):

    def __init__(self, client: commands.Bot, ctx: commands.Context, target_member: discord.Member) -> None:
        super().__init__(timeout=60)
        self.client = client
        self.ctx = ctx
        self.target_member = target_member
        

    @discord.ui.button(label="See Infractions", style=4, emoji="❗", custom_id=f"user_infractions", disabled=True)
    async def see_infractions_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's infractions. """

        new_ctx = self.ctx
        new_ctx.author = interaction.user

        if await utils.is_allowed([mod_role_id, admin_role_id]).predicate(new_ctx):
            await interaction.response.defer()
            return await self.client.get_cog("Moderation").infractions(ctx=self.ctx, member=self.target_member)
    
    @discord.ui.button(label="See Profile", style=1, emoji="👤", custom_id=f"user_profile")
    async def see_profile_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's profile. """
        
        await interaction.response.defer()
        await self.client.get_cog("SlothCurrency").profile(ctx=self.ctx, member=self.target_member)

    @discord.ui.button(label="See Info", style=2, emoji="ℹ️", custom_id=f"user_info")
    async def see_info_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's info. """

        await interaction.response.defer()
        await self.client.get_cog("SlothReputation").info(ctx=self.ctx, member=self.target_member)



class Test(discord.ui.View):

    def __init__(self) -> None:
        super().__init__()


    @discord.ui.button(style=discord.ButtonStyle.success, label="test", custom_id="test")
    async def test_btn(self, button: discord.ui.button, interaction: discord.Interaction) -> None:

        self.test_btn.disabled = True

        await interaction.response.edit_message(view=self)

        await interaction.channel.send('button disabled!')
        

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


class ConfirmButton(discord.ui.View):
    def __init__(self, timeout: int = None):
        super().__init__(timeout=timeout)
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.button, interaction: discord.Interaction):
        self.value = False
        self.stop()