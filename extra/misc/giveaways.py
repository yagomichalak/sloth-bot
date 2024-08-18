from discord.ext import commands
from mysqldb import DatabaseCore
from typing import List, Union, Optional
from random import choice

class GiveawaysTable(commands.Cog):
    """ Class for managing the Giveaways table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()
    
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_giveaways(self, ctx: commands.Context) -> None:
        """ Creates the Giveaways table. """

        member = ctx.author
        await ctx.message.delete()

        if await self.check_giveaways_exists():
            return await ctx.send(f"**Table `Giveaways` already exists, {member.mention}!**")
        
        await self.db.execute_query("""
            CREATE TABLE Giveaways (
                message_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                prize VARCHAR(100) DEFAULT NULL,
                winners INT DEFAULT 1,
                deadline_ts BIGINT NOT NULL,
                notified TINYINT(1) DEFAULT 0,
                role_id BIGINT DEFAULT NULL,
                user_id BIGINT NOT NULL,
                PRIMARY KEY(message_id)
            )""")

        await ctx.send(f"**Table `Giveaways` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_giveaways(self, ctx: commands.Context) -> None:
        """ Creates the Giveaways table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_giveaways_exists():
            return await ctx.send(f"**Table `Giveaways` doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE Giveaways")

        await ctx.send(f"**Table `Giveaways` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_giveaways(self, ctx: commands.Context) -> None:
        """ Creates the Giveaways table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_giveaways_exists():
            return await ctx.send(f"**Table `Giveaways` doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM Giveaways")

        await ctx.send(f"**Table `Giveaways` reset, {member.mention}!**")

    async def check_giveaways_exists(self) -> bool:
        """ Checks whether the Giveaways table exists. """

        return await self.db.table_exists("Giveaways")

    async def insert_giveaway(
        self, message_id: int, channel_id: int, user_id: int, 
        prize: str, winners: int, deadline_ts: int, role_id: Optional[int] = None) -> None:
        """ Inserts a giveaway.
        :param message_id: The ID of the message in which the giveaway is attached to.
        :param channel_id: The ID of the channel in which the giveaway is made.
        :param prize: The prize of the giveaway.
        :param winners: The amount of winners for the giveaway.
        :param deadline_ts: The deadline timestamp of the giveaway.
        :param role_id: The ID of the role for role-only giveaways. [Optional] """

        await self.db.execute_query("""
            INSERT INTO Giveaways (message_id, channel_id, prize, winners, deadline_ts, role_id, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", (
                message_id, channel_id, prize, winners, deadline_ts, role_id, user_id))

    async def get_giveaways(self) -> List[List[Union[str, int]]]:
        """ Gets all active giveaways. """

        return await self.db.execute_query("SELECT * FROM Giveaways", fetch="all")

    async def get_user_giveaways(self, user_id: int) -> List[List[Union[str, int]]]:
        """ Gets all active giveaways from a specific user.
        :param user_id: The ID of the user to get giveaways from. """

        return await self.db.execute_query("SELECT * FROM Giveaways WHERE user_id = %s", (user_id,), fetch="all")

    async def get_giveaway(self, message_id: int) -> List[Union[str, int]]:
        """ Gets a specific active giveaways.
        :param message_id: The ID of the message in which the giveaway is attached to. """

        return await self.db.execute_query("SELECT * FROM Giveaways WHERE message_id =  %s", (message_id,), fetch="one")

    async def get_due_giveaways(self, current_ts: int) -> List[List[Union[str, int]]]:
        """ Gets due giveaways.
        :param current_ts: The current timestamp to compare to registered giveaways' timestamps. """

        return await self.db.execute_query("SELECT * FROM Giveaways WHERE deadline_ts <= %s AND notified = 0", (current_ts,), fetch="all")

    async def update_giveaway(self, message_id: int, notified: Optional[int] = 1) -> None:
        """ Updates the giveaway's notified status.
        :param message_id: The ID of the message of the giveaway.
        :param notified: If it's gonna be set to true or false. [Optional][Default = 1 = True] """

        await self.db.execute_query("UPDATE Giveaways SET notified = %s WHERE message_id = %s", (notified, message_id))

    async def update_giveaway_deadline(self, message_id: int, current_ts: int) -> None:
        """ Updates the giveaway's deadline timestamp..
        :param message_id: The ID of the message of the giveaway.
        :param current_ts: The current timestamp. """

        await self.db.execute_query("UPDATE Giveaways SET deadline_ts = %s WHERE message_id = %s", (current_ts, message_id))

    async def delete_giveaway(self, message_id: int) -> None:
        """ Deletes a giveaway.
        :param message_id: The ID of the message in which the giveaway is attached to. """

        await self.db.execute_query("DELETE FROM Giveaways WHERE message_id = %s", (message_id,))

    async def delete_old_giveaways(self, current_ts: int) -> None:
        """ Deletes old ended giveaways of at least 2 days ago. """

        await self.db.execute_query("""
            DELETE FROM Giveaways WHERE notified = 1 AND %s - deadline_ts >= 172800""", (current_ts,))


class GiveawayEntriesTable(commands.Cog):
    """ Class for managing the GiveawayEntries table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_giveaway_entries(self, ctx: commands.Context) -> None:
        """ Creates the GiveawayEntries table. """

        member = ctx.author
        await ctx.message.delete()

        if await self.check_giveaway_entries_exists():
            return await ctx.send(f"**Table `GiveawayEntries` already exists, {member.mention}!**")
        
        await self.db.execute_query("""
            CREATE TABLE GiveawayEntries (
                user_id BIGINT NOT NULL,
                message_id BIGINT NOT NULL,
                PRIMARY KEY (user_id, message_id),
                CONSTRAINT fk_ga_msg_id FOREIGN KEY (message_id) REFERENCES Giveaways (message_id) ON UPDATE CASCADE ON DELETE CASCADE
            )""")

        await ctx.send(f"**Table `GiveawayEntries` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_giveaway_entries(self, ctx: commands.Context) -> None:
        """ Creates the GiveawayEntries table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_giveaway_entries_exists():
            return await ctx.send(f"**Table `GiveawayEntries` doesn't exist, {member.mention}!**")

        await self.db.execute_query("DROP TABLE GiveawayEntries")

        await ctx.send(f"**Table `GiveawayEntries` dropped, {member.mention}!**")


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_giveaway_entries(self, ctx: commands.Context) -> None:
        """ Creates the GiveawayEntries table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_giveaway_entries_exists():
            return await ctx.send(f"**Table `GiveawayEntries` doesn't exist yet, {member.mention}!**")

        await self.db.execute_query("DELETE FROM GiveawayEntries")

        await ctx.send(f"**Table `GiveawayEntries` reset, {member.mention}!**")

    async def check_giveaway_entries_exists(self) -> bool:
        """ Checks whether the GiveawayEntries table exists. """

        return await self.db.table_exists("GiveawayEntries")

    async def insert_giveaway_entry(self, user_id: int, message_id: int) -> None:
        """ Inserts an entry for an active giveaway.
        :param user_id: The ID of the user who's participating in the giveaway.
        :param message_id: The ID of the message of the giveaway the user is participating in. """

        await self.db.execute_query("INSERT INTO GiveawayEntries (user_id, message_id) VALUES (%s, %s)", (user_id, message_id))


    async def get_giveaway_entry(self, user_id: int, message_id: int) -> List[Union[str, int]]:
        """ Gets a specific entry from an active giveaway.
        :param user_id: The ID of the user to get.
        :param message_id: The ID of the message of the giveaway. """

        return await self.db.execute_query("SELECT * FROM GiveawayEntries WHERE user_id = %s AND message_id = %s", (user_id, message_id), fetch="one")

    async def get_giveaway_entries(self, message_id: int) -> List[List[Union[str, int]]]:
        """ Gets all entries from an active giveaway.
        :param message_id: The ID of the message of the giveaway. """

        return await self.db.execute_query("SELECT * FROM GiveawayEntries WHERE message_id = %s", (message_id,), fetch="all")

    async def delete_giveaway_entry(self, user_id: int, message_id: int) -> None:
        """ Deletes an entry from an active giveaway.
        :param user_id: The ID of the user who was participating in the giveaway.
        :param message_id: The ID of the message of the giveaway the user was participating in. """

        await self.db.execute_query("DELETE FROM GiveawayEntries WHERE user_id = %s AND message_id = %s", (user_id, message_id))

    async def get_winners(self, giveaway: List[Union[str, int]], entries: List[List[Union[str, int]]]) -> str:
        """ Gets text-formatted winners from giveaways.
        :param giveaway: The giveaway to get the winners from. """

        if not entries:
            return 'No one, since there were no entries in this giveaway'

        amount_of_winners = giveaway[3]

        winners = []

        while True:
            winner = choice(entries)
            # Checks whether winner is not in the list yet
            if winner not in winners:
                winners.append(winner)

            # Checks whether it sorted the required amount of winners
            if len(winners) == amount_of_winners:
                break

            # Checks whether there are enough entries to sort more winners
            if len(entries) < amount_of_winners:
                break

        return ', '.join([f"<@{w[0]}>" for w in winners])
