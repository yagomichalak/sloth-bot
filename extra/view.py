# import.standard
import json
import os
from functools import partial
from pprint import pprint
from typing import Any, Dict, List, Optional, Union

# import.thirdparty
import discord
from discord.ext import commands

# import.local
from extra import utils
from extra.prompt.menu import ConfirmButton
from .menu import ConfirmSkill
from .modals import (BootcampFeedbackModal, DebateManagerApplicationModal,
                     EventHostApplicationModal, ModeratorApplicationModal,
                     TeacherApplicationModal)
from .select import ReportStaffSelect, ReportSupportSelect

# variables.role
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
analyst_debugger_role_id: int = int(os.getenv('ANALYST_DEBUGGER_ROLE_ID', 123))
# sloth_subscriber_sub_id = int(os.getenv("SLOTH_SUBSCRIBER_SUB_ID", 123))


class ReportSupportView(discord.ui.View):
    """ View for the ReportSupport menu. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        super().__init__(timeout=None)
        self.client = client
        self.cog = client.get_cog("ReportSupport")
        patreon_button = discord.ui.Button(style=5, label="Support us on Patreon!", url="https://www.patreon.com/Languagesloth", emoji="<:patreon:831401582426980422>", row=1)
        website_button = discord.ui.Button(style=5, label="Our website", url="https://languagesloth.com", emoji="<:Sloth:686237376510689327>", row=1)
        # sub_button = discord.ui.Button(sku_id=sloth_subscriber_sub_id, row=2)
        self.add_item(patreon_button)
        self.add_item(website_button)
        # self.add_item(sub_button)

    @discord.ui.button(label="Apply for Teacher!", style=3, custom_id="apply_to_teach", emoji="🧑‍🏫", row=0)
    async def apply_to_teach_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for starting the Teacher application. """

        member = interaction.user

        # Apply to be a Teacher
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await interaction.response.send_message(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**", ephemeral=True)

        await interaction.response.send_modal(TeacherApplicationModal(self.client))

    @discord.ui.button(label="Apply for Moderator!", style=3, custom_id="apply_to_moderate", emoji="👮", row=0)
    async def apply_to_moderate_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for starting the Moderator application. """

        member = interaction.user

        # Apply to be a Moderator
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await interaction.response.send_message(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**", ephemeral=True)

        await interaction.response.send_modal(ModeratorApplicationModal(self.client))

    @discord.ui.button(label="Apply for Event Host!", style=3, custom_id="apply_to_host_events", emoji="🎉", row=0)
    async def apply_to_event_host_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for starting the Event Host application. """

        member = interaction.user

        # Apply to be an Event Host
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await interaction.response.send_message(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**", ephemeral=True)

        await interaction.response.send_modal(EventHostApplicationModal(self.client))

    @discord.ui.button(label="Apply for Debate Manager!", style=3, custom_id="apply_to_manage_debates", emoji="🌐", row=0)
    async def apply_to_debate_manager_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for starting the Debate Manager application. """

        member = interaction.user

        # Apply to be a Debate Manager
        member_ts = self.cog.cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 1800:
                return await interaction.response.send_message(
                    f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**", ephemeral=True)

        await interaction.response.send_modal(DebateManagerApplicationModal(self.client))

    @discord.ui.button(label="Get your own Custom Bot (not for free)", style=1, custom_id="get_custom_bot", emoji="🤖", row=2)
    async def bot_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for buying a custom bot. """

        member = interaction.user
        guild = interaction.guild
        await interaction.response.defer(ephemeral=True)

        member_ts = self.cog.bot_cache.get(member.id)
        time_now = await utils.get_timestamp()
        if member_ts:
            sub = time_now - member_ts
            if sub <= 240:
                return await interaction.followup.send(
                    f"**You are on cooldown to use this, try again in {round(240-sub)} seconds**", ephemeral=True)

        self.cog.bot_cache[member.id] = time_now

        with open('extra/random/texts/other/dnk.txt', 'r', encoding="utf-8") as file:
            dnk_text = file.read()

        website_link = "https://languagesloth.com/bots/commission"

        # Order a bot
        embed = discord.Embed(
            title="__Commission a Bot!__",
            description=dnk_text,
            color=member.color,
            timestamp=interaction.message.created_at,
            url=website_link
        )
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(label="Go to website!", url=website_link)
        )
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Verify", style=1, custom_id="verify_id", emoji="☑️", row=2)
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

    @discord.ui.button(label="Report a User or Get Server/Role Support!", style=4, custom_id="report_support", emoji="<:politehammer:608941633454735360>", row=3)
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

    @discord.ui.button(label="Report a Staff member!", style=4, custom_id="report_staff", emoji="<:leoblabla:978481579590570034>", row=3)
    async def report_staff_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button for reporting a Staff member. """

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
        view.add_item(ReportStaffSelect(self.client))
        await interaction.followup.send(content="How can we help you?", view=view, ephemeral=True)

class QuickButtons(discord.ui.View):

    def __init__(self, client: commands.Bot, ctx: commands.Context, target_member: Union[discord.Member, discord.User]) -> None:
        super().__init__(timeout=60)
        self.client = client
        self.ctx = ctx
        self.target_member = target_member

    @discord.ui.button(label="File", style=4, emoji="🧾", custom_id=f"user_infractions")
    async def infractions_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's infractions and their watchlist entries. """

        new_ctx = self.ctx
        new_ctx.author = interaction.user

        if await utils.is_allowed([mod_role_id, admin_role_id, analyst_debugger_role_id]).predicate(new_ctx) or await utils.is_subscriber(throw_exc=False).predicate(new_ctx):
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

    @discord.ui.button(label="Snipe", style=2, emoji="🔍", custom_id=f"user_snipe")
    async def snipe_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Show's the member's last deleted messages. """

        await interaction.response.defer()
        ctx = await self.client.get_context(interaction.message)
        await self.client.get_cog("Moderation").snipe(ctx, message=str(self.target_member.id))

    @discord.ui.button(label="History", style=2, emoji="📍", custom_id=f"user_vh")
    async def vh_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Show's the member's voice history. """

        await interaction.response.defer()
        ctx = await self.client.get_context(interaction.message)
        await self.client.get_cog("VoiceChannelActivity").voice_history(ctx, member=self.target_member)

    @discord.ui.button(label="Fake Acc.", style=2, emoji="🥸", custom_id=f"user_fake_accounts")
    async def fake_accounts_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's fake accounts. """

        new_ctx = self.ctx
        new_ctx.author = interaction.user
        if await utils.is_allowed([mod_role_id, admin_role_id]).predicate(new_ctx):
            await interaction.response.defer()
            await self.client.get_cog("Moderation").fake_accounts(self.ctx, member=self.target_member)

    @discord.ui.button(label="Mod. Nick", style=2, emoji="🤕", custom_id=f"user_moderated_nickname")
    async def moderated_nickname_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Shows the member's fake accounts. """

        new_ctx = self.ctx
        new_ctx.author = interaction.user
        if await utils.is_allowed([mod_role_id, admin_role_id]).predicate(new_ctx):
            await interaction.response.defer()
            await self.client.get_cog("Moderation").show_moderated_nickname(self.ctx, member=self.target_member)


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

        self.stop()
        ctx = await self.client.get_context(interaction.message)
        member = interaction.user
        ctx.author = member

        m, s = divmod(self.user_info[2], 60)
        h, m = divmod(m, 60)

        await interaction.response.defer()
        SlothCurrency = self.client.get_cog('SlothCurrency')
        is_sub = await utils.is_subscriber(check_adm=False, throw_exc=False).predicate(ctx)
        cmsg, message_times = await SlothCurrency.convert_messages(self.user_info[1], is_sub)
        ctime, time_times = await SlothCurrency.convert_time(self.user_info[2], is_sub)

        if cmsg == ctime == 0:
            return await interaction.followup.send(f"**You have nothing to exchange, {member.mention}!**")

        expected_money: int = cmsg + ctime
        confirm_view = ConfirmButton(member, timeout=60)

        await interaction.followup.send(
            embed=discord.Embed(
                description=f"**{member.mention}, are you sure you want to exchange your `{h:d}h`, `{m:02d}m` and `{self.user_info[1]} messages` for `{expected_money}łł`?**",
                color=member.color,
            ), view=confirm_view
        )
        await confirm_view.wait()
        await utils.disable_buttons(confirm_view)
        await confirm_view.interaction.message.edit(view=confirm_view)

        if confirm_view.value is None:
            return await confirm_view.interaction.followup.send(f"**{member.mention}, you took too long to answer...**")

        if not confirm_view.value:
            return await confirm_view.interaction.followup.send(f"**{member.mention}, not exchanging, then!**")

        await SlothCurrency.exchange(confirm_view.interaction, cmsg, message_times, ctime, time_times)
        # Updates user Activity Status and Money
        await SlothCurrency.update_user_server_messages(member.id, -message_times * 50)
        await SlothCurrency.update_user_server_time(member.id, -time_times * 1800)
        await SlothCurrency.update_user_money(member.id, expected_money)
        SlothReputation = self.client.get_cog("SlothReputation")
        await SlothReputation.insert_sloth_actions(label="message-exchange", user_id=member.id, target_id=member.id, int_content=message_times * 50)
        await SlothReputation.insert_sloth_actions(label="time-exchange", user_id=member.id, target_id=member.id, int_content=time_times * 1800)

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

class UserPetView(discord.ui.View):
    """ View for the UserPet selection. """

    def __init__(self, member: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.pets = self.get_pets()
        self.selected_pet: str = None

        options = [
            discord.SelectOption(label=pet, description=values['description'], emoji=values['emoji'])
            for pet, values in self.pets.items()]

        pets_select = discord.ui.Select(
            placeholder="Select the kind of Pet you want to hatch your egg to.", custom_id="user_pet_view_select_id", 
            options=options)

        pets_select.callback = partial(self.select_pet_select, pets_select)

        self.children.insert(0, pets_select)

    def get_pets(self) -> List[Dict[str, str]]:
        """ Gets a list of pets to select. """

        data = {}
        with open(f'extra/random/json/pets.json', 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data
    
    async def select_pet_select(self, select: discord.ui.select, interaction: discord.Interaction) -> None:
        """ Callback for a select menu option. """

        embed = interaction.message.embeds[0]
        selected_option = interaction.data['values'][0]
        embed.clear_fields()
        embed.add_field(name="Selected Pet Breed:", value=f"{selected_option} {self.pets[selected_option]['emoji']}")
        embed.set_image(url=self.pets[selected_option]['url'])
        self.selected_pet = selected_option

        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Confirm", custom_id="confirm_pet_selection_id", style=discord.ButtonStyle.success, emoji="✅", row=1)
    async def confirm_pet_selection_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Confirms the pet selection. """

        if not self.selected_pet:
            return await interaction.response.send_message("**You must choose an option to confirm!**", ephemeral=True)

        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Cancel", custom_id="cancel_pet_selection_id", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def cancel_pet_selection_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the pet selection. """

        await interaction.response.defer()
        self.selected_pet = None
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Checks whether the click was done by the author of the command. """

        return self.member.id == interaction.user.id

class UserBabyView(discord.ui.View):
    """ View for the UserBaby selection. """

    def __init__(self, member: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.babies = self.get_baby_classes()
        self.selected_baby: str = None

        options = [
            discord.SelectOption(label=baby, description=values['description'], emoji=values['emoji'])
            for baby, values in self.babies.items()]

        babies_select = discord.ui.Select(
            placeholder="Select the Sloth Class you want your Baby baby to be born in.", custom_id="user_baby_view_select_id", 
            options=options)

        babies_select.callback = partial(self.select_baby_select, babies_select)

        self.children.insert(0, babies_select)

    def get_baby_classes(self) -> List[Dict[str, str]]:
        """ Gets a list of sloth classes to select. """

        data = {}
        with open(f'extra/random/json/baby_classes.json', 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    async def select_baby_select(self, select: discord.ui.select, interaction: discord.Interaction) -> None:
        """ Callback for a select menu option. """

        embed = interaction.message.embeds[0]
        selected_option = interaction.data['values'][0]
        embed.clear_fields()
        embed.add_field(name="Selected Sloth Class:", value=f"{selected_option} {self.babies[selected_option]['emoji']}")
        embed.set_image(url=self.babies[selected_option]['url'])
        self.selected_baby = selected_option

        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Confirm", custom_id="confirm_baby_selection_id", style=discord.ButtonStyle.success, emoji="✅", row=1)
    async def confirm_baby_selection_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Confirms the baby selection. """

        if not self.selected_baby:
            return await interaction.response.send_message("**You must choose an option to confirm!**", ephemeral=True)

        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Cancel", custom_id="cancel_baby_selection_id", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def cancel_baby_selection_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the baby selection. """

        await interaction.response.defer()
        self.selected_baby = None
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Checks whether the click was done by the author of the command. """

        return self.member.id == interaction.user.id


class BootcampFeedbackView(discord.ui.View):

    def __init__(self, client: commands.Bot, member: discord.Member, perpetrator: discord.Member, current_ts: int) -> None:
        super().__init__(timeout=60)
        self.client = client
        self.cog: commands.Cog = client.get_cog("Bootcamp")
        self.member = member
        self.perpetrator = perpetrator
        self.questions = {
            1: {"message": "How much has the learner improved since start/last meeting?", "type": discord.InputTextStyle.paragraph, "max_length": 200, "answer": "", "rating": 0},
            2: {"message": "Has the learner completed the tasks set by native?", "type": discord.InputTextStyle.singleline, "max_length": 3, "answer": "", "rating": 0},
            3: {"message": "Does the learner show dedication to learning the language?", "type": discord.InputTextStyle.singleline, "max_length": 3, "answer": "", "rating": 0},
        }
        
        self.unique_id = f"{current_ts}-{self.member.id}-{self.perpetrator.id}"

        # Adds the question buttons
        self.add_question_buttons()

    def add_question_buttons(self) -> None:
        
        for qi in self.questions.keys():
            question_button = discord.ui.Button(
                label=f"Question #{qi}", style=discord.ButtonStyle.blurple, emoji="❓", custom_id=f"{self.unique_id}-{qi}"
            )
            question_button.callback = partial(self.question_callback, question_button)
            self.children.append(question_button)

        # Adds the feedback button
        send_feedback_button = discord.ui.Button(
            label=f"Send Feedback", style=discord.ButtonStyle.danger, emoji="📨", custom_id="send_feedback", disabled=True
        )
        send_feedback_button.callback = partial(self.send_feedback, send_feedback_button)
        self.children.append(send_feedback_button)
            
    async def question_callback(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Callback for each click on the questions buttons. """

        question_index = int(button.custom_id.replace(f"{self.unique_id}-", ""))
        modal = BootcampFeedbackModal(self.client, view=self, questions=self.questions, index_question=question_index)
        await interaction.response.send_modal(modal=modal)

    async def send_feedback(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Button to send the feedback data to the API. """

        await interaction.response.defer()
        self.children.clear()

        # Logic here
        for question_index, question_data in self.questions.items():
            # Maps the data
            data = {
                "user_id": self.member.id,
                "perpetrator_id": self.perpetrator.id,
                "question": question_index,
                "answer": question_data["answer"],
                "rating": question_data["rating"],
            }
            # Sends it to the API
            await self.cog.post_user_feedback_data(data)

        await interaction.followup.edit_message(
            interaction.message.id,
            content=f"Feedback successfully given to {self.member.mention}",
            view=self
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.perpetrator.id == interaction.user.id
