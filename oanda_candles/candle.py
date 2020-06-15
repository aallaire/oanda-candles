from time_int import TimeInt
from typing import Tuple
from magic_kind import MagicKind

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
            TimeInt.from_unix(data["time"]),
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

    def __eq__(self, other):
        """Comparison only uses age of candle and if it is complete or not."""
        if not isinstance(other, Candle):
            return NotImplemented
        if self.time != other.time:
            return False
        elif self.complete != other.complete:
            return False
        return True

    def __lt__(self, other):
        """More recent candles are considered greater than older candles.

        Note that closed candles are considered more recent then
        candles of the same time that are not yet closed.
        """
        if not isinstance(other, Candle):
            return NotImplemented
        if self.time < other.time:
            return True
        elif self.time > other.time:
            return False
        elif other.complete and not self.complete:
            return True
        else:
            return False

    def __hash__(self):
        """Hash only cares about time of candle."""
        return hash(self.time)
