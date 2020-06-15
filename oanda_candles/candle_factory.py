from typing import Optional
from time_int import TimeInt

from forex_types import Pair
from oandapyV20 import API
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
from oandapyV20.endpoints.instruments import InstrumentsCandles

from .gran import Gran
from .candle_sequence import CandleSequence


class CandleFactory:
    """For getting candles using queries to Oanda V20 API"""

    SANE_LOOP_LIMIT = 500

    DEFAULT_MAX_COUNT = 10_000

    def __init__(self, api: API, pair: Pair, gran: Gran):
        """Prepare to summon candles for given pair and granularity.

        Args:
            api: api object to send queries to.
            pair: forex pair which candles are about.
            gran: oanda granularity e.g. "H2" for two hour candles.
        """
        self.instrument = str(pair)
        self.api = api
        self.pair = pair
        self.gran = gran
        self.base_params = {
            "granularity": gran,
            "price": "BAM",
        }

    def _get_batch(self, end_time: TimeInt) -> CandleSequence:
        """Helper for get_candles that makes a single query to Oanda.

        Note, Oanda V20 has a default batch size of 500 candles and
        maximum of 2000. We do not specify the number of candles in
        a batch and presume the default is a reasonable choice. If
        experience eventually shows otherwise, we may want to add
        a count parameter in the future.
        """
        params = dict(self.base_params)
        if end_time < TimeInt.MAX:
            params["to"] = str(end_time)
        request = InstrumentsCandles(instrument=self.instrument, params=params)
        response = self.api.request(request)
        return CandleSequence.from_oanda(response)

    def get_candles(
        self,
        max_count: int = DEFAULT_MAX_COUNT,
        start_time: Optional[TimeInt] = None,
        end_time: Optional[TimeInt] = None,
    ) -> Optional[CandleSequence]:
        """Get candles from oanda in one or more batches.

        Candles are retrieved starting at the end_time and working backwards
        into the past. If left as None, the current time will be used as the
        end_time.

        The max_count argument is a hard limit to how many candles into the
        past are retrieved.

        The optional start_time will limit candles retrieved to those that
        are started after it.

        Even without a start_time argument there may be fewer than max_count
        candles available from Oanda.

        Args:
            max_count: after this many candles retrieved stop. Must be a positive integer.
            start_time: Do not retrieve candles earlier than this. If None, limit is max_count.
            end_time: Start retrieving candles on or before this time. If None, use the current time.
        Returns:
            CandleSequence of zero to max_count candles.
        """
        # Process arguments
        assert max_count > 0
        start_time = TimeInt.MIN if start_time is None else start_time
        combined = CandleSequence(self.pair, self.gran, [])
        # Retrieve candle sequences in batches and merge them into combined sequence
        count = 0
        earliest = TimeInt.MAX if end_time is None else end_time
        loop_count = 0
        while (
            count < max_count
            and start_time < earliest
            and loop_count <= self.SANE_LOOP_LIMIT
        ):
            loop_count += 1
            batch = self._get_batch(earliest + 60)
            if combined:
                combined = CandleSequence.merge(batch, combined)
            else:
                combined = batch
            earliest = combined.start
            print(f"loop count: {loop_count}")
            count = len(combined)
        # Returned the combined sequence
        return combined
