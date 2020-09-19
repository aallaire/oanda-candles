from typing import List, Optional

from forex_types import Pair

from oanda_candles.candle import Candle
from oanda_candles.gran import Gran

from .candle_client import CandleClient
from .candle_collector import CandleCollector


class CandleMeister:
    """Class method/singleton-ish variant on CandleClient"""

    __client: Optional[CandleClient] = None
    __token: Optional[str] = None
    __account_type: Optional[str] = None

    @classmethod
    def init_meister(cls, token: str, real: bool = False):
        """Make a single internal CandleClient object."""
        if (cls.__client is None) or (token != cls.__token) or (real != cls.__real):
            cls.__client = CandleClient(token, real)
            cls.__token = token
            cls.__real = real

    @classmethod
    def get_client(cls):
        return cls.__client

    @classmethod
    def get_collector(cls, pair: Pair, gran: Gran) -> CandleCollector:
        return cls.__client.get_collector(pair, gran)

    @classmethod
    def grab(cls, pair: Pair, gran: Gran, count: int) -> List[Candle]:
        collector = cls.get_collector(pair, gran)
        return collector.grab(count)

    @classmethod
    def grab_offset(
        cls, pair: Pair, gran: Gran, offset: int, count: int
    ) -> List[Candle]:
        collector = cls.get_collector(pair, gran)
        collector.grab_offset(offset, count)
