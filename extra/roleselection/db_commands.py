# import.standard
from typing import List, Union

# import.thirdparty
from discord.ext import commands

# import.local
from mysqldb import DatabaseCore

class RoleSelectionDatabaseCommands(commands.Cog):
    """ Category for the selection menu system's database commands and methods. """

    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def create_table_selection_menu(self, ctx: commands.Context) -> None:
        """ (OWNER) Creates the SelectionMenu table. """

        await ctx.message.delete()
        member = ctx.author

        if await self.check_table_selection_menu_exists():
            return await ctx.send(f"**Table `SelectionMenu` already exists, {member.mention}!**", delete_after=5)

        await self.db.execute_query("""
        CREATE TABLE SelectionMenu (
            message_id BIGINT NOT NULL,
            channel_id BIGINT NOT NULL,
            guild_id BIGINT NOT NULL,

            label VARCHAR(80) NOT NULL,
            emoji VARCHAR(150) NOT NULL,
            role_id BIGINT NOT NULL,
            placeholder VARCHAR(100) NOT NULL
        )
        """)
        await ctx.send("**Table `SelectionMenu` has been created!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def drop_table_selection_menu(self, ctx: commands.Context) -> None:
        """ (OWNER) Drops the SelectionMenu table. """

        await ctx.message.delete()
        member = ctx.author

        if not await self.check_table_selection_menu_exists():
            return await ctx.send(f"**Table `SelectionMenu` doesn't exist, {member.mention}!**", delete_after=5)

        await self.db.execute_query("DROP TABLE SelectionMenu")
        await ctx.send("**Table `SelectionMenu` has been dropped!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reset_table_selection_menu(self, ctx: commands.Context) -> None:
        """ (OWNER) Resets the SelectionMenu table. """

        await ctx.message.delete()
        member = ctx.author

        if not await self.check_table_selection_menu_exists():
            return await ctx.send(f"**Table `SelectionMenu` doesn't exist yet, {member.mention}!**", delete_after=5)

        await self.db.execute_query("DELETE FROM SelectionMenu")
        await ctx.send("**Table `SelectionMenu` has been reset!**", delete_after=5)

    async def check_table_selection_menu_exists(self) -> bool:
        """ Checks whether the SelectionMenu table exists. """

        return await self.db.table_exists("SelectionMenu")

    # ===== Database Methods =====
    async def get_select_by_id(self, role_id: str, message_id: int, guild_id: int) -> List[Union[int, str]]:
        """ Gets a select from its custom ID.
        :param role_id: The role ID of the select.
        :param message_id: The message ID in which the select is in.
        :param guild_id: The ID of the guild in which the menu is in. """

        return await self.db.execute_query("""
        SELECT * FROM SelectionMenu WHERE role_id = %s AND message_id = %s AND guild_id = %s
        """, (role_id, message_id, guild_id), fetch="one")

    async def get_selection_menus_by_message_id_and_placeholder(self, message_id: int) -> List[List[int]]:
        """ Gets all registered Selection Menus by message ID and group by placeholder.
        :param message_id: The ID of the message. """

        return await self.db.execute_query("""
            SELECT * FROM SelectionMenu 
            WHERE message_id = %s GROUP BY placeholder""", (message_id,), fetch="all")

    async def get_selection_menus(self) -> List[List[int]]:
        """ Gets all registered Selection Menus. """

        return await self.db.execute_query("SELECT * FROM SelectionMenu ORDER BY guild_id, channel_id, message_id", fetch="all")

    async def get_selection_menu(self, message_id: int, guild_id: int) -> List[int]:
        """ Gets a specific Selection Menu.
        :param message_id: The message ID of the Selection Menu.
        :param guild_id: The server ID in which the Selection Menu was created. """

        return await self.db.execute_query(
            "SELECT * FROM SelectionMenu WHERE message_id = %s AND guild_id = %s", (message_id, guild_id), fetch="one")

    async def insert_menu_select(self,
        message_id: int, channel_id: int, guild_id: int, label: str, emoji: str, role_id: int, placeholder: str) -> None:
        """ Inserts a Selection Menu.
        :param message_id: The ID of the message in which the menu is located.
        :param channel_id: The ID of the channel in which the menu message is located.
        :param guild_id: The ID of the guild in which the menu was created.
        :param label: The label of the select.
        :param emoji: The emoji of the select.
        :param role_id: The ID of the role of the select option.
        :param placeholder: The placeholder of the select. """

        await self.db.execute_query("""INSERT INTO SelectionMenu (
            message_id, channel_id, guild_id, label, emoji, role_id, placeholder) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (message_id, channel_id, guild_id, label, emoji, role_id, placeholder))

    # ===== Delete methods =====

    async def delete_menu_select(self, message_id: int, channel_id: int, guild_id: int, role_id: str) -> None:
        """ Deletes a select from a Role Selection menu.
        :param message_id:
        :param channel_id:
        :param guild_id:
        :param role_id: """

        await self.db.execute_query("""
        DELETE FROM SelectionMenu
        WHERE message_id = %s AND channel_id = %s AND guild_id = %s AND role_id = %s
        """, (message_id, channel_id, guild_id, role_id))

    async def delete_selection_menu_by_message_id(self, message_id: int, guild_id: int) -> None:
        """ Deletes a Role Selection menu by message ID.
        :param message_id: The message ID of the menu.
        :param guild_id: The ID of the server in which the Selection Menu was created. """

        await self.db.execute_query("DELETE FROM SelectionMenu WHERE message_id = %s AND guild_id = %s", (message_id, guild_id))

    async def delete_selection_menu_by_message_id_and_placeholder(self, message_id: int, guild_id: int, placeholder: str) -> None:
        """ Deletes a Role Selection menu by message ID and placeholder.
        :param message_id: The message ID of the menu.
        :param guild_id: The ID of the server in which the Selection Menu was created.
        :param placeholder: The placeholder of the select. """

        await self.db.execute_query("DELETE FROM SelectionMenu WHERE message_id = %s AND guild_id = %s AND placeholder = %s", (
            message_id, guild_id, placeholder))

    async def delete_selection_menu_by_channel_id(self, channel_id: int, guild_id: int) -> None:
        """ Deletes a Role Selection menu by channel ID.
        :param channel_id: The ID of the channel in which the Selection Menu was created.
        :param guild_id: The ID of the server in which the Selection Menu was created. """

        await self.db.execute_query("DELETE FROM SelectionMenu WHERE channel_id = %s AND guild_id = %s", (channel_id, guild_id))

    async def delete_selection_menu_by_guild_id(self, guild_id: int) -> None:
        """ Deletes a Role Selection menu by guild ID.
        :param guild_id: The ID of the server in which the Selection Menu was created. """

        await self.db.execute_query("DELETE FROM SelectionMenu WHERE guild_id = %s", (guild_id,))
