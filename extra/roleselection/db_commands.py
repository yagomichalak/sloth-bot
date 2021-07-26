import discord
from discord import guild
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union


class RoleSelectionDatabaseCommands(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @commands.command(hidden=True)
    @commands.is_owner()
    async def create_table_selection_menu(self, ctx: commands.Context) -> None:
        """ (OWNER) Creates the SelectionMenu table. """

        await ctx.message.delete()
        member = ctx.author

        if await self.check_table_selection_menu_exists():
            return await ctx.send(f"**Table `SelectionMenu` already exists, {member.mention}!**", delete_after=5)

        mycursor, db = await the_database()
        await mycursor.execute("""
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
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table `SelectionMenu` has been created!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def drop_table_selection_menu(self, ctx: commands.Context) -> None:
        """ (OWNER) Drops the SelectionMenu table. """

        await ctx.message.delete()
        member = ctx.author

        if not await self.check_table_selection_menu_exists():
            return await ctx.send(f"**Table `SelectionMenu` doesn't exist, {member.mention}!**", delete_after=5)

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SelectionMenu")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table `SelectionMenu` has been dropped!**", delete_after=5)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reset_table_selection_menu(self, ctx: commands.Context) -> None:
        """ (OWNER) Resets the SelectionMenu table. """

        await ctx.message.delete()
        member = ctx.author

        if not await self.check_table_selection_menu_exists():
            return await ctx.send(f"**Table `SelectionMenu` doesn't exist yet, {member.mention}!**", delete_after=5)

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SelectionMenu")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Table `SelectionMenu` has been reset!**", delete_after=5)

    async def check_table_selection_menu_exists(self) -> bool:
        """ Checks whether the SelectionMenu table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'SelectionMenu'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    # ===== Database Methods =====
    @staticmethod
    async def get_button_by_id(custom_id: str, message_id: int, guild_id: int) -> List[Union[int, str]]:
        """ Gets a button from its custom ID.
        :param custom_id: The custom ID of the button.
        :param message_id: The message ID in which the button is in.
        :param guild_id: The ID of the guild in which the menu is in. """

        mycursor, _ = await the_database()
        await mycursor.execute("""
        SELECT * FROM SelectionMenu WHERE custom_id = %s AND message_id = %s AND guild_id = %s
        """, (custom_id, message_id, guild_id))
        button = await mycursor.fetchone()
        await mycursor.close()
        return button
        

    @staticmethod
    async def get_selection_menus() -> List[List[int]]:
        """ Gets all registered Selection Menus. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM SelectionMenu ORDER BY guild_id, channel_id, message_id")
        selection_menus = await mycursor.fetchall()
        await mycursor.close()
        return selection_menus

    @staticmethod
    async def get_selection_menu(message_id: int, guild_id: int) -> List[int]:
        """ Gets a specific Selection Menu.
        :param message_id: The message ID of the Selection Menu.
        :param guild_id: The server ID in which the Selection Menu was created. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM SelectionMenu WHERE message_id = %s AND guild_id = %s", (message_id, guild_id))
        selection_menu = await mycursor.fetchone()
        await mycursor.close()
        return selection_menu

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

        mycursor, db = await the_database()
        await mycursor.execute("""INSERT INTO SelectionMenu (
            message_id, channel_id, guild_id, style, label, emoji, custom_id) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (message_id, channel_id, guild_id, style, label, emoji, custom_id))
        await db.commit()
        await mycursor.close()



    # ===== Delete methods =====

    @staticmethod
    async def delete_menu_button(message_id: int, channel_id: int, guild_id: int, custom_id: str) -> None:
        """ Deletes a button from a Role Selection menu.
        :param message_id:
        :param channel_id:
        :param guild_id:
        :param custom_id: """

        mycursor, db = await the_database()
        await mycursor.execute("""
        DELETE FROM SelectionMenu
        WHERE message_id = %s AND channel_id = %s AND guild_id = %s AND custom_id = %s
        """, (message_id, channel_id, guild_id, custom_id))
        await db.commit()
        await mycursor.close()

    @staticmethod
    async def delete_selection_menu_by_message_id(message_id: int, guild_id: int) -> None:
        """ Deletes a Role Selection menu by message ID.
        :param message_id: The message ID of the menu.
        :param guild_id: The ID of the server in which the Selection Menu was created. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SelectionMenu WHERE message_id = %s AND guild_id = %s", (message_id, guild_id))
        await db.commit()
        await mycursor.close()

    @staticmethod
    async def delete_selection_menu_by_channel_id(channel_id: int, guild_id: int) -> None:
        """ Deletes a Role Selection menu by channel ID.
        :param channel_id: The ID of the channel in which the Selection Menu was created.
        :param guild_id: The ID of the server in which the Selection Menu was created. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SelectionMenu WHERE channel_id = %s AND guild_id = %s", (channel_id, guild_id))
        await db.commit()
        await mycursor.close()

    @staticmethod
    async def delete_selection_menu_by_guild_id(guild_id: int) -> None:
        """ Deletes a Role Selection menu by guild ID.
        :param guild_id: The ID of the server in which the Selection Menu was created. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SelectionMenu WHERE guild_id = %s", (guild_id,))
        await db.commit()
        await mycursor.close()
