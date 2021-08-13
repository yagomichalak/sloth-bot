import discord
from discord import activity
from discord.ext import commands
from typing import Optional, List, Dict, Union
from random import choice
from extra import utils
from functools import partial
import json

class HugView(discord.ui.View):

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Hug', style=discord.ButtonStyle.blurple, custom_id='hug_id', emoji="🤗")
    async def hug_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Hugs someone. """

        hugs: List[str] = [
            'https://c.tenor.com/OXCV_qL-V60AAAAC/mochi-peachcat-mochi.gif',
            'https://c.tenor.com/wqCAHtQuTnkAAAAC/milk-and-mocha-hug.gif',
            'https://c.tenor.com/7xJoTToAJC8AAAAd/hug-love.gif',
            'https://c.tenor.com/Zd3o8HgqWKYAAAAC/milk-and-mocha-hug.gif',
            'https://c.tenor.com/0PIj7XctFr4AAAAC/a-whisker-away-hug.gif'
        ]

        embed = discord.Embed(
            title="__Hug__",
            description=f"🤗 {self.member.mention} hugged {self.target.mention} 🤗",
            color=discord.Color.gold(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(hugs))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the hug action. """

        await self.disable_buttons(interaction)
        self.stop()

    async def disable_buttons(self, interaction: discord.Interaction, followup: bool = False) -> None:

        for child in self.children:
            child.disabled = True

        if followup:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.member.id == interaction.user.id

class BootView(discord.ui.View):

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Where it hits', style=discord.ButtonStyle.blurple, custom_id='general_kick_id', emoji="🦵")
    async def general_kick_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Kicks someone without aiming in a specific place. """

        general_kicks: List[str] = [
            'https://c.tenor.com/vTA-IZFcc3AAAAAC/drop-kick-kick.gif',
            'https://c.tenor.com/TY_AmszVhJIAAAAC/oh-yeah-high-kick.gif',
            'https://c.tenor.com/SddY3UqUHOAAAAAC/kick-cartoon.gif',
            'https://c.tenor.com/Lyqfq7_vJnsAAAAC/kick-funny.gif',
            'https://c.tenor.com/U0wSQ2s0sloAAAAC/ninja-kick.gif',
            'https://c.tenor.com/NRKMXEvslqIAAAAd/flying-kick-drop-kick.gif',
            'https://c.tenor.com/qEVxKG7ihzUAAAAC/kick-woman-lol.gif',
            'https://c.tenor.com/s7s5glHMddQAAAAC/in-yo-face-flying-side-kick.gif',
            'https://c.tenor.com/M9qJRj5Bo_wAAAAC/alita-high-kick.gif',
            'https://c.tenor.com/DYLiR4obvyAAAAAC/superman-ball.gif'
        ]

        embed = discord.Embed(
            title="__General Kick__",
            description=f"🦵 {self.member.mention} landed a majestic kick on {self.target.mention} 🦵",
            color=discord.Color.dark_purple(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(general_kicks))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Butt Kick', style=discord.ButtonStyle.blurple, custom_id='butt_kick_id', emoji="<a:peepoHonkbutt:757358697033760918>")
    async def butt_kick_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Kicks someone on the butt. """

        butt_kicks: List[str] = [
            'https://c.tenor.com/EkzVxMWJ3hgAAAAd/looney-tunes-elmer.gif',
            'https://c.tenor.com/lzeoLQIX-Q8AAAAd/bette-midler-danny-devito.gif',
            'https://c.tenor.com/7Etzg8KbgE0AAAAC/kick-butt-kick.gif',
            'https://c.tenor.com/q6pML2by038AAAAC/kick-in-the-butt-fly-away.gif',
            'https://c.tenor.com/HePCe_y82xYAAAAd/kick-ass.gif',
            'https://c.tenor.com/-JaZ46RC530AAAAd/elephant-kick.gif',
            'https://c.tenor.com/esCHs7tm78UAAAAC/spongebob-squarepants-get-out.gif',
            'https://c.tenor.com/Z3i_1Nyi99MAAAAd/kick-gif-angry.gif',
            'https://c.tenor.com/XtMM61RE0hwAAAAC/angry-gif.gif',
            'https://c.tenor.com/a9g3WrRNf24AAAAC/teddy-bear-kick.gif'
        ]

        embed = discord.Embed(
            title="__Butt Kick__",
            description=f"<a:peepoHonkbutt:757358697033760918> {self.member.mention} kicked {self.target.mention}'s butt <a:peepoHonkbutt:757358697033760918>",
            color=discord.Color.dark_purple(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(butt_kicks))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the hug action. """

        await self.disable_buttons(interaction)
        self.stop()

    async def disable_buttons(self, interaction: discord.Interaction, followup: bool = False) -> None:

        for child in self.children:
            child.disabled = True

        if followup:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.member.id == interaction.user.id

class SlapView(discord.ui.View):

    def __init__(self, client: commands.Cog, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.client = client
        self.member = member
        self.target = target


    @discord.ui.button(label='Angry Slap', style=discord.ButtonStyle.blurple, custom_id='angry_slap_id', emoji="<:zslothree:695411876581867610>")
    async def angry_slap_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Slaps someone in an angry way. """

        slaps: List[str] = [
            'https://c.tenor.com/3gXMa4UqiGgAAAAC/slap-slow-motion-slap.gif',
            'https://c.tenor.com/An1M1IByKBUAAAAC/slap-annoyed.gif',
            'https://c.tenor.com/aBXNFj2yXagAAAAC/kevin-hart-slap.gif'
        ]

        embed = discord.Embed(
            title="__Angry Slap__",
            description=f"<a:angry_sloth:737806820546052166> {self.member.mention} slapped {self.target.mention} <:zslothree:695411876581867610>",
            color=self.member.color,
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(slaps))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Sexy Slap', style=discord.ButtonStyle.blurple, custom_id='sexy_slap_id', emoji="<:creep:676070700951273491>")
    async def sexy_slap_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Slaps someone in a sexy way. """

        slaps: List[str] = [
            'https://c.tenor.com/-nt9Dj8Ei14AAAAd/tap-that.gif',
            'https://c.tenor.com/p4nJMjBtwIMAAAAC/cats-funny.gif',
            'https://c.tenor.com/wKKCNA6Ni-MAAAAC/cheh-t1-t1lose.gif'
        ]

        embed = discord.Embed(
            title="__Sexy Slap__",
            description=f"😏 {self.member.mention} slapped {self.target.mention} <:creep:676070700951273491>",
            color=self.member.color,
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(slaps))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        member_marriage = await self.client.get_cog('SlothClass').get_user_marriage(self.member.id)
        cheating_view = None
        if (partner := member_marriage['partner']) and self.target.id != partner:
            cheating_view = CheatingView(self.client, self.member, self.target, member_marriage)

        if cheating_view:
            await interaction.response.send_message(
                content=self.target.mention, embed=embed, 
                view=cheating_view
            )
        else:
            await interaction.response.send_message(
                content=self.target.mention, embed=embed)
            
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the slap action. """

        await self.disable_buttons(interaction)
        self.stop()

    async def disable_buttons(self, interaction: discord.Interaction, followup: bool = False) -> None:

        for child in self.children:
            child.disabled = True

        if followup:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.member.id == interaction.user.id

class KissView(discord.ui.View):

    def __init__(self, client: commands.Cog, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.client = client
        self.member = member
        self.target = target


    @discord.ui.button(label='Kiss on the Cheek', style=discord.ButtonStyle.blurple, custom_id='cheek_kiss_id', emoji="☺️")
    async def cheek_kiss_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Kisses someone on the cheek. """

        c_kisses: List[str] = [
            'https://c.tenor.com/gg9g7PNgXG8AAAAC/poke-cheek-kiss.gif',
            'https://c.tenor.com/jO_rdniHzDYAAAAC/logan-lerman-photoshoot.gif',
            'https://c.tenor.com/CvR5bB7ame4AAAAC/love-pat.gif',
            'https://c.tenor.com/h9A4bnxJys8AAAAC/cheek-kiss.gif',
            'https://c.tenor.com/73-1_tVGfg8AAAAC/lick-kiss.gif'
        ]

        embed = discord.Embed(
            title="__Cheek Kiss__",
            description=f"😗 {self.member.mention} cheek kissed {self.target.mention} 😗",
            color=discord.Color.red(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(c_kisses))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()
    
    @discord.ui.button(label='Mouth Kiss', style=discord.ButtonStyle.blurple, custom_id='mouth_kiss_id', emoji="💋")
    async def mouth_kiss_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Kisses someone on the mouth. """

        m_kisses: List[str] = [
            'https://c.tenor.com/sx0mJIjy61gAAAAC/milk-and-mocha-bear-couple.gif',
            'https://c.tenor.com/hK8IUmweJWAAAAAC/kiss-me-%D0%BB%D1%8E%D0%B1%D0%BB%D1%8E.gif',
            'https://c.tenor.com/Aaxuq2evHe8AAAAC/kiss-cute.gif',
            'https://c.tenor.com/A0ixOj7Y1WUAAAAC/kiss-anime.gif',
            'https://c.tenor.com/ErAPuiWY46QAAAAC/kiss-anime.gif'
        ]

        embed = discord.Embed(
            title="__Mouth Kiss__",
            description=f"😚💋 {self.member.mention} kissed {self.target.mention} on the mouth 😚💋",
            color=discord.Color.dark_red(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(m_kisses))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        member_marriage = await self.client.get_cog('SlothClass').get_user_marriage(self.member.id)
        cheating_view = None
        if (partner := member_marriage['partner']) and self.target.id != partner:
            cheating_view = CheatingView(self.client, self.member, self.target, member_marriage)

        if cheating_view:
            await interaction.response.send_message(
                content=self.target.mention, embed=embed, 
                view=cheating_view
            )
        else:
            await interaction.response.send_message(
                content=self.target.mention, embed=embed)
            
        await self.disable_buttons(interaction, followup=True)
        self.stop()


    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the slap action. """

        await self.disable_buttons(interaction)
        self.stop()


    async def disable_buttons(self, interaction: discord.Interaction, followup: bool = False) -> None:

        for child in self.children:
            child.disabled = True

        if followup:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.member.id == interaction.user.id


class CheatingView(discord.ui.View):

    def __init__(self, client, cheater: discord.Member, lover: discord.Member, marriage: Dict[str, Union[str, int]]):
        super().__init__(timeout=300)
        self.client = client
        self.cheater = cheater
        self.lover = lover
        self.marriage = marriage

    @discord.ui.button(label="Spot Cheating", style=discord.ButtonStyle.red, custom_id='cheating_id', emoji='<:pepeOO:572067085371572224>')
    async def spot_cheating_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Spots a cheating and prompts the user for an action. """

        catches: List[str] = [
            'https://c.tenor.com/JdcMIoNEIiQAAAAd/wow-oh-wow.gif',
            'https://c.tenor.com/GLZUkFLcqeQAAAAC/yawnface.gif',
            'https://c.tenor.com/QA6mPKs100UAAAAC/caught-in.gif',
            'https://c.tenor.com/MwSZE9vo12QAAAAC/caught-in.gif',
            'https://c.tenor.com/r32RUQV_Ph4AAAAC/got-caught-you-got-caught.gif',
            'https://c.tenor.com/uCU7zeq9f0sAAAAC/caught-jbtzxclsv.gif',
            'https://c.tenor.com/SpLyAIKkR5MAAAAC/bb12-big-brother12.gif',
            'https://c.tenor.com/uOMOHvke4xUAAAAC/you-wit-mate-funny.gif'
        ]

        embed = discord.Embed(
            title="__I Caught You!__",
            description=f"<:tony:686282295141072950> <@{self.marriage['partner']}> caught {self.cheater.mention} cheating on them with {self.lover.mention} <:tony:686282295141072950>",
            color=discord.Color.dark_red(),
            timestamp=interaction.message.created_at
        )

        partner = await interaction.guild.fetch_member(self.marriage['partner'])
        embed.set_author(name=partner.display_name, url=partner.avatar.url, icon_url=partner.avatar.url)
        embed.set_thumbnail(url=self.lover.avatar.url)
        embed.set_image(url=choice(catches))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        view = CheatingActionView(self.client, self.cheater, self.lover, self.marriage)

        await interaction.response.send_message(content=self.cheater.mention, embed=embed, view=view)


    async def disable_buttons(self, interaction: discord.Interaction, followup: bool = False) -> None:

        for child in self.children:
            child.disabled = True

        if followup:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.marriage['partner'] == interaction.user.id



class CheatingActionView(discord.ui.View):

    def __init__(self, client, cheater: discord.Member, lover: discord.Member, marriage: Dict[str, Union[str, int]]):
        super().__init__(timeout=60)
        self.client = client
        self.cheater = cheater
        self.lover = lover
        self.marriage = marriage
        self.sloth_class = client.get_cog('SlothClass')

    @discord.ui.button(label="Forgive", style=discord.ButtonStyle.green, custom_id='forgive_id', emoji='<:zslothcow:870057897718079558>')
    async def forgive_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Forgives the betrayal. """

        forgives: List[str] = [
            'https://c.tenor.com/bibl6p_LwSwAAAAC/forgiven-iforgiveyou.gif',
            'https://c.tenor.com/nm2tdIZoBlAAAAAC/vagrant-queen-syfy.gif',
            'https://c.tenor.com/PlIHEkBGuzwAAAAC/forgiven-benedict-townsend.gif',
            'https://c.tenor.com/IaKaFPa63aMAAAAd/all-can-be-forgiven-bricky.gif',
            'https://c.tenor.com/ZzpBrs9XNe4AAAAC/john-de-lancie-the-q.gif',
            'https://c.tenor.com/iu01f1INoxUAAAAC/forgive-sherlock.gif',
            'https://c.tenor.com/SbH68O5P73sAAAAC/its-okay-joseph-gordon-levitt.gif'
        ]

        embed = discord.Embed(
            title="__That Sin has been Forgiven!__",
            description=f"<:zslotheyesrolling:688071367505215560> <@{self.marriage['partner']}> has forgiven {self.cheater.mention} for cheating on them <:zslotheyesrolling:688071367505215560>",
            color=discord.Color.green(),
            timestamp=interaction.message.created_at
        )

        partner = await interaction.guild.fetch_member(self.marriage['partner'])

        embed.set_author(name=partner.display_name, url=partner.avatar.url, icon_url=partner.avatar.url)
        embed.set_thumbnail(url=self.lover.avatar.url)
        embed.set_image(url=choice(forgives))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.cheater.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)

    @discord.ui.button(label="Force divorce", style=discord.ButtonStyle.red, custom_id='divorce_id', emoji='<:zslothtoxic:695420110420312125>')
    async def force_divorce_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Force-divorces the partner, making them pay the divorce cost. """

        divorces: List[str] = [
            'https://c.tenor.com/lNBksxJBJdUAAAAC/divorce-bye.gif',
            'https://c.tenor.com/6qcBNvYNX8IAAAAd/borkybepis-adus.gif',
            'https://c.tenor.com/lzeoLQIX-Q8AAAAd/bette-midler-danny-devito.gif',
            'https://c.tenor.com/KlOTwe1onr8AAAAC/lets-get-a-divorce-divorce.gif',
            'https://c.tenor.com/5fw1ga-D8mEAAAAC/its-over-scrubs.gif',
            'https://c.tenor.com/YpW23O0lyF8AAAAC/laughing-funny.gif',
            'https://c.tenor.com/V1FtFCYeMZQAAAAd/divorce-divorce-you.gif'
        ]

        embed = discord.Embed(
            title="__That Sin cannot be Forgiven!__",
            description=f"<:wrong:735204715415076954> <@{self.marriage['partner']}> didn't forgive {self.cheater.mention}'s betrayal and force-divorced them, making them pay for the divorce cost. They broke up! <:wrong:735204715415076954>",
            color=discord.Color.dark_red(),
            timestamp=interaction.message.created_at
        )

        partner = await interaction.guild.fetch_member(self.marriage['partner'])

        embed.set_author(name=partner.display_name, url=partner.avatar.url, icon_url=partner.avatar.url)
        embed.set_thumbnail(url=self.lover.avatar.url)
        embed.set_image(url=choice(divorces))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        # Updates marital status and subtracts the cheater's money
        try:
            await self.sloth_class.delete_skill_action_by_target_id_and_skill_type(partner.id, skill_type='marriage')
            await self.sloth_class.delete_skill_action_by_user_id_and_skill_type(partner.id, skill_type='marriage')
            await self.sloth_class.update_user_money(self.cheater.id, -500)
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"**Something went wrong with it, {partner.mention}!**")
        else:
            await interaction.response.send_message(content=self.cheater.mention, embed=embed)
        finally:
            await self.disable_buttons(interaction, followup=True)

    @discord.ui.button(label="Knock 'em out!", style=discord.ButtonStyle.gray, custom_id='ko_id', emoji='<a:zslothgiveme:709909994203512902>')
    async def knock_out_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Beats and knocks-your partner out, so they rethink before cheating on you again. """

        partner_id = self.marriage['partner']
        embed = await self.sloth_class.get_hit_embed(interaction.channel, partner_id, self.cheater.id)

        current_ts = await utils.get_timestamp()
        try:
            await self.sloth_class.insert_skill_action(
                user_id=partner_id, skill_type="hit", skill_timestamp=current_ts,
                target_id=self.cheater.id, channel_id=interaction.channel_id
            )
        except:
            await interaction.response.send_message(f"**Something went wrong with it, <@{partner_id}>!**")
        else:
            await interaction.response.send_message(content=self.cheater.mention, embed=embed)
        finally:
            await self.disable_buttons(interaction, followup=True)


    async def disable_buttons(self, interaction: discord.Interaction, followup: bool = False) -> None:

        for child in self.children:
            child.disabled = True

        if followup:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.marriage['partner'] == interaction.user.id



class HoneymoonView(discord.ui.View):

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target
        self.value = None
        self.embed: discord.Embed = None

        self.place: Dict[str, Dict[str, str]] = {}
        self.activity: Dict[str, Dict[str, str]] = {}

        self.current_place: Dict[str, Dict[str, str]] = None
        self.places: Dict[str, Dict[str, str]] = self.get_places()

        options = [
            discord.SelectOption(label=place, description=values['description'], emoji=values['emoji'])
            for place, values in self.places.items()]

        places_select = discord.ui.Select(placeholder="Where do you wanna go to?",
        custom_id="honeymoon_id", min_values=1, max_values=1, options=options)

        places_select.callback = partial(self.place_to_go_button, places_select)

        self.children.insert(0, places_select)

    def get_places(self) -> Dict[str, Dict[str, str]]:
        data = {}
        with open('./extra/slothclasses/places.json', 'r', encoding="utf-8") as f:
            data = json.loads(f.read())
        return data

    async def place_to_go_button(self, select: discord.ui.select, interaction: discord.Interaction) -> None:
        """ Handles the selected option for the member's honeymoon spot. """

        embed = interaction.message.embeds[0]
        selected_item = interaction.data['values'][0]
        place = self.places.get(selected_item)
        self.current_place = place

        if url := place.get('url'):
            embed.set_image(url=url)

        self.activities_to_do_button.disabled = False
        self.activities_to_do_button.options = [
            discord.SelectOption(label=activity, emoji="🎉") for activity in place['activities']
        ]

        self.place = place
        embed.clear_fields()
        embed.add_field(name=f"__Place:__ {selected_item}", value=place['description'], inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)


    @discord.ui.select(placeholder="Select an activity to do there.", custom_id="activity_id", disabled=True, row=1, options=[
        discord.SelectOption(label="I'm a placeholder", value="no")
    ])
    async def activities_to_do_button(self, select: discord.ui.select, interaction: discord.Interaction) -> None:
        """ Handles the selected option for the member's honeymoon spot. """

        embed = interaction.message.embeds[0]
        selected_item = interaction.data['values'][0]

        place = self.current_place
        activity = place['activities'][selected_item]
        self.activity = activity

        if url := activity.get('url'):
            embed.set_thumbnail(url=url)
        else:
            embed.set_thumbnail(url='https://i.pinimg.com/originals/87/35/53/873553eeb255e47b1b4b440e4302e17f.gif')

        embed.remove_field(1)
        embed.add_field(name=f"__Activity:__", value=selected_item, inline=False)
        
        await interaction.response.edit_message(embed=embed)


    @discord.ui.button(label='Go to Honeymoon!', style=discord.ButtonStyle.blurple, custom_id='hug_id', emoji="🍯", row=2)
    async def honeymoon_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:

        member = interaction.user

        if not self.place:
            return await interaction.response.send_message(f"You need to select a place, {member.mention}", ephemeral=True)

        if not self.activity:
            return await interaction.response.send_message(f"You need to select an activity, {member.mention}", ephemeral=True)

        self.value = True
        self.embed = interaction.message.embeds[0]
        await self.disable_buttons(interaction)
        self.stop()


    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌", row=2)
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the slap action. """

        self.value = False

        await self.disable_buttons(interaction)
        self.stop()


    async def disable_buttons(self, interaction: discord.Interaction, followup: bool = False) -> None:

        for child in self.children:
            child.disabled = True

        if followup:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.member.id == interaction.user.id


class PunchView(discord.ui.View):

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Punch Face', style=discord.ButtonStyle.blurple, custom_id='punch_face_id', emoji="👊")
    async def punch_face_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Punches someone in the face. """

        face_punches: List[str] = [
            'https://c.tenor.com/-dK24mwTyKwAAAAC/tv-shows-supernatural.gif',
            'https://c.tenor.com/7JVff7vMCVkAAAAC/face-punch-punch.gif',
            'https://c.tenor.com/fGAET2FAoo4AAAAC/nice-punch-in-the-face.gif',
            'https://c.tenor.com/vmVpJSYqBG0AAAAC/punch-in.gif',
            'https://c.tenor.com/il5bBmkDl88AAAAC/punch-face.gif',
            'https://c.tenor.com/-5LK7k-ZwScAAAAC/machi-bunny.gif',
            'https://c.tenor.com/zVecK1PLcXwAAAAC/face-punch.gif',
            'https://c.tenor.com/6yellz_5L0gAAAAC/emma-roberts-chanel-oberlin.gif',
            'https://c.tenor.com/-xdO8DGiLKgAAAAC/hit-punch.gif',
            'https://c.tenor.com/HgsdyL6Uvc0AAAAC/punch-in-your-face.gif'
        ]

        embed = discord.Embed(
            title="__Punch Face__",
            description=f"👊 {self.member.mention} punched {self.target.mention} in the face, right in the bull's eyes! 👊",
            color=discord.Color.dark_teal(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(face_punches))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Punch Throat', style=discord.ButtonStyle.blurple, custom_id='throat_punch_id', emoji="<:zsimpysloth:737321065662906389>")
    async def punch_throat_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Punches someone in the face. """

        throat_punches: List[str] = [
            'https://c.tenor.com/Io4G6owWrbcAAAAC/throat-punch-identity-thief.gif',
            'https://c.tenor.com/1I3eQKMos60AAAAd/throat-punch-punch-in-the-throat.gif',
            'https://c.tenor.com/SUdP1RlArSsAAAAC/punch-in-the-throat-becky-lynch.gif',
            'https://c.tenor.com/rt20YcF6lrgAAAAC/cindy-salmon-throat-punch.gif',
            'https://c.tenor.com/Qj7KR47o7hYAAAAC/paraisopolis-punch.gif',
            'https://c.tenor.com/Nh9RmNtX2A8AAAAC/throat-punch-the-hardy-bucks.gif',
            'https://c.tenor.com/zwOfGyvEi2cAAAAC/punch-neck.gif',
            'https://c.tenor.com/LBYkRjujBfIAAAAC/becky-lynch.gif'
        ]

        embed = discord.Embed(
            title="__Punch Throat__",
            description=f"<:zsimpysloth:737321065662906389> {self.member.mention} punched {self.target.mention} in the throat <:zsimpysloth:737321065662906389>",
            color=discord.Color.dark_teal(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(throat_punches))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Uppercut', style=discord.ButtonStyle.blurple, custom_id='uppercut_id', emoji="💪")
    async def uppercut_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Gives someone an uppercut in the face. """

        uppercuts: List[str] = [
            'https://c.tenor.com/tzSoBm8TvbQAAAAC/punch-godzilla.gif',
            'https://c.tenor.com/CxwPJZ9wgggAAAAC/anime-uppercut.gif',
            'https://c.tenor.com/kFL3iEag_60AAAAC/azumanga-daioh-azumanga.gif',
            'https://c.tenor.com/RpOAc1a4oaQAAAAd/cesaro-uppercut.gif',
            'https://c.tenor.com/zfKYZkbGuecAAAAd/hajime-no-ippo-ippo.gif',
            'https://c.tenor.com/IMnY5rH7m3UAAAAC/%E0%B9%82%E0%B8%94%E0%B8%99%E0%B8%95%E0%B9%88%E0%B8%AD%E0%B8%A2-%E0%B8%81%E0%B8%AD%E0%B8%A5%E0%B9%8C%E0%B8%9F.gif',
            'https://c.tenor.com/VkByZU-h2QMAAAAC/donkey-kong-uppercut-donkey-kong.gif',
            'https://c.tenor.com/OgjecYD39HEAAAAC/usyk-uppercut.gif',
            'https://c.tenor.com/4z26A7YW15EAAAAd/strong-heavy-punch.gif',
            'https://c.tenor.com/WZI35DJcOucAAAAC/mike-tyson-punch.gif'
        ]

        embed = discord.Embed(
            title="__Punch Face__",
            description=f"💪 {self.member.mention} blew a fabulous uppercut on {self.target.mention}'s chin 💪",
            color=discord.Color.dark_teal(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(uppercuts))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Punch Stomach', style=discord.ButtonStyle.blurple, custom_id='punch_stomach_id', emoji="<:eau:875729754215571487>")
    async def punch_stomach_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Punches someone in the stomach. """

        stomach_punches: List[str] = [
            'https://c.tenor.com/CLj5PsMhCLkAAAAC/naruto-sasuke.gif',
            'https://c.tenor.com/fIrHXnCVQugAAAAC/punch-belly.gif',
            'https://c.tenor.com/LE7zzsWtHfgAAAAC/punch-in-the-guts-punching.gif',
            'https://c.tenor.com/WzXRQw6pPRoAAAAC/punch-jab.gif',
            'https://c.tenor.com/fGD_kutTO20AAAAC/goku-punch.gif',
            'https://c.tenor.com/N1a51WnErtUAAAAC/gut-punch.gif',
            'https://c.tenor.com/WWitSk2MYI0AAAAd/hulk-giganto.gif',
            'https://c.tenor.com/SJcivTfdcmkAAAAd/megatron-gut-punch.gif',
            'https://c.tenor.com/yddbbkaUQFYAAAAC/punch-sucker-punch.gif',
            'https://c.tenor.com/E7i694cxM6wAAAAC/shrek-punch.gif'   
        ]

        embed = discord.Embed(
            title="__Punch Stomach__",
            description=f"<:eau:875729754215571487> {self.member.mention} punched {self.target.mention} in the stomach <:eau:875729754215571487>",
            color=discord.Color.dark_teal(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(stomach_punches))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Punchline', style=discord.ButtonStyle.gray, custom_id='punchline_id', emoji="<:I_smell_your_sins:666322848922599434>")
    async def punchline_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Punches, a line. """

        punchlines = {}
        with open('./extra/slothclasses/punchlines.json', 'r', encoding="utf-8") as f:
            punchlines = json.loads(f.read())

        punchline_images: List[str] = [
            'https://c.tenor.com/lyILvkdNTB0AAAAC/willem-dafoe-laugh.gif',
            'https://c.tenor.com/ecAzU-fj7LEAAAAC/crazy-jim-carrey.gif',
            'https://c.tenor.com/yGhUqB860GgAAAAC/worriedface.gif',
            'https://c.tenor.com/wIxFiobxxbIAAAAd/john-jonah-jameson-lol.gif',
            'https://c.tenor.com/UAynAquzjogAAAAC/spit-take.gif',
            'https://c.tenor.com/Sca0lXAwijYAAAAC/laughing-giggle.gif',
            'https://c.tenor.com/QOXAGHah7MEAAAAC/bilelaca-laugh.gif',
            'https://c.tenor.com/JCYLRqm7oyIAAAAd/trying-not-to-laugh-zoom-in.gif',
            'https://c.tenor.com/rmtvkkGm7xYAAAAC/laugh-cant-hold-it-in.gif',
            'https://c.tenor.com/s1Pu2LSTV7YAAAAd/wtf-laugh.gif'
        ]

        embed = discord.Embed(
            title="__Punch Face__",
            description=f"<:I_smell_your_sins:666322848922599434> {self.member.mention} just told {self.target.mention} a questionable joke:\n\n***** {choice(list(punchlines.values()))} <:I_smell_your_sins:666322848922599434>",
            color=discord.Color.dark_purple(),
            timestamp=interaction.message.created_at,
            url='https://thoughtcatalog.com/january-nelson/2018/12/69-punchlines-so-stupid-they-are-actually-funny/'
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(punchline_images))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the hug action. """

        await self.disable_buttons(interaction)
        self.stop()

    async def disable_buttons(self, interaction: discord.Interaction, followup: bool = False) -> None:

        for child in self.children:
            child.disabled = True

        if followup:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.member.id == interaction.user.id
