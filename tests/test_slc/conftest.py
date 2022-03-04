from dataclasses import dataclass
import io
import os
import json
from datetime import datetime
from functools import cached_property
from contextlib import suppress
import traceback
from typing import (
    Any,
    Dict,
    Iterable,
    Literal,
    List,
    Tuple,
    Union,
    Callable,
    Optional,
    Protocol,
    TypedDict,
)

import mysql.connector
import pytest
import dotenv
from cached_method import cached_method
from ..utils.utils import build_cursor_results_as_dict

dotenv.load_dotenv(override=True)  # type: ignore

BASE_DIR = os.path.dirname(__file__)

USERS_JSON_PATH = BASE_DIR + "/../data/users.json"

_NULL = None
_EMPTY_STRING: Literal[''] = ''
_INSERT = "INSERT"
_DELETE = "DELETE"
_SELECT = "SELECT"

# Database
DB_HOST = os.getenv("SLOTH_DB_HOST")
DB_USER = os.getenv("SLOTH_DB_USER")
DB_PASSWORD = os.getenv("SLOTH_DB_PASSWORD")
DB_NAME = os.getenv("SLOTH_DB_NAME")

class Cursor(Protocol):
    """ Cursor to execute actions in the database. """

    lastrowid: Any  # id can be any type

    def execute(self, query: str) -> Any:
        ...

    def fetchone(self) -> Any:
        ...

    def fetchall(self) -> List[Any]:
        ...

    def close(self) -> None:
        ...


class Connection(Protocol):
    """ Database connection. """

    def close(self) -> None:
        ...

    def cursor(self) -> Cursor:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


QueryKind = Literal["INSERT", "DELETE", "SELECT"]


class Query:
    """ Representação da query. """

    __slots__ = ("kind", "table", "query")

    def __init__(
        self,
        kind: QueryKind,
        table: str,
        query: str,
    ) -> None:
        self.kind = kind
        self.table = table
        self.query = query

    def __str__(self) -> str:
        return self.query


class Result:
    """ Useful class for testing and debugging.
    
    .. note::
        This class can be considered as a wrapper for the `Cursor`
        class, but uses `cached_property` and `cached_method`. """

    def __init__(self, cursor: Cursor, **options: Any) -> None:
        self.cursor = cursor
        self._options = options

    @cached_property
    def commited(self) -> bool:
        """ Returns `True` if the query was commited. """

        return self._options.pop("commited", False)

    @cached_property
    def lastrowid(self) -> Any:
        """ Returns the last row id of the cursor. """

        return self.cursor.lastrowid

    @cached_method
    def asdict(self) -> Dict[str, Any]:
        """ Returns a dictionary with the result of the cursor (`fetchone`). """

        result = build_cursor_results_as_dict(self.cursor)
        return result[0]

    @cached_method
    def all_asdict(self) -> List[Dict[str, Any]]:
        """ Returns all the results (`fetchall`) of the cursor as a list of dictionaries. """

        return build_cursor_results_as_dict(self.cursor)

class DatabaseDriver:
    """ Driver to perform the CRUD actions in the database. """

    __slots__ = ("cursor", "connection")

    cursor: Cursor
    connection: Connection

    def __init__(
        self,
        cursor: Cursor,
        connection: Connection,
    ) -> None:
        self.cursor = cursor
        self.connection = connection

    def _parse(self, value: Any) -> str:
        """ Parses a value to a string.
        If the value is a string, it will be quoted.
        If the value is a datetime, it will be converted to a
        isoformat. """

        if isinstance(value, str):
            return repr(value)

        if isinstance(value, datetime):
            return f"'{value.isoformat()}'"

        with suppress(Exception):
            return json.dumps(value)

        return str(value)

    def _query(self, kind: QueryKind, table: str, raw: str) -> Query:
        """ Creates a query.
        It can be used to mock the database. """

        return Query(kind, table, raw)

    def _insert_query(
        self,
        table: str,
        data: Dict[str, Any],
        *,
        parse: Optional[Callable[[Any], str]] = None,
    ) -> Query:
        """ Creates an insert query.
        The `data` argument is a dictionary of column names and
        values.
        The `parse` argument is a function that converts the value to
        a string. """

        assert data, "data must not be empty"

        if not parse:
            parse = self._parse

        sep = ", "

        columns = sep.join(data.keys())

        values = map(parse, data.values())
        values = sep.join(values)

        return self._query(
            _INSERT, table,
            f"INSERT INTO {table} ({columns}) VALUES ({values}) RETURNING *;"
        )

    def _delete_query(
        self,
        table: str,
        conditions: Optional[str] = None,
        # The type of `returning` is explicitly; it is not a union.
        # It is Optional[Iterable[str]] because it can be empty.
        returning: Optional[Union[str, Iterable[str]]] = None,
    ) -> Query:
        """ Creates a delete query. """

        query = f"DELETE FROM {table}"

        if conditions:
            query += f" WHERE {conditions}"

        if returning:
            if not isinstance(returning, str):
                # Don't check if `returning` is an `Iterable`, because
                # a `isintance(str, Iterable)` is always true.
                returning = ", ".join(returning)

            assert returning, "returning must not be empty"

            query += f" RETURNING {returning}"

        query += ';'

        return self._query(
            _DELETE, table,
            f"DELETE FROM {table} WHERE {conditions};",
        )

    def _select_query(
        self,
        table: str,
        fields: Optional[Iterable[str]] = None,
        conditions: Optional[str] = None,
    ) -> Query:
        """ Executes a Select query in the database. """

        fields = ", ".join(fields or '*') or '*'

        return self._query(
            _SELECT, table,
            f"SELECT {fields} FROM {table} WHERE {conditions};",
        )

    @staticmethod
    def _required_keys(
        keys: Iterable[str],
        data: Dict[str, Any],
        table: str,
    ) -> None:
        """ Asserts that the `keys` are present in `data`.
        Raises an `ValueError` if the `keys` are not present. """

        keys = set(keys) - data.keys()

        if keys:
            raise ValueError(f"{table} must have the following keys: {keys}")

    def execute(
        self,
        query: Union[str, Query],
        *,
        commit: bool = True,
    ) -> Result:
        """ Executes the `query`.
        If `commit` is `True`, the transaction is committed. """

        kind = None

        if isinstance(query, Query):
            # It is not necessary to check if `query` is a `Query`.
            # We can use only `str(query)`, but it is more readable.
            kind = query.kind
            query = str(query)
        else:
            with suppress(Exception):
                kind = query.split(' ', 1)[0]

        options: Dict[str, Any] = dict()

        self.cursor.execute(query)

        if commit and kind in (_INSERT, _DELETE, None):
            self.connection.commit()
            options["commited"] = True

        return Result(self.cursor, **options)

    def close(self) -> None:
        """ Closes the cursor and connection. """

        self.cursor.close()
        self.connection.close()

    def rollback(self) -> None:
        """ Rolls back the transaction. """

        self.connection.rollback()

    def delete(self, table: str, id_: Any, column: str = "id") -> Result:
        """ Deletes a row from the database. """

        id_ = self._parse(id_)

        query = self._delete_query(table, f"{column} = {id_}")
        return self.execute(query)

    def get(self, table: str, id_: Any, column: str = 'id') -> Any:
        """ Gets an OLI by ID. """

        id_ = self._parse(id_)
        query = self._select_query(table, None, f"{column} = {id_}")
        result = self.execute(query)

        return result.asdict()


@dataclass
class DiscordMember:
    id: int
    nick: str
    premium_since: str
    joined_at: str
    is_pending: bool
    pending: bool
    communication_disabled_until: str
    username: str
    discriminator: str
    display_avatar: str
    avatar: str
    public_flags: int
    mute: str
    deaf: str
    roles: list
    guild: dict


def get_users() -> Dict[str, Any]:
    """ Returns a dictionary with all users. """

    with open(USERS_JSON_PATH, 'r', encoding="utf-8") as f:
        users = json.loads(f.read())

    parse = DiscordMember

    try:
        data = map(lambda i: parse(**i), users)
        return list(data)
    except TypeError:
        traceback.print_exc()
        pytest.fail("data must be a list of DiscordMember")


def createConnection() -> List[Any]:
    connection = mysql.connector.connect(
        host=os.getenv("SLOTH_DB_HOST"),
        user=os.getenv("SLOTH_DB_USER"),
        passwd=os.getenv("SLOTH_DB_PASSWORD"),
        database=os.getenv("SLOTH_DB_NAME"))
    cursor = connection.cursor()
    connection.autocommit = False
    return cursor, connection