import base64
import hashlib
import hmac
import math
import pprint
import time
import urllib

import requests

from mangus import config

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

        mt = microtime(False)
        mt_array = mt.split(" ")[:2]
        return mt_array[1] + mt_array[0][2:5]

    def _sign_payload(self, payload):
        e_uri_data = urllib.parse.urlencode(payload)
        nonce = self._nonce
        hmac_data = payload['endpoint'] + chr(0) + e_uri_data + chr(0) + nonce

        hmh = hmac.new(bytes(self.SECRET.encode('utf-8')), hmac_data.encode('utf-8'), hashlib.sha512)
        signature = hmh.hexdigest()
        api_sign = base64.b64encode(signature.encode('utf-8'))
        return {
            "Api-Key": self.KEY,
            "Api-Sign": api_sign,
            'Api-Nonce': nonce
        }

    def balances(self):
        endpoint = '/info/balance'
        payload = {
            "endpoint": endpoint
        }

        url = self.URL + endpoint
        r = requests.post(url, data=payload, headers=self._sign_payload(payload))
        return r.json()

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
    pprint.pprint(client.balances())
