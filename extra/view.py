import discord
from extra import utils
from discord.ext import commands
from typing import List, Union, Optional, Dict, Any
from .menu import ConfirmSkill
from .select import ReportSupportSelect
import os
import json


mod_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))

class ReportSupportView(discord.ui.View):

    def __init__(self, client: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.client = client
        self.cog = client.get_cog('ReportSupport')
        patreon_button = discord.ui.Button(style=5, label="Support us on Patreon!", url="https://www.patreon.com/Languagesloth", emoji="<:patreon:831401582426980422>", row=2)
        self.children.insert(4, patreon_button)


    @discord.ui.button(label="Apply for Teacher!", style=3, custom_id=f"apply_to_teach", emoji="🧑‍🏫")
    async def apply_to_teach_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for starting the Teacher application. """

        await interaction.response.defer()
        member = interaction.user

        # Apply to be a Teacher
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await interaction.followup.send(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**", ephemeral=True)

        self.cog.cache[member.id] = time_now
        await self.cog.send_teacher_application(member)

    @discord.ui.button(label="Apply for Moderator!", style=3, custom_id=f"apply_to_moderate", emoji="👮")
    async def apply_to_moderate_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for starting the Moderator application. """

        await interaction.response.defer()
        member = interaction.user

        # Apply to be a Moderator
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await interaction.followup.send(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**", ephemeral=True)

        self.cog.cache[member.id] = time_now
        await self.cog.send_moderator_application(member)

    @discord.ui.button(label="Apply for Event Manager!", style=3, custom_id=f"apply_to_manage_events", emoji="🎉")
    async def apply_to_event_manager_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for starting the Event Manager application. """

        await interaction.response.defer()
        member = interaction.user

        # Apply to be an Event Manager
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await interaction.followup.send(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**", ephemeral=True)

        self.cog.cache[member.id] = time_now
        await self.cog.send_event_manager_application(member)

    @discord.ui.button(label="Apply for Debate Manager!", style=3, custom_id=f"apply_to_manage_debates", emoji="🌐")
    async def apply_to_debate_manager_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for starting the Debate Manager application. """

        await interaction.response.defer()
        member = interaction.user

        # Apply to be a Debate Manager
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await interaction.followup.send(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**", ephemeral=True)

        self.cog.cache[member.id] = time_now
        await self.cog.send_debate_manager_application(member)


    @discord.ui.button(label="Get your own Custom Bot (not for free)", style=1, custom_id=f"get_custom_bot", emoji="🤖", disabled=True, row=2)
    async def bot_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for buying a custom bot. """

        member = interaction.user

        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 240:
                return await member.send(
                    f"**You are on cooldown to use this, try again in {round(240-sub)} seconds**", ephemeral=True)
            
        await interaction.response.defer()

        self.cog.cache[member.id] = time_now
        # Order a bot
        dnk = self.client.get_user(int(os.getenv('DNK_ID')))
        embed = discord.Embed(title="New possible order!",
            description=f"{member.mention} ({member.id}) might be interested in buying something from you!",
            color=member.color)
        embed.set_thumbnail(url=member.display_avatar)
        await dnk.send(embed=embed)
        await member.send(f"**If you are really interested in **buying** a custom bot, send a private message to {dnk.mention}!**")
        await self.cog.dnk_embed(member)

    @discord.ui.button(label="Verify", style=1, custom_id=f"verify_id", emoji="☑️", row=2)
    async def verify_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for starting the verification process. """

        await interaction.response.defer()

        member = interaction.user
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()

        if member_ts:
            sub = time_now - member_ts
            if sub <= 240:
                return await interaction.followup.send(
                    f"**You are on cooldown to use this, try again in {round(240-sub)} seconds, {member.mention}!**", ephemeral=True)
        
        self.cog.cache[member.id] = time_now
        await self.cog.send_verified_selfies_verification(interaction)

    @discord.ui.button(label="Report a User or Get Server/Role Support!", style=4, custom_id=f"report_support", emoji="<:politehammer:608941633454735360>", row=3)
    async def report_support_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for reporting someone. """

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
            return await self.client.get_cog("Moderation").infractions(self.ctx, message=str(self.target_member.id))
    
    @discord.ui.button(label="Profile", style=1, emoji="👤", custom_id=f"user_profile")
    async def profile_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's profile. """
        
        await interaction.response.defer()
        await self.client.get_cog("SlothCurrency")._profile(self.ctx, member=self.target_member)

    @discord.ui.button(label="Info", style=2, emoji="ℹ️", custom_id=f"user_info")
    async def info_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's info. """

        await interaction.response.defer()
        await self.client.get_cog("SlothReputation")._info(self.ctx, member=self.target_member)

    @discord.ui.button(label="Fake Accounts", style=2, emoji="🥸", custom_id=f"user_fake_accounts")
    async def fake_accounts_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's fake accounts. """

        new_ctx = self.ctx
        new_ctx.author = interaction.user
        if await utils.is_allowed([mod_role_id, admin_role_id]).predicate(new_ctx):
            await interaction.response.defer()
            await self.client.get_cog("Moderation").fake_accounts(self.ctx, member=self.target_member)



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

    def __init__(self, client: commands.Bot, role_id: int = None) -> None:
        super().__init__(timeout=None)
        self.client = client
        self.role_id = role_id


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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Checks whether the user has permissions to interact with this view. """

        member = interaction.user

        if self.role_id is not None:
            if await utils.is_allowed([self.role_id], check_adm=False).predicate(member=member, channel=interaction.channel):
                return True
            else:
                await interaction.response.send_message(
                    f"**You don't have the required role to interact with this giveaway, {member.mention}!** ⚠️", 
                    ephemeral=True)
                return False
        else:
            return True


class SoundBoardButton(discord.ui.Button):
    """ Button of the soundboard. """

    def __init__(self, style: discord.ButtonStyle = discord.ButtonStyle.blurple, emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None, custom_id: Optional[str] = None, row: Optional[int] = None) -> None:
        super().__init__(style=style, label='\u200b', emoji=emoji, custom_id=custom_id, row=row)


    async def callback(self, interaction: discord.Interaction) -> None:
        """ Soundboard's button callback. """

        await interaction.response.defer()
        sound: Dict[str, str] = self.view.sounds.get(self.custom_id)
        await self.play_sound(interaction, sound)

    async def play_sound(self, interaction: discord.Interaction, sound: Dict[str, Dict[str, str]]) -> None:
        """ Plays a sound in the voice channel. """

        author = interaction.user

        author_state = author.voice
        if not (vc := author_state and author_state.channel):
            return await interaction.followup.send(f"**You're not in a VC!**", ephemeral=True)

        if (ovc := author.guild.voice_client) and ovc.channel.id != vc.id:
            return await interaction.followup.send(f"**You are not in the origin voice channel ({ovc.channel.mention})!**", ephemeral=True)

        await utils.audio(self.view.client, vc, author, sound['path'])

class SoundBoardView(discord.ui.View):
    """ View for the soundboard. """

    def __init__(self, ctx: commands.Context, client: commands.Bot, setting: str, timeout: Optional[float] = 180) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.client = client
        self.setting = setting
        self.sounds: List[Dict[str, str]] = self.get_sounds(self.setting)

        counter: int = 0
        for i in range(4):
            for _ in range(5):
                current_sound: Dict[str, str] = list(self.sounds.items())[counter][1]
                counter += 1
                button = SoundBoardButton(style=current_sound['style'], custom_id=f"sb_btn_{counter}_id", emoji=current_sound['emoji'], row=i)
                self.add_item(button)

    def get_sounds(self, json_name: str = 'sounds') -> List[Dict[str, str]]:
        """ Gets a list of sounds to play on the soundboard. """

        data = {}
        with open(f'extra/random/json/{json_name}.json', 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id