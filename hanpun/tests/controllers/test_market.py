from hanpun import const
from hanpun.controller.market import MarketController
from hanpun.models import ExchangeMarket
from hanpun.tests.controllers.base import TestBaseController


class TestMarketController(TestBaseController):
    def setUp(self):
        super().setUp()
        m1 = ExchangeMarket(name='aaaa')
        m2 = ExchangeMarket(name='bbbb')
        self.db_session.add_all([m1, m2])
        self.db_session.commit()

    def test_all_markets(self):
        mc = MarketController(self.db_session)
        markets = mc.all_markets()

        self.assertGreater(len(markets), 0)
        names = [m.name for m in markets]
        for available_market_name in const.AVAILABLE_MARKETS:
            self.assertIn(available_market_name, names)
