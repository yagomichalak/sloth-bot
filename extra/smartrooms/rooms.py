
from mysqldb import the_database
from abc import abstractclassmethod, ABC
from typing import Any
import asyncio

class SmartRoom(ABC):
    """ Base class for SmartRooms. """

    @abstractclassmethod
    async def format_data(cls) -> Any: pass

    @abstractclassmethod
    async def insert(cls) -> Any: pass

    @abstractclassmethod
    async def update(cls) -> Any: pass

    @abstractclassmethod
    async def delete(cls) -> Any: pass


class BasicRoom(SmartRoom):
    """ Class for BasicRooms. """

    async def format_data(cls) -> Any: pass

    async def insert(cls) -> Any: pass

    async def update(cls) -> Any: pass

    async def delete(cls) -> Any: pass

class PremiumRoom(SmartRoom):
    """ Class for PremiumRooms. """

    async def format_data(cls) -> Any: pass

    async def insert(cls) -> Any:

        print('Inserting Premium Room into the database...')

    async def update(cls) -> Any: pass

    async def delete(cls) -> Any: pass

class GalaxyRoom(SmartRoom):
    """ Class for GalaxyRooms. """

    async def format_data(cls) -> Any: pass

    async def insert(cls) -> Any:

        print('Inserting Galaxy Room into the database...')

    async def update(cls) -> Any: pass

    async def delete(cls) -> Any: pass


# galaxy_room = GalaxyRoom()

# asyncio.run(galaxy_room.insert())