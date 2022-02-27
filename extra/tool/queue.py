from discord.ext import commands
from mysqldb import the_database
from typing import List, Tuple

class QueuesTable(commands.Cog):
    """ Class for managing the QueueTable table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_queues(self, ctx: commands.Context) -> None:
        """ Creates the Queues table. """

        member = ctx.author
        await ctx.message.delete()

        if await self.check_table_queues_exists():
            return await ctx.send(f"**Table `Queues` already exists, {member.mention}!**")
        
        mycursor, db = await the_database()
        await mycursor.execute("""
        CREATE TABLE Queues (
            owner_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            sorted TINYINT DEFAULT 0,
            PRIMARY KEY (owner_id, user_id)
        )
        """)
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `Queues` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_queues(self, ctx: commands.Context) -> None:
        """ Creates the Queues table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_table_queues_exists():
            return await ctx.send(f"**Table `Queues` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Queues")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `Queues` dropped, {member.mention}!**")


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_queues(self, ctx: commands.Context) -> None:
        """ Creates the Queues table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_table_queues_exists():
            return await ctx.send(f"**Table `Queues` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Queues")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `Queues` reset, {member.mention}!**")

    async def check_table_queues_exists(self) -> bool:
        """ Checks whether the Queues table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Queues'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_queue_users(self, users: List[int]) -> None:
        """ Insert users into a Queue.
        :param users: The users to insert. """

        mycursor, db = await the_database()
        await mycursor.executemany("INSERT IGNORE INTO Queues (owner_id, user_id) VALUES (%s, %s)", users)
        await db.commit()
        await mycursor.close()

    async def get_queue_users(self, owner_id: int) -> List[int]:
        """ Gets Queue users.
        :param owner_id: The owner ID of the queue from which to get users. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Queues WHERE owner_id = %s", (owner_id,))
        users = await mycursor.fetchall()
        await mycursor.close()
        return users

    async def update_queue_users_state(self, owner_id: int, maybe: int = 1) -> None:
        """ Updates the sorted state of queue members.
        :param owner_id: The ID of the owner of the queue.
        :param maybe: True or False but as integer. 0-1 """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE Queues SET sorted = %s WHERE owner_id = %s", (maybe, owner_id))
        await db.commit()
        await mycursor.close()

    async def update_queue_specific_users_state(self, users: List[Tuple[int]]) -> None:
        """ Updates the sorted state of specific queue members.
        :param users: The list of users to update. """

        mycursor, db = await the_database()
        await mycursor.executemany("UPDATE Queues SET sorted = %s WHERE owner_id = %s and user_id = %s", users)
        await db.commit()
        await mycursor.close()


    async def delete_queue_user(self, owner_id: int, user_id: int) -> None:
        """ Deletes a user from a Queue.
        :param owner_id: The ID of the owner of the queue.
        :param user_id: The ID of the user to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Queues WHERE owner_id = %s AND user_id = %s", (owner_id, user_id))
        await db.commit()
        await mycursor.close()

    async def delete_specific_queue_users(self, users: List[int]) -> None:
        """ Deletes a user from a Queue.
        :param users: The list of users to delete. """

        mycursor, db = await the_database()
        await mycursor.executemany("DELETE FROM Queues WHERE owner_id = %s AND user_id = %s", users)
        await db.commit()
        await mycursor.close()

    async def delete_queue_users(self, owner_id: int) -> None:
        """ Deletes all users from a Queue.
        :param owner_id: The ID of the owner of the queue. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Queues WHERE owner_id = %s", (owner_id,))
        await db.commit()
        await mycursor.close()