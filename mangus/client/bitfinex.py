import pprint
import base64
import hashlib
import hmac
import json
from decimal import Decimal

import time

import requests

from mangus import config

PROTOCOL = 'https'
HOST = 'api.bitfinex.com'
VERSION = 'v1'


class Symbol:
    XRP = 'xrpusd'
    ETH = 'ethusd'


class Client:
    def __init__(self, key, secret):
        self.URL = f'{PROTOCOL}://{HOST}/{VERSION}'
        self.KEY = key
        self.SECRET = secret

    def _sign_payload(self, payload):
        j = json.dumps(payload)
        data = base64.standard_b64encode(j.encode('utf8'))

        h = hmac.new(self.SECRET.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        return {
            "X-BFX-APIKEY": self.KEY,
            "X-BFX-SIGNATURE": signature,
            "X-BFX-PAYLOAD": data
        }

    @property
    def _nonce(self):
        return str(time.time() * 1000000)

    def place_order(self, amount, price, side, ord_type, symbol='btcusd', exchange='bitfinex'):
        """
        Submit a new order.
        :param amount:
        :param price:
        :param side: either 'buy' or 'sell'
        :param ord_type:
        :param symbol:
        :param exchange:
        :return:
        """
        payload = {
            "request": "/v1/order/new",
            "nonce": self._nonce,
            "symbol": symbol,
            "amount": str(Decimal(amount)),
            "price": str(Decimal(price)),
            "exchange": exchange,
            "side": side,
            "type": ord_type
        }
        print(payload)

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/order/new", headers=signed_payload, verify=True)
        json_resp = r.json()

        try:
            json_resp['order_id']
        except:
            return json_resp['message']

        return json_resp

    def cancel_all_orders(self):
        """
        Cancel all orders
        :return:
        """

        payload = {
            'request': '/v1/order/cancel/all',
            'nonce': self._nonce
        }
        signed_payload = self._sign_payload(payload=payload)
        r = requests.post(f'{self.URL}/order/cancel/all', headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp

    def balances(self):
        """
        Fetch balances

        :return:
        """
        payload = {
            'request': '/v1/balances',
            'nonce': self._nonce
        }

        signed_payload = self._sign_payload(payload=payload)
        r = requests.post(f'{self.URL}/balances', headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp

    def account_fees(self):
        """
        Fetch balances

        :return:
        """
        payload = {
            'request': '/v1/account_fees',
            'nonce': self._nonce
        }

        signed_payload = self._sign_payload(payload=payload)
        r = requests.post(f'{self.URL}/account_fees', headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp


if __name__ == '__main__':
    client = Client(key=config.BITFINEX_API_KEY, secret=config.BITFINEX_SECRET_API_KEY)
    # # pprint.pprint(client.balances())
    # # pprint.pprint(client.cancel_all_orders())
    # pprint.pprint(client.account_fees())
    # # pprint.pprint(
    # #     client.place_order(amount=4.99, price=0.1527, side='sell', ord_type='exchange limit', symbol='xrpusd'))
