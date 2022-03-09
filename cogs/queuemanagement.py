import discord
from discord.ext import commands
import os
from extra import utils
from random import shuffle
from extra.tool.queue import QueuesTable

moderator_role_id = int(os.getenv('MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID', 123))
event_host_role_id = int(os.getenv('EVENT_MANAGER_ROLE_ID', 123))

class QueueManagement(QueuesTable):
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
            
def setup(client) -> None:
    client.add_cog(QueueManagement(client))