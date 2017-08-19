import datetime
from pprint import pprint

from mangus.controller.market import MarketController
from mangus.exc import MangusError
from mangus.models.exchange import TradeFee, WithdrawalFee
from mangus.models.ticker import Ticker
from mangus.storage import db_session


# r u trush market_price?

def check_market_price(tickers):
    assert len(tickers) > 100, f'ticker count {len(tickers)}'
    last_price = tickers[0].last_price

    # ALLOWED_ERROR_RANGE_PER = 0.1
    ALLOWED_ERROR_RANGE_PER = 3
    for t in tickers:
        error_range = abs(last_price - t.last_price)
        error_range_perc = error_range / last_price * 100
        if error_range_perc >= ALLOWED_ERROR_RANGE_PER:
            raise MangusError(f'error_range {error_range_perc}')

    return tickers[0]


def calc():
    mc = MarketController(db_session=db_session)
    markets = mc.all_markets()

    since = datetime.datetime.now() - datetime.timedelta(minutes=180)
    ticker_bucket = []

    for market in markets:
        tickers = (db_session
                   .query(Ticker)
                   .filter(Ticker.exchange_market_id == market.id,
                           Ticker.created_at >= since)
                   .order_by(Ticker.created_at.desc())
                   .all())
        # tickers 가 100개 이상이 되야지 믿을수 있지.
        if len(tickers) > 100:
            ticker_bucket.append(tickers)

    # 거래소 믿을수 있는 시장가 구하기
    market_last_tickers = []
    for tickers in ticker_bucket:
        try:
            market_last_tickers.append(check_market_price(tickers))
        except Exception as e:
            print(e)

    pprint([(ticker.exchange_market.name, ticker.last_price, ticker.created_at) for ticker in market_last_tickers])

    # 수익성 가장 좋은 market 찾기 ask = 판매가, bid = 구매가
    low_ask_ticker = None
    high_bid_ticker = None
    for ticker in market_last_tickers:
        low_ask_ticker = ticker if low_ask_ticker is None or ticker.last_price < low_ask_ticker.last_price else low_ask_ticker
        high_bid_ticker = ticker if high_bid_ticker is None or ticker.last_price > high_bid_ticker.last_price else high_bid_ticker

    amount = 10000
    print(f'low_ticker {low_ask_ticker.last_price} {low_ask_ticker.exchange_market.name}')
    print(f'high_ticker {high_bid_ticker.last_price} {high_bid_ticker.exchange_market.name}')
    profit_per_unit = high_bid_ticker.bid - low_ask_ticker.ask
    print(f'profit_per_unit {profit_per_unit} {profit_per_unit / low_ask_ticker.ask * 100}% ')

    fee_sum = 0
    for ticker in [low_ask_ticker, high_bid_ticker]:
        trade_ob = ticker.exchange_market.trade_fees.filter(TradeFee.symbol == ticker.symbol).first()
        trade_fee = amount * ticker.last_price * (trade_ob.fee_percent / 100)
        print(f'ticker {ticker} trade_fee {trade_fee}')
        withdrawal_ob = ticker.exchange_market.withdrawal_fees.filter(WithdrawalFee.symbol == ticker.symbol).first()
        withdrawal_fee = ticker.last_price * (withdrawal_ob.fee / 100)
        print(f'ticker {ticker} withdrawal_fee {withdrawal_fee}')

        fee_sum += trade_fee + withdrawal_fee
    print(f'total fee : ${fee_sum}')
    print(
        f'estimated profit amount : ${(profit_per_unit * amount)- fee_sum} used_money : ${low_ask_ticker.last_price * amount}')


if __name__ == '__main__':
    calc()
