import base64
import hashlib
import hmac
import json
import pprint

import time

import requests

from mangus import config

PROTOCOL = 'https'
HOST = 'api.coinone.co.kr'


class Client:
    def __init__(self, key, secret):
        assert key
        assert secret
        self.URL = f'{PROTOCOL}://{HOST}'
        self.KEY = key
        self.SECRET = secret

    @property
    def _nonce(self):
        return time.time() * 1000000

    def _sign_payload(self, payload):
        j = json.dumps(payload)
        data = base64.standard_b64encode(j.encode('utf8'))

        h = hmac.new(self.SECRET.encode('utf8'), data, hashlib.sha512)
        signature = h.hexdigest()
        return {
            'Content-type': 'application/json',
            "X-COINONE-SIGNATURE": signature,
            "X-COINONE-PAYLOAD": data
        }

    def balances(self):
        payload = {
            'nonce': self._nonce,
            'access_token': self.KEY,
        }
        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + '/v2/account/balance', headers=signed_payload, verify=True)
        json_resp = r.json()
        return json_resp

    def limit_orders(self, currency):
        payload = {
            'access_token': self.KEY,
            'currency': currency,
            'nonce': self._nonce,
        }
        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + '/v2/order/limit_orders/', headers=signed_payload, verify=True)
        json_resp = r.json()
        return json_resp


if __name__ == '__main__':
    client = Client(key=config.COINONE.API_KEY, secret=config.COINONE.SECRET_API_KEY)
    # pprint.pprint(client.balances())
    pprint.pprint(client.limit_orders('btc'))
