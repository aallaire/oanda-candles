from .const import Paths
from .candle_bank import CandleBank


class Initializer:

    initialized = False

    @classmethod
    def initialize(cls):
        if not cls.initialized:
            cls.initialized = True
            Paths.init_paths()
            CandleBank.create_dirs()
