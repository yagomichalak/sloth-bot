import aiomysql
import asyncio
#from contextlib import asynccontextmanager
import os
from typing import Optional, Iterable, Any, Tuple
from dotenv import load_dotenv
load_dotenv()

loop = asyncio.get_event_loop()

#@asynccontextmanager
async def the_database():
    pool = await aiomysql.create_pool(
        host=os.getenv("SLOTH_DB_HOST"),
        user=os.getenv("SLOTH_DB_USER"),
        password=os.getenv("SLOTH_DB_PASSWORD"),
        db=os.getenv("SLOTH_DB_NAME"), loop=loop)
    db = await pool.acquire()
    mycursor = await db.cursor()
    return mycursor, db

django_loop = asyncio.get_event_loop()
async def the_django_database():
    pool = await aiomysql.create_pool(
        host=os.getenv("DJANGO_DB_HOST"),
        user=os.getenv("DJANGO_DB_USER"),
        password=os.getenv("DJANGO_DB_PASSWORD"),
        db=os.getenv("DJANGO_DB_NAME"), loop=django_loop)

    db = await pool.acquire()
    mycursor = await db.cursor()
    return mycursor, db


class DatabaseCore:
    
    async def execute_query(self,
        query: str,
        values: Iterable,
        connection: Optional[Tuple[object, object]] = None,
        commit: bool = True,
        close_connection: bool = True,
        fetch: Optional[str] = None
    ) -> Optional[Any]:
        """ Executes a database query.
        :param query: The query itself to run.
        :param cursor: The cursor to use.
        :param commit: Whether to commit the changes or not.
        :param open_connection: Whether to close the connection or not.
        :param fetch: Whether to fetch one, all or no objects from the cursor.
        """

        data = None
        if not connection:
            mycursor, db = await the_database()
        else:
            mycursor, db = connection

        # Executes the query
        await mycursor.execute(query, values)

        if commit:
            await db.commit()

        if fetch == "one":
            data = await mycursor.fetchone()

        elif fetch == "all":
            data = await mycursor.fetchall()

        if close_connection:
            await mycursor.close()

        return data

    async def table_exists(self, table_name: str) -> bool:
        """ Checks whether a given table exists or not.
        :param table_name: The table name to check. """

        return any(self.execute_query(
            query="SHOW TABLE STATUS LIKE %s;",
            values=(table_name,),
            fetch="all",
        ))
