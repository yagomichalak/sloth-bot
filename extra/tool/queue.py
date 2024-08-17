from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List, Tuple


class QueuesTable(commands.Cog):
    """ Class for managing the QueueTable table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_queues(self, ctx: commands.Context) -> None:
        """ Creates the Queues table. """

        member = ctx.author
        await ctx.message.delete()

        if await self.check_table_queues_exists():
            return await ctx.send(f"**Table `Queues` already exists, {member.mention}!**")
        
        await self.db.execute_query("""
        CREATE TABLE Queues (
            owner_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            sorted TINYINT DEFAULT 0,
            PRIMARY KEY (owner_id, user_id)
        )
        """)

        await ctx.send(f"**Table `Queues` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_queues(self, ctx: commands.Context) -> None:
        """ Creates the Queues table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_table_queues_exists():
            return await ctx.send(f"**Table `Queues` doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE Queues")

        await ctx.send(f"**Table `Queues` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_queues(self, ctx: commands.Context) -> None:
        """ Creates the Queues table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_table_queues_exists():
            return await ctx.send(f"**Table `Queues` doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM Queues")

        await ctx.send(f"**Table `Queues` reset, {member.mention}!**")

    async def check_table_queues_exists(self) -> bool:
        """ Checks whether the Queues table exists. """

        return await self.db.table_exists("Queues")

    async def insert_queue_users(self, users: List[int]) -> None:
        """ Insert users into a Queue.
        :param users: The users to insert. """

        await self.db.execute_query("INSERT IGNORE INTO Queues (owner_id, user_id) VALUES (%s, %s)", users, execute_many=True)

    async def get_queue_users(self, owner_id: int) -> List[int]:
        """ Gets Queue users.
        :param owner_id: The owner ID of the queue from which to get users. """

        return await self.db.execute_query("SELECT * FROM Queues WHERE owner_id = %s", (owner_id,), fetch="all")

    async def update_queue_users_state(self, owner_id: int, maybe: int = 1) -> None:
        """ Updates the sorted state of queue members.
        :param owner_id: The ID of the owner of the queue.
        :param maybe: True or False but as integer. 0-1 """

        await self.db.execute_query("UPDATE Queues SET sorted = %s WHERE owner_id = %s", (maybe, owner_id))

    async def update_queue_specific_users_state(self, users: List[Tuple[int]]) -> None:
        """ Updates the sorted state of specific queue members.
        :param users: The list of users to update. """

        await self.db.execute_query("UPDATE Queues SET sorted = %s WHERE owner_id = %s and user_id = %s", users, execute_many=True)

    async def delete_queue_user(self, owner_id: int, user_id: int) -> None:
        """ Deletes a user from a Queue.
        :param owner_id: The ID of the owner of the queue.
        :param user_id: The ID of the user to delete. """

        await self.db.execute_query("DELETE FROM Queues WHERE owner_id = %s AND user_id = %s", (owner_id, user_id))

    async def delete_specific_queue_users(self, users: List[int]) -> None:
        """ Deletes a user from a Queue.
        :param users: The list of users to delete. """

        await self.db.execute_query("DELETE FROM Queues WHERE owner_id = %s AND user_id = %s", users, execute_many=True)

    async def delete_queue_users(self, owner_id: int) -> None:
        """ Deletes all users from a Queue.
        :param owner_id: The ID of the owner of the queue. """

        await self.db.execute_query("DELETE FROM Queues WHERE owner_id = %s", (owner_id,))
