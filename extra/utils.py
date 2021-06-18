from datetime import datetime
import re
from pytz import timezone

async def get_timestamp(tz: str = 'Etc/GMT') -> int:
    """ Gets the current timestamp.
    :param tz: The timezone to get the timstamp from. Default = Etc/GMT """

    tzone = timezone(tz)
    the_time = datetime.now(tzone)
    return the_time.timestamp()

async def parse_time(tz: str = 'Etc/GMT') -> str:
    """ Parses time from the current timestamp.
    :param tz: The timezone to get the timstamp from. Default = Etc/GMT """

    return datetime(*map(int, re.split(r'[^\d]', str(datetime.now(tz)).replace('+00:00', ''))))
