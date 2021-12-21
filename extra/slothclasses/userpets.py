import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union, Optional
from extra import utils


class UserPetsTable(commands.Cog):
    """ Class for the UserPets table and its commands and methods. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_pets(self, ctx) -> None:
        """ Creates the UserPets table in the database. """

        member: discord.Member = ctx.author
        if await self.check_user_pets_table_exists():
            return await ctx.send(f"**The UserPets table already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE UserPets (
            user_id BIGINT NOT NULL,
            pet_name VARCHAR(25) DEFAULT 'Egg',
            pet_breed VARCHAR(25) DEFAULT 'Egg',
            life_points TINYINT(3) DEFAULT 100,
            food TINYINT(3) DEFAULT 100,
            life_points_ts BIGINT NOT NULL,
            food_ts BIGINT NOT NULL,
            PRIMARY KEY (user_id)
            ) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**`UserPets` table created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_pets(self, ctx) -> None:
        """ Drops the UserPets table from the database. """

        member: discord.Member = ctx.author
        if not await self.check_user_pets_table_exists():
            return await ctx.send(f"**The UserPets table doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE UserPets")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**`UserPets` table dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_pets(self, ctx) -> None:
        """ Resets the UserPets table in the database. """

        member: discord.Member = ctx.author
        if not await self.check_user_pets_table_exists():
            return await ctx.send(f"**The UserPets table doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserPets")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**`UserPets` table reset, {member.mention}!**")

    async def check_user_pets_table_exists(self) -> bool:
        """ Checks whether the UserPets table exists in the database. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'UserPets'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_user_pet(self, user_id: int, pet_name: Optional[str] = None, pet_breed: Optional[str] = None) -> None:
        """ Inserts a User Pet.
        :param user_id: The ID of the user owner of the pet.
        :param pet_name: The name of the pet. [Optional]
        :param pet_breed: The breed of the pet. [Optional]"""

        current_ts = await utils.get_timestamp()
        current_ts = current_ts + 3600

        mycursor, db = await the_database()
        if pet_name and pet_breed:
            await mycursor.execute("INSERT INTO UserPets (user_id, pet_name, pet_breed, life_points_ts, food_ts) VALUES (%s, %s, %s, %s, %s)", (user_id, pet_name, pet_breed, current_ts, current_ts))
        else:
            await mycursor.execute("INSERT INTO UserPets (user_id, life_points_ts, food_ts) VALUES (%s, %s, %s)", (user_id, current_ts, current_ts))
        await db.commit()
        await mycursor.close()

    async def get_user_pet(self, user_id: int) -> List[Union[str, int]]:
        """ Get the user's pet.
        :param user_id: The ID of the pet's owner. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserPets WHERE user_id = %s", (user_id,))
        user_pet = await mycursor.fetchone()
        await mycursor.close()
        return user_pet

    async def get_pets(self) -> List[List[Union[str, int]]]:
        """ Get all user pets. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserPets")
        user_pets = await mycursor.fetchall()
        await mycursor.close()
        return user_pets

    async def get_hungry_pets(self, current_ts: int) -> List[List[Union[str, int]]]:
        """ Get all user hungry pets.
        :param current_ts: The current timestamp. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM UserPets WHERE %s - food_ts >= 3600", (current_ts,))
        user_pets = await mycursor.fetchall()
        await mycursor.close()
        return user_pets

    async def update_user_pet_name(self, user_id: int, pet_name: str) -> None:
        """ Updates the User Pet's name.
        :param user_id: The ID of the pet's owner.
        :param pet_name: The new pet name to update to. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserPets SET pet_name = %s WHERE user_id = %s", (pet_name, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_pet_breed(self, user_id: int, pet_breed: str) -> None:
        """ Updates the User Pet's breed.
        :param user_id: The ID of the pet's owner.
        :param pet_breed: The new pet breed to update to. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserPets SET pet_breed = %s WHERE user_id = %s", (pet_breed, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_pet_lp(self, user_id: int, increment: int = 5, current_ts: Optional[int] = None) -> None:
        """ Updates the User Pet's life points.
        :param user_id: The ID of the pet's owner.
        :param increment: The increment value to apply. [Default = 5] (Can be negative)
        :param current_ts: The current timestamp. [Optional] """

        mycursor, db = await the_database()
        if current_ts:
            await mycursor.execute("UPDATE UserPets SET life_points = life_points + %s, life_points_ts = %s WHERE user_id = %s", (increment, current_ts, user_id))
        else:
            await mycursor.execute("UPDATE UserPets SET life_points = life_points + %s WHERE user_id = %s", (increment, user_id))

        await db.commit()
        await mycursor.close()

    async def update_user_pet_food(self, user_id: int, increment: int = 5, current_ts: Optional[int] = None) -> None:
        """ Updates the User Pet's food status.
        :param user_id: The ID of the pet's owner.
        :param increment: The increment value to apply. [Default = 5] (Can be negative)
        :param current_ts: The current timestamp. [Optional] """

        mycursor, db = await the_database()
        if current_ts:
            await mycursor.execute("UPDATE UserPets SET food = food + %s, food_ts = %s WHERE user_id = %s", (increment, current_ts, user_id))
        else:
            await mycursor.execute("UPDATE UserPets SET food = food + %s WHERE user_id = %s", (increment, user_id))

        await db.commit()
        await mycursor.close()


    async def delete_user_pet(self, user_id: int) -> None:
        """ Deletes the user's pet.
        :param user_id: The ID of the pet's owner. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserPets WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

