from requests import Session
from typing import Dict, List, Tuple

from forex_types import Pair

from oanda_candles.candle import Candle
from oanda_candles.gran import Gran

from .candle_collector import CandleCollector


class CandleClient:
    def __init__(self, token: str, real: bool = False):
        self.__token = token
        self.__real = real
        self.__session = Session()
        self.__collections: Dict[Tuple[Pair, Gran], CandleCollector] = {}

    @property
    def real(self):
        return self.__real

    @property
    def session(self):
        return self.__session

    @property
    def token(self):
        return self.__token

    def get_collector(self, pair: Pair, gran: Gran) -> CandleCollector:
        key_tuple = (pair, gran)
        if key_tuple not in self.__collections:
            self.__collections[key_tuple] = CandleCollector(self, pair, gran)
        return self.__collections[key_tuple]

    def grab(self, pair: Pair, gran: Gran, count: int) -> List[Candle]:
        collector = self.get_collector(pair, gran)
        return collector.grab(count)

    def grab_offset(
        self, pair: Pair, gran: Gran, offset: int, count: int
    ) -> List[Candle]:
        collector = self.get_collector(pair, gran)
        return collector.grab_offset(offset, count)
