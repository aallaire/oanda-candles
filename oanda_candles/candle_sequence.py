from typing import Optional, Tuple, Iterable
from forex_types import Pair
from time_int import TimeInt
import json

from .gran import Gran, GRAN_DICT
from .candle import Candle


class CandleSequenceError(Exception):
    """For candle data problems."""


class CandleSequence:
    """Series of Candle objects for same pair and granularity.

    Attributes:
       pair: the forex pair the candles represent e.g. Pair("AUD_USD").
       gran: the candle granularity for example Gran.H1 for one hour candles
       last: optional last candle that is not necessarily complete.
       start: TimeInt of the start of the first candle
       end: TimeInt of the start of the last candle
       candles: tuple of candle objects.
    """

    def __init__(self, pair: Pair, gran: Gran, candles: Iterable[Candle]):
        """Create Candle Sequence.

        Args:
            pair: forex pair that candle data is about
            gran: candle duration/granularity.
            candles: one or more Candle objects in order.
        Raises:
            CandleSequenceError: if candles not in chronological order.
            CandleSequenceError: if candles have repeats.
            CandleSequenceError: if any candle other than last is not complete.
        """
        # Gather candles into a list while inspecting them for problems.
        previous_time = TimeInt.MIN
        previous_incomplete = False
        candle_list = []
        for candle in candles:
            if previous_incomplete:
                raise CandleSequenceError("Incomplete candle before end of sequence.")
            elif candle.time <= previous_time:
                raise CandleSequenceError("Candles not in chronological order.")
            previous_incomplete = not candle.complete
            candle_list.append(candle)
        # Set attributes
        self.candles: Tuple[Candle] = tuple(candle_list)
        self.pair: Pair = pair
        self.gran: Gran = gran
        if self.candles:
            self.first: Optional[Candle] = self.candles[0]
            self.last: Optional[Candle] = self.candles[-1]
            self.start: TimeInt = self.first.time
            self.end: TimeInt = self.last.time
        else:
            self.first: Optional[Candle] = None
            self.last: Optional[Candle] = None
            self.start: TimeInt = TimeInt.MAX
            self.end: TimeInt = TimeInt.MIN

    def make_copy(self) -> "CandleSequence":
        """Return a copy of this CandleSequence."""
        return CandleSequence(self.pair, self.gran, self.candles)

    @classmethod
    def from_oanda(cls, data: dict) -> "CandleSequence":
        """Make a CandleSequence from dictionary from oanda v20 query."""
        pair = Pair(data["instrument"])
        gran = GRAN_DICT[data["granularity"]]
        candles = [Candle.from_oanda(_) for _ in data["candles"]]
        return CandleSequence(pair, gran, candles)

    def to_storage_json(self) -> str:
        """Convert data necessary to reconstruct sequence to a json string."""
        return json.dumps(
            {
                "pair": self.pair.name,
                "gran": self.gran.oanda,
                "candles": [_.to_tuple() for _ in self.candles],
            },
            sort_keys=True,
            indent=4,
        )

    @classmethod
    def from_storage_json(cls, json_string: str) -> "CandleSequence":
        """Create CandleSequence from string stored by to_storage_json."""
        data = json.loads(json_string)
        pair = Pair(data["pair"])
        gran = GRAN_DICT[data["gran"]]
        candles = [Candle.from_tuple(_) for _ in data["candles"]]
        return CandleSequence(pair, gran, candles)

    def __getitem__(self, item: int):
        return self.candles[item]

    def __len__(self):
        return len(self.candles)

    def __iter__(self):
        for candle in self.candles:
            yield candle

    def __bool__(self):
        return bool(self.candles)
