from datetime import datetime
import re

async def get_timestamp() -> int:
    """ Gets the current timestamp. """

    epoch = datetime.utcfromtimestamp(0)
    the_time = (datetime.utcnow() - epoch).total_seconds()
    return the_time

async def parse_time() -> str:
    return datetime(*map(int, re.split(r'[^\d]', str(datetime.utcnow()).replace('+00:00', ''))))
