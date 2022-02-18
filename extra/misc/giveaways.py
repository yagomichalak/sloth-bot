import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union, Optional
from random import choice

class GiveawaysTable(commands.Cog):
    """ Class for managing the Giveaways table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
    
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_giveaways(self, ctx: commands.Context) -> None:
        """ Creates the Giveaways table. """

        member = ctx.author
        await ctx.message.delete()

        if await self.check_giveaways_exists():
            return await ctx.send(f"**Table `Giveaways` already exists, {member.mention}!**")
        
        mycursor, db = await the_database()
        await mycursor.execute("""
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
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `Giveaways` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_giveaways(self, ctx: commands.Context) -> None:
        """ Creates the Giveaways table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_giveaways_exists():
            return await ctx.send(f"**Table `Giveaways` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Giveaways")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `Giveaways` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_giveaways(self, ctx: commands.Context) -> None:
        """ Creates the Giveaways table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_giveaways_exists():
            return await ctx.send(f"**Table `Giveaways` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Giveaways")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `Giveaways` reset, {member.mention}!**")

    async def check_giveaways_exists(self) -> bool:
        """ Checks whether the Giveaways table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Giveaways'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

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

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO Giveaways (message_id, channel_id, prize, winners, deadline_ts, role_id, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", (
                message_id, channel_id, prize, winners, deadline_ts, role_id, user_id))
        await db.commit()
        await mycursor.close()

    async def get_giveaways(self) -> List[List[Union[str, int]]]:
        """ Gets all active giveaways. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Giveaways")
        giveaways = await mycursor.fetchall()
        await mycursor.close()
        return giveaways

    async def get_user_giveaways(self, user_id: int) -> List[List[Union[str, int]]]:
        """ Gets all active giveaways from a specific user.
        :param user_id: The ID of the user to get giveaways from. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Giveaways WHERE user_id = %s", (user_id,))
        giveaways = await mycursor.fetchall()
        await mycursor.close()
        return giveaways

    async def get_giveaway(self, message_id: int) -> List[Union[str, int]]:
        """ Gets a specific active giveaways.
        :param message_id: The ID of the message in which the giveaway is attached to. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Giveaways WHERE message_id =  %s", (message_id,))
        giveaway = await mycursor.fetchone()
        await mycursor.close()
        return giveaway

    async def get_due_giveaways(self, current_ts: int) -> List[List[Union[str, int]]]:
        """ Gets due giveaways.
        :param current_ts: The current timestamp to compare to registered giveaways' timestamps. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Giveaways WHERE deadline_ts <= %s AND notified = 0", (current_ts,))
        giveaways = await mycursor.fetchall()
        await mycursor.close()
        return giveaways

    async def update_giveaway(self, message_id: int, notified: Optional[int] = 1) -> None:
        """ Updates the giveaway's notified status.
        :param message_id: The ID of the message of the giveaway.
        :param notified: If it's gonna be set to true or false. [Optional][Default = 1 = True] """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE Giveaways SET notified = %s WHERE message_id = %s", (notified, message_id))
        await db.commit()
        await mycursor.close()

    async def update_giveaway_deadline(self, message_id: int, current_ts: int) -> None:
        """ Updates the giveaway's deadline timestamp..
        :param message_id: The ID of the message of the giveaway.
        :param current_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE Giveaways SET deadline_ts = %s WHERE message_id = %s", (current_ts, message_id))
        await db.commit()
        await mycursor.close()

    async def delete_giveaway(self, message_id: int) -> None:
        """ Deletes a giveaway.
        :param message_id: The ID of the message in which the giveaway is attached to. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Giveaways WHERE message_id = %s", (message_id,))
        await db.commit()
        await mycursor.close()

    async def delete_old_giveaways(self, current_ts: int) -> None:
        """ Deletes old ended giveaways of at least 2 days ago. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            DELETE FROM Giveaways WHERE notified = 1 AND %s - deadline_ts >= 172800""", (current_ts,))
        await db.commit()
        await mycursor.close()

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
        
        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE GiveawayEntries (
                user_id BIGINT NOT NULL,
                message_id BIGINT NOT NULL,
                PRIMARY KEY (user_id, message_id),
                CONSTRAINT fk_ga_msg_id FOREIGN KEY (message_id) REFERENCES Giveaways (message_id) ON UPDATE CASCADE ON DELETE CASCADE
            )""")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `GiveawayEntries` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_giveaway_entries(self, ctx: commands.Context) -> None:
        """ Creates the GiveawayEntries table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_giveaway_entries_exists():
            return await ctx.send(f"**Table `GiveawayEntries` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE GiveawayEntries")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `GiveawayEntries` dropped, {member.mention}!**")


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_giveaway_entries(self, ctx: commands.Context) -> None:
        """ Creates the GiveawayEntries table. """

        member = ctx.author
        await ctx.message.delete()

        if not await self.check_giveaway_entries_exists():
            return await ctx.send(f"**Table `GiveawayEntries` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM GiveawayEntries")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Table `GiveawayEntries` reset, {member.mention}!**")

    async def check_giveaway_entries_exists(self) -> bool:
        """ Checks whether the GiveawayEntries table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'GiveawayEntries'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    async def insert_giveaway_entry(self, user_id: int, message_id: int) -> None:
        """ Inserts an entry for an active giveaway.
        :param user_id: The ID of the user who's participating in the giveaway.
        :param message_id: The ID of the message of the giveaway the user is participating in. """

        mycursor, db = await the_database()
        await mycursor.execute("INSERT INTO GiveawayEntries (user_id, message_id) VALUES (%s, %s)", (user_id, message_id))
        await db.commit()
        await mycursor.close()


    async def get_giveaway_entry(self, user_id: int, message_id: int) -> List[Union[str, int]]:
        """ Gets a specific entry from an active giveaway.
        :param user_id: The ID of the user to get.
        :param message_id: The ID of the message of the giveaway. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM GiveawayEntries WHERE user_id = %s AND message_id = %s", (user_id, message_id))
        entry = await mycursor.fetchone()
        await mycursor.close()
        return entry

    async def get_giveaway_entries(self, message_id: int) -> List[List[Union[str, int]]]:
        """ Gets all entries from an active giveaway.
        :param message_id: The ID of the message of the giveaway. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM GiveawayEntries WHERE message_id = %s", (message_id,))
        entries = await mycursor.fetchall()
        await mycursor.close()
        return entries

    async def delete_giveaway_entry(self, user_id: int, message_id: int) -> None:
        """ Deletes an entry from an active giveaway.
        :param user_id: The ID of the user who was participating in the giveaway.
        :param message_id: The ID of the message of the giveaway the user was participating in. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM GiveawayEntries WHERE user_id = %s AND message_id = %s", (user_id, message_id))
        await db.commit()
        await mycursor.close()

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
