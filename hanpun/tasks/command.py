import datetime
from pprint import pprint
import time

from hanpun import const
from hanpun.controller.market import MarketController
from hanpun.controller.trade import TradeController, OrderStatus
from hanpun.exc import HanpunError
from hanpun.models.exchange import TradeFee, WithdrawalFee, ExchangeMarket
from hanpun.models.ticker import Ticker, CurrencySymbol
from hanpun.storage import db_session


# r u trush market_price?

def check_market_price(tickers):
    assert len(tickers) > 100, f'ticker count {len(tickers)}'
    last_price = tickers[0].last_price

    ALLOWED_ERROR_RANGE_PER = 0.1
    for t in tickers:
        error_range = abs(last_price - t.last_price)
        error_range_perc = error_range / last_price * 100
        if error_range_perc >= ALLOWED_ERROR_RANGE_PER:
            raise HanpunError(f'error_range {error_range_perc}')

    return tickers[0]


def calc():
    mc = MarketController(db_session=db_session)
    markets = mc.all_markets()
    tc = TradeController(db_session=db_session)

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
        except HanpunError as e:
            print(e)

    print(f'markets {[ticker.exchange_market.name for ticker in market_last_tickers]}')
    assert len(market_last_tickers) > 0, '현재 가치있는 거래소가 없음.'

    # 수익성 가장 좋은 market 찾기 ask = 판매가, bid = 구매가
    low_ask_ticker = None
    high_bid_ticker = None
    for ticker in market_last_tickers:
        low_ask_ticker = ticker if low_ask_ticker is None or ticker.last_price < low_ask_ticker.last_price else low_ask_ticker
        high_bid_ticker = ticker if high_bid_ticker is None or ticker.last_price > high_bid_ticker.last_price else high_bid_ticker

    balance_amount = tc.balance(low_ask_ticker.exchange_market, CurrencySymbol.USD)
    assert balance_amount > 0, 'balances에 돈이 없다 ㅠ'

    buyable_amount = balance_amount / low_ask_ticker.last_price
    print(f'---------------------------------------------------------------------------')
    print(f'low_ticker {low_ask_ticker.last_price} {low_ask_ticker.exchange_market.name}')
    print(f'high_ticker {high_bid_ticker.last_price} {high_bid_ticker.exchange_market.name}')
    profit_per_unit = high_bid_ticker.bid - low_ask_ticker.ask
    print(f'profit_per_unit {profit_per_unit} {profit_per_unit / low_ask_ticker.last_price * 100}% ')
    print(f'buy_available_amount {buyable_amount} balance_amount {balance_amount} ')
    print(f'---------------------------------------------------------------------------')

    fee_sum = 0
    for ticker in [low_ask_ticker, high_bid_ticker]:
        trade_ob = ticker.exchange_market.trade_fees.filter(TradeFee.symbol == ticker.symbol).first()
        trade_fee = buyable_amount * ticker.last_price * (trade_ob.fee_percent / 100)
        withdrawal_ob = ticker.exchange_market.withdrawal_fees.filter(WithdrawalFee.symbol == ticker.symbol).first()
        withdrawal_fee = ticker.last_price * withdrawal_ob.fee

        print(f'ticker {ticker.exchange_market.name} trade_fee {trade_fee}')
        print(f'ticker {ticker.exchange_market.name} withdrawal_fee {withdrawal_fee}')

        fee_sum += trade_fee + withdrawal_fee
    print(f'total fee : ${fee_sum}')
    estimated_profit_price = (profit_per_unit * buyable_amount) - fee_sum
    used_money = low_ask_ticker.last_price * buyable_amount
    print(f'estimated profit amount : ${estimated_profit_price} used_money : ${used_money}')
    print(f'profit_per {estimated_profit_price / used_money}%')

    # assert estimated_profit_price > 0, '이득이 마이너스는 아니여야잖아'

    try:
        # 어마운트를 1로 조정
        exchange_market = low_ask_ticker.exchange_market
        order_id = tc.exchange_buy(exchange_market, symbol=low_ask_ticker.symbol, amount=buyable_amount,
                                   price=low_ask_ticker.ask)
        for idx in range(10):
            order_status = tc.order_status(exchange_market, order_id)
            print(f'order_status {order_status}')
            if order_status == OrderStatus.SUCCESS:
                balance_amount = tc.balance(low_ask_ticker.exchange_market, symbol=low_ask_ticker.symbol)

                withdraw(
                    symbol=low_ask_ticker.symbol,
                    amount=balance_amount,
                    to_market=high_bid_ticker.exchange_market, from_market=low_ask_ticker.exchange_market)
                break
            if order_status == OrderStatus.IS_CANCELLED:
                raise HanpunError('OrderStatus.IS_CANCELLED')
            time.sleep(1)

        tc.cancel_all_orders(exchange_market)
        raise HanpunError('timeout error')
    except Exception as e:
        print(e)
        raise e


def withdraw(symbol: CurrencySymbol, amount, from_market, to_market):
    tc = TradeController(db_session=db_session)
    tc.withdraw(symbol=symbol, amount=amount, from_market=from_market, to_market=to_market)
    print(f'symbol {symbol}, amount {amount}, from_market {from_market} to_market {to_market}')


if __name__ == '__main__':
    calc()
