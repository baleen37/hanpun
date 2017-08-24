import base64
import hashlib
import hmac
import math
import pprint
import time
import urllib

import requests

from hanpun import config
from hanpun.models.ticker import CurrencySymbol

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
            "endpoint": endpoint,
        }

        url = self.URL + endpoint
        r = requests.post(url, data=payload, headers=self._sign_payload(payload))
        return r.json()

    def ticker(self, currency: CurrencySymbol.XRP):
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
        assert isinstance(currency, CurrencySymbol)
        endpoint = f'/public/ticker/{currency.name}'
        r = requests.get(self.URL + endpoint, timeout=10)
        json_resp = r.json()
        return json_resp

    def new_sell_order(self, symbol: CurrencySymbol, amount):
        """
        상품 판매
        :param symbol: CurrencySymbol
        :param amount: 수량 - 1회 최소 수량 (BTC: 0.001 | ETH: 0.01 | DASH: 0.01 | LTC: 0.1 | ETC: 0.1 | XRP: 10 | BCH: 0.01)
        - 1회 거래 한도 : 1억원
        :return:
        """
        assert isinstance(symbol, CurrencySymbol)
        assert amount
        endpoint = f'/trade/market_sell'
        payload = {
            "endpoint": endpoint,
            'currency': symbol.name,
            'units': amount
        }

        url = self.URL + endpoint
        r = requests.post(url, data=payload, headers=self._sign_payload(payload))
        return r.json()['order_id']

    def new_buy_order(self, symbol: CurrencySymbol, amount):
        """
        상품 구매
        :param symbol: CurrencySymbol
        :param amount: 수량 - 1회 최소 수량 (BTC: 0.001 | ETH: 0.01 | DASH: 0.01 | LTC: 0.1 | ETC: 0.1 | XRP: 10 | BCH: 0.01)
        - 1회 거래 한도 : 1억원
        :return:
        """
        assert isinstance(symbol, CurrencySymbol)
        endpoint = f'/trade/market_buy'
        payload = {
            "endpoint": endpoint,
            'currency': symbol.name,
            'units': amount
        }

        url = self.URL + endpoint
        r = requests.post(url, data=payload, headers=self._sign_payload(payload))
        return r.json()['order_id']

    def orders(self, symbol: CurrencySymbol, count=1000):
        """
        판구매 거래 주문 등록 또는 진행 중인 거래
        :param symbol:
        :param count: default 100
        :return:
        """
        assert isinstance(symbol, CurrencySymbol)
        endpoint = f'/info/orders'
        payload = {
            "endpoint": endpoint,
            'currency': symbol.name,
            'count': count,
        }

        url = self.URL + endpoint
        r = requests.post(url, data=payload, headers=self._sign_payload(payload))
        return r.json()

    def cancel_order(self, symbol: CurrencySymbol, order_id, trade_type):
        assert isinstance(symbol, CurrencySymbol)
        assert order_id
        assert trade_type in ['bid', 'ask']
        endpoint = f'/trade/cancel'
        payload = {
            "endpoint": endpoint,
            'currency': symbol.name,
            'type': trade_type,
            'order_id': order_id
        }

        url = self.URL + endpoint
        r = requests.post(url, data=payload, headers=self._sign_payload(payload))
        return r.json()

    def cancel_all_orders(self, symbol: CurrencySymbol):
        assert isinstance(symbol, CurrencySymbol)
        res = self.orders(symbol)
        if len(res['data']) < 1:
            return 0

        for order in res['data']:
            order_id = order['order_id']
            trade_type = order['type']
            self.cancel_order(symbol=symbol, order_id=order_id, trade_type=trade_type)
        return len(res['data'])

    def withdraw(self, symbol: CurrencySymbol, amount, address, destination=None):
        assert isinstance(symbol, CurrencySymbol)
        assert amount
        assert address

        # xrp 일때만 destination tag 가 필요
        if symbol == CurrencySymbol.XRP:
            assert destination

        endpoint = f'/trade/btc_withdrawal'
        payload = {
            "endpoint": endpoint,
            'currency': symbol.name,
            'units': amount,
            'address': address,
            'destination': destination,
        }

        url = self.URL + endpoint
        r = requests.post(url, data=payload, headers=self._sign_payload(payload))
        return r.json()

    def order_status(self):
        # TODO : 주문이 끝났는지 확인
        pass


if __name__ == '__main__':
    client = Client(key=config.BITHUMB.API_KEY, secret=config.BITHUMB.SECRET_API_KEY)
    # pprint.pprint(client.balances())
    # pprint.pprint(client.new_buy_order(symbol=CurrencySymbol.XRP, amount=10))
    pprint.pprint(client.new_sell_order(symbol=CurrencySymbol.XRP, amount=10.0))
    # pprint.pprint(client.orders(symbol=CurrencySymbol.XRP))
    # pprint.pprint(client.cancel_order(symbol=CurrencySymbol.XRP, order_id='1503070938067', trade_type='bid'))
    # pprint.pprint(client.cancel_all_orders(symbol=CurrencySymbol.XRP))
    # pprint.pprint(client.withdraw(symbol=CurrencySymbol.XRP, amount=21, address=config.BITFINEX.XRP_ADDRESS,
    #                               destination=config.BITFINEX.XRP_DESTINATION_TAG))
