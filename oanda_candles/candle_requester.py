from requests import Session
from typing import List
from urllib.parse import urljoin

from forex_types import Pair
from time_int import TimeInt

from oanda_candles.gran import Gran
from oanda_candles.candle import Candle


class UrlRoot:
    real_url = "https://api-fxtrade.oanda.com"
    practice_url = "https://api-fxpractice.oanda.com"


class CandleRequester:
    def __init__(self, client, pair: Pair, gran: Gran):
        self.session: Session = client.session
        root_url = UrlRoot.real_url if client.real else UrlRoot.practice_url
        self.url = urljoin(root_url, f"/v3/instruments/{pair}/candles")
        self.headers = {
            "Accept-Datetime-Format": "UNIX",
            "Authorization": f"Bearer {client.token}",
            "ContentType": "application/json",
        }
        self.params = {
            "alignmentTimezone": "Etc/GMT+1",
            "dailyAlignment": 23,
            "granularity": str(gran),
            "price": "BAM",
            "weeklyAlignment": "Sunday",
        }
        self.history_reached: bool = False

    def get(self, count: int) -> List[Candle]:
        """Request the most recent count candles."""
        if count < 5000:
            return self._request(count=count)
        candles = self._request(count=2000)
        if len(candles) >= 2000:
            extra = count - 2000
            self.prepend(candles, extra)
        return candles

    def get_before(self, time: TimeInt, count: int) -> List[Candle]:
        return self._request(count=count, before=time)

    def get_after(self, time: TimeInt):
        return self._request(after=time)

    def prepend(self, candles: List[Candle], count: int) -> bool:
        """Prepend candles to front of a list (recurse if needed).

        Args:
            candles: list of candles that is prepended with older candles.
            count: number of candles to prepend. If 0 or less do nothing.
        Returns:
            True if the requested number of candles is provided.
            False if Oanda ran out of candles to give us.
        """
        if count <= 0:
            return True
        first_candle_time = candles[0].time if candles else TimeInt.now()
        pull_size = count if count <= 5000 else 2000
        new_candles = self._request(count=pull_size, before=first_candle_time)
        if len(new_candles):
            candles[0:0] = new_candles
            if len(new_candles) < pull_size:
                return False
            else:
                if count > pull_size:
                    return self.prepend(candles, count - pull_size)
                return True
        return False

    def extend(self, candles: List[Candle]) -> bool:
        """Extend candles to back of a list up to current time (recurse if needed).

        Args:
            candles: list of candles that is extended with newer candles.
        Returns:
            True if the last candle we end up with is complete
            False if the lst candle we end up with is partial
        """
        if candles:
            last_candle_time = candles[-1].time
            new_candles = self._request(after=last_candle_time, count=5000)
            candles[-1:] = new_candles
            if len(new_candles) >= 5000:
                self.extend(candles)
        else:
            candles[:] = self._request(count=100)
        return candles[-1].complete

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _request(
        self, count: int = None, before: int = None, after: int = None
    ) -> List[Candle]:
        params = dict(self.params)
        if count is not None:
            params["count"] = count
        if after is not None:
            params["from"] = after
        if before is not None:
            params["to"] = before
        response = self.session.get(self.url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [Candle.from_oanda(_) for _ in data["candles"]]
