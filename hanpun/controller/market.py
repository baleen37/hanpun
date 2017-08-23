from hanpun import const
from hanpun.controller.base import BaseController
from hanpun.exc import HanpunError
from hanpun.models.exchange import ExchangeMarket


class MarketController(BaseController):
    def all_markets(self):
        """
        :return: ExchangeMarket list
        """
        markets = self.db_session.query(ExchangeMarket).filter(
            ExchangeMarket.name.in_(const.AVAILABLE_MARKETS)
        ).all()

        assert len(markets) > 0

        return markets

    def get_market(self, name):
        """
        :param name: bitfinex, coinone, bithumb
        :return: ExchangeMarket
        """
        assert name in [const.BITFINEX, const.COINONE, const.BITHUMB]
        market = self.db_session.query(ExchangeMarket).filter(ExchangeMarket.name == name).first()

        if not market:
            raise HanpunError('market is none')

        return market
