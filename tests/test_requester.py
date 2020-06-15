"""Sadly, this unit test relies on hitting the real Oanda V20 API.

There seems no point in mocking it out, since most of what we are testing
is to see if we are anticipating its behavior correctly.

The tests in this module require the env var OANDA_TOKEN to be set
to a valid oanda access token (preferably a demo account).
"""

import os
import pytest
from datetime import datetime
from time_int import TimeInt

from oanda_candles import CandleRequester, Pair, Gran, CandleSequence
from oanda_candles.gran_unit import GranUnit


TOKEN = os.environ.get("OANDA_TOKEN")
# Skip this module if we don'thave the token
if TOKEN is None:
    pytest.skip(
        "OANDA_TOKEN env var not set, skipping requester tests.",
        allow_module_level=True,
    )


class TestRequester:

    pair = Pair("audusd")
    gran = Gran.H1

    requester = CandleRequester(TOKEN, pair, gran)

    start = TimeInt(datetime(year=2020, month=3, day=4, hour=12).timestamp())
    end = TimeInt(datetime(year=2020, month=4, day=8, hour=12).timestamp())
    later = TimeInt(datetime(year=2020, month=5, day=24, hour=12).timestamp())

    four_days = GranUnit.DAY.duration * 4
    one_hour = GranUnit.HOUR.duration

    @staticmethod
    def _count_one_hour_gaps(candles: CandleSequence) -> int:
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
    def _how_recent(candles: CandleSequence) -> int:
        """Determine how many seconds ago last candle started."""
        return TimeInt.utcnow() - candles.end

    @classmethod
    def _validate_sequence(cls, candles: CandleSequence):
        """Assert that it is a candle sequence and such."""
        assert candles.pair == cls.pair
        assert candles.gran == cls.gran
        assert isinstance(candles, CandleSequence)
        assert candles.end > candles.start
        assert candles.start == candles.first.time
        assert candles.end == candles.last.time

    def test_default(self):
        candles = self.requester.request()
        self._validate_sequence(candles)
        assert len(candles) == 500
        assert self._count_one_hour_gaps(candles) > 400
        assert self._how_recent(candles) < GranUnit.DAY.duration * 4

    def test_count(self):
        candles = self.requester.request(count=20)
        self._validate_sequence(candles)
        assert len(candles) == 20
        assert self._count_one_hour_gaps(candles) > 10
        assert self._how_recent(candles) < GranUnit.DAY.duration * 4

    def test_end(self):
        candles = self.requester.request(end=self.end)
        self._validate_sequence(candles)
        assert len(candles) == 500
        assert self._count_one_hour_gaps(candles) == 495
        assert self._how_recent(candles) > GranUnit.DAY.duration * 4
        assert candles.end == self.end - 3600

    def test_end_count(self):
        candles = self.requester.request(end=self.end, count=20)
        self._validate_sequence(candles)
        assert len(candles) == 20
        assert self._count_one_hour_gaps(candles) == 19
        assert candles.end == self.end - 3600

    def test_start(self):
        candles = self.requester.request(start=self.start)
        self._validate_sequence(candles)
        assert len(candles) == 500
        assert self._count_one_hour_gaps(candles) > 490
        assert candles.start == self.start
        candles2 = self.requester.request(start=self.start, include_first=False)
        assert isinstance(candles2, CandleSequence)
        assert len(candles2) == 499
        assert self._count_one_hour_gaps(candles2) > 490
        assert candles.start + 3600 == candles2.start

    def test_start_count(self):
        candles = self.requester.request(start=self.start, count=10)
        self._validate_sequence(candles)
        assert len(candles) == 10
        assert self._count_one_hour_gaps(candles) == 9
        assert candles.start == self.start
        candles2 = self.requester.request(
            start=self.start, count=10, include_first=False
        )
        self._validate_sequence(candles2)
        assert len(candles2) == 9
        assert self._count_one_hour_gaps(candles2) == 8
        assert candles.start + 3600 == candles2.start

    def test_start_end(self):
        candles = self.requester.request(start=self.start, end=self.end)
        self._validate_sequence(candles)
        assert len(candles) == 600
        assert self._count_one_hour_gaps(candles) == 594
        assert candles.start == self.start
        candles2 = self.requester.request(
            start=self.start, end=self.end, include_first=False
        )
        self._validate_sequence(candles2)
        assert len(candles2) == 599
        assert self._count_one_hour_gaps(candles2) == 593
        assert candles[1].time == candles2.start
