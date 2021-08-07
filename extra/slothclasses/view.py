import discord
from discord.ext import commands
from typing import Optional, List, Dict, Union
from random import choice
from extra import utils

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