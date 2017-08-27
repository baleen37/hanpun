from hanpun import config, const
from hanpun.api.bitfinex import BitfinexApi
from hanpun.api.bithumb import BithumbApi
from hanpun.api.yahoo import YahooApi
from hanpun.controller.market import MarketController
from hanpun.controller.ticker import TickerController
from hanpun.models.ticker import CurrencySymbol
from hanpun.storage import db_session
from hanpun.tasks.celeryapp import app


@app.task
def tick_bitfinex():
    try:
        symbol = CurrencySymbol.XRP
        bitfinex = BitfinexApi(key=config.BITFINEX.API_KEY, secret=config.BITHUMB.SECRET_API_KEY)
        json = bitfinex.ticker(symbol)

        bid = json['bid']
        ask = json['ask']
        last_price = json['last_price']

        market = MarketController(db_session).get_market(const.BITFINEX)
        ticker = TickerController(db_session).create_ticker(market=market, symbol=symbol, bid=bid, ask=ask,
                                                            last_price=last_price)
        db_session.commit()

        return f'ticker: last_price {ticker.last_price}'
    except Exception as e:
        print(json)
        raise e


@app.task
def tick_bithumb():
    try:
        bithumb = BithumbApi(key=config.BITHUMB.API_KEY, secret=config.BITHUMB.SECRET_API_KEY)
        symbol = CurrencySymbol.XRP

        json = bithumb.ticker(symbol)
        market = MarketController(db_session).get_market(const.BITHUMB)

        bid = float(json['data']['buy_price']) / YahooApi.usd_krw_exchange_rate()
        ask = float(json['data']['sell_price']) / YahooApi.usd_krw_exchange_rate()
        last_price = float(json['data']['closing_price']) / YahooApi.usd_krw_exchange_rate()

        ticker = TickerController(db_session).create_ticker(market=market, symbol=symbol, bid=bid, ask=ask,
                                                            last_price=last_price)
        db_session.commit()
        return f'ticker: last_price {ticker.last_price}'
    except Exception as e:
        print(json)
        raise e
