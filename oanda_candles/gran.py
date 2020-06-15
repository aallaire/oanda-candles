from typing import Optional, Set, Dict

from .gran_unit import GranUnit


class Gran:
    """Granularity unit for oanda V20 candles"""

    S5 = S10 = S15 = S30 = None
    M1 = M2 = M4 = M5 = M10 = M15 = M30 = None
    H1 = H2 = H3 = H4 = H6 = H8 = H12 = None
    D = W = M = None

    def __init__(self, unit: GranUnit, amount: Optional[int]):
        if amount is None:
            self.oanda = unit.letter  # e.g. "M" for monthly
            self.name = unit.name
            self.duration = unit.duration
        else:
            self.oanda = f"{unit.letter}{amount}"  # e.g. "M1" for one minute
            self.name = f"{amount} {unit.name}"
            self.duration = amount * unit.duration

    def __str__(self):
        return self.oanda

    def __eq__(self, other):
        if not isinstance(other, Gran):
            return NotImplemented
        return self.duration == other.duration

    def __lt__(self, other):
        if not isinstance(other, Gran):
            return NotImplemented
        return self.duration < other.duration

    def __hash__(self):
        return hash(self.duration)


Gran.S5 = Gran(GranUnit.SECOND, 5)
Gran.S10 = Gran(GranUnit.SECOND, 10)
Gran.S15 = Gran(GranUnit.SECOND, 15)
Gran.S30 = Gran(GranUnit.SECOND, 30)
Gran.M1 = Gran(GranUnit.MINUTE, 1)
Gran.M2 = Gran(GranUnit.MINUTE, 2)
Gran.M4 = Gran(GranUnit.MINUTE, 4)
Gran.M5 = Gran(GranUnit.MINUTE, 5)
Gran.M10 = Gran(GranUnit.MINUTE, 10)
Gran.M15 = Gran(GranUnit.MINUTE, 15)
Gran.M30 = Gran(GranUnit.MINUTE, 30)
Gran.H1 = Gran(GranUnit.HOUR, 1)
Gran.H2 = Gran(GranUnit.HOUR, 2)
Gran.H3 = Gran(GranUnit.HOUR, 3)
Gran.H4 = Gran(GranUnit.HOUR, 4)
Gran.H6 = Gran(GranUnit.HOUR, 6)
Gran.H8 = Gran(GranUnit.HOUR, 8)
Gran.H12 = Gran(GranUnit.HOUR, 12)
Gran.D = Gran(GranUnit.DAY, None)
Gran.W = Gran(GranUnit.DAY, None)
Gran.M = Gran(GranUnit.DAY, None)

GRAN_TUPLE = (
    Gran.S5,
    Gran.S10,
    Gran.S15,
    Gran.S30,
    Gran.M1,
    Gran.M2,
    Gran.M4,
    Gran.M5,
    Gran.M10,
    Gran.M15,
    Gran.M30,
    Gran.H1,
    Gran.H2,
    Gran.H3,
    Gran.H4,
    Gran.H6,
    Gran.H8,
    Gran.H12,
    Gran.D,
    Gran.W,
    Gran.M,
)

GRAN_SET: Set[Gran] = set(GRAN_TUPLE)
GRAN_DICT: Dict[str, Gran] = {_.oanda: _ for _ in GRAN_TUPLE}
