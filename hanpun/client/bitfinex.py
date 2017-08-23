import pprint
import base64
import hashlib
import hmac
import json
from decimal import Decimal

import time

import requests

from hanpun import config
from hanpun.exc import HanpunError
from hanpun.models.ticker import CurrencySymbol

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

    def place_order(self, amount, price, side, symbol, ord_type='exchange limit', exchange='bitfinex'):
        """
        Submit a new order.
        :param amount:
        :param price:
        :param side: either 'buy' or 'sell'
        :param ord_type: exchange limit
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

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/order/new", headers=signed_payload, verify=True, timeout=10)
        json_resp = r.json()

        try:
            json_resp['order_id']
        except:
            raise HanpunError(json_resp.get('message', 'Unknown error'))

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
        r = requests.post(f'{self.URL}/order/cancel/all', headers=signed_payload, verify=True, timeout=10)
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
        r = requests.post(f'{self.URL}/balances', headers=signed_payload, verify=True, timeout=10)
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
        r = requests.post(f'{self.URL}/account_fees', headers=signed_payload, verify=True, timeout=10)
        json_resp = r.json()

        return json_resp

    def withdraw(self, symbol, amount, address, payment_id=None, wallet_selected='exchange'):
        """
        withdrawal

        :param symbol:
        :param wallet_selected:
        :param amount:
        :param address:
        :param payment_id:
        :return:
        """

        to_withdraw_type_dict = [
            (CurrencySymbol.BTC, 'bitcoin'),
            (CurrencySymbol.ETH, 'ethereum'),
            (CurrencySymbol.XRP, 'ripple')
        ]

        withdraw_type = None
        for _type in to_withdraw_type_dict:
            if symbol == _type[0]:
                withdraw_type = _type[1]

        assert withdraw_type in ['bitcoin', 'litecoin', 'ethereum', 'ethereumc', 'mastercoin', 'zcash', 'monero',
                                 'wire', 'dash', 'ripple', 'eos']
        assert wallet_selected in ['trading', 'exchange', 'deposit']

        payload = {
            'request': '/v1/withdraw',
            'withdraw_type': withdraw_type,
            'walletselected': wallet_selected,
            'amount': str(Decimal(amount)),
            'address': address,
            'payment_id': payment_id,
            'nonce': self._nonce
        }

        signed_payload = self._sign_payload(payload=payload)
        r = requests.post(f'{self.URL}/withdraw', headers=signed_payload, verify=True, timeout=10)
        json_resp = r.json()

        return json_resp

    def ticker(self, currency):
        assert currency

        r = requests.get(f'{self.URL}/pubticker/{currency}', verify=True, timeout=10)
        json_resp = r.json()

        return json_resp

    def order_status(self, order_id):
        assert order_id, 'order_id is none'

        payload = {
            'request': '/v1/order/status',
            'order_id': order_id,
            'nonce': self._nonce
        }

        signed_payload = self._sign_payload(payload=payload)
        r = requests.post(f'{self.URL}/order/status', headers=signed_payload, verify=True, timeout=10)
        json_resp = r.json()

        return json_resp


if __name__ == '__main__':
    client = Client(key=config.BITFINEX.API_KEY, secret=config.BITFINEX.SECRET_API_KEY)
    # pprint.pprint(client.ticker('xrpusd'))
    # pprint.pprint(client.balances())
    # pprint.pprint(client.cancel_all_orders())
    pprint.pprint(client.order_status(3480981615))
    # # pprint.pprint(
    # #     client.place_order(amount=4.99, price=0.1527, side='sell', ord_type='exchange limit', symbol='xrpusd'))
    # pprint.pprint(
    #     client.withdraw('ripple', 'exchange', 25, address=config.BITHUMB.XRP_ADDRESS,
    #                     payment_id=config.BITHUMB.XRP_DESTINATION_TAG))
