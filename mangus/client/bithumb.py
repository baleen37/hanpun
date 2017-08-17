import base64
import hashlib
import hmac
import json
import pprint

import time
import urllib

import math
import requests

from mangus import config
from mangus.models.ticker import Ticker, CurrencySymbol

PROTOCOL = 'https'
HOST = 'api.bithumb.com'


class Client:
    def __init__(self, key, secret):
        assert key
        assert secret
        self.URL = f'{PROTOCOL}://{HOST}'
        self.KEY = key
        self.SECRET = secret

    @property
    def _nonce(self):
        def microtime(get_as_float=False):
            if get_as_float:
                return time.time()
            else:
                return '%f %d' % math.modf(time.time())

        def usecTime():
            mt = microtime(False)
            mt_array = mt.split(" ")[:2];
            return mt_array[1] + mt_array[0][2:5];

        return usecTime()

    def _sign_payload(self, payload):
        str_data = urllib.parse.urlencode(payload)

        nonce = self._nonce

        data = payload['endpoint'] + chr(0) + str_data + chr(0) + nonce

        j = json.dumps(payload)
        # data = base64.standard_b64encode(j.encode('utf8'))

        h = hmac.new(self.SECRET.encode('utf8'), data.encode('utf-8'), hashlib.sha512)
        signature = h.hexdigest()
        return {
            'Content-type': 'application/json',
            "Api-Key": signature,
            "Api-Sign": data,
            'Api-Nonce': str(self._nonce)
        }

    def balances(self):
        endpoint = '/info/balance'
        payload = {
            'nonce': self._nonce,
            'access_token': self.KEY,
            'endpoint': endpoint,
        }
        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + endpoint, headers=signed_payload, verify=True)
        json_resp = r.json()
        return json_resp

    def ticker(self, currency):
        """
        :param currency:
        :return:
        opening_price	최근 24시간 내 시작 거래금액
        closing_price	최근 24시간 내 마지막 거래금액
        min_price	최근 24시간 내 최저 거래금액
        max_price	최근 24시간 내 최고 거래금액
        average_price	최근 24시간 내 평균 거래금액
        units_traded	최근 24시간 내 Currency 거래량
        volume_1day	최근 1일간 Currency 거래량
        volume_7day	최근 7일간 Currency 거래량
        buy_price	거래 대기건 최고 구매가
        sell_price	거래 대기건 최소 판매가
        date	현재 시간 Timestamp
        """
        assert currency, ['btc', 'eth', 'dash', 'ltc', 'etc', 'xrp', 'bch']
        endpoint = f'/public/ticker/{currency}'
        r = requests.get(self.URL + endpoint, timeout=10)
        json_resp = r.json()
        return json_resp


if __name__ == '__main__':
    client = Client(key=config.BITTHUMB.API_KEY, secret=config.BITTHUMB.SECRET_API_KEY)
    # pprint.pprint(client.balances())
    json = client.ticker('xrp')
    ticker = Ticker(
        symbol=CurrencySymbol.XRP,
        bid=json['data']['buy_price'],
        ask=json['data']['sell_price'],
        last_price=json['data']['closing_price']
    )
    print(ticker)
