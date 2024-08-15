from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List, Union


class RoleSelectionDatabaseCommands(commands.Cog):
    """ Class for RoleSelection database commands and methods. """

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

            style TINYINT(1) NOT NULL,
            label VARCHAR(80) NOT NULL,
            emoji VARCHAR(150) NOT NULL,
            custom_id VARCHAR(100) NOT NULL
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
    @staticmethod
    async def get_button_by_id(custom_id: str, message_id: int, guild_id: int) -> List[Union[int, str]]:
        """ Gets a button from its custom ID.
        :param custom_id: The custom ID of the button.
        :param message_id: The message ID in which the button is in.
        :param guild_id: The ID of the guild in which the menu is in. """

        return await DatabaseCore().execute_query("""
        SELECT * FROM SelectionMenu WHERE custom_id = %s AND message_id = %s AND guild_id = %s
        """, (custom_id, message_id, guild_id), fetch="one")       

    @staticmethod
    async def get_selection_menus() -> List[List[int]]:
        """ Gets all registered Selection Menus. """

        return await DatabaseCore().execute_query("SELECT * FROM SelectionMenu ORDER BY guild_id, channel_id, message_id", fetch="all")

    @staticmethod
    async def get_selection_menu(message_id: int, guild_id: int) -> List[int]:
        """ Gets a specific Selection Menu.
        :param message_id: The message ID of the Selection Menu.
        :param guild_id: The server ID in which the Selection Menu was created. """

        return await DatabaseCore().execute_query("SELECT * FROM SelectionMenu WHERE message_id = %s AND guild_id = %s", (message_id, guild_id), fetch="one")

    @staticmethod
    async def insert_menu_button(
        message_id: int, channel_id: int, guild_id: int, style: int, label: str, emoji: str, custom_id: str) -> None:
        """ Inserts a Selection Menu.
        :param message_id: The ID of the message in which the menu is located.
        :param channel_id: The ID of the channel in which the menu message is located.
        :param guild_id: The ID of the guild in which the menu was created.
        :param style: The style of the button. (1-4)
        :param label: The label of the button.
        :param emoji: The emoji of the button.
        :param custom_id: The custom ID of the button. """

        await DatabaseCore().execute_query("""INSERT INTO SelectionMenu (
            message_id, channel_id, guild_id, style, label, emoji, custom_id) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (message_id, channel_id, guild_id, style, label, emoji, custom_id))

    # ===== Delete methods =====

    @staticmethod
    async def delete_menu_button(message_id: int, channel_id: int, guild_id: int, custom_id: str) -> None:
        """ Deletes a button from a Role Selection menu.
        :param message_id:
        :param channel_id:
        :param guild_id:
        :param custom_id: """

        await DatabaseCore().execute_query("""
        DELETE FROM SelectionMenu
        WHERE message_id = %s AND channel_id = %s AND guild_id = %s AND custom_id = %s
        """, (message_id, channel_id, guild_id, custom_id))

    @staticmethod
    async def delete_selection_menu_by_message_id(message_id: int, guild_id: int) -> None:
        """ Deletes a Role Selection menu by message ID.
        :param message_id: The message ID of the menu.
        :param guild_id: The ID of the server in which the Selection Menu was created. """

        await DatabaseCore().execute_query("DELETE FROM SelectionMenu WHERE message_id = %s AND guild_id = %s", (message_id, guild_id))

    @staticmethod
    async def delete_selection_menu_by_channel_id(channel_id: int, guild_id: int) -> None:
        """ Deletes a Role Selection menu by channel ID.
        :param channel_id: The ID of the channel in which the Selection Menu was created.
        :param guild_id: The ID of the server in which the Selection Menu was created. """

        await DatabaseCore().execute_query("DELETE FROM SelectionMenu WHERE channel_id = %s AND guild_id = %s", (channel_id, guild_id))

    @staticmethod
    async def delete_selection_menu_by_guild_id(guild_id: int) -> None:
        """ Deletes a Role Selection menu by guild ID.
        :param guild_id: The ID of the server in which the Selection Menu was created. """

        await DatabaseCore().execute_query("DELETE FROM SelectionMenu WHERE guild_id = %s", (guild_id,))
