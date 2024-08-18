import aiomysql
import asyncio
#from contextlib import asynccontextmanager
import os
from typing import Optional, Iterable, Any, Tuple, Literal, Union, Dict
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
    
    COMMITABLE_METHODS = (
        "CREATE", "DROP", "INSERT",
        "UPDATE", "DELETE",
    )
    
    async def get_connection(self, database_name: str) -> Tuple[object, object]:
        """ Gets the database connection.
        :param database_name: The name of the database to get. """
        
        pool = await aiomysql.create_pool(
            host=os.getenv(f"{database_name.upper()}_DB_HOST"),
            user=os.getenv(f"{database_name.upper()}_DB_USER"),
            password=os.getenv(f"{database_name.upper()}_DB_PASSWORD"),
            db=os.getenv(f"{database_name.upper()}_DB_NAME"),
            loop=django_loop,
        )

        db = await pool.acquire()
        mycursor = await db.cursor()
        return mycursor, db
    
    async def execute_query(self,
        query: str,
        values: Iterable = [],
        connection: Optional[Tuple[object, object]] = None,
        execute_many: bool = False,
        fetch: Optional[Literal["one", "all"]] = None,
        database_name: Literal["sloth", "django"] = "sloth",
        description: bool = False
    ) -> Union[Tuple[Dict[str, Any], Optional[Any], Optional[Any]]]:
        """ Executes a database query.
        :param query: The query itself to run.
        :param values: The values to pass in to the query.
        :param fetch: Whether to fetch one, all or no objects from the cursor.
        """

        data = [] if fetch == "all" else None
        fetch = None if not fetch else fetch.lower()
        if not connection:
            mycursor, db = await self.get_connection(database_name)
        else:
            mycursor, db = connection

        try:
            # Executes the query
            if execute_many:
                await mycursor.executemany(query, values)
            else:
                await mycursor.execute(query, values)

            if query.upper().startswith(self.COMMITABLE_METHODS):
                await db.commit()

            if fetch == "one":
                data = await mycursor.fetchone()

            elif fetch == "all":
                data = await mycursor.fetchall()
        except Exception as e:
            print("Error at query:", str(query))
            print("Error:", str(e))
        finally:
            await mycursor.close()

        if description:
            return data, mycursor.description
        return data

    async def table_exists(self, table_name: str) -> bool:
        """ Checks whether a given table exists or not.
        :param table_name: The table name to check. """

        return any(await self.execute_query(
            query="SHOW TABLE STATUS LIKE %s;",
            values=(table_name,),
            fetch="all",
        ))
