from hanpun.controller.base import BaseController
from hanpun.models.exchange import ExchangeMarket
from hanpun.models.ticker import CurrencySymbol, Ticker


class TickerController(BaseController):
    def last_ticker(self, market_id, symbol: CurrencySymbol):
        """
        :return: ExchangeMarket list
        """
        ticker = (self.db_session.query(Ticker)
                  .filter(Ticker.symbol == symbol,
                          Ticker.exchange_market_id == market_id)
                  .order_by(Ticker.id.desc())
                  .first())
        return ticker

    def create_ticker(self, market, symbol: CurrencySymbol, bid, ask, last_price):
        assert symbol
        assert bid
        assert ask
        assert last_price

        ticker = Ticker(
            exchange_market=market,
            symbol=symbol,
            bid=bid,
            ask=ask,
            last_price=last_price
        )
        self.db_session.add(ticker)
        return ticker
