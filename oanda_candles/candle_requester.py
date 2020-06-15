from forex_types import Pair
from oandapyV20 import API
from time_int import TimeInt
from oandapyV20.endpoints.instruments import InstrumentsCandles
from typing import Optional, Union
from datetime import datetime
import json

from .candle_sequence import CandleSequence
from .gran import Gran


class CandleRequester:
    """For getting candle data with queries to Oanda V20 API."""

    DEFAULT_COUNT = 500
    MAX_COUNT = 5000

    def __init__(self, token: str, pair: Pair, gran: Gran):
        """Init object to request candles of a given pair and granularity.

        Args:
            token: secret access token to oanda account
            pair: forex pair which candles are about.
            gran: oanda granularity e.g. "H2" for two hour candles.
        """
        # Create oandapyV20 API object.
        self.api = API(access_token=token, headers={"Accept-Datetime-Format": "UNIX"})
        # Handle case of pair or gran being passed as a str.
        if isinstance(pair, str):
            pair = Pair(pair)
        if isinstance(gran, str):
            gran = Gran(gran)
        # Now make basic assignments of instance data
        self.instrument = str(pair)
        self.pair = pair
        self.gran = gran
        self.base_params = {
            "granularity": str(gran),
            "price": "BAM",
        }

    def request(
        self,
        start: Union[TimeInt, datetime, None] = None,
        end: Union[TimeInt, datetime, None] = None,
        count: Optional[int] = None,
        include_first=True,
    ) -> CandleSequence:
        """Make request for candles from Oanda V20.

        Args:
            start: Start of time range.
            end: End of time range.
            count: Number of candles to retrieve.
            include_first: whether to include first candle at start time.
        Raises:
            ValueError: if start, end, and count are all set.
        """
        if isinstance(start, datetime):
            start = TimeInt(start.timestamp())
        if isinstance(end, datetime):
            end = TimeInt(end.timestamp())
        params = dict(self.base_params)
        if start is None and end is None and count is None:
            params["count"] = self.DEFAULT_COUNT
        elif start is None and end is None:
            params["count"] = count
        elif start is None and count is None:
            params["count"] = self.DEFAULT_COUNT
            params["to"] = str(end)
        elif start is None:
            params["count"] = count
            params["to"] = str(end)
        elif end is None and count is None:
            params["from"] = str(start)
            params["includeFirst"] = include_first
        elif end is None:
            params["from"] = str(start)
            params["count"] = count
            params["includeFirst"] = include_first
        elif count is None:
            params["from"] = str(start)
            params["to"] = str(end)
            params["includeFirst"] = include_first
        else:
            raise ValueError(f"Specified start, end, as well as count.")
        request = InstrumentsCandles(instrument=self.instrument, params=params)
        response = self.api.request(request)
        return CandleSequence.from_oanda(response)
