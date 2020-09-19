"""Sadly, this unit test relies on hitting the real Oanda V20 API.

There seems no point in mocking it out, since most of what we are testing
is to see if we are anticipating its behavior correctly.

The tests in this module require the env var OANDA_TOKEN to be set
to a valid oanda access token for a practice/demo account.
"""

import os
import pytest
from typing import List
from time_int import TimeInt

from oanda_candles import CandleMeister, Pair, Gran, Candle
from oanda_candles.gran_unit import GranUnit


TOKEN = os.environ.get("OANDA_TOKEN")
# Skip this module if we don'thave the token
if TOKEN is None:
    pytest.skip(
        "OANDA_TOKEN env var not set, skipping requester tests.",
        allow_module_level=True,
    )

CandleMeister.init_meister(TOKEN, real=False)


class TestRequester:
    @staticmethod
    def _count_one_hour_gaps(candles: List[Candle]) -> int:
        """Determine how many gaps between candles are one hour apart."""
        hour_count = 0
        previous = TimeInt.MIN
        for candle in candles:
            delta = candle.time - previous
            previous = candle.time
            if delta == 3600:
                hour_count += 1
        return hour_count

    @staticmethod
    def _in_order(candles: List[Candle]) -> bool:
        """Determine if time attribute of candles strictly increases."""
        if candles:
            previous_time = candles[0].time - 1
            for candle in candles:
                if candle.time <= previous_time:
                    return False
                previous_time = candle.time
        return True

    @staticmethod
    def _how_recent(candles: List[Candle]) -> int:
        """Determine how many seconds ago last candle started."""
        return TimeInt.now() - candles[-1].time

    def test_grab(self):
        pair = Pair.AUD_USD
        gran = Gran.H1
        col = CandleMeister.get_collector(pair, gran)
        candles = col.grab(5000)
        assert len(candles) == 5000
        assert self._in_order(candles)
        assert self._count_one_hour_gaps(candles) > 4000
        assert self._how_recent(candles) < GranUnit.DAY.duration * 4
        candles = col.grab(9000)
        assert len(candles) == 9000
        assert self._count_one_hour_gaps(candles) > 8500
        offset_candles = col.grab_offset(1000, 8000)
        assert len(offset_candles) == 8000
        assert self._in_order(candles)
        for ndx in range(8000):
            assert candles[ndx].time == offset_candles[ndx].time
            assert candles[ndx].low_fp == offset_candles[ndx].low_fp
        candles = CandleMeister.grab(pair, gran, 5000)
        assert len(candles) == 5000
        assert self._in_order(candles)
        assert self._count_one_hour_gaps(candles) > 4000
        assert self._how_recent(candles) < GranUnit.DAY.duration * 4
        client = CandleMeister.get_client()
        candles = client.grab(pair, gran, 5000)
        assert len(candles) == 5000
        assert self._in_order(candles)
        assert self._count_one_hour_gaps(candles) > 4000
        assert self._how_recent(candles) < GranUnit.DAY.duration * 4

    def test_end_of_history(self):
        monthly_beast = CandleMeister.get_collector(Pair.GBP_JPY, Gran.M)
        candles = monthly_beast.grab(10_000)
        assert monthly_beast.end_of_history
        assert len(candles) < 10_000
        quarter_hour_euro = CandleMeister.get_collector(Pair.EUR_USD, Gran.M15)
        candles = quarter_hour_euro.grab(1000)
        assert not quarter_hour_euro.end_of_history
        assert len(candles) == 1000
