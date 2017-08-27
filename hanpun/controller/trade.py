import enum

from sqlalchemy.orm.scoping import ScopedSession

from hanpun import config, const
from hanpun.api.bitfinex import BitfinexApi
from hanpun.api.bithumb import BithumbApi
from hanpun.controller.base import BaseController
from hanpun.exc import HanpunError
from hanpun.models.exchange import ExchangeMarket, ExchangeMarketBalance
from hanpun.models.ticker import CurrencySymbol


class OrderStatus(enum.Enum):
    Error = 0
    SUCCESS = 1
    IN_PROGRESS = 2
    IS_CANCELLED = 3


class TradeController(BaseController):
    def __init__(self, db_session: ScopedSession):
        super().__init__(db_session)
        self.finex = BitfinexApi(config.BITFINEX.API_KEY, config.BITFINEX.SECRET_API_KEY)
        self.thumb = BithumbApi(config.BITHUMB.API_KEY, config.BITHUMB.SECRET_API_KEY)

    def balance(self, market, symbol: CurrencySymbol):
        """get my balance
        :param market:
        :param symbol:
        :return:  해당 market의 symbol amount
        """
        if market.name == const.BITFINEX:
            json = self.finex.balances()
            currency = symbol.value
            for item in json:
                if item['currency'] == currency and item['type'] == 'exchange':
                    return float(item['available'])
        elif market.name == const.BITHUMB:
            json = self.thumb.balances()
            data = json['data']
            print(data)
            if symbol == CurrencySymbol.USD:
                return float(data['total_krw']) / YahooClient.usd_krw_exchange_rate()
            if symbol == CurrencySymbol.XRP:
                return float(data['available_xrp'])
            else:
                raise NotImplementedError()
        return 0

    def exchange_sell(self, market, symbol: CurrencySymbol, amount, price):
        """
        :param market:
        :param symbol:
        :param amount:
        :param price:
        :return: order_id
        """
        if market.name == const.BITFINEX:
            json = self.finex.place_order(amount=amount, price=price, side='sell', symbol=symbol.value + 'usd')
            return json
        elif market.name == const.BITHUMB:
            json = self.thumb.new_sell_order(symbol=symbol, amount=amount)
            return json
        raise HanpunError('not impl')

    def exchange_buy(self, market, symbol: CurrencySymbol, amount, price):
        if market.name == const.BITFINEX:
            json = self.finex.place_order(amount=amount, price=price, side='buy', symbol=symbol.value + 'usd')
            return json['id']
        elif market.name == const.BITHUMB:
            json = self.thumb.new_buy_order(symbol=symbol, amount=amount)
            print(json)
        raise HanpunError('not impl')

    def order_status(self, market, order_id):
        if market.name == const.BITFINEX:
            json = self.finex.order_status(order_id=order_id)
            if float(json['remaining_amount']) < 0.01:
                return OrderStatus.SUCCESS
            elif bool(json['is_cancelled']):
                return OrderStatus.IS_CANCELLED
            else:
                return OrderStatus.IN_PROGRESS
        elif market.name == const.BITHUMB:
            pass
        raise HanpunError('not impl')

    def cancel_all_orders(self, market):
        print(f'cancel_all_orders market {market.name}')
        if market.name == const.BITFINEX:
            json = self.finex.cancel_all_orders()
            return json
        raise HanpunError('not impl')

    def withdraw(self, symbol: CurrencySymbol, amount, from_market, to_market):
        assert all([symbol, from_market, to_market])
        assert amount > 0

        to_balance = to_market.balances.filter(ExchangeMarketBalance.symbol == symbol).first()
        assert to_balance, '계좌가 없습니다.'

        if from_market.name == const.BITFINEX:
            json = self.finex.withdraw(symbol=symbol, amount=amount, address=to_balance.address,
                                       payment_id=to_balance.destination)
            return json

        raise HanpunError('not impl')

    def deposit_history(self, market: ExchangeMarket, symbol: CurrencySymbol):
        assert market
        assert symbol

        if market.name == const.BITHUMB:
            res = self.thumb.user_transactions(symbol=symbol, search=TransactionSearchType.DEPOSIT)
            return res
