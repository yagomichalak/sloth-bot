from datetime import datetime
from mysqldb import the_database
import re
from pytz import timezone

async def get_timestamp() -> int:
    """ Gets the current timestamp. """

    epoch = datetime.utcfromtimestamp(0)
    # - epoch#).total_seconds()
    tzone = timezone('Etc/GMT')
    the_time = datetime.now(tzone)
    return the_time.timestamp()

async def parse_time() -> str:
    return datetime(*map(int, re.split(r'[^\d]', str(datetime.utcnow()).replace('+00:00', ''))))
