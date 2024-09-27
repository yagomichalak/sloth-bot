# import.standard
from typing import List, Union, Optional

# import.thirdparty
from discord.ext import commands

# import.local
from mysqldb import DatabaseCore
from extra import utils


class SlothActionsTable(commands.Cog):
    """ Class for managing the SlothActions table in the database. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client
        self.db = DatabaseCore()

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_actions(self, ctx) -> None:
        """ (ADM) Creates the SlothActions table. """

        if await self.check_table_sloth_actions():
            return await ctx.send("**Table __SlothActions__ already exists!**")

        await ctx.message.delete()
        await self.db.execute_query("""CREATE TABLE SlothActions (
            label VARCHAR(100) NOT NULL,
            user_id BIGINT NOT NULL,
            target_id BIGINT DEFAULT NULL,
            text_content VARCHAR(255) DEFAULT NULL,
            int_content VARCHAR(100) DEFAULT NULL,
            created_ts BIGINT NOT NULL
        ) """)

        return await ctx.send("**Table __SlothActions__ created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_sloth_actions(self, ctx) -> None:
        """ (ADM) Creates the SlothActions table """

        if not await self.check_table_sloth_actions():
            return await ctx.send("**Table __SlothActions__ doesn't exist!**")

        await ctx.message.delete()
        await self.db.execute_query("DROP TABLE SlothActions")

        return await ctx.send("**Table __SlothActions__ dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_sloth_actions(self, ctx) -> None:
        """ (ADM) Creates the SlothActions table """

        if not await self.check_table_sloth_actions():
            return await ctx.send("**Table __SlothActions__ doesn't exist yet!**")

        await ctx.message.delete()
        await self.db.execute_query("DELETE FROM SlothActions")

        return await ctx.send("**Table __SlothActions__ reset!**", delete_after=3)

    async def check_table_sloth_actions(self) -> bool:
        """ Checks if the SlothActions table exists """

        return await self.db.table_exists("SlothActions")

    async def insert_sloth_actions(self,
        label: str,
        user_id: Optional[int] = None,
        target_id: Optional[int] = None,
        text_content: Optional[str] = None,
        int_content: Optional[int] = None,
    ) -> None:
        """ Inserts an entry concerning the user's last seen datetime.
        :param label: The label of the Sloth Action.
        :param user_id: The user ID.
        :param target_id: The target ID.
        :param text_content: The text related to the action.
        :param int_content: The int related to the action. """

        created_ts = await utils.get_timestamp()
        await self.db.execute_query("""
            INSERT INTO SlothActions (
                label, user_id, target_id, text_content, int_content, created_ts
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (label, user_id, target_id, text_content, int_content, created_ts))

    async def get_sloth_actions(self, user_id: int, label: Optional[str] = None) -> List[List[Union[str, int]]]:
        """ Gets the user's sloth actions.
        :param user_id: The ID of the user.
        :param label: The label of the actions. [Optional] """

        if label:
            return await self.db.execute_query("SELECT * FROM SlothActions WHERE user_id = %s AND label = %s", (user_id, label), fetch="all")
        else:
            return await self.db.execute_query("SELECT * FROM SlothActions WHERE user_id = %s", (user_id,), fetch="all")

    async def get_sloth_actions_counter(self, user_id: int, label: Optional[str] = None) -> List[List[Union[str, int]]]:
        """ Gets the user's sloth actions.
        :param user_id: The ID of the user.
        :param label: The label of the actions. [Optional] """

        if label:
            return await self.db.execute_query("SELECT label, COUNT(*) FROM SlothActions WHERE user_id = %s AND label = %s GROUP BY label", (user_id, label), fetch="all")

        return await self.db.execute_query("SELECT label, COUNT(*) FROM SlothActions WHERE user_id = %s GROUP BY label", (user_id,), fetch="all")

    async def delete_sloth_actions(self, user_id: int, label: Optional[str] = None) -> None:
        """ Deletes all Sloth Actions from a user.
        :param user_id: The user ID.
        :param label: The label of the actions. """

        if label:
            await self.db.execute_query("DELETE FROM SlothActions WHERE user_id = %s", (user_id, label))
        else:
            await self.db.execute_query("DELETE FROM SlothActions WHERE user_id = %s", (user_id))
