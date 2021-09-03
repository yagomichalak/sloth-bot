import discord
from discord.ext import commands
from typing import Optional, List, Dict, Union
from random import choice
from extra import utils
from functools import partial
import json

class HugView(discord.ui.View):
    """ View for the hug skill. """

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
    """ View for the boot skill. """

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
        """ Cancels the kick action. """

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
    """ View for the slap skill. """

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
            'https://c.tenor.com/wKKCNA6Ni-MAAAAC/cheh-t1-t1lose.gif',
            'https://c.tenor.com/bOERuBKmDSoAAAAC/michael-jackson-sexy.gif',
            'https://c.tenor.com/PHTpoMvPk_EAAAAC/ass-slap-slap.gif',
            'https://c.tenor.com/WgHlS-sXVHIAAAAC/tinkerbell-spank.gif',
            'https://c.tenor.com/9DZ7tx1JATkAAAAC/happy-bunny-pig.gif',
            'https://c.tenor.com/eS3xAaYHDeMAAAAC/ass-ass-slap.gif',
            'https://c.tenor.com/CyczLT_QsPIAAAAC/hobo-bros-sexy.gif',
            'https://c.tenor.com/13Tuskb4T8EAAAAC/elizabeth-olsen-aubrey-plaza.gif',
            'https://c.tenor.com/YIWoKVWn3FUAAAAC/happy-spank.gif',
            'https://c.tenor.com/bHE5Txlp5-8AAAAC/slap-butts-anime.gif',
            'https://c.tenor.com/2o9uTHxpw3UAAAAC/punishment-beat-ass.gif',
            'https://c.tenor.com/Zl2DQ6lc2-gAAAAC/slap-butt-naughty.gif',
            'https://c.tenor.com/oUwdLFkrzaMAAAAd/walrus-slaps.gif',
            'https://c.tenor.com/H3lLTaQZRuwAAAAC/butt-slap-adventure-time.gif'

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
    """ View for the kiss skill. """

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
            'https://c.tenor.com/ErAPuiWY46QAAAAC/kiss-anime.gif',
            'https://c.tenor.com/4GdkzkTQdI8AAAAC/kissing-love.gif',
            'https://c.tenor.com/lsOkG57_ibIAAAAd/kiss-lip-kiss.gif',
            'https://c.tenor.com/uF0-jdZRkLYAAAAC/kissing-kiss.gif',
            'https://c.tenor.com/3kvvlXjRse0AAAAC/kiss-lip-kiss.gif',
            'https://c.tenor.com/RZEZVjS3MeMAAAAC/forcibly-kissing-deep-kiss.gif',
            'https://c.tenor.com/teTesMTK_c4AAAAC/shiksha-wedding.gif',
            'https://c.tenor.com/RrUKz9kC3bUAAAAi/dovey-bunnies-kisses.gif',
            'https://c.tenor.com/FDcq03ZLNX0AAAAi/love-couple.gif',
            'https://c.tenor.com/LbOTuZXj9y4AAAAC/cat-love.gif',
            'https://c.tenor.com/OhTr6EO7u14AAAAC/love-you-kiss.gif',
            'https://c.tenor.com/xTSmPl72UjYAAAAC/kiss-blushing.gif',
            'https://c.tenor.com/Gr8BaRWOudkAAAAC/brown-and-cony-kiss.gif',
            'https://c.tenor.com/uhB9b3AzxrQAAAAC/brown.gif',
            'https://c.tenor.com/cK2c6eQ7Is8AAAAC/cony-and-brown-hug.gif',
            'https://c.tenor.com/sXNJMF5vI8oAAAAC/love-peachcat.gif',
            'https://c.tenor.com/MXd8Xby7jnMAAAAC/davydoff-love.gif',
            'https://c.tenor.com/yWGhrAd0cioAAAAC/kissing-couple.gif'

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
    """ View for the spot cheating feature. """

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
    """ View for the cheating spotted feature. """

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
    """ View for the honeymoon skill. """

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
    """ View for the punch skill. """

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
            description=f"👊 {self.member.mention} punched {self.target.mention} in the face, right in the bull's-eye! 👊",
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
            title="__Uppercut__",
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
            title="__Punchline__",
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
        """ Cancels the punch action. """

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


class GiveView(discord.ui.View):
    """ View for the give skill. """

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target

        self.foods: Dict[str, Dict[str, str]] = self.get_foods()

        options = [
            discord.SelectOption(label=food, emoji=values['emoji'])
            for food, values in self.foods.items()]

        foods_select = discord.ui.Select(placeholder="What do you wanna give them?",
        custom_id="give_select_id", min_values=1, max_values=1, options=options)

        foods_select.callback = partial(self.give_button, foods_select)

        self.children.insert(0, foods_select)

    def get_foods(self) -> Dict[str, Dict[str, str]]:
        data = {}
        with open('./extra/slothclasses/foods.json', 'r', encoding="utf-8") as f:
            data = json.loads(f.read())
        return data

    async def give_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Gives someone something. """


        selected = interaction.data['values'][0]
        option = self.foods[selected]

        embed = discord.Embed(
            title=f"__{option['name']}__",
            description=f"{option['emoji']} {option['sentence']} {option['emoji']}".format(member=self.member, target=self.target),
            color=discord.Color.magenta(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(option['gifs']))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nothing', style=discord.ButtonStyle.red, custom_id='nothing_id', emoji="❌", row=2)
    async def nothing_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the give action. """

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


class TickleView(discord.ui.View):
    """ View for the tickle skill. """

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Tickle', style=discord.ButtonStyle.blurple, custom_id='tickle_id', emoji="<:zslothlmao:686697712074490055>")
    async def tickle_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Tickles someone. """

        tickles: List[str] = [
            'https://c.tenor.com/PXL1ONAO9CEAAAAC/tickle-laugh.gif',
            'https://c.tenor.com/nl5AkvIm4GoAAAAC/tickle-feet.gif',
            'https://c.tenor.com/Adn9UkNqEtwAAAAC/tickling-tickle.gif',
            'https://c.tenor.com/Og-eJJHrT_0AAAAC/kid-baby.gif',
            'https://c.tenor.com/iUM413zNYrEAAAAC/tickling-couple.gif',
            'https://c.tenor.com/78fdLe3dNdUAAAAd/francisco-tickled-tickle-torture.gif',
            'https://c.tenor.com/lif_b3wnZZ4AAAAC/spongebob-squidward.gif',
            'https://c.tenor.com/c_UdaYn6VYoAAAAd/tickle-tickling.gif',
            'https://c.tenor.com/d2C6eS9nUUIAAAAC/blue-bugcat.gif',
            'https://c.tenor.com/x_I7TZjIRlQAAAAC/teddy-bear-tickle.gif'
        ]

        embed = discord.Embed(
            title="__Tickling__",
            description=f"<:zslothlmao:686697712074490055> {self.member.mention} tickled {self.target.mention} <:zslothlmao:686697712074490055>",
            color=discord.Color.dark_gray(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(tickles))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the tickling action. """

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

class YeetView(discord.ui.View):
    """ View for the yeet skill. """

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Something', style=discord.ButtonStyle.blurple, custom_id='yeet_something_id', emoji="🤾‍♂️")
    async def yeet_something_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Yeets something at someone. """

        yeets: List[str] = [
            'https://c.tenor.com/WLb6BqWpdM8AAAAd/ball-throw.gif',
            'https://c.tenor.com/ZaVIDZ0qKa8AAAAC/mad-throw.gif',
            'https://c.tenor.com/9bbuTshmG60AAAAC/nice-throw-radio.gif',
            'https://c.tenor.com/e89L3JtrLbgAAAAd/rage-i-quit.gif',
            'https://c.tenor.com/GiaMbnaK00YAAAAC/guy-throwing-trash-can-at-someone.gif',
            'https://c.tenor.com/iokjb-fPg9MAAAAi/machiko-rabbit.gif',
            'https://c.tenor.com/18DiP6FCXvwAAAAC/shoe-throw.gif',
            'https://c.tenor.com/V_s9qJt0kM4AAAAC/stitch-throw.gif'
        ]

        embed = discord.Embed(
            title="__Yeet!__",
            description=f"🤾‍♂️ {self.member.mention} yeeted something at {self.target.mention} 🤾‍♂️",
            color=discord.Color.fuchsia(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(yeets))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Someone', style=discord.ButtonStyle.blurple, custom_id='yeet_someone_id', emoji="<:ytho:738497432693899275>")
    async def yeet_someone_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Yeets someone; your target. """

        yeets: List[str] = [
            'https://c.tenor.com/lNBksxJBJdUAAAAC/divorce-bye.gif',
            'https://c.tenor.com/VtA1UeS5LiYAAAAC/couple-pissed.gif',
            'https://c.tenor.com/Ia58SdP_5MIAAAAC/lion-king-toss.gif',
            'https://c.tenor.com/EkQS-yDvuw4AAAAC/pool-throw.gif',
            'https://c.tenor.com/mAEWXuWQqkkAAAAC/wtf-is.gif',
            'https://c.tenor.com/Eqzbcyujjw0AAAAd/throw-child-throw-kid.gif',
            'https://c.tenor.com/xrFSa7f68XAAAAAC/anime-throw.gif',
            'https://c.tenor.com/I3oebKLZ6m4AAAAd/hulk-angry.gif',
            'https://c.tenor.com/eF9c4AaclvIAAAAC/link-pig.gif',
            'https://c.tenor.com/fihwHmmeW0QAAAAC/rude-cat-throw.gif',
            'https://c.tenor.com/gISSJc70lH4AAAAC/yeet-naruto.gif',
            'https://c.tenor.com/mlMJ08Y5-BcAAAAC/see-ya-ya-yeet.gif',
            'https://c.tenor.com/yhz79wkknsYAAAAd/yeet-cat.gif'

        ]

        embed = discord.Embed(
            title="__Yeet!__",
            description=f"<:ytho:738497432693899275> {self.member.mention} yeeted {self.target.mention} <:ytho:738497432693899275>",
            color=discord.Color.fuchsia(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(yeets))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the yeet action. """

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

class BegView(discord.ui.View):
    """ View for the beg skill. """

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Beg', style=discord.ButtonStyle.blurple, custom_id='beg_id', emoji="🙏")
    async def beg_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Begs to someone. """

        begs: List[str] = [
            'https://c.tenor.com/q0_DMRk8Sj4AAAAC/please-liz-lemon.gif',
            'https://c.tenor.com/vsEiQ8Y3SQIAAAAd/please-sir-i-want-some-more.gif',
            'https://c.tenor.com/6KWWOtjSg0cAAAAC/milk-and-mocha-please.gif',
            'https://c.tenor.com/qrG--zXkCbEAAAAC/beg-gautam-gulati.gif',
            'https://c.tenor.com/7mMi6D1sCVYAAAAC/puss-in-boots-cat.gif',
            'https://c.tenor.com/0Ik1bWBf320AAAAC/cat-please-please.gif',
            'https://c.tenor.com/bWORgu_eREwAAAAC/pretty-please-prettyy-pleasee.gif',
            'https://c.tenor.com/LiHM-ToVoQEAAAAC/simpsons-beg.gif',
            'https://c.tenor.com/RzSxJdPrru8AAAAC/can-cj.gif',
            'https://c.tenor.com/u8X2NzZgtZYAAAAC/please-beg.gif',
            'https://c.tenor.com/oPDqKpmXylAAAAAd/i-beg-you-saturday-night-live.gif',
            'https://c.tenor.com/-KWybOCTNHoAAAAC/sponge-bob-mr-crabs.gif',
            'https://c.tenor.com/5t74NylYumsAAAAC/im-begging-you-please.gif',
            'https://c.tenor.com/u10jiuAXnmUAAAAC/per-favore-ti-prego.gif',
            'https://c.tenor.com/tpA9Lnbv0WwAAAAC/im-begging-you-please-please-please-praying.gif',
            'https://c.tenor.com/DLj3LemHpooAAAAC/bduck-duck.gif',
            'https://c.tenor.com/AaGZvgXirZAAAAAC/father-in-heaven-i-beg-of-you-eric-cartman.gif',
            'https://c.tenor.com/MnAM9lW9xYIAAAAC/stephen-colbert-beg.gif',
            'https://c.tenor.com/7jajSp78eTsAAAAC/im-begging-you-coach-ben-hopkins.gif',
            'https://c.tenor.com/t5gXP3bQ6FAAAAAC/supernatural-dean-winchester.gif',
            
        ]

        embed = discord.Embed(
            title="__Begging__",
            description=f"🙏 {self.member.mention} begged {self.target.mention} 🙏",
            color=discord.Color.dark_orange(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(begs))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the begging action. """

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

class PatView(discord.ui.View):
    """ View for the pat skill. """

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Pat', style=discord.ButtonStyle.blurple, custom_id='beg_id', emoji="🖐️")
    async def pat_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Pats something at someone. """

        pats: List[str] = [
            'https://c.tenor.com/nwbxEGQINOsAAAAd/pet-dog.gif',
            'https://c.tenor.com/9FVTXVpYPWUAAAAC/kitten-kittens.gif',
            'https://c.tenor.com/jkIeSOUiNBgAAAAC/bunny-cute.gif',
            'https://c.tenor.com/nUNorsu3_RIAAAAd/cat-sweet.gif',
            'https://c.tenor.com/-xLNpZn2ypoAAAAC/mine-animal.gif',
            'https://c.tenor.com/f3rcK4rA6sIAAAAC/bunny.gif',
            'https://c.tenor.com/Uxl8H7KhXzQAAAAC/dog-monkey.gif',
            'https://c.tenor.com/n6km1_0i97kAAAAC/anime-cat.gif',
            'https://c.tenor.com/UTZOodcQt3IAAAAC/doggo-petting.gif',
            'https://c.tenor.com/IuD4UPlUI_MAAAAd/cute-owl.gif',
            'https://c.tenor.com/ykE14C6EUO0AAAAC/mocha-dog.gif',
            'https://c.tenor.com/Yg8Mvtr3LR0AAAAC/cute-dog.gif',
            'https://c.tenor.com/5s87oz-N8VoAAAAd/cockroach-pet.gif',
            'https://c.tenor.com/XybizgnL1zQAAAAd/kittens-cute.gif',
            'https://c.tenor.com/X_kiZEj9X38AAAAC/dogs-puppy.gif',
            'https://c.tenor.com/0K5GUyL-KI8AAAAC/trees-can.gif',
            'https://c.tenor.com/fVkPn-dI70wAAAAC/cat-pet.gif',
            'https://c.tenor.com/MgfEseP2_PAAAAAC/frog-pat-head.gif',
            'https://c.tenor.com/ITGImjl7YXoAAAAd/fox-relaxed.gif',
            'https://c.tenor.com/QzypKfkMA9MAAAAd/guinea-pig-pet.gif',
            'https://c.tenor.com/cQ2VwOHNDJsAAAAC/baby-panda.gif',
            'https://c.tenor.com/XVgmW5qJpcsAAAAC/felizins-pet-pet.gif',
            
        ]

        embed = discord.Embed(
            title="__Patting__",
            description=f"🖐️ {self.member.mention} patted {self.target.mention} 🖐️",
            color=discord.Color.blurple(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(pats))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the pat action. """

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

class WhisperView(discord.ui.View):
    """ View for the whisper skill. """

    def __init__(self, member: discord.Member, target: discord.Member, text: str, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target
        self.text = text


    @discord.ui.button(label='Whisper', style=discord.ButtonStyle.blurple, custom_id='whisper_id', emoji="🤫")
    async def whisper_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Whispers something in someone's ear. """

        whisperings: List[str] = [
          'https://c.tenor.com/4w1ZuqnoGO4AAAAC/dexter-whisper.gif',
          'https://c.tenor.com/ST1Xf5EXlgAAAAAC/whisper-jimmy-fallon.gif',
          'https://c.tenor.com/BefNvhbd5hYAAAAC/whisper-surprised.gif',
          'https://c.tenor.com/3E4Deyxqq5IAAAAC/gal-gadot-ww.gif',
          'https://c.tenor.com/Qy7yI3pD5YcAAAAd/whisper.gif',
          'https://c.tenor.com/huj1jCMArV4AAAAd/callum-kerr-my-therapist-friend.gif',
          'https://c.tenor.com/ivNVSogpSGQAAAAC/whisper-donald-duck.gif',
          'https://c.tenor.com/HJXeufjWdDgAAAAC/whisper-bullshit.gif',
          'https://c.tenor.com/WfhkJWbkSW4AAAAd/hazel-english-shaking.gif',
          'https://c.tenor.com/rzEb-LoREzEAAAAd/ear-hear.gif',
          'https://c.tenor.com/2MAJh8k28a0AAAAC/younger-tv-younger.gif',
          'https://c.tenor.com/h2CWY5U2EJEAAAAd/secret-whisper.gif',
          'https://c.tenor.com/QezMpZnZeO0AAAAC/foodwars-first10seconds.gif',
          'https://c.tenor.com/LEeStfoJROcAAAAd/chew-your.gif',
          'https://c.tenor.com/RNTP-WAqMzUAAAAC/sandra-oh-andy-samberg.gif',
          'https://c.tenor.com/zXApXPOshXMAAAAC/de-storm-de-storm-youtube.gif',
          'https://c.tenor.com/ihscqSUt6hIAAAAd/dog-funny.gif',
          'https://c.tenor.com/5qSWtK6aoGkAAAAC/school-of-rock-whisper-gossip.gif'  
        ]

        embed = discord.Embed(
            title="__Whisper__",
            description=f"""🤫 {self.member.mention} whispered ||**"{self.text}"**|| into {self.target.mention}'s ear 🤫""",
            color=discord.Color.dark_gold(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(whisperings))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the whisper action. """

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




class HandshakeView(discord.ui.View):
    """ A view for the handshaking skill """

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Handshake', style=discord.ButtonStyle.blurple, custom_id='handshake_id', emoji="🤝")
    async def handshake_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Handshakes someone. """

        handshakes: List[str] = [
            "https://c.tenor.com/ytbz1Epg7Q8AAAAC/predator-arnold.gif",
            "https://c.tenor.com/1AOd8kRKXSsAAAAd/kirito-handshake.gif",
            "https://c.tenor.com/cxsA-a-8uz0AAAAC/tom-and-jerry-jerry-the-mouse.gif",
            "https://c.tenor.com/dJ-fCu3ZdMYAAAAd/handshake-agree.gif",
            "https://c.tenor.com/Jk5DASrKx3QAAAAC/my-girl-seal-friendship.gif",
            "https://c.tenor.com/Xv360gzJarQAAAAC/young-boy-football.gif",
            "https://c.tenor.com/9UxelIPA3dEAAAAC/hand-shake-phone.gif",
            "https://c.tenor.com/e7B8WV5Ow7EAAAAC/drake-will-ferrell.gif",
            "https://c.tenor.com/jkRs8LGfq0oAAAAd/hulk-hogan-shake-hands.gif",
            "https://c.tenor.com/9t3luBDOyHEAAAAC/the-simpsons-simpson.gif",
            "https://c.tenor.com/ob72I2v2zTsAAAAC/hand-shake.gif",
            "https://c.tenor.com/Iy4VniPfZQAAAAAC/secret-handshake-trouble.gif",
            "https://c.tenor.com/jRj2B9Q0gIIAAAAC/dog-handshake.gif",
            "https://c.tenor.com/P8UB_ldN6e4AAAAd/quando-rondo-handshake.gif",
            "https://c.tenor.com/5m5QGsVqkR8AAAAC/shake-hands-tom-and-jerry.gif",
            "https://c.tenor.com/JGeVX_nI39MAAAAC/shake-handshake.gif",
            "https://c.tenor.com/El24Zpa9_QUAAAAC/bean-girl.gif",
            "https://c.tenor.com/kPbvjinMD_0AAAAC/manly-handshake-fma-brotherhood.gif",
            "https://c.tenor.com/9LbEpuHBPScAAAAd/brooklyn-nine-nine-amy-and-rosa.gif",
            "https://c.tenor.com/PNLY3dijcIkAAAAC/trump-macron-macron-trump.gif"
        ]

        embed = discord.Embed(
            title="__Handshake__",
            description=f"🤝 {self.member.mention} handshaked {self.target.mention} 🤝",
            color=discord.Color.brand_green(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(handshakes))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the handshaking action. """

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


class PeekView(discord.ui.View):
    """ A view for the peek skill """

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Peek', style=discord.ButtonStyle.blurple, custom_id='peek_id', emoji="👀")
    async def peek_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Peeks at someone. """

        peeks: List[str] = [
            'https://c.tenor.com/Y8TRAK82_s4AAAAd/bill-nye.gif',
            'https://c.tenor.com/kXh4odz0PW0AAAAC/arrested-development-creep.gif',
            'https://c.tenor.com/Nt4mzB-VTlEAAAAC/bh187-spongebob.gif',
            'https://c.tenor.com/_Mgx_mhOaYkAAAAC/creep-creepy.gif',
            'https://c.tenor.com/BLwyj1w3rJUAAAAC/ariel-hiding.gif',
            'https://c.tenor.com/gFT6-1jcnXoAAAAd/peaking-peak.gif',
            'https://c.tenor.com/y2uSpFdZMp4AAAAC/unicorn-store-kit.gif',
            'https://c.tenor.com/vhxaixvLUz4AAAAd/stalking-spying.gif',
            'https://c.tenor.com/MlFGQLY79l0AAAAC/crazy-peak.gif',
            'https://c.tenor.com/nb-IK5uyZDsAAAAC/peek-a-boo-hide.gif',
            'https://c.tenor.com/25nv4JkM1CcAAAAC/baby-yoda-peek.gif',
            'https://c.tenor.com/-to5I8QJL-8AAAAd/peek-hiding.gif',
            'https://c.tenor.com/RUcs87FiJA8AAAAd/cute-cat.gif',
            'https://c.tenor.com/vgYj0v3_A0kAAAAC/anime-peek.gif',
            'https://c.tenor.com/djPemeJ4XEkAAAAC/sneak-sneaky.gif',
            'https://c.tenor.com/P7hbsoaPg-AAAAAC/cat-sneak.gif',
            'https://c.tenor.com/lZ0UXRHaTXMAAAAC/life-stalk.gif',
            'https://c.tenor.com/BP_m_CFVMEMAAAAC/uncle-buck-peek.gif',
            'https://c.tenor.com/rx5QhSm0ty8AAAAd/yoda-hello.gif',
            'https://c.tenor.com/5Ovv19thBygAAAAC/mario-peek.gif',
            'https://c.tenor.com/Mp-nTZCIxW0AAAAC/alf-blinds.gif',

        ]

        embed = discord.Embed(
            title="__Peek__",
            description=f"👀 {self.member.mention} peeked at {self.target.mention} 👀",
            color=discord.Color.brand_red(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(peeks))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the peek action. """

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

class DriveOverView(discord.ui.View):
    """ A view for the drive over skill """

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Drive Over', style=discord.ButtonStyle.blurple, custom_id='peek_id', emoji="🚗")
    async def drive_over_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Drives over someone. """

        runovers: List[str] = [
            'https://c.tenor.com/gSkcprb8EaAAAAAd/mike-barreras.gif',
            'https://c.tenor.com/XLdjjRtww6gAAAAd/run-drive-safe.gif',
            'https://c.tenor.com/c1Wq8nV4sG0AAAAd/powercrash-kid-crash.gif',
            'https://c.tenor.com/Kmai1S8zCscAAAAC/runover-ranover.gif',
            'https://c.tenor.com/545ezhrKz6UAAAAC/free-guy-ryan-reynolds.gif',
            'https://c.tenor.com/CYnm0RkWYN4AAAAC/ran-over-car.gif',
            'https://c.tenor.com/FwmAvRG1j9MAAAAC/horse-woman.gif',
            'https://c.tenor.com/NQ9aYFDJ7dsAAAAd/hit-and-run-run-over.gif',
            'https://c.tenor.com/CCl1Y2jnJUQAAAAd/hit-by-a-car-run-over.gif',
            'https://c.tenor.com/fycpf_htEugAAAAd/panda-yite.gif'
        ]

        embed = discord.Embed(
            title="__Drive Over__",
            description=f"🚗 {self.member.mention} drove over {self.target.mention} 🚗",
            color=discord.Color.brand_red(),
            timestamp=interaction.message.created_at
        )

        embed.set_author(name=self.member.display_name, url=self.member.avatar.url, icon_url=self.member.avatar.url)
        embed.set_thumbnail(url=self.target.avatar.url)
        embed.set_image(url=choice(runovers))
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)

        await interaction.response.send_message(content=self.target.mention, embed=embed)
        await self.disable_buttons(interaction, followup=True)
        self.stop()

    @discord.ui.button(label='Nevermind', style=discord.ButtonStyle.red, custom_id='nevermind_id', emoji="❌")
    async def nevermind_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:
        """ Cancels the drive over action. """

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