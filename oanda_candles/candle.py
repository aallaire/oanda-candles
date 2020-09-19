from datetime import datetime
from time import struct_time
from typing import Tuple

from forex_types import FracPips, Price
from magic_kind import MagicKind
from time_int import TimeInt

from .quote_kind import QuoteKind
from .ohlc import Ohlc


class PriceKind(MagicKind):
    ASK: str = "ask"
    BID: str = "bid"
    MID: str = "mid"


class Candle:
    def __init__(self, ask: Ohlc, bid: Ohlc, mid: Ohlc, time: TimeInt, complete: bool):
        self.ask = ask
        self.bid = bid
        self.mid = mid
        self.time = time
        self.complete = complete

    @classmethod
    def from_oanda(cls, data: dict) -> "Candle":
        """Put together candle from dict data returned from V20 candle query.

        Args:
            data: dictionary from candle query with candle specific data.
        """
        return Candle(
            Ohlc.from_oanda(data["ask"]),
            Ohlc.from_oanda(data["bid"]),
            Ohlc.from_oanda(data["mid"]),
            TimeInt.from_float_string(data["time"]),
            data["complete"],
        )

    def to_tuple(self) -> Tuple[Tuple, Tuple, Tuple, int, bool]:
        """Get tuple that can be used in json serialization of Candle."""
        return (
            self.ask.to_tuple(),
            self.bid.to_tuple(),
            self.mid.to_tuple(),
            int(self.time),
            self.complete,
        )

    @classmethod
    def from_tuple(cls, data: Tuple[Tuple, Tuple, Tuple, int, bool]) -> "Candle":
        """Create Candle object from tuple like one created by to_tuple method."""
        return cls(
            Ohlc.from_tuple(data[0]),
            Ohlc.from_tuple(data[1]),
            Ohlc.from_tuple(data[2]),
            TimeInt(data[3]),
            data[4],
        )

    def quote(self, kind: QuoteKind):
        if kind == QuoteKind.ASK:
            return self.ask
        elif kind == QuoteKind.BID:
            return self.bid
        else:
            return self.mid

    def __str__(self):
        return f"<Candle: {self.time.get_pretty()}>"

    def __eq__(self, other) -> bool:
        """Comparison includes all the data in candle."""
        if isinstance(other, Candle):
            return (
                self.ask == other.ask
                and self.bid == other.bid
                and self.mid == other.mid
                and self.time == other.time
                and self.complete == other.complete
            )
        else:
            return NotImplemented

    def __hash__(self):
        """We just use time to hash candles into buckets."""
        return hash(self.time)

    @property
    def high(self) -> Price:
        """highest ask price."""
        return self.ask.h

    @property
    def low(self) -> Price:
        """lowest bid price."""
        return self.bid.l

    @property
    def high_fp(self) -> FracPips:
        """highest ask price as fraction pips"""
        return self.ask.h_fp

    @property
    def low_fp(self) -> FracPips:
        """lowest bid price as fractional pips"""
        return self.bid.l_fp

    @property
    def time_dt(self) -> datetime:
        """Start time of candle as a datetime (datetime package)."""
        return self.time.get_datetime()

    @property
    def time_st(self) -> struct_time:
        """Start time of candle as struct_time (time package)."""
        return self.time.get_struct_time()
