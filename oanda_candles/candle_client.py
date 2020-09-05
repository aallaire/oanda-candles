from typing import List, Optional

from forex_types import Pair

from .candle_collector import CandleCollector
from .candle import Candle
from .gran import Gran


class CandleClient:
    def __init__(self, token: str):
        self.token = token
        self._collectors = {}

    def grab(self, pair: Pair, gran: Gran, count: int) -> List[Candle]:
        """Grab latest count candles for pair and gran"""
        collector = self._collectors.get((pair, gran))
        if collector is None:
            collector = self._collectors[(pair, gran)] = CandleCollector(
                self.token, pair, gran
            )
        return collector.grab(count)

    def get_collector(self, pair: Pair, gran: Gran) -> CandleCollector:
        """Get the collector that matches pair and gran."""
        collector = self._collectors.get((pair, gran))
        if collector is None:
            collector = self._collectors[(pair, gran)] = CandleCollector(
                self.token, pair, gran
            )
        return collector


class CandleMeister:
    """Class method/singleton-ish variant on CandleClient"""

    __client: Optional[CandleClient] = None
    __token: Optional[str] = None

    @classmethod
    def init_meister(cls, token: str):
        """Make a single internal CandleClient object with token."""
        if (cls.__client is None) or (token != cls.__token):
            cls.__client = CandleClient(token)
            cls.__token = token

    @classmethod
    def grab(cls, pair: Pair, gran: Gran, count: int) -> List[Candle]:
        return cls.__client.grab(pair, gran, count)

    @classmethod
    def get_collector(cls, pair: Pair, gran: Gran) -> CandleCollector:
        return cls.__client.get_collector(pair, gran)

    @classmethod
    def clear_cache(cls):
        cls.__client = CandleClient(cls.__token)
