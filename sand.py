from forex_types import Pair
from pathlib import Path
import json
from time_int import TimeInt
from datetime import datetime, timedelta
import os


NOW = datetime.utcnow()
HOUR_AGO = NOW - timedelta(hours=1)
FIVE_HOURS_AGO = NOW - timedelta(hours=5)
LAST_WEEK = NOW - timedelta(days=7)
THREE_HUNDRED_DAYS_AGO = NOW - timedelta(days=300)

print(f"{NOW}")
print(f"{FIVE_HOURS_AGO}")


from oanda_candles import CandleRequester, Pair, Gran

TOKEN_JSON = Path.home().joinpath(".oanda-candles", "tokens.json")


def get_token() -> str:
    """Get demo token from TOKEN_JSON."""
    content = TOKEN_JSON.read_text()
    token_dict = json.loads(content)
    return token_dict["demo"]


def report(candles):
    for candle in candles:
        print(f"    {candle.time.get_pretty()}")
    print(f"{candles.pair} {candles.gran}")
    print(f"Num Candles : {len(candles)}")
    if candles:
        print(f"First Candle: {candles[0]}")
        print(f"Last Candle : {candles[-1]}")
        print(f"Start       : {candles.start.get_pretty()}")
        print(f"End         : {candles.end.get_pretty()}")


token = os.environ["OANDA_TOKEN"]
aud_usd = Pair("aud_usd")
requester = CandleRequester(token, aud_usd, Gran.H1)


# candles = requester.request(start=start, include_first=False)
candles = requester.request(start=THREE_HUNDRED_DAYS_AGO, count=2000)
report(candles)


"""
# factory = client.new_candle_factory(aud_usd, "H1")
candles = requester.starting_from(TimeInt(1591885739))
report(candles)
candles = requester.starting_after(TimeInt(1591885739))
report(candles)
"""
