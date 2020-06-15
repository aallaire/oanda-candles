from typing import Iterable
from pathlib import Path

from forex_types import Pair

from .gran import Gran, GRAN_TUPLE
from .const import Paths

import pickle


class CandleBank:
    """API to store CandleSequence objects on disk."""

    @classmethod
    def create_dirs(cls):
        """Create any missing directories in tree."""
        for bank in CandleBank.iter_banks():
            bank.get_dir_path().mkdir(parents=True, exist_ok=True)

    @classmethod
    def iter_banks(cls) -> Iterable["CandleBank"]:
        """Iterate over CandleBanks."""
        for pair in Pair.iter_pairs():
            for gran in GRAN_TUPLE:
                yield CandleBank(pair, gran)

    def __init__(self, pair: Pair, gran: Gran):
        self.pair = pair
        self.gran = gran

    def get_dir_path(self) -> Path:
        return Paths.CANDLE_DATA_DIR.joinpath(str(self.pair), str(self.gran))

    def get_file_path(self) -> Path:
        return Paths.CANDLE_DATA_DIR.joinpath(
            str(self.pair), str(self.gran), "candles_cache"
        )

    @classmethod
    def write(cls, sequence):
        bank = cls(sequence.pair, sequence.gran)
        path = bank.get_file_path()
        path.write_bytes(pickle.loads(sequence))

    @classmethod
    def read(cls, pair, gran):
        bank = cls(pair, gran)
        path = bank.get_file_path()
        return pickle.loads(path.read_bytes())
