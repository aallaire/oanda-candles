# oanda-candles
Client to make getting Oanda candle data easy.

### Quick Example
```python
import os
from oanda_candles import CandleClient, Pair, Gran

token = os.getenv("OANDA_TOKEN")

# Initialize Client with token, real as False for practice account.
client = CandleClient(token, real=False)

# Initialize collector for Euro/US Dollar 4 hour candles.
collector = client.get_collector(Pair.EUR_USD, Gran.H4)

# Print the opening and closing bid price of the most recent 100 candles.
candles = collector.grab(100)
for candle in candles:
    print(f"{candle.time.get_pretty()}: Open bid: {candle.bid.o} Close bid: {candle.bid.c}")

# Get list of 300 candles from 8000 candles back
special_300 = collector.grab_offset(8000, 300)
```

### Public Classes in this Package
| Class | Description
| ----- |:-----|
| Candle | Data about one candle containing a start time and three Ohlc objects for the bid, mid, and ask prices |
| CandleClient | Collection of one CandleCollector for each combination of `pair` and `gran` |
| CandleCollector | For grabbing candles for a specific `pair` and `gran` |
| CandleMeister | Provides a single CandleCollector so one does not have to pass it around between modules |
| Gran | Candle granularity (duration), one of the spefic values allowed by Oanda's API such as Gran.H6 for six hour |
| Ohlc | Contains open, high, low, and closing prices as attrs `o`, `h`, `l`, and `c` |
| Pair | One of 28 forex currency pairs. Can be specified like `Pair.EUR_USD` or `Pair("eurusd")` |
| TimeInt | Integer subclass representing time since Jan 1, 1970 in UTC, candles have this as their `time` attribute |


### Some Features
1. Candle data is cached automatically so calling `grab` or `grab_offset` for same candles do not require another server requests.
1. However, when candles are grabbed, the cache is updated to include the most recent candles provided at least
three seconds have passed since the last time they were updated.
1. The Candle objects returned have the bid, mid, and ask prices and have times expressed as UTC epoch integers.
1. Candles are aligned to reasonable offset defaults (month candles start at start of month in UTC).
1. Candle alignment is preset to always start days and month candles on the start of the day and month UTC.

### Some Limitations.
1. Requires secret Oanda Access token to initialize client.
1. Only candle granularity levels supported by Oanda's V20 RestfulAPI are available.
1. Only forex pairs (instruments) supported by the forex-types package are supported (The 28 pair combinations for the 8 major currencies).
1. Not all the options of Oanda's V20 candle endpoint are available. Rather reasonable values are already preset.
(considering the very odd defaults and the confusing way the options work, this is kind of a feature type limitation,
still in a future version these likely should be made configurable for any masachists that want to mess with them).



### Steps followed by `grab` and `grab_offset` methods
When either the `grab` or `grab_offset` methods are called on a particular `CandleCollector` object, it:
1. Makes sure candle cache is up to date with latest candles by querying Oanda if its been longer than 3 seconds since this was last done.
1. If the candles in the cache do not go back far enough to provide the number requested get older candles from Oanda until it does.
1. Return the requested candles, while keeping the cached list for the next grab calls.


#### CAVEAT:
This is still a beta type package--although between 0.0.10 and 0.1.0 it became somewhat less beta-ish.

#### Version history.

new in version 0.1.0:
1. Reliance on opandaV20 package was dropped in favor of using requests package directly.
1. Everything was refactored into smaller simpler less "exploratory" code.
1. Updating TimeInt package to 0.0.9 which is entirely UTC, without any accidental local times popping in.
1. Month candles are aligned right at start of month UTC. And day candles at start of day and so forth.
1. CandleSequence class which had no real utility compared to highe level grab classes were refactored out. 
1. Only tested refactoring by hand, unittests have to be rewritten (since they were full of funky time alignment that we no longer have.)

new in version 0.0.10:
1. Updated time-int dependency from 0.0.6 to 0.0.7.

new in version 0.0.9:
1. CandleMeister and CandleClient now have a method to get the collector they use
for a specific pair and granularity.
1. Updated some dependencies to latest versions.

new in version 0.0.8:
1. Added CandleClient to manage multiple CandleCollector objects from one object.
1. Plus a CandleMeister that wraps a single CandleClient for easy global access
1. Fixed a bug that was causing too many requests when they were not needed.
1. Had idea for `tail` method as a variant on `grab` method, where it returns only
the newest candle information since the last call to eitehr `grab` or `tail`. Made
a place holder for it, but not implementing it yet.
1. Still behind on unit tests, but still was able to do sand-box testing with market open.
--which is how I found and fixed bug above. This package is still far from prime time ready.


new in version 0.0.7:
1. The `CandleSequence` has been cleaned up and plans to add merging have been abandoned.
1. The `Candle` class no longer has `__lt__` overloaded and `__eq__` is now based on all the values being equal rather than just the candle time.
1. A new `CandleCollector` class is added which is like a higher level `CandleSequence` specifically designed for chart applications that always want a specific number of latest candles. 
1. No unit testing has been added for these changes, they have only been sand-boxed, so they may not work as advertised. Also the market was closed when I sand-boxed `CandleCollector`, so some of its heursitics have not even been sand-box tested yet.



### About Oanda Access Tokens
Using this package requires an access token to a user's
Oanda brokerage account. This module only uses the token to
request candle data, but such tokens can be used to make
trades on the account. It is recommended that access
tokens from a demo as opposed to a live accounts be used.
 
Demo account tokens can be generated by a signed in user here:

https://www.oanda.com/demo-account/tpa/personal_token

**Warning**: Oanda sometimes takes their API down for maintenance.
This seems to mostly occur shortly after the market closes at the end of
the trading week (at 5pm New York time). During the maintenance you
may get a 401 http response that looks like your token is not valid
even if it is.

