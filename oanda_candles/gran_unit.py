class SecondsPer:
    SECOND = 1
    MINUTE = 60
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR
    WEEK = 7 * DAY
    MONTH = 30 * DAY


class GranUnit:
    """Time unit used in granularity, such as seconds or months."""

    def __init__(self, letter: str, name: str, duration: int):
        """Define unit of granularity time.

        Args:
            letter: The letter associated with time in oanda Gran string.
            name: name of the time unit.
            duration: duration in seconds (months approximated as 30 days).
        """
        self.letter = letter
        self.name = name
        self.duration = duration

    def __eq__(self, other: "GranUnit"):
        if isinstance(other, GranUnit):
            return NotImplemented
        return self.duration == other.duration

    def __lt__(self, other: "GranUnit"):
        if isinstance(other, GranUnit):
            return NotImplemented
        return self.duration < other.duration

    def __hash__(self):
        return hash(self.duration)

    SECOND = None
    MINUTE = None
    HOUR = None
    DAY = None
    WEEK = None
    MONTH = None


GranUnit.SECOND = GranUnit("S", "second", SecondsPer.SECOND)
GranUnit.MINUTE = GranUnit("M", "minute", SecondsPer.MINUTE)
GranUnit.HOUR = GranUnit("H", "hour", SecondsPer.HOUR)
GranUnit.DAY = GranUnit("D", "daily", SecondsPer.DAY)
GranUnit.WEEK = GranUnit("W", "weekly", SecondsPer.WEEK)
GranUnit.MONTH = GranUnit("M", "monthly", SecondsPer.MONTH)
