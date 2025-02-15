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

from .modals import UserReportStaffDetailModal, UserReportSupportDetailModal

# variables.role
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
analyst_debugger_role_id: int = int(os.getenv('ANALYST_DEBUGGER_ROLE_ID', 123))
# sloth_subscriber_sub_id = int(os.getenv("SLOTH_SUBSCRIBER_SUB_ID", 123))

# variables.textchannel.misc
frog_catchers_channel_id: int = int(os.getenv("FROG_CATCHERS_CHANNEL_ID", 123))


class ReportView(discord.ui.View):
    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """
        super().__init__(timeout=None)
        self.client = client
        self.cog = client.get_cog("ReportSupport")

        report_select = discord.ui.Select(
            placeholder="Get help or report someone",
            options=[
                discord.SelectOption(label="Report a User", description="File a complaint against a user breaking the rules of the server",
                                     value="report_user", emoji="<:ReportUser:1337405689500405880>"),
                discord.SelectOption(label="Role help", description="Get help for setting up your roles",
                                     value="report_help", emoji="<:Role:1337405699931504676>"),
                discord.SelectOption(label="General Help", description="Ask general questions about the server to a staff member ",
                                     value="report_support", emoji="<:General:1337405674157637662>"),
                discord.SelectOption(label="Staff misconduct", description="File a complaint against a staff member",
                                     value="report_staff", emoji="<:ReportStaff:1337405681829154827>"),
                discord.SelectOption(label="Verify", description="Get the verified role in the server",
                                     value="verify", emoji="<:Verify:1337405709050187819>"),
                discord.SelectOption(label="Our Website", description="Check our website and create your sloth account",
                                     value="website", emoji="<:Website:1337405716645810186>"),
                discord.SelectOption(label="Lessons Calendar", description="Stay up to date with all our classes",
                                     value="calendar", emoji="<:Calendar:1337406344835104809>"),
                discord.SelectOption(label="Clear select", value="clear", emoji="<:red_clear:1337404359624888350>"),
            ],
            custom_id="report_select",
            row=0
        )
        report_select.callback = self.report_select_callback
        self.add_item(report_select)

    async def report_select_callback(self, interaction: discord.Interaction) -> None:
        """ Callback for report select menu. """
        member = interaction.user
        time_now = await utils.get_timestamp()

        if interaction.data["values"][0] == "website":
            embed = discord.Embed(description="Check our website and create your sloth account below",
                                  color=0xdd3849)
            button = discord.ui.Button(label="Open Website", url="https://languagesloth.com/",
                                       emoji="<:Website:1337405716645810186>")
            view = discord.ui.View()
            view.add_item(button)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif interaction.data["values"][0] == "calendar":
            embed = discord.Embed(description="Open website and stay up to date with all our classes and events",
                                  color=0xdd3849)
            button = discord.ui.Button(label="Open Lessons Calendar", url="https://languagesloth.com/class/calendar/",
                                       emoji="<:Calendar:1337406344835104809>")
            view = discord.ui.View()
            view.add_item(button)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif interaction.data["values"][0] == "report_staff":
            modal = UserReportStaffDetailModal(self.client, interaction.data['values'][0])
            await interaction.response.send_modal(modal)

        elif interaction.data["values"][0] == "report_user":
            modal = UserReportSupportDetailModal(self.client, interaction.data['values'][0])
            await interaction.response.send_modal(modal)

        elif interaction.data["values"][0] == "report_help" or interaction.data["values"][0] == "report_support":
            modal = UserReportSupportDetailModal(self.client, interaction.data['values'][0])
            await modal.callback(interaction)

        elif interaction.data["values"][0] == "verify":
            member_ts = self.cog.cache.get(member.id)
            if member_ts and time_now - member_ts <= 240:
                return await interaction.followup.send(
                    f"**You are on cooldown to use this, try again in {round(240 - (time_now - member_ts))} seconds, {member.mention}!**",
                    ephemeral=True)
            else:
                await interaction.response.edit_message(view=self)
            self.cog.cache[member.id] = time_now
            await self.cog.send_verified_selfies_verification(interaction)

        else:
            await interaction.response.edit_message(view=self)


class PremiumView(discord.ui.View):
    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """
        super().__init__(timeout=None)
        self.client = client
        self.cog = client.get_cog("ReportSupport")

        premium_select = discord.ui.Select(
            placeholder="Get access to special privileges",
            options=[
                discord.SelectOption(label="Patrons", description="Support the server by becoming a patreon",
                                     value="patrons", emoji="<:Patreon:1337398905364811776>"),
                discord.SelectOption(label="Frog Catcher", description="Support the server by becoming a frog catcher",
                                     value="frog_catcher", emoji="<:FrogCatcher:1337398915816882176>"),
                discord.SelectOption(label="Clear select", value="clear", emoji="<:green_clear:1337404379875115071>")
            ],
            custom_id="supports",
            row=0
        )

        premium_select.callback = self.premium_callback
        self.add_item(premium_select)

    async def premium_callback(self, interaction: discord.Interaction) -> None:
        """ Callback for apply select menu. """
        member = interaction.user
        time_now = await utils.get_timestamp()

        if interaction.data["values"][0] == "patrons":
            embed = discord.Embed(description="Become a Patreon",
                                  color=0x3A9D76)
            button = discord.ui.Button(label="Patreon", url="https://www.patreon.com/languagesloth/",
                                       emoji="<:Patreon:1337398905364811776>")
            view = discord.ui.View()
            view.add_item(button)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif interaction.data["values"][0] == "frog_catcher":
            sloth_subscriber_role_id = int(os.getenv("SLOTH_SUBSCRIBER_ROLE_ID", 123))
            sloth_subscriber_sub_id = int(os.getenv("SLOTH_SUBSCRIBER_SUB_ID", 123))
            sloth_twenty_k_leaves_bundle_id = int(os.getenv("SLOTH_TWENTY_K_LEAVES_BUNDLE_ID", 123))
            sloth_marriage_bundle_id = int(os.getenv("SLOTH_MARRIAGE_BUNDLE_ID", 123))
            sloth_golden_leaf_id = int(os.getenv("SLOTH_GOLDEN_LEAF_ID", 123))

            # Descriptive Embed
            embed = discord.Embed(
                title="__Sloth Subscriber__",
                description="For getting access to some extra features, commands and server perks.",
                color=0x3A9D76
            )
            embed.add_field(
                name="🎲 __Gambling__",
                value="> Access to gambling commands like `z!coinflip`, `z!blackjack`, `z!whitejack`, `z!slots`, etc.",
                inline=False
            )
            embed.add_field(
                name="💍 __Polygamy & Golden Leaves__",
                value="> You'll receive `5 Golden Leaves` <:golden_leaf:1289365306413813810> per month, and you can also `marry up to 4 people` at the same time.",
                inline=False
            )
            embed.add_field(
                name="<:richsloth:701157794686042183> __Bonus Activity Exchange & Leaves__",
                value="> Receive `3000 leaves` 🍃 per month, and get twice as many leaves for exchanging your activity statuses, that is, the time you spent in the VCs and messages sent.",
                inline=False
            )
            embed.add_field(
                name="🕰️ __Cooldown Reset & Reduction__",
                value="> Reset all of your Sloth Skills automatically upon subscribing (and on subscription renewal), and reduce by `50% the cooldown` of your next skills.",
                inline=False
            )
            embed.add_field(
                name="🚨 __Check Infractions__",
                value=f"> Check other people's infractions in <#{frog_catchers_channel_id}>.",
                inline=False
            )
            embed.add_field(
                name="🦥 __Sloth Subscriber role__",
                value=f"> Get the <@&{sloth_subscriber_role_id}>, whose color can be changed once a week for `1 Golden Leaf` <:golden_leaf:1289365306413813810>.",
                inline=False
            )
            embed.add_field(
                name=f"__Mastersloth Class__",
                value=f"> Become a `Mastersloth` for `5 Golden Leaves` <:golden_leaf:1289365306413813810> and have ALL skills of the other Sloth Classes in your skill set.",
                inline=False
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/980613341858914376/1316585723570163722/image.png?ex=675b9581&is=675a4401&hm=e69b1ec43d9ff32d1a641e17925fd874715c24b4bd8f86dba3f6ba72ee9b12ec&")

            # Subscription Views
            view = discord.ui.View()
            view.add_item(discord.ui.Button(sku_id=sloth_subscriber_sub_id, row=0))
            view.add_item(discord.ui.Button(sku_id=sloth_golden_leaf_id, row=0))
            view.add_item(discord.ui.Button(sku_id=sloth_twenty_k_leaves_bundle_id, row=1))
            view.add_item(discord.ui.Button(sku_id=sloth_marriage_bundle_id, row=1))

            return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        else:
            await interaction.response.edit_message(view=self)


class ApplyView(discord.ui.View):
    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """
        super().__init__(timeout=None)
        self.client = client
        self.cog = client.get_cog("ReportSupport")

        apply_select = discord.ui.Select(
            placeholder="Apply for staff positions",
            options=[
                discord.SelectOption(label="Moderator",
                                     description="Enforce rules to maintain a positive environment",
                                     value="apply_to_moderate", emoji="<:Moderator:1337403244628148234>"),

                discord.SelectOption(label="Designer", # APPLICATION DOESN'T EXIST
                                     description="Keep the server visually appealing and fresh",
                                     value="apply_to_designer", emoji="<:Designer:1337403199539384413>"),

                discord.SelectOption(label="Teacher",
                                     description="Share your knowledge and educate the community",
                                     value="apply_to_teach", emoji="<:Teacher:1337403258196721746>"),

                discord.SelectOption(label="Event Host",
                                     description="Organize movies, debates, and other events",
                                     value="apply_to_host_events", emoji="<:Event:1337403220544323634>"),

                discord.SelectOption(label="Content Creator", # APPLICATION DOESN'T EXIST
                                     description="Promote the server on TikTok/YouTube",
                                     value="apply_to_content_creator", emoji="<:Contenter:1337403191314092043>"),

                discord.SelectOption(label="Giveaway Manager", # APPLICATION DOESN'T EXIST
                                     description="Plan and manage giveaways for our community",
                                     value="apply_to_giveaway_manager", emoji="<:Giveaway:1337403233391476778>"),

                discord.SelectOption(label="Analyst & Debugger", # APPLICATION DOESN'T EXIST
                                     description="sudo rm -rf / *",
                                     value="apply_to_analyst_debugger", emoji="<:Developer:1337403211912319078>"),

                discord.SelectOption(label="Debate Organizer",  # APPLICATION DOESN'T EXIST
                                     description="Host debates",
                                     value="apply_to_debate", emoji="<:Debate:1340355499325001809>"),


                discord.SelectOption(label="Clear select", value="clear", emoji="<:blue_clear:1337404369699737641>"),
            ],
            custom_id="apply_select",
            row=0
        )

        apply_select.callback = self.apply_select_callback
        self.add_item(apply_select)

    async def apply_select_callback(self, interaction: discord.Interaction) -> None:
        """ Callback for apply select menu. """
        member = interaction.user
        time_now = await utils.get_timestamp()

        if interaction.data["values"][0] == "apply_to_teach":
            member_ts = self.cog.cache.get(member.id)
            if member_ts and time_now - member_ts <= 1800:
                return await interaction.followup.send(
                    f"**You are on cooldown to apply, try again in {(1800 - (time_now - member_ts)) / 60:.1f} minutes**",
                    ephemeral=True)
            else:
                await interaction.response.send_modal(TeacherApplicationModal(self.client))

        elif interaction.data["values"][0] == "apply_to_moderate":
            member_ts = self.cog.cache.get(member.id)
            if member_ts and time_now - member_ts <= 1800:
                return await interaction.followup.send(
                    f"**You are on cooldown to apply, try again in {(1800 - (time_now - member_ts)) / 60:.1f} minutes**",
                    ephemeral=True)
            else:
                await interaction.response.send_modal(ModeratorApplicationModal(self.client))

        elif interaction.data["values"][0] == "apply_to_host_events":
            member_ts = self.cog.cache.get(member.id)
            if member_ts and time_now - member_ts <= 1800:
                return await interaction.followup.send(
                    f"**You are on cooldown to apply, try again in {(1800 - (time_now - member_ts)) / 60:.1f} minutes**",
                    ephemeral=True)
            else:
                await interaction.response.send_modal(EventHostApplicationModal(self.client))

        elif interaction.data["values"][0] == "apply_to_manage_debates":
            member_ts = self.cog.cache.get(member.id)
            if member_ts and time_now - member_ts <= 1800:
                return await interaction.followup.send(
                    f"**You are on cooldown to apply, try again in {(1800 - (time_now - member_ts)) / 60:.1f} minutes**",
                    ephemeral=True)
            else:
                await interaction.response.send_modal(DebateManagerApplicationModal(self.client))

        elif interaction.data["values"][0] == "clear":
            await interaction.response.edit_message(view=self)

        else:
            return await interaction.response.send_message(
                "**This isn't ready**",
                ephemeral=True)


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

        is_allowed = await utils.is_allowed([mod_role_id, admin_role_id, analyst_debugger_role_id]).predicate(new_ctx)
        is_sub = await utils.is_subscriber(throw_exc=False).predicate(new_ctx)
        if is_allowed or is_sub:
            if not is_allowed and interaction.channel.id != frog_catchers_channel_id:
                return await interaction.response.send_message(f"**Subs can only see infractions in the <#{frog_catchers_channel_id}> channel!**")
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

class WarnRulesView(discord.ui.View):
    """ View for the WarnRules selection. """

    def __init__(self, member: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.selected_rule: str = None

        options = [
            discord.SelectOption(label="R1", description="NSFW is forbidden."),
            discord.SelectOption(label="R2", description="Be respectful."),
            discord.SelectOption(label="R3", description="Avoid controversy."),
            discord.SelectOption(label="R4", description="Advertising is forbidden."),
            discord.SelectOption(label="R5", description="Do not dox."),
            discord.SelectOption(label="R6", description="Do not spam."),
            discord.SelectOption(label="R7", description="Do not impersonate others."),
            discord.SelectOption(label="R8", description="Do not beg."),
            discord.SelectOption(label="R9", description="Do not cause drama."),
        ]

        rule_select = discord.ui.Select(
            placeholder="Choose a rule for this warn...", custom_id="warn_rules_view_select_id", 
            options=options)

        rule_select.callback = partial(self.select_rule_select, rule_select)

        self.children.insert(0, rule_select)

    async def select_rule_select(self, select: discord.ui.select, interaction: discord.Interaction) -> None:
        """ Callback for a select menu option. """

        embed = interaction.message.embeds[0]
        selected_label = interaction.data['values'][0]
        selected_option = next((option for option in select.options if option.label == selected_label), None)
        embed.clear_fields()
        embed.add_field(name="Selected Rule:", value=f"{selected_label}: {selected_option.description}")
        self.selected_rule = selected_option

        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Confirm", custom_id="confirm_rule_selection_id", style=discord.ButtonStyle.success, emoji="✅", row=1)
    async def confirm_rule_selection_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Confirms the rule selection. """

        if not self.selected_rule:
            return await interaction.response.send_message("**You must choose an option to confirm!**", ephemeral=True)

        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Cancel", custom_id="cancel_rule_selection_id", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def cancel_rule_selection_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the rule selection. """

        await interaction.response.defer()
        self.selected_rule = None
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Checks whether the click was done by the author of the command. """

        return self.member.id == interaction.user.id