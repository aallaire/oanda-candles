from typing import List, Optional

from forex_types import Pair, Price
from time_int import TimeInt
from time import monotonic

from .candle import Candle
from .candle_requester import CandleRequester
from .candle_sequence import CandleSequence
from .gran import Gran


class CandleCollector:
    def __init__(self, token: str, pair: Pair, gran: Gran):
        """Candle Holders start off empty.

        Args:
            token: Access token for Oanda V20 API
            pair: the forex pair that candles are about.
            gran: the time granularity of candles to hold.
        """
        self.requester: CandleRequester = CandleRequester(token, pair, gran)
        # _history_complete for if we reached first candle available
        self._history_complete = False
        # Set _low and _high prices to that of first candle then load candles
        # by using extend method (which will adjust low and high from there).
        sequence = self.requester.request(count=500)
        self._low: Price = sequence.first.bid.l
        self._high: Price = sequence.first.ask.h
        self._candles: List[Candle] = [candle for candle in sequence]
        self._update_low_and_high()
        # _last_update for when we last updated candles to current time.
        self._last_update = monotonic()
        # for tracking if the same candle was closed on different updates:
        self._sleepy_candle: Optional[Candle] = None
        self._is_sleepy = False

    def __len__(self):
        return len(self._candles)

    def get_highest(self) -> Price:
        """Get highest ask price in collection."""
        return self._high

    def get_age(self) -> float:
        """Get number of seconds since last update."""
        return monotonic() - self._last_update

    def is_fresh(self) -> bool:
        """Determine if last get_candles results are reasonably fresh."""
        age = monotonic() - self._last_update
        return age < self.requester.gran.freshness

    def is_sleepy(self) -> bool:
        """Indicates if new candle data has been coming in at sleepy pace.

        The rule is that if we have had the same last closed candle
        for updates that are 10 or more seconds apart, that we consider
        the rate of new data "sleepy". This will of course happen when
        the market is closed, but may happen for other reasons.

        When we detect sleepiness, we throttle back how often calls to
        the grab method will check for more recent data.
        """
        return self._is_sleepy

    def is_complete(self) -> bool:
        """Determine if last candle in collection is complete."""
        return self._candles[-1].complete

    def get_lowest(self) -> Price:
        """Get lowest bid price in collection."""
        return self._low

    def get_start(self) -> TimeInt:
        """Get starting time of first candle."""
        return self._candles[0].time

    def get_end(self) -> TimeInt:
        """Get starting time of last candle."""
        return self._candles[-1].time

    def history_complete(self):
        """Is our history known to reach as far back as Oanda supports."""
        return self._history_complete

    def grab(self, count: int) -> List[Candle]:
        """Get the last count number of candles.

        This will expand collection if it has to to get the
        most recent count candles. It is possible it may return
        fewer than count candles if they are not available.
        For example 1000 monthly candles ago was in 1936, so
        its doubtful Oanda will give you so many months.

        Args:
            count: get only (up to) the last number of candles.
        """
        self._update_past(count)
        self._update_present()
        return self._candles[-count:]

    def tail(self) -> List[Candle]:
        """Get only more recent information since last grab or tail."""
        # TODO
        raise NotImplemented("Nice idea maybe, but not implemented yet.")

    # --------------------------------------------------------------------------
    # Helper Methods
    # --------------------------------------------------------------------------
    def _update_present(self) -> bool:
        """Bring candles in collection up to date with the present.

        Or do nothing if this has been done too recently.

        Here "too recently" follows some heuristic logic based on the
        granularity and whether the API seems to have had new data recently.

        Returns:
            True iff at least some new data was retrieved (including any
                 difference of price for current candle).
        """
        # Skip if it has not been long enough.
        freshness = 60 if self._is_sleepy else self.requester.gran.freshness
        elapsed_time = monotonic() - self._last_update
        if elapsed_time < freshness:
            return False
        # We now presume that API is not sleepy until shown otherwise.
        self._is_sleepy = False
        # Get some data about the current state of candles in case we need
        # Make request for the maximum of 5000 newer candles (although we
        # most often need very few candles, there may be times we will need
        # to catch up on a big gap--and it doesn't seem to cost extra to
        # ask Oanda for more candles than they have available yet).
        sequence = self.requester.request(start=self.get_end(), count=5000)
        if len(sequence) == 1:
            # In this case just have a new version of the last candle.
            # We should check if its any different than previous version.
            old_last: Candle = self._candles[-1]
            new_last: Candle = sequence[0]
            self._last_update = monotonic()
            if old_last == new_last:
                if elapsed_time > 300:
                    # No new data for more than 5 minutes indicates sleepiness.
                    self._is_sleepy = True
                return False
            else:
                self._extend(sequence)
                return True
        elif sequence:
            # In this case we have new candles, so we should add them.
            self._extend(sequence)
            # If we got a full load of 5000 candles, add more til we are caught up.
            while len(sequence) >= 5000:
                sequence = self.requester.request(start=self.get_end(), count=5000)
                self._extend(sequence)
            self._last_update = monotonic()
            return True
        else:
            # In this case we got no information
            if elapsed_time > 300:
                # No new data for more than 5 minutes indicates sleepiness.
                self._is_sleepy = True
            return False

    def _update_past(self, count: int = 500) -> bool:
        """Add previous batch candles to front of collection.

        Args:
            count: the total number of candles we should end up with.
        Returns:
            True if candles added or False if we have reached limit.
        """
        return_value = False
        still_need = max(count - len(self._candles), 0)
        while still_need and not self._history_complete:
            if still_need < 500:
                batch = 500
            elif still_need > 5000:
                batch = 5000
            else:
                batch = still_need
            just_before_start = self.get_start() - 1
            sequence = self.requester.request(end=just_before_start, count=batch)
            if sequence:
                self._prepend(sequence)
                return_value = True
                still_need = max(count - len(self._candles), 0)
            else:
                self._history_complete = True
        return return_value

    def _extend(self, sequence: CandleSequence):
        """Extend self._candles by candle sequence."""
        if sequence:
            # If we have an incomplete candle on the end, remove it.
            if self._candles and not self._candles[-1].complete:
                self._candles.pop()
            # Append new candles from sequence that are more recent than
            # the last candle
            end = self.get_end()
            for candle in sequence:
                if candle.time > end:
                    self._candles.append(candle)
            self._update_low_and_high()

    def _prepend(self, sequence: CandleSequence):
        """Prepend candle sequence to front of self._candles."""
        if sequence:
            start = self.get_start()
            new_list = []
            for candle in sequence:
                if candle.time < start:
                    new_list.append(candle)
            if new_list:
                old_list = self._candles
                self._candles = new_list
                self._candles.extend(old_list)
            self._update_low_and_high()

    def _update_low_and_high(self):
        """Helper to update the low and high price values"""
        first_candle = self._candles[0]
        low = first_candle.bid.l
        high = first_candle.ask.h
        for candle in self._candles:
            if candle.bid.l < low:
                low = candle.bid.l
            if candle.ask.h > high:
                high = candle.ask.h
        self._low = low
        self._high = high
