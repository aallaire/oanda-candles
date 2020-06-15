class QuoteKind:
    """Kind of quoted price. e.g. the ask, bid, or mid."""

    ASK = BID = MID = None

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, QuoteKind):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other):
        if not isinstance(other, QuoteKind):
            return NotImplemented
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)


QuoteKind.ASK = QuoteKind("ask")
QuoteKind.BID = QuoteKind("bid")
QuoteKind.MID = QuoteKind("mid")
