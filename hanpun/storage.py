from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker

from mangus import config, const
from mangus.models.base import Base
from mangus.models.exchange import ExchangeMarket, WithdrawalFee, ExchangeMarketBalance, TradeFee
from mangus.models.ticker import CurrencySymbol

engine = create_engine(config.DB_URL)

db_session = scoped_session(sessionmaker(bind=engine))


def import_modules():
    import importlib
    from mangus import models
    for m in models.__all__:
        importlib.import_module('mangus.models.' + m, __name__)
        print(m)


def init_db():
    import_modules()
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)


def drop_db():
    import_modules()
    Base.metadata.bind = engine
    Base.metadata.drop_all(engine)


def exchange_market_initial(*args, **kwargs):
    print(f'exchange_market_initial')
    db_session.add(ExchangeMarket(name=const.BITFINEX))
    db_session.add(ExchangeMarket(name=const.BITHUMB))
    db_session.add(ExchangeMarket(name=const.COINONE))
    db_session.commit()


def withdraw_fee_initial(*args, **kwargs):
    print(f'withdraw_fee_initial')
    # bithumb
    bithumb = db_session.query(ExchangeMarket).filter(ExchangeMarket.name == const.BITHUMB).first()
    bithumb.withdrawal_fees.append(WithdrawalFee(
        symbol=CurrencySymbol.XRP,
        fee=0.01,
        min_amount=21,
    ))
    db_session.add(bithumb)

    # bitfinex
    bitfinex = db_session.query(ExchangeMarket).filter(ExchangeMarket.name == const.BITFINEX).first()
    bitfinex.withdrawal_fees.append(WithdrawalFee(
        symbol=CurrencySymbol.XRP,
        fee=0.01,
        min_amount=20,
    ))
    db_session.add(bithumb)
    db_session.commit()


def initial_trade_fees(*args, **kwargs):
    print(f'initial_trade_fees')
    # bithumb
    bithumb = db_session.query(ExchangeMarket).filter(ExchangeMarket.name == const.BITHUMB).first()
    bithumb.trade_fees.append(TradeFee(
        symbol=CurrencySymbol.XRP,
        fee_percent=0.15,
        min_amount=0,
    ))
    db_session.add(bithumb)

    # bitfinex
    bitfinex = db_session.query(ExchangeMarket).filter(ExchangeMarket.name == const.BITFINEX).first()
    bitfinex.trade_fees.append(TradeFee(
        symbol=CurrencySymbol.XRP,
        fee_percent=0.15,
        min_amount=0,
    ))
    db_session.add(bithumb)
    db_session.commit()


def initial_exchange_market_balances(*args, **kwargs):
    print(f'initial_exchange_market_balances')
    # bithumb
    bithumb = db_session.query(ExchangeMarket).filter(ExchangeMarket.name == const.BITHUMB).first()
    bithumb.balances.append(ExchangeMarketBalance(
        symbol=CurrencySymbol.XRP,
        address=config.BITHUMB.XRP_ADDRESS,
        destination=config.BITHUMB.XRP_DESTINATION_TAG,
    ))
    db_session.add(bithumb)

    # bitfinex
    bitfinex = db_session.query(ExchangeMarket).filter(ExchangeMarket.name == const.BITFINEX).first()
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
