from discord import user
from mysqldb import the_database
import discord
from discord.ext import commands
import os
from extra import utils
from typing import List, Tuple
from random import shuffle

moderator_role_id = int(os.getenv('MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
owner_role_id = int(os.getenv('OWNER_ROLE_ID'))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))
event_host_role_id = int(os.getenv('EVENT_MANAGER_ROLE_ID'))

class QueueManagement(commands.Cog):
    """ Category for creating, managing and interacting with queues. """

    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print('QueueManagement cog is online!')

    @commands.group()
    @utils.is_allowed([event_host_role_id, teacher_role_id, moderator_role_id, admin_role_id, owner_role_id], throw_exc=True)
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
            description=f', '.join([f"<@{q[1]}> ({q[2]})" for q in queue]),
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=author.display_avatar)
        embed.set_footer(text="0 - Not sorted | 1 - Sorted", icon_url=guild.icon.url)
        
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

    @queue.command(aliases=['remove_members', 'removemembers', 'removelist', 'remove_member_list', 'removememberlist'])
    async def remove(self, ctx) -> None:
        """ Removes one or more members from the your queue list. """

        author = ctx.author

        members = await utils.get_mentions(ctx.message)
        if not members:
            return await ctx.send(f"**Please, inform one or more members, {author.mention}!**")

        formatted_users = [(author.id, m.id) for m in members]
        await self.delete_specific_queue_users(formatted_users)
        await ctx.send(f"**Successfully removed the users from your Queue, {author.mention}!**")

    @queue.command(aliases=['erase'])
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


        if len(not_sorted) < number:
            return await ctx.send(f"**You want `{number}` members, but your queue list only has `{len(not_sorted)}` unsorted members remaining, {author.mention}!**")

        shuffle(not_sorted)
        sorted = not_sorted[:number]
        await self.update_queue_specific_users_state([(1, s[0], s[1]) for s in sorted])

        embed = discord.Embed(
            title=f"__Sorted {number} Members!__",
            description=', '.join([f"<@{s[1]}>" for s in sorted]),
            color=author.color,
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=embed)


    @queue.command()
    async def reset(self, ctx) -> None:
        """ Resets the queue members state,
        where it says whether they have been sorted yet or not. """

        author = ctx.author
        if not await self.get_queue_users(author.id):
            return await ctx.send(f"**You don't even have a queue with members, {author.mention}!**")

        await self.update_queue_users_state(author.id, 0)
        await ctx.send(f"**Successfully updated queue member states, {author.mention}!**")
    

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
        return users

    async def delete_queue_user(self, owner_id: int, user_id: int) -> None:
        """ Deletes a user from a Queue.
        :param owner_id: The ID of the owner of the queue.
        :param user_id: The ID of the user to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Queues WHERE owner_id = %s AND user_id = %s", (owner_id, user))
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
        

def setup(client) -> None:
    client.add_cog(QueueManagement(client))