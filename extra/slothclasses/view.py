import discord
from discord.ext import commands
from typing import Optional, List, Dict, Union
from random import choice

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
            title="__Hug__",
            description=f"🤗 {self.member.mention} hugged {self.target.mention} 🤗",
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

        await interaction.response.send_message(content=self.target.mention, embed=embed)
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

class HoneymoonView(discord.ui.View):

    def __init__(self, member: discord.Member, target: discord.Member, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.target = target


    @discord.ui.button(label='Hug', style=discord.ButtonStyle.blurple, custom_id='hug_id', emoji="")
    async def honeymoon_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None: pass


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
        super().__init__(timeout=10)
        self.client = client
        self.cheater = cheater
        self.lover = lover
        self.marriage = marriage

    @discord.ui.button(label="Spot Cheating", style=discord.ButtonStyle.red, custom_id='cheating_id', emoji='<:pepeOO:572067085371572224>')
    async def spot_cheating_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None:

        print('yeah')
        pass


    async def disable_buttons(self, interaction: discord.Interaction, followup: bool = False) -> None:

        for child in self.children:
            child.disabled = True

        if followup:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.member.id == interaction.user.id