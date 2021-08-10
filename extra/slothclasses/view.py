import discord
from discord.ext import commands
from typing import Optional, List, Dict, Union
from random import choice
from extra import utils
from functools import partial

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
            description=f"🦵 {self.member.mention} landed a magestic kick on {self.target.mention} 🦵",
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

        self.places: Dict[str, Dict[str, str]] = {
            "St. Lucia": {
                "value": "St. Lucia",
                "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbIODnrv3_2VO-oAfpp9vgKfufdNUFwvs864eEUKHhA8jVeqRlsk3YkGCGniE83SVpxoU&usqp=CAU",
                "description": "If you're seeking a luxurious Caribbean honeymoon, look no further than St. Lucia.", "emoji": "⛰️"},
            "Bora Bora": {
                "value": "Bora Bora",
                "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoRXIc9H14Wt9ch6OGrp3Ym0rDXwSaMOv13h84fXRhvGf1gJ-QQNeUQnAf2z2duY7AK_w&usqp=CAU",
                "description": "Bora Bora's jaw-dropping scenery is just the tip of the iceberg – or, rather, the volcano.", "emoji": "⛰️"},
            "Maldives": {
                "value": "Maldives",
                "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJT6FRG4GdWt1HkpyIM9UXIXql-0OrRbXu1JS1qsii2jYlB7qKbBVfv73Q5rZQR6qezPs&usqp=CAU",
                "description": "If you and your sweetheart truly want to get away from it all, head to the Maldives.", "emoji": "🤿"},
            "Fiji": {
                "value": "Fiji",
                "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHBvj2ujzvF8NUL70ZmHj2jmgCxmngNN5cQrSO49-EN0Uf6T3ARGlWhXp-aUjcmg2mVr4&usqp=CAU",
                "description": "Fiji's serene beaches offer complete seclusion for postnuptial relaxation", "emoji": "🛖"},
            "Maui": {
                "value": "Maui",
                "url": "https://www.visiteosusa.com.br/sites/default/files/styles/16_9_1280x720/public/2016-10/Getty_520143072_Brand_City_Maui_Hero_FinalCrop.jpg?itok=0dFZb9Z6",
                "description": "Jungles to explore, volcanoes to tour and trails to hike, the Hawaiian island of Maui is a must.", "emoji": "🌴"},
            "Amalfi Coast": {
                "value": "Amalfi Coast",
                "url": "https://res.cloudinary.com/dsmafmqwi/image/upload/c_fill,f_auto,h_1280,q_auto/v1/virtualtrips/locations/azeqdfwgqi39hakenk1q",
                "description": "The Amalfi Coast's colorful villages, crystal-clear water and rugged shoreline are a perfect match.", "emoji": "🌅"},
            "Bali": {
                "value": "Bali",
                "url": "https://www.costacruzeiros.com/content/dam/costa/costa-magazine/articles-magazine/travel/bali-travel/bali_m.jpg.image.694.390.low.jpg",
                "description": "Towering volcanoes and stone temples provide an unforgettable backdrop for any honeymoon vacation.", "emoji": "⛱️"},
            "Tahiti": {
                "value": "Tahiti",
                "url": "https://ganeshturismo.com.br/wp-content/uploads/2019/08/pacotes-de-viagem-tahiti.jpg",
                "description": "French Polynesia's largest island is just as romantic as more popular honeymoon locales.", "emoji": "🛳️"},
            "Santorini": {
                "value": "Santorini",
                "url": "https://www.costacruzeiros.com/content/dam/costa/costa-magazine/article-images/things-to-do-in-santorini/santorini-cosa-vedere1.jpg.image.694.390.low.jpg",
                "description": "Known for its brilliant sunsets, rich Greek food & romantic hotels. Almost tailor-made for newlyweds", "emoji": "🏖️"},
            "Kauai": {
                "value": "Kauai",
                "url": "https://www.gohawaii.com/sites/default/files/styles/image_gallery_bg_xl/public/hero-unit-images/Napali_0_1.jpg?itok=S0scQXWt",
                "description": "This Hawaiian island offers luxury resorts and secluded stretches of sand for any kind of couple.", "emoji": "⛰️"},
            "Hawaii": {
                "value": "Hawaii",
                "url": "https://www.costacruzeiros.com/content/dam/costa/costa-magazine/articles-magazine/islands/hawaii-island/hawaii_m.jpg.image.694.390.low.jpg",
                "description": "Hawaii's Big Island can offer you a relaxing honeymoon or one filled with adventure.", "emoji": "🌋"},
            "Mauritius": {
                "value": "Mauritius",
                "url": "https://dbui4lb3qzbcx.cloudfront.net/imagens/611a829010cce7484e24dfc9d9d18674.jpeg",
                "description": "Mauritius turquoise waters, abundant wildlife & luxe resorts make it an ideal choice for newlyweds.", "emoji": "🌅"},
            "Florence": {
                "value": "Florence",
                "url": "https://lp-cms-production.imgix.net/2019-06/GettyImages-174463015_high.jpg",
                "description": "Florence, Italy, is a city renowned for its art, history and mouthwatering Italian cuisine", "emoji": "🕌"},
            "Paris": {
                "value": "Paris",
                "url": "https://veja.abril.com.br/wp-content/uploads/2016/05/alx_lista-capitais-europa-mundo-20100806-002_original3.jpeg",
                "description": "Newlyweds travel to the City of Light for the ultimate experience in sophistication and romance.", "emoji": "<:toureiffel:716592371583942676>"},
            "Phuket": {
                "value": "Phuket",
                "url": "https://www.costacruzeiros.com/content/dam/costa/costa-magazine/articles-magazine/islands/phuket-island/phuket_m.jpg.image.694.390.low.jpg",
                "description": "White sand beaches, and abundance of cultural sites. A great choice for adventure and relaxation.", "emoji": "🏞️"},
            "Cinque Terre": {
                "value": "Cinque Terre",
                "url": "https://img.itinari.com/pages/images/original/6ec803a9-2376-44b7-8b92-8347dccad652-istock-610863516.jpg?ch=DPR&dpr=1&w=1600&s=38b3f7002a442e612563308e36b0ff80",
                "description": "Northwestern Italy remote coastal region featuring beaches more suitable for sunbathing & swimming.", "emoji": "🛶"},
            "St. Barts": {
                "value": "St. Barts",
                "url": "https://media-cdn.tripadvisor.com/media/photo-s/1c/df/23/29/eden-rock-lifestyle.jpg",
                "description": "The French Caribbean island of St. Barts offers chic hotels and bistros in a laid-back setting.", "emoji": "⛵"},
            "Tuscany": {
                "value": "Tuscany",
                "url": "https://www.pandotrip.com/wp-content/uploads/2018/07/Amazing-landscape-of-Val-d%E2%80%99Orcia-Tuscany-Italy.jpg",
                "description": "From luxury villas to aromatic cuisine, Italy's countryside teems with romance.", "emoji": "🏘️"},
            "British Virgin Islands": {
                "value": "British Virgin Islands",
                "url": "https://travel.home.sndimg.com/content/dam/images/travel/fullrights/2018/4/19/0/CI_BVI_Tourist_Board-Scrub-Island-Resort-Dusk.jpg.rend.hgtvcom.966.644.suffix/1524159978953.jpeg",
                "description": "For newlyweds who dream of spending their days on the water and their nights in a high-end hotel.", "emoji": "⛵"},
            "Lake Como": {
                "value": "Lake Como",
                "url": "https://images.contentstack.io/v3/assets/blt00454ccee8f8fe6b/blt5508c8547b26bd6d/606faf3dd8743426b393ea62/US_LakeComo_IT_Header.jpg",
                "description": "Attractive and stunning lake setting located in northern Italy about 50 miles north of Milan.", "emoji": "🗻"}
            
        }

        options = [
            discord.SelectOption(label=place, description=values['description'], emoji=values['emoji'])
            for place, values in self.places.items()]

        places_select = discord.ui.Select(placeholder="Where do you wanna go to?",
        custom_id="honeymoon_id", min_values=1, max_values=1, options=options)

        places_select.callback = partial(self.place_to_go_button, places_select)

        self.children.insert(0, places_select)



    async def place_to_go_button(self, select: discord.ui.select, interaction: discord.Interaction) -> None:
        """ Handles the selected option for the member's honeymoon spot. """

        embed = interaction.message.embeds[0]
        selected_item = interaction.data['values'][0]
        place = self.places.get(selected_item)
        if place:
            embed.set_image(url=place['url'])
        embed.clear_fields()
        embed.add_field(name=f"__Place:__ {selected_item}", value=place['description'])
        
        await interaction.response.edit_message(embed=embed)


    @discord.ui.button(label='Go to Honeymoon!', style=discord.ButtonStyle.blurple, custom_id='hug_id', emoji="🍯", row=1)
    async def honeymoon_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:


        value = True
        await self.disable_buttons(interaction)
        self.stop()


    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌", row=1)
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the slap action. """

        value = False

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
