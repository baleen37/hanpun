import datetime
import time

from mangus import config, const
from mangus.client.bithumb import Client as BithumbClient
from mangus.client.bitfinex import Client as BitfinexClient
from mangus.client.yahoo import YahooClient
from mangus.models.exchange import ExchangeMarket
from mangus.models.ticker import Ticker, CurrencySymbol
from mangus.storage import db_session


def bitfinex_ticker():
    bitfinex = BitfinexClient(key=config.BITFINEX.API_KEY, secret=config.BITHUMB.SECRET_API_KEY)
    json = bitfinex.ticker('xrpusd')

    market = (db_session.query(ExchangeMarket)
              .filter(ExchangeMarket.name == const.BITFINEX)
              .first())
    ticker = Ticker(
        exchange_market=market,
        symbol=CurrencySymbol.XRP,
        bid=json['bid'],
        ask=json['ask'],
        last_price=json['last_price']
    )
    db_session.add(ticker)
    db_session.commit()


def bithumb_ticker():
    bithumb = BithumbClient(key=config.BITHUMB.API_KEY, secret=config.BITHUMB.SECRET_API_KEY)
    json = bithumb.ticker(CurrencySymbol.XRP)
    market = (db_session.query(ExchangeMarket)
              .filter(ExchangeMarket.name == const.BITHUMB)
              .first())
    ticker = Ticker(
        exchange_market=market,
        symbol=CurrencySymbol.XRP,
        bid=float(json['data']['buy_price']) / YahooClient.usd_krw_exchange_rate(),
        ask=float(json['data']['sell_price']) / YahooClient.usd_krw_exchange_rate(),
        last_price=float(json['data']['closing_price']) / YahooClient.usd_krw_exchange_rate()
    )
    db_session.add(ticker)
    db_session.commit()


if __name__ == '__main__':
    while True:
        print(f'tick... {datetime.datetime.now()}')
        try:
            bithumb_ticker()
        except Exception as e:
            print(e)
        try:
            bitfinex_ticker()
        except Exception as e:
            print(e)
        time.sleep(0.2)
