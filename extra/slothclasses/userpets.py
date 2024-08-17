import discord
from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List, Union, Optional
from extra import utils


class UserPetsTable(commands.Cog):
    """ Class for the UserPets table and its commands and methods. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_pets(self, ctx) -> None:
        """ Creates the UserPets table in the database. """

        member: discord.Member = ctx.author
        if await self.check_user_pets_table_exists():
            return await ctx.send(f"**The UserPets table already exists, {member.mention}!**")

        await self.db.execute_query("""CREATE TABLE UserPets (
            user_id BIGINT NOT NULL,
            pet_name VARCHAR(25) DEFAULT 'Egg',
            pet_breed VARCHAR(25) DEFAULT 'Egg',
            life_points TINYINT(3) DEFAULT 100,
            food TINYINT(3) DEFAULT 100,
            life_points_ts BIGINT NOT NULL,
            food_ts BIGINT NOT NULL,
            birth_ts BIGINT DEFAULT NULL,
            auto_feed TINYINT(1) DEFAULT 0,
            PRIMARY KEY (user_id)
            ) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)

        await ctx.send(f"**`UserPets` table created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_pets(self, ctx) -> None:
        """ Drops the UserPets table from the database. """

        member: discord.Member = ctx.author
        if not await self.check_user_pets_table_exists():
            return await ctx.send(f"**The UserPets table doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE UserPets")

        await ctx.send(f"**`UserPets` table dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_pets(self, ctx) -> None:
        """ Resets the UserPets table in the database. """

        member: discord.Member = ctx.author
        if not await self.check_user_pets_table_exists():
            return await ctx.send(f"**The UserPets table doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM UserPets")

        await ctx.send(f"**`UserPets` table reset, {member.mention}!**")

    async def check_user_pets_table_exists(self) -> bool:
        """ Checks whether the UserPets table exists in the database. """

        return await self.db.table_exists("UserPets")

    async def insert_user_pet(self, user_id: int, pet_name: Optional[str] = None, pet_breed: Optional[str] = None) -> None:
        """ Inserts a User Pet.
        :param user_id: The ID of the user owner of the pet.
        :param pet_name: The name of the pet. [Optional]
        :param pet_breed: The breed of the pet. [Optional]"""

        current_ts = await utils.get_timestamp()
        other_ts = current_ts + 3600

        if pet_name and pet_breed:
            await self.db.execute_query("""
            INSERT INTO UserPets (
                user_id, pet_name, pet_breed, life_points_ts, food_ts, birth_ts
            ) VALUES (%s, %s, %s, %s, %s, %s)""", (user_id, pet_name, pet_breed, other_ts, other_ts, current_ts))
        else:
            await self.db.execute_query("""
            INSERT INTO UserPets (
                user_id, life_points_ts, food_ts, birth_ts
            ) VALUES (%s, %s, %s, %s)""", (user_id, other_ts, other_ts, current_ts))

    async def get_user_pet(self, user_id: int) -> List[Union[str, int]]:
        """ Get the user's pet.
        :param user_id: The ID of the pet's owner. """

        return await self.db.execute_query("SELECT * FROM UserPets WHERE user_id = %s", (user_id,), fetch="one")

    async def get_pets(self) -> List[List[Union[str, int]]]:
        """ Get all user pets. """

        return await self.db.execute_query("SELECT * FROM UserPets", fetch="all")

    async def get_hungry_pets(self, current_ts: int) -> List[List[Union[str, int]]]:
        """ Get all user hungry pets.
        :param current_ts: The current timestamp. """

        return await self.db.execute_query("SELECT * FROM UserPets WHERE %s - food_ts >= 7200", (current_ts,), fetch="all")

    async def update_user_pet_name(self, user_id: int, pet_name: str) -> None:
        """ Updates the User Pet's name.
        :param user_id: The ID of the pet's owner.
        :param pet_name: The new pet name to update to. """

        await self.db.execute_query("UPDATE UserPets SET pet_name = %s WHERE user_id = %s", (pet_name, user_id))

    async def update_user_pet_breed(self, user_id: int, pet_breed: str) -> None:
        """ Updates the User Pet's breed.
        :param user_id: The ID of the pet's owner.
        :param pet_breed: The new pet breed to update to. """

        await self.db.execute_query("UPDATE UserPets SET pet_breed = %s WHERE user_id = %s", (pet_breed, user_id))

    async def update_user_pet_name_breed_and_birth_ts(self, user_id: int, pet_name: str, pet_breed: str, birth_ts: int) -> None:
        """ Updates the User Pet's breed.
        :param user_id: The ID of the pet's owner.
        :param pet_name: The new pet name to update to.
        :param pet_breed: The new pet breed to update to.
        :param birth_ts: The birth timestamp """

        await self.db.execute_query("""
            UPDATE UserPets SET pet_name = %s, pet_breed = %s, birth_ts = %s WHERE user_id = %s
        """, (pet_name, pet_breed, birth_ts, user_id))

    async def update_user_pet_lp(self, user_id: int, increment: int = 5, current_ts: Optional[int] = None) -> None:
        """ Updates the User Pet's life points.
        :param user_id: The ID of the pet's owner.
        :param increment: The increment value to apply. [Default = 5] (Can be negative)
        :param current_ts: The current timestamp. [Optional] """

        if current_ts:
            await self.db.execute_query("UPDATE UserPets SET life_points = life_points + %s, life_points_ts = %s WHERE user_id = %s", (increment, current_ts, user_id))
        else:
            await self.db.execute_query("UPDATE UserPets SET life_points = life_points + %s WHERE user_id = %s", (increment, user_id))

    async def update_user_pet_food(self, user_id: int, increment: int = 5, current_ts: Optional[int] = None) -> None:
        """ Updates the User Pet's food status.
        :param user_id: The ID of the pet's owner.
        :param increment: The increment value to apply. [Default = 5] (Can be negative)
        :param current_ts: The current timestamp. [Optional] """

        if current_ts:
            await self.db.execute_query("UPDATE UserPets SET food = food + %s, food_ts = %s WHERE user_id = %s", (increment, current_ts, user_id))
        else:
            await self.db.execute_query("UPDATE UserPets SET food = food + %s WHERE user_id = %s", (increment, user_id))

    async def update_pet_auto_feed(self, user_id: int, auto_feed: bool = True) -> None:
        """ Updates the the pet's auto pay mode.
        :param user_id: The ID of the user who's the owner of the pet.
        :param auto_feed: Whether to put it into auto pay mode or not. [Default = True] """

        auto_feed = 1 if auto_feed else 0
        await self.db.execute_query("UPDATE UserPets SET auto_feed = %s WHERE user_id = %s", (auto_feed, user_id))

    async def delete_user_pet(self, user_id: int) -> None:
        """ Deletes the user's pet.
        :param user_id: The ID of the pet's owner. """

        await self.db.execute_query("DELETE FROM UserPets WHERE user_id = %s", (user_id,))
