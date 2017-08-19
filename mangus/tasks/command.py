import datetime
import pprint

import pytz

from mangus import const
from mangus.models.exchange import ExchangeMarket
from mangus.models.ticker import Ticker
from mangus.storage import db_session


def calc():
    bithumb = (db_session.query(ExchangeMarket).filter(ExchangeMarket.name == const.BITHUMB).first())
    bitfinex = (db_session.query(ExchangeMarket).filter(ExchangeMarket.name == const.BITFINEX).first())

    tz = pytz.timezone('Asia/Seoul')
    since = datetime.datetime.now(tz=tz) - datetime.timedelta(minutes=60 * 9)
    pprint.pprint(since)
    tickers = (db_session
               .query(Ticker)
               .filter(Ticker.exchange_market == bithumb,
                       Ticker.created_at >= since)
               .order_by(Ticker.created_at.desc())
               )
    pprint.pprint([t.created_at for t in tickers])


if __name__ == '__main__':
    calc()
