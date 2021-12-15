import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union, Optional


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

        mycursor, db = await the_database()
        if pet_name and pet_breed:
            await mycursor.execute("INSERT INTO UserPets (user_id, pet_name, pet_breed) VALUES (%s, %s, %s)", (user_id, pet_name, pet_breed))
        else:
            await mycursor.execute("INSERT INTO UserPets (user_id) VALUES (%s)", (user_id,))
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

    async def delete_user_pet(self, user_id: int) -> None:
        """ Deletes the user's pet.
        :param user_id: The ID of the pet's owner. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM UserPets WHERE user_id = %s", (user_id,))
        await db.commit()
        await mycursor.close()

