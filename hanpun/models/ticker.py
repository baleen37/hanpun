import enum
from sqlalchemy import Column, Float, String, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import INTEGER, Integer, Date, Enum

from hanpun.common.datetime import TZDateTime
from hanpun.models.base import Base


class CurrencySymbol(enum.Enum):
    USD = 'usd'
    BTC = 'btc'
    ETH = 'eth'
    XRP = 'xrp'


class Ticker(Base):
    __tablename__ = 'tickers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(Enum(CurrencySymbol), index=True, nullable=False)
    bid = Column(Float, nullable=False, default=0)
    ask = Column(Float, nullable=False, default=0)
    last_price = Column(Float, nullable=False, default=0)
    created_at = Column(TZDateTime, nullable=False, server_default=func.now())

    exchange_market_id = Column(ForeignKey('exchange_markets.id'), nullable=False)

    exchange_market = relationship('ExchangeMarket')
