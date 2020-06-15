"""Object to represent time range/count of candles to be retrieved.

When retrieving candles we want to specify one or more of the following:
    start: TimeInt of first candle to be retrieved.
    end: TimeInt of the last candle to be retrieved.
    count: Number of candles to be retrieved.

There is a problem with specifying all three before we retrieve
data though--since the number of candles between start and end may
not be count. We do NOT trust ourselves to calculate how many
candles this will be--since there could be times the market
was closed or will be closed that we do not know about. And there
may be times that Oanda is missing candle data for some other
reason for a time period we expected there to be some.

However after we have retrieved candles and are storing them, it
is good to know all three. In this case we are storing a statement
about how many candles fall between start and end. But if end is
in the future more candles may be added before the end is reached
making the count not true.

Because of all this, a distinction is made between a "realized"
CandleRange where we have already passed the end time and retrieved
all the candles, and those for which we do not know all three
attributes yet.
"""

from time_int import TimeInt
from typing import Optional


class CandleRange:
    def __init__(
        self,
        start: Optional[TimeInt] = None,
        end: Optional[TimeInt] = None,
        count: Optional[int] = None,
    ):
        self.realized = False
