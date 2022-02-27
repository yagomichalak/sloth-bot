import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List, Union

class MemberReminderTable(commands.Cog):
    """ Class for managing the MemberReminder table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_member_reminder(self, ctx) -> None:
        """ (ADM) Creates the MemberReminder table. """

        if await self.check_table_member_reminder():
            return await ctx.send("**Table __MemberReminder__ already exists!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("""CREATE TABLE MemberReminder (
            reminder_id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            text VARCHAR(100) NOT NULL,
            reminder_timestamp BIGINT NOT NULL,
            remind_in BIGINT NOT NULL,
            PRIMARY KEY (reminder_id)
            ) """)
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __MemberReminder__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_member_reminder(self, ctx) -> None:
        """ (ADM) Creates the MemberReminder table """

        if not await self.check_table_member_reminder():
            return await ctx.send("**Table __MemberReminder__ doesn't exist!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE MemberReminder")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __MemberReminder__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_member_reminder(self, ctx) -> None:
        """ (ADM) Creates the MemberReminder table """

        if not await self.check_table_member_reminder():
            return await ctx.send("**Table __MemberReminder__ doesn't exist yet!**")

        await ctx.message.delete()
        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM MemberReminder")
        await db.commit()
        await mycursor.close()

        return await ctx.send("**Table __MemberReminder__ reset!**", delete_after=3)

    async def check_table_member_reminder(self) -> bool:
        """ Checks if the MemberReminder table exists """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'MemberReminder'")
        table_info = await mycursor.fetchone()
        await mycursor.close()

        if table_info:
            return True
        else:
            return False

    async def insert_member_reminder(self, user_id: int, text: str, reminder_timestamp: int, remind_in: int) -> None:
        """ Inserts an entry concerning the user's last seen datetime.
        :param user_id: The ID of the user.
        :param text: The text that has to be reminded.
        :param reminder_timestamp: The current timestamp.
        :param remind_in: The amount of seconds to wait until reminding the user. """

        mycursor, db = await the_database()
        await mycursor.execute("""
        INSERT INTO MemberReminder (user_id, text, reminder_timestamp, remind_in) 
        VALUES (%s, %s, %s, %s)""", (user_id, text, reminder_timestamp, remind_in))
        await db.commit()
        await mycursor.close()

    async def get_member_reminders(self, user_id: int) -> List[List[Union[str, int]]]:
        """ Gets the user's reminders.
        :param user_id: The ID of the user. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM MemberReminder WHERE user_id = %s", (user_id,))
        reminders = await mycursor.fetchall()
        await mycursor.close()
        return reminders

    async def get_reminder(self, reminder_id: int) -> List[Union[str, int]]:
        """ Gets a reminder by ID.
        :param reminder_id: The reminder ID. """
        
        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM MemberReminder WHERE reminder_id = %s", (reminder_id,))
        reminder = await mycursor.fetchone()
        await mycursor.close()
        return reminder

    async def get_due_reminders(self, current_ts: int) -> List[int]:
        """ Gets reminders that are due.. 
        :param current_ts: The current timestamp. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM MemberReminder WHERE (%s -  reminder_timestamp) >= remind_in", (current_ts,))
        reminders = [(m[0], m[1], m[2]) for m in await mycursor.fetchall()]
        await mycursor.close()
        return reminders

    async def delete_member_reminder(self, reminder_id: int) -> None:
        """ Updates the user's last seen datetime.
        :param reminder_id: The ID of the reminder to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM MemberReminder WHERE reminder_id = %s", (reminder_id,))
        await db.commit()
        await mycursor.close()