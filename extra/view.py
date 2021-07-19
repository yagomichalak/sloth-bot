import discord
from discord.ext import commands
from typing import List, Dict, Union, Any
from .menu import ConfirmSkill

class QuickButtons(discord.ui.View):

    def __init__(self) -> None:
        super().__init__()


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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        return self.user_info[0] == interaction.user.id


class ConfirmButton(discord.ui.View):
    def __init__(self):
        super().__init__()
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