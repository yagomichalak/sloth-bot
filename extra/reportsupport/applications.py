import discord
from discord.ext import commands
from mysqldb import the_database
from typing import List

class ApplicationsTable(commands.Cog):
    """ Cog for managing applications. """

    def __init__(self, client) -> None:
        self.client = client

    # Applications

    async def get_application_by_message(self, message_id: int, application_type: str) -> List[str]:
        """ Gets a application application from the database by message ID.
        :param message_id: The message ID.
        :param application_type: The type of the application. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Applications WHERE message_id = %s AND application_type = %s", (message_id, application_type))
        application_app = await mycursor.fetchone()
        await mycursor.close()
        return application_app

    async def get_application_by_channel(self, channel_id: int, application_type: str) -> List[str]:
        """ Gets a application application from the database by channel ID.
        :param channel_id: The text channel ID.
        :param application_type: The type of the application. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM Applications WHERE txt_id = %s AND application_type = %s", (channel_id, application_type))
        application_app = await mycursor.fetchone()
        await mycursor.close()
        return application_app

    async def save_application(self, message_id: int, applicant_id: int, application_type: str) -> None:
        """ Saves a application application into the database.
        :param message_id: The ID of the applicaiton message.
        :param applicant_id: The application ID.
        :param application_type: The type of the application. """

        mycursor, db = await the_database()
        await mycursor.execute(
            """
            INSERT INTO Applications (message_id, applicant_id, application_type)
            VALUES (%s, %s, %s)""", (message_id, applicant_id, application_type)
            )
        await db.commit()
        await mycursor.close()

    async def update_application(self, applicant_id: int, txt_id: int, vc_id: int, application_type: str) -> None:
        """ Updates the application; adding the txt and vc ids into it.
        :param applicant_id: The application ID.
        :param txt_id: The text channel ID.
        :param vc_id: The voice channel ID.
        :param application_type: The type of application to update. """

        mycursor, db = await the_database()
        await mycursor.execute(
            """UPDATE Applications SET
            channel_open = 1, txt_id = %s, vc_id = %s
            WHERE applicant_id = %s AND application_type = %s""", (txt_id, vc_id, applicant_id, application_type)
            )
        await db.commit()
        await mycursor.close()

    async def delete_application(self, message_id: int, application_type: str) -> None:
        """ Deletes a application application from the database.
        :param message_id: The application message's ID.
        :param application_type: The type of application to delete. """

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Applications WHERE message_id = %s AND application_type = %s", (message_id, application_type))
        await db.commit()
        await mycursor.close()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_application(self, ctx) -> None:
        """ (ADM) Creates the Applications table. """

        if await self.table_applications_exists():
            return await ctx.send("**Table `Applications` already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE Applications (
                message_id BIGINT, applicant_id BIGINT,
                application_type VARCHAR(50),
                channel_open TINYINT(1) DEFAULT 0,
                txt_id BIGINT DEFAULT NULL, vc_id BIGINT DEFAULT NULL
            )""")

        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `Applications` created!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_application(self, ctx) -> None:
        """ (ADM) Drops the Applications table. """

        if not await self.table_applications_exists():
            return await ctx.send("**Table `Applications` doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE Applications")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `Applications` dropped!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_applications(self, ctx) -> None:
        """ (ADM) Resets the Applications table. """

        if not await self.table_applications_exists():
            return await ctx.send("**Table `Applications` doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM Applications")
        await db.commit()
        await mycursor.close()

        await ctx.send("**Table `Applications` reset!**")

    async def table_applications_exists(self) -> bool:
        """ Checks whether the Applications table exists. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'Applications'")
        exists = await mycursor.fetchall()
        await mycursor.close()

        if len(exists):
            return True
        else:
            return False
