# oanda-candles
Oanda forex candle API built on top of oandapyV20

### Oanda Access Token
Using this package requires an access token to a user's
Oanda brokerage account. This module only uses the token to
request candle data, but such tokens can be used to make
trades on the account. It is recommended that access
tokens from a demo as opposed to a live accounts be used.
 
Demo account tokens can be generated by a signed in user here:

https://www.oanda.com/demo-account/tpa/personal_token


### CandleRequester class.
Supposing that `token` is set to an Oanda access token, one could print
the opening bid price of the latest 100 trading hours for the Aussie like this: 

```python
from oanda_candles import CandleRequester, Pair, Gran

aud_usd = Pair("audusd")
requester = CandleRequester(token, aud_usd, Gran.H1)
candles = requester.request(count=100)

for candle in candles:
    print(candle.bid.o)
```



### Request Ranges
The `CandleRequester.request()` has `start`, `end`, and `count`
optional parameters used to specify how many candles and from when.

| parameter | valid types | valid range | default |
|: --- |: --- |:----|:----|
| start | TimeInt, datetime, None | epoch to now | None |
| end | TimeInt, datetime, None | epoch to now | now | 
| count | int, None | 1 to 5000 | 500 |

It does not make sense to set all three of these parameters, but you can
specify any single one of them, or any two of them, or none of them.
The behavior for when they are set or unset is shown in this table:


| start | end | count | behavior |
|: --- |: --- |:----|: --- |
| -- | -- | -- | Get latest 500 candles |
| -- | -- | set | Get latest count candles |
| -- | set | -- | Get last 500 candles up until the end time |
| -- | set | set | Get last count candles up until the end time | 
| set | -- | -- | Get the first 500 candles from start time | 
| set | -- | set | Get the first count candles from start time |
| set | set | -- | Get candles from start to end times | 
| set | set | set | ValueError (there might be a different count in the range) | 
