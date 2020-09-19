from typing import Any, List
from time import monotonic

from forex_types import Pair

from oanda_candles.gran import Gran
from oanda_candles.candle import Candle


from .candle_requester import CandleRequester


class CandleCollector:

    # LONG_ENOUGH is in seconds. We skip looking for more recent candles
    # unless its been this many seconds since we last retrieved them.
    LONG_ENOUGH = 3.0

    def __init__(self, client: Any, pair: Pair, gran: Gran):
        self.requester = CandleRequester(client, pair, gran)
        self._cache: List[Candle] = []
        self.last_update: float = monotonic() - self.LONG_ENOUGH - 1
        self.end_of_history: bool = False

    def __len__(self):
        return len(self._cache)

    def update_recent(self) -> bool:
        mono_time: float = monotonic()
        if mono_time > self.last_update + self.LONG_ENOUGH:
            self.last_update = mono_time
            self.requester.extend(self._cache)
            return True
        return False

    def update_history(self, count: int) -> bool:
        if not self.end_of_history:
            self.end_of_history = not self.requester.prepend(self._cache, count)
        return not self.end_of_history

    def grab(self, count: int) -> List[Candle]:
        if not self._cache and count <= 5000:
            self._cache = self.requester.get(count)
            self.last_update = monotonic()
        self.update_recent()
        missing = count - len(self._cache)
        self.update_history(missing)
        return self._cache[-count:]

    def grab_offset(self, offset: int, count: int) -> List[Candle]:
        total = offset + count
        if not self._cache and total <= 5000:
            self._cache = self.requester.get(total)
            self.last_update = monotonic()
        self.update_recent()
        total_needed = offset + count
        missing = total_needed - len(self._cache)
        self.update_history(missing)
        return self._cache[-total_needed:-offset]
