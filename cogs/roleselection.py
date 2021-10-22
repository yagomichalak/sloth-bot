from datetime import time
import discord
from discord.ext import commands

from extra.prompt.menu import prompt_emoji_guild, prompt_message_guild, get_role_response

from extra.roleselection.db_commands import RoleSelectionDatabaseCommands
from extra.roleselection.menu import RoleSelect, ManageRoleSelectionMenu
from extra.prompt.menu import ConfirmButton

from functools import partial
from typing import Dict


class RoleSelection(RoleSelectionDatabaseCommands):
    """ Category for managing and interacting with Role Selection menus. """

    def __init__(self, client) -> None:
        self.client = client
        self.db = super()


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Makes all existing Role Selection menus in the database consistent on Discord. """

        selection_menus = await self.get_selection_menus()
        messages = {}
        # Groups all selection options by message
        for select_option in selection_menus:
            try:
                if not messages.get(select_option[0]):
                    messages[select_option[0]] = [select_option[3:]]
                else:
                    messages[select_option[0]].append(select_option[3:])
            except Exception as e:
                print('error in roleselection', e)

        # Makes all drop-downs
        for message_id, select_options in messages.items():
            try:
                view = discord.ui.View(timeout=None)
                options = {}
                for select_option in select_options:
                    index = select_option[3]

                    if not options.get(index):                        
                        options[index] = [discord.SelectOption(label=select_option[0], emoji=select_option[1], value=str(select_option[2]))]
                    else:
                        options[index].append(discord.SelectOption(label=select_option[0], emoji=select_option[1], value=str(select_option[2])))

                for key, values in options.items():
                    select = RoleSelect(placeholder=key, custom_id=key.lower().replace(' ', '_'), options=values)
                    view.add_item(select)

                self.client.add_view(view=view, message_id=message_id)
            except Exception as e:
                print('ERROR IN RoleSelection', e)
            else:
                continue

        print('RoleSelection cog is online!')


    @commands.group(name='menu')
    @commands.has_permissions(administrator=True)
    async def _menu(self, ctx) -> None:
        """ Command manager of the Role Selection menu system. """

        if ctx.invoked_subcommand:
            return

        cmd = self.client.get_command(ctx.command.name)
        prefix = self.client.command_prefix
        subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands]

        subcommands = '\n'.join(subcommands)
        embed = discord.Embed(
            title="__Subcommads__:",
            description=f"```apache\n{subcommands}```",
            color=ctx.author.color,
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=embed)
    
    @_menu.command(name='add')
    async def _add(self, ctx, message_id: int = None) -> None:
        """ Subcommand for adding drop-downs to a message. """

        await ctx.message.delete()
        member = ctx.author

        if not message_id:
            return await ctx.send(f"**Please, inform a `message ID`, {member.mention}!**", delete_after=5)
        
        msg = await ctx.channel.fetch_message(message_id)
        if msg is None:
            return await ctx.send(f"**Message not found, {member.mention}!**", delete_after=5)

        embed = discord.Embed(description="**What is the default placeholder for the select?**", color=member.color, timestamp=ctx.message.created_at)
        # Question 1 - Label:
        initial_msg = await ctx.send(embed=embed)
        placeholder = await prompt_message_guild(self.client, member=member, channel=ctx.channel, limit=100)
        await initial_msg.delete()

        view = discord.ui.View.from_message(msg, timeout=None)
        for child in view.children:
            child.callback = partial(RoleSelect.callback, child)

        select = RoleSelect(placeholder=placeholder, custom_id=placeholder.lower().replace(' ', '_'), options=[])
        view.add_item(select)
        while True:

            select_configs = await self.ask_select_questions(ctx, msg)
            if not select_configs:
                break
            
            
            view.children[-1].options.append(discord.SelectOption(**select_configs))

            try:
                await self.db.insert_menu_select(msg.id, msg.channel.id, msg.guild.id, *select_configs.values(), placeholder)
            except Exception as e:
                print(e)
                await ctx.send(f"**I couldn't add your button to the database, {member.mention}!**", delete_after=5)

            await msg.edit(view=view)
            confirm_view = ConfirmButton(member)
            embed = discord.Embed(description=f"**Wanna add more options into your select menu, {member.mention}?**", color=member.color)
            confirm_msg = await ctx.channel.send("\u200b", embed=embed, view=confirm_view)
            
            
            await confirm_view.wait()
            await confirm_msg.delete()
            if confirm_view.value is None or not confirm_view.value:
                break


        self.client.add_view(view=view, message_id=msg.id)
        await ctx.send(f"**Menu successfully completed, {member.mention}!**", delete_after=5)

    @_menu.command(name='edit')
    async def _edit(self, ctx, message_id: int = None) -> None:
        """ Subcommand for editing an existing menu:
        - Adding more options to a drop-down;
        - Deleting options from a drop-down;
        - Deleting a drop-down;
        - Deleting the whole menu; """

        member = ctx.author
        guild = ctx.guild

        await ctx.message.delete()

        if not message_id:
            return await ctx.send(f"**Please, inform a message ID, {member.mention}!**")

        selection_menu = await self.get_selection_menu(message_id, guild.id)
        if not selection_menu:
            return await ctx.send(f"**No menus with that ID were found, {member.mention}!**", delete_after=3)

        if not (channel := discord.utils.get(guild.text_channels, id=selection_menu[1])):
            await self.db.delete_selection_menu_by_channel_id(selection_menu[1], guild.id)
            return await ctx.send(f"**Channel and message of the Menu don't exist anymore, {member.mention}!**", delete_after=3)

        if (message := await channel.fetch_message(selection_menu[0])) is None:
            await self.db.delete_selection_menu_by_message_id(selection_menu[0], guild.id)
            return await ctx.send(f"**Message of the Menu doesn't exist anymore, {member.mention}!**", delete_after=3)
        
        embed = discord.Embed(
            title=f"__Editing Menu__ ({message_id})",
            color=member.color,
            timestamp=ctx.message.created_at
        )

        embed.set_author(name=guild.name, url=guild.icon.url, icon_url=guild.icon.url)
        embed.set_footer(text=f"Being edited by {member}", icon_url=member.avatar.url)

        view = ManageRoleSelectionMenu(self.client, message)

        msg = await ctx.send("\u200b", embed=embed, view=view)
        try:
            await view.wait()
            await msg.delete()
        except:
            pass

    async def ask_select_questions(self, ctx: commands.Context, message: discord.Message) -> Dict[str, str]:
        """ Asks questions to the user for the select creation.
        :param ctx: The context of the initial command.
        :param message: The message of the menu.  """

        member = ctx.author
        channel = ctx.channel

        # BTN Questions: style, label, emoji, role
        
        slct_configs: Dict[str, str] = {}

        embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)

        # Question 1 - Label:
        embed.description = "**What is the label of your button?**"
        initial_message = await ctx.send(embed=embed)
        label = await prompt_message_guild(self.client, member=member, channel=channel, limit=80)
        if not label: return False
        slct_configs['label'] = label

        # Question 2 - Emoji:
        embed.description = "**Type an emoji to attach to the button**"
        await initial_message.edit(embed=embed)
        emoji = await prompt_emoji_guild(self.client, member=member, channel=channel, limit=100)
        # emoji = await prompt_message_guild(self.client, member=member, channel=channel, limit=100)
        if not emoji: return False
        slct_configs['emoji'] = emoji

        # Question 3 - Role:
        embed.description = "**Type a role! (@role /role id/role name)**"
        await initial_message.edit(embed=embed)
        while True:
            role = await get_role_response(self.client, ctx, msg=initial_message, member=member, embed=embed, channel=channel)
            if not role: return False
            slct_configs['value'] = int(role.id)

            if await self.db.get_select_by_id(int(role.id), message.id, message.guild.id):
                await ctx.send("**There is already a select option with this role in this menu, type another role!**", delete_after=3)
            else:
                break

        await initial_message.delete()

        return slct_configs


def setup(client) -> None:
    client.add_cog(RoleSelection(client))