import hashlib
import hmac
import pprint
import time
from urllib.parse import urlencode

import requests

from hanpun import config

PROTOCOL = 'https'
HOST = 'bittrex.com/api/v1.1'


class BittrexApi:
    def __init__(self, key, secret):
        self.URL = f'{PROTOCOL}://{HOST}'
        self.KEY = key
        self.SECRET = secret

    @property
    def _nonce(self):
        return str(int(time.time() * 1000))

    def api_requests(self, method, url, payload):
        assert method in ['get', 'post']
        headers = {
            'api_sign': hmac.new(self.SECRET.encode(), self.URL.encode(), hashlib.sha512).hexdigest()
        }
        request_url = self.URL + url

        request_url += '/apikey=' + self.KEY + "&nonce=" + self._nonce + '&'

        request_url += urlencode(payload)

        print(request_url)
        if method == 'get':
            return requests.get(url=request_url, headers=headers)
        elif method == 'post':
            return requests.post(url=request_url, headers=headers)

    def get_ticker(self, market):
        """
        Used to get the current tick values for a market.
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :return: Current values for given market in JSON
        :rtype : dict
        """
        return self.api_requests('get', '/public/getticker', {'market': market})


if __name__ == '__main__':
    bittrex = BittrexApi(config.BITTREX.API_KEY, config.BITTREX.SECRET_API_KEY)
    pprint.pprint(bittrex.get_ticker('USDT-XRP'))
