import os
from pathlib import Path


class Paths:
    ACCOUNT_JSON = None
    CANDLE_DATA_DIR = None
    ROOT = None

    @classmethod
    def init_paths(cls):
        if os.name == "nt":  # implies Windows system
            new_root = Path.home().joinpath("AppData", "Local", "PythonOandaCandles")
        else:
            new_root = Path.home().joinpath(".python-oanda-candles")
        cls.ROOT = new_root
        cls.ACCOUNT_JSON = cls.ROOT.joinpath("account.json")
        cls.CANDLE_DATA_DIR = cls.ROOT.joinpath("candle_data")


class WebLinks:
    paper = "https://www.oanda.com/demo-account/tpa/personal_token"
    live = "https://www.oanda.com/account/tpa/personal_token"
