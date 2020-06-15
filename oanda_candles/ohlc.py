from forex_types import Price
from typing import Tuple


class Ohlc:
    """Open, High, Low, Close prices"""

    def __init__(self, o: Price, h: Price, l: Price, c: Price):
        self.o = o
        self.h = h
        self.l = l
        self.c = c

    def to_tuple(self) -> Tuple[str, str, str, str]:
        """Get tuple that can be used in json serialization of Ohlc."""
        return str(self.o), str(self.h), str(self.l), str(self.c)

    @classmethod
    def from_tuple(cls, data: Tuple[str, str, str, str]) -> "Ohlc":
        """Create Ohlc object from tuple like one created by to_tuple method."""
        return cls(Price(data[0]), Price(data[1]), Price(data[2]), Price(data[3]))

    @classmethod
    def from_oanda(cls, data: dict) -> "Ohlc":
        """Put together ohlc from dict data returned from V20 candle query."""
        return cls(
            Price(data["o"]), Price(data["h"]), Price(data["l"]), Price(data["c"])
        )
