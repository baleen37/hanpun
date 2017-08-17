from sqlalchemy import Column, func, Integer, String, ForeignKey, Enum, Float, UniqueConstraint
from sqlalchemy.orm import relationship, backref

from mangus.common.datetime import TZDateTime
from mangus.models.base import Base
from mangus.models.ticker import CurrencySymbol


class WithdrawalFee(Base):
    __tablename__ = 'withdrawal_fees'
    __table_args__ = (
        UniqueConstraint('exchange_market_id', 'symbol', name='_withdrawal_fees_exchange_market_id_n_symbol_uc'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange_market_id = Column(ForeignKey('exchange_markets.id'), nullable=False)
    symbol = Column(Enum(CurrencySymbol), index=True, nullable=False)
    fee = Column(Float, nullable=False)
    created_at = Column(TZDateTime, nullable=False, server_default=func.now())

    exchange = relationship('ExchangeMarket', backref=backref('withdrawal_fees'))


class TradeFee(Base):
    __tablename__ = 'trade_fees'
    __table_args__ = (
        UniqueConstraint('exchange_market_id', 'symbol', name='_trade_fees_exchange_market_id_n_symbol_uc'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange_market_id = Column(ForeignKey('exchange_markets.id'), nullable=False)
    symbol = Column(Enum(CurrencySymbol), index=True, nullable=False)
    fee = Column(Float, nullable=False)
    created_at = Column(TZDateTime, nullable=False, server_default=func.now())

    exchange = relationship('ExchangeMarket', backref=backref('trade_fees'))


class ExchangeMarket(Base):
    __tablename__ = 'exchange_markets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(TZDateTime, nullable=False, server_default=func.now())
