from forex_types import Pair

from .candle_factory import CandleFactory
from .candle_requester import CandleRequester
from oandapyV20 import API
from .initializer import Initializer


class Client:
    def __init__(self, token: str):
        """Initialize with access token.

        Use this link is for access token to your live account:
            https://www.oanda.com/account/tpa/personal_token

        Use this link for access token to your demo account:
           https://www.oanda.com/demo-account/tpa/personal_token

        Warning:
           Although the CandleFactory code only uses this token to
        read candle data from Oanda, if somebody got a hold of your
        live token they could make trades on your behalf or cause
        other mischief with your live account. So keep it secure.
        If you think it might have been compromised, go to link
        above and revoke it right away.

        Args:
            token: str, access token to a demo or live account.
        """
        Initializer.initialize()
        self.api = API(access_token=token, headers={"Accept-Datetime-Format": "UNIX",})

    def new_candle_factory(self, pair: Pair, gran: str):
        return CandleFactory(self.api, pair, gran)

    def ger_requester(self, pair: Pair, gran: str):
        return CandleRequester(self.api, pair, gran)
