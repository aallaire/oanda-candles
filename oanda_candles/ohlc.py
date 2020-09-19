from forex_types import Price, FracPips
from typing import Tuple


class Ohlc:
    """Open, High, Low, Close prices"""

    def __init__(self, o: Price, h: Price, l: Price, c: Price):
        self.o = o
        self.h = h
        self.l = l
        self.c = c

    @property
    def o_fp(self) -> FracPips:
        """Open price as Fractional Pips."""
        return FracPips.from_price(self.o)

    @property
    def h_fp(self) -> FracPips:
        """High price as Fractional Pips."""
        return FracPips.from_price(self.h)

    @property
    def l_fp(self) -> FracPips:
        """Low price as Fractional Pips."""
        return FracPips.from_price(self.l)

    @property
    def c_fp(self) -> FracPips:
        """Closing price as Fractional Pips."""
        return FracPips.from_price(self.c)

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

    def __eq__(self, other) -> bool:
        """Equal only when all four prices are equal."""
        if isinstance(other, Ohlc):
            return (
                self.o == other.o
                and self.h == other.h
                and self.l == other.l
                and self.c == other.c
            )
        else:
            return NotImplemented
