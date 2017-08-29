from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker

from hanpun import config, const
from hanpun.controller.market import MarketController
from hanpun.models import ExchangeMarketBalance, ExchangeMarket, WithdrawalFee, CurrencySymbol, TradeFee
from hanpun.models.base import Base

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
engine.echo = config.DB_ECHO

db_session = scoped_session(sessionmaker(bind=engine))


def init_db():
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.bind = engine
    db_session.commit()
    Base.metadata.drop_all(engine)



def exchange_market_initial(*args, **kwargs):
    print(f'exchange_market_initial')
    for market in const.MARKETS:
        db_session.add(ExchangeMarket(name=market))
    db_session.commit()


def withdraw_fee_initial(*args, **kwargs):
    print(f'withdraw_fee_initial')
    mc = MarketController(db_session=db_session)
    # bithumb
    bithumb = mc.get_market(const.BITHUMB)
    bithumb.withdrawal_fees.append(WithdrawalFee(
        symbol=CurrencySymbol.XRP,
        fee=0.01,
        min_amount=21,
    ))
    db_session.add(bithumb)

    # bitfinex
    bitfinex = mc.get_market(const.BITFINEX)
    bitfinex.withdrawal_fees.append(WithdrawalFee( symbol=CurrencySymbol.XRP, fee=0.01,
        min_amount=20,
    ))
    db_session.add(bithumb)
    db_session.commit()


def initial_trade_fees(*args, **kwargs):
    print(f'initial_trade_fees')
    mc = MarketController(db_session=db_session)
    # bithumb
    bithumb = mc.get_market(const.BITHUMB)
    bithumb.trade_fees.append(TradeFee(
        symbol=CurrencySymbol.XRP,
        fee_percent=0.15,
        min_amount=0,
    ))
    db_session.add(bithumb)

    # bitfinex
    bitfinex = mc.get_market(const.BITFINEX)
    bitfinex.trade_fees.append(TradeFee(
        symbol=CurrencySymbol.XRP,
        fee_percent=0.15,
        min_amount=0,
    ))
    db_session.add(bithumb)
    db_session.commit()


def initial_exchange_market_balances(*args, **kwargs):
    print(f'initial_exchange_market_balances')
    mc = MarketController(db_session=db_session)
    # bithumb
    bithumb = mc.get_market(const.BITHUMB)
    bithumb.balances.append(ExchangeMarketBalance(
        symbol=CurrencySymbol.XRP,
        address=config.BITHUMB.XRP_ADDRESS,
        destination=config.BITHUMB.XRP_DESTINATION_TAG,
    ))
    db_session.add(bithumb)

    # bitfinex
    bitfinex = mc.get_market(const.BITFINEX)
    bitfinex.balances.append(ExchangeMarketBalance(
        symbol=CurrencySymbol.XRP,
        address=config.BITFINEX.XRP_ADDRESS,
        destination=config.BITFINEX.XRP_DESTINATION_TAG,
    ))
    db_session.add(bithumb)
    db_session.commit()


event.listen(ExchangeMarket.__table__, 'after_create', exchange_market_initial)
event.listen(WithdrawalFee.__table__, 'after_create', withdraw_fee_initial)
event.listen(TradeFee.__table__, 'after_create', initial_trade_fees)
event.listen(ExchangeMarketBalance.__table__, 'after_create', initial_exchange_market_balances)
