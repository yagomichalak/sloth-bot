import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union

class UserItemsTable(commands.Cog):
    """ Class for the UserItems table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    
    # Database commands
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_items(self, ctx) -> None:
        """ (ADM) Creates the UserItems table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author

        if await self.check_user_items_table_exists():
            return await ctx.send(f"**The `UserItems` table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
        CREATE TABLE UserItems (
            user_id bigint, item_name VARCHAR(30), enable VARCHAR(10), 
            item_type VARCHAR(10), image_name VARCHAR(50))""")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table `UserItems` created, {member.mention}!**")

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def drop_table_user_items(self, ctx) -> None:
        """ (ADM) Drops the UserItems table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author

        if not await self.check_user_items_table_exists():
            return await ctx.send(f"**The `UserItems` table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserItems")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table `UserItems` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_items(self, ctx) -> None:
        """ (ADM) Resets the UserItems table. """

        await ctx.message.delete()
        member: discord.Member = ctx.author

        if not await self.check_user_items_table_exists():
            return await ctx.send(f"**The `UserItems` table doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserItems")
        await db.commit()
        await mycursor.close()

        return await ctx.send(f"**Table `UserItems` reset, {member.mention}!**")

    # ===== SHOW =====

    async def check_user_items_table_exists(self) -> bool:
        """ Checks whether the UserItems table exists in the database. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW STATUS LIKE 'UserItems'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    # ===== INSERT =====

    async def insert_user_item(self, user_id: int, item_name: str, enable: str, item_type: str, item_image: str) -> None:
        """ Inserts an item to the user inventory.
        :param user_id: The ID of the user.
        :param item_name: The name of the item to insert.
        :param enable: Whether to insert it as equipped or unequipped.
        :param item_type: The type of the item. (head/foot/hand/body/background)
        :param item_image: The name of the image that illustrates the item. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO UserItems (user_id, item_name, enable, item_type, image_name) VALUES (%s, %s, %s, %s, %s)",
                               (user_id, item_name.title(), enable, item_type.lower(), item_image))
        await db.commit()
        await mycursor.close()

    # ===== DELETE =====

    async def remove_user_item(self, user_id: int, item_name: str) -> None:
        """ Removes an item from the user's inventory.
        :param user_id: The ID of the user from whom to remove the item.
        :param item_name: The name of the item to remove. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserItems WHERE item_name = %s and user_id = %s", (item_name, user_id))
        await db.commit()
        await mycursor.close()

    # ===== UPDATE =====

    async def update_user_item_info(self, user_id: int, item_name: str, enable: str) -> None:
        """ Updates the user's item enabled state.
        :param user_id: The ID of the user owner of the item.
        :param item_name: The name of the item.
        :param enable: The new state to set the item to. (equipped/unequipped) """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserItems SET enable = %s WHERE user_id = %s and item_name = %s", (enable, user_id, item_name))
        await db.commit()
        await mycursor.close()

    # ===== SELECT =====

    async def get_user_item(self, user_id: int, item_name: str) -> List[Union[int, str]]:
        """ Gets a specific item from the user's inventory.
        :param user_id: The ID of the user from whom to get the item.
        :param item_name: The name of the item to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserItems WHERE user_id = %s AND item_name = %s", (user_id, item_name))
        item_system = await mycursor.fetchone()
        await mycursor.close()
        return item_system

    async def get_user_items(self, user_id: int) -> List[List[Union[int, str]]]:
        """ Gets all items from the user's inventory.
        :param user_id: The ID of the user from whom to get the items. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserItems WHERE user_id = %s ORDER BY user_id", (user_id,))
        item_system = await mycursor.fetchall()
        await mycursor.close()
        return item_system

    async def get_user_specific_type_item(self, user_id, item_type) -> str:
        """ Gets a random item of a specific type from the user.
        :param user_id: The ID of the user from whom to get the item.
        :param item_type: The type of the item to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT item_name, image_name FROM UserItems WHERE user_id = %s and item_type = %s and enable = 'equipped'", (user_id, item_type))
        spec_type_items = await mycursor.fetchone()
        await mycursor.close()
        if spec_type_items and spec_type_items[1]:
            return f'./sloth_custom_images/{item_type}/{spec_type_items[1]}'

        else:
            return f'./sloth_custom_images/{item_type}/base_{item_type}.png'

    async def check_user_can_equip(self, user_id: int, item_name: str) -> bool:
        """ Checks whether a user can equip a specific item.
        :param user_id: The ID of the user to check.
        :param item_name: The name of the item. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT item_type FROM UserItems WHERE user_id = %s AND item_name = %s", (user_id, item_name))
        item_type = await mycursor.fetchone()
        
        await mycursor.execute(
            "SELECT * FROM UserItems WHERE user_id = %s and item_type = %s and enable = 'equipped'",
            (user_id, item_type[0]))
        equipped_item = await mycursor.fetchall()
        await mycursor.close()

        if len(equipped_item) != 0 and len(item_type) != 0:
            return False
        else:
            return True

    async def check_user_can_unequip(self, user_id, item_name: str) -> bool:
        """ Checks whether a user can unequip a specific item.
        :param user_id: The ID of the user to check.
        :param item_name: The name of the item. """

        mycursor, _ = await the_database()
        await mycursor.execute(
            "SELECT * FROM UserItems WHERE user_id = %s and item_name = %s and enable = 'unequipped'", (user_id, item_name.title()))
        unequipped_item = await mycursor.fetchall()
        await mycursor.close()

        if len(unequipped_item) != 0:
            return False
        else:
            return True

    async def get_user_specific_item(self, user_id: int, item_name: str) -> List[Union[str, int]]:
        """ Gets a user's specific item.
        :param user_id: The ID of the user from whom to get the item.
        :param item_name: The name of the item to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserItems WHERE user_id = %s and item_name = %s", (user_id, item_name))
        item_system = await mycursor.fetchone()
        await mycursor.close()
        return item_system

    async def get_user_registered_items(self, user_id: int) -> List[List[Union[str, int]]]:
        """ Gets all UserItems that are registered on the website.
        :param user_id: The ID of the user to get the items from. """

        mycursor, _ = await the_database()
        await mycursor.execute("""
            SELECT SSI.* FROM UserItems AS UI 
            LEFT JOIN slothdjango.shop_shopitem AS SSI ON UI.item_name = SSI.item_name
            WHERE user_id = %s
        """, (user_id,))
        user_items = await mycursor.fetchall()
        await mycursor.close()
        return user_items

    async def get_top_ten_item_counter_users(self) -> List[List[int]]:
        """ Gets the item counter of the top ten users with most items. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT user_id, COUNT(*) FROM UserItems GROUP BY user_id ORDER BY COUNT(*) DESC LIMIT 10")
        item_counters = await mycursor.fetchall()
        await mycursor.close()
        return item_counters

    async def get_item_counter_users(self) -> List[List[int]]:
        """ Gets the item counter of the all users with most items. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT user_id, COUNT(*) FROM UserItems GROUP BY user_id ORDER BY COUNT(*) DESC")
        item_counters = await mycursor.fetchall()
        await mycursor.close()
        return item_counters