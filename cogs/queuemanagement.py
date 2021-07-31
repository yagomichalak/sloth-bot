from discord import user
from mysqldb import the_database
import discord
from discord import client
from discord.ext import commands
import os
from extra import utils
from typing import List, Dict

moderator_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
owner_role_id = int(os.getenv('OWNER_ROLE_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))


class QueueManagement(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client
        # self.queues: Dict[int, List[int]] = {}

    @commands.Cog.listener()
    async def on_ready(self) -> None:


        # queues = await self.get_queues()
        # for queue in queues:
        #     if not self.queues.get(queue[0]):
        #         self.queues[queue[0]] = [queue[1:]]
        #     else:
        #         self.queues[queue[0]].append(queue[1:])

        print('QueueManagement cog is online!')

    @commands.group()
    @utils.is_allowed([teacher_role_id, moderator_role_id, admin_role_id, owner_role_id])
    async def queue(self, ctx) -> None:
        """ Command for managing and interacting with a queue.
        (Use this without a subcommand to see all subcommands available) """
        if ctx.invoked_subcommand:
            return

        cmd = self.client.get_command('queue')
        prefix = self.client.command_prefix
        subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands
            ]

        subcommands = '\n'.join(subcommands)
        items_embed = discord.Embed(
            title="__Subcommads__:",
            description=f"```apache\n{subcommands}```",
            color=ctx.author.color,
            timestamp=ctx.message.created_at
        )

        await ctx.send(embed=items_embed)

    @queue.command(aliases=['view', 'display', 'show'])
    async def see(self, ctx) -> None:
        """ Adds a list of members to do something with them later. """

        author = ctx.author
        guild = ctx.guild

        if not (queue := await self.get_queue_users(author.id)):
            return await ctx.send(f"**You don't have an active queue, {author.mention}!**")

        embed = discord.Embed(
            title=f"__{author.display_name}'s Queue__",
            description=f', '.join([f"<@{q}>" for q in queue]),
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=author.avatar.url)
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)
        
        await ctx.send(embed=embed)

    
    @queue.command(aliases=['add_members', 'addmembers', 'addlist', 'add_member_list', 'addmemberlist'])
    async def add(self, ctx) -> None:
        """ Adds a list of members to do something with them later. """

        author = ctx.author

        members = await utils.get_mentions(ctx.message)
        if not members:
            return await ctx.send(f"**Please, inform one or more members, {author.mention}!**")

        formatted_users = [(author.id, m.id) for m in members]
        await self.insert_queue_users(formatted_users)
        await ctx.send(f"**Successfully added `{len(members)}` into your Queue, {author.mention}!**")

    @queue.command(aliases=['delete', 'remove'])
    async def clear(self, ctx) -> None:
        """ Adds a list of members to do something with them later. """

        author = ctx.author
        if not await self.get_queue_users(author.id):
            return await ctx.send(f"**You don't a queue to clear, {author.mention}!**")

        await self.delete_queue_users(author.id)
        await ctx.send(f"**Successfully `cleared` your Queue, {author.mention}!**")


    @queue.command(aliases=['shuffle', 'random'])
    async def sort(self, ctx, number: int = None) -> None:
        """ Sorts X random members from the queue and returns them.
        :param number: The number of members to return. """

        author = ctx.author
        if not (queue := await self.get_queue_users(author.id)):
            return await ctx.send(f"**You don't have a queue to get members from, {author.mention}!**")

        if not number:
            return await ctx.send(f"**Please, provide a number of members to retrieve, {author.mention}!**")

        not_sorted = [qm for qm in queue if not qm[2]]
        if not not_sorted:
            return await ctx.send(
                f"**You have no members left to sort, considering reseting your queue members state with `z!queue reset`, {author.mention}!**")


    @queue.command()
    async def reset(self, ctx) -> None:
        """ Resets the queue members state,
        where it says whether they have been sorted yet or not. """

        author = ctx.author
        if not await self.get_queue_users(author.id):
            return await ctx.send(f"**You don't even have a queue with members, {author.mention}!**")

        await self.update_queue_users_state(author.id)
    

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

        mycursor, db = await the_database()
        await mycursor.execute("SELECT * FROM Queues WHERE owner_id = %s", (owner_id,))
        users = await mycursor.fetchall()
        await mycursor.close()
        return [u[1] for u in users]

    async def delete_queue_user(self, owner_id: int, user_id: int) -> None:
        """ Deletes a user from a Queue.
        :param owner_id: The ID of the owner of the queue.
        :param user_id: The ID of the user to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Queues WHERE owner_id = %s AND user_id = %s", (owner_id, user))
        await db.commit()
        await mycursor.close()

    async def delete_queue_users(self, owner_id: int) -> None:
        """ Deletes all users from a Queue.
        :param owner_id: The ID of the owner of the queue. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Queues WHERE owner_id = %s", (owner_id,))
        await db.commit()
        await mycursor.close()

    async def update_queue_users_state(self, owner_id: int) -> None:
        """ Updates the sorted state of queue members.
         """

        pass
        

def setup(client) -> None:
    client.add_cog(QueueManagement(client))