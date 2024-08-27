# import.standard
from typing import List, Union

# import.thirdparty
from discord.ext import commands

# import.local
from mysqldb import DatabaseCore

class MemberReminderTable(commands.Cog):
    """ Class for managing the MemberReminder table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_member_reminder(self, ctx) -> None:
        """ (ADM) Creates the MemberReminder table. """

        if await self.check_table_member_reminder():
            return await ctx.send("**Table __MemberReminder__ already exists!**")

        await ctx.message.delete()
        await self.db.execute_query("""CREATE TABLE MemberReminder (
            reminder_id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            text VARCHAR(100) NOT NULL,
            reminder_timestamp BIGINT NOT NULL,
            remind_in BIGINT NOT NULL,
            PRIMARY KEY (reminder_id)
            ) """)

        return await ctx.send("**Table __MemberReminder__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_member_reminder(self, ctx) -> None:
        """ (ADM) Creates the MemberReminder table """

        if not await self.check_table_member_reminder():
            return await ctx.send("**Table __MemberReminder__ doesn't exist!**")

        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE MemberReminder")

        return await ctx.send("**Table __MemberReminder__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_member_reminder(self, ctx) -> None:
        """ (ADM) Creates the MemberReminder table """

        if not await self.check_table_member_reminder():
            return await ctx.send("**Table __MemberReminder__ doesn't exist yet!**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM MemberReminder")

        return await ctx.send("**Table __MemberReminder__ reset!**", delete_after=3)

    async def check_table_member_reminder(self) -> bool:
        """ Checks if the MemberReminder table exists """

        return await self.db.table_exists("MemberReminder")

    async def insert_member_reminder(self, user_id: int, text: str, reminder_timestamp: int, remind_in: int) -> None:
        """ Inserts an entry concerning the user's last seen datetime.
        :param user_id: The ID of the user.
        :param text: The text that has to be reminded.
        :param reminder_timestamp: The current timestamp.
        :param remind_in: The amount of seconds to wait until reminding the user. """

        await self.db.execute_query("""
        INSERT INTO MemberReminder (user_id, text, reminder_timestamp, remind_in) 
        VALUES (%s, %s, %s, %s)""", (user_id, text, reminder_timestamp, remind_in))

    async def get_member_reminders(self, user_id: int) -> List[List[Union[str, int]]]:
        """ Gets the user's reminders.
        :param user_id: The ID of the user. """

        return await self.db.execute_query("SELECT * FROM MemberReminder WHERE user_id = %s", (user_id,), fetch="all")

    async def get_reminder(self, reminder_id: int) -> List[Union[str, int]]:
        """ Gets a reminder by ID.
        :param reminder_id: The reminder ID. """
        
        return await self.db.execute_query("SELECT * FROM MemberReminder WHERE reminder_id = %s", (reminder_id,), fetch="one")

    async def get_due_reminders(self, current_ts: int) -> List[int]:
        """ Gets reminders that are due.. 
        :param current_ts: The current timestamp. """

        reminders = await self.db.execute_query("SELECT * FROM MemberReminder WHERE (%s -  reminder_timestamp) >= remind_in", (current_ts,), fetch="all")
        return [(m[0], m[1], m[2]) for m in reminders]

    async def delete_member_reminder(self, reminder_id: int) -> None:
        """ Updates the user's last seen datetime.
        :param reminder_id: The ID of the reminder to delete. """

        await self.db.execute_query("DELETE FROM MemberReminder WHERE reminder_id = %s", (reminder_id,))
