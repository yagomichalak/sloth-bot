import discord
from discord.ext import commands
from typing import Optional

class HugView(discord.ui.View):

    def __init__(self, member: discord.Member, timeout: Optional[float] = None):
        super().__init__(timeout=timeout)


    @discord.ui.button(label='Hug', style=discord.ButtonStyle.blurple, custom_id='hug_id', emoji="")
    async def hug_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None: pass

class HugView(discord.ui.View):

    def __init__(self, member: discord.Member, timeout: Optional[float] = None):
        super().__init__(timeout=timeout)


    @discord.ui.button(label='Hug', style=discord.ButtonStyle.blurple, custom_id='hug_id', emoji="")
    async def hug_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None: pass

class SlapView(discord.ui.View):

    def __init__(self, member: discord.Member, timeout: Optional[float] = None):
        super().__init__(timeout=timeout)


    @discord.ui.button(label='Hug', style=discord.ButtonStyle.blurple, custom_id='hug_id', emoji="")
    async def hug_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None: pass

class KissView(discord.ui.View):

    def __init__(self, member: discord.Member, timeout: Optional[float] = None):
        super().__init__(timeout=timeout)


    @discord.ui.button(label='Hug', style=discord.ButtonStyle.blurple, custom_id='hug_id', emoji="")
    async def hug_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None: pass

class HoneymoonView(discord.ui.View):

    def __init__(self, member: discord.Member, timeout: Optional[float] = None):
        super().__init__(timeout=timeout)


    @discord.ui.button(label='Hug', style=discord.ButtonStyle.blurple, custom_id='hug_id', emoji="")
    async def honeymoon_button(self, button: discord.ui.button, interaction: discord.Interaction) -> None: pass