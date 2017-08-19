from sqlalchemy import Column, func, Integer, String, ForeignKey, Enum, Float, UniqueConstraint
from sqlalchemy.orm import relationship, backref

from mangus.common.datetime import TZDateTime
from mangus.models.base import Base
from mangus.models.ticker import CurrencySymbol


class WithdrawalFee(Base):
    """
    거래소 출금 수수료
    """
    __tablename__ = 'withdrawal_fees'
    __table_args__ = (
        UniqueConstraint('exchange_market_id', 'symbol', name='_withdrawal_fees_exchange_market_id_n_symbol_uc'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange_market_id = Column(ForeignKey('exchange_markets.id'), nullable=False)
    symbol = Column(Enum(CurrencySymbol), index=True, nullable=False)
    fee = Column(Float, nullable=False)
    min_amount = Column(Float, nullable=False, default=0)
    created_at = Column(TZDateTime, nullable=False, server_default=func.now())

    exchange = relationship('ExchangeMarket', backref=backref('withdrawal_fees', lazy='dynamic'))


class TradeFee(Base):
    """
    거래소 거래 수수료
    """
    __tablename__ = 'trade_fees'
    __table_args__ = (
        UniqueConstraint('exchange_market_id', 'symbol', name='_trade_fees_exchange_market_id_n_symbol_uc'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange_market_id = Column(ForeignKey('exchange_markets.id'), nullable=False)
    symbol = Column(Enum(CurrencySymbol), index=True, nullable=False)
    fee_percent = Column(Float, nullable=False)
    min_amount = Column(Float, nullable=False, default=0)
    created_at = Column(TZDateTime, nullable=False, server_default=func.now())

    exchange = relationship('ExchangeMarket', backref=backref('trade_fees', lazy='dynamic'))


class ExchangeMarketBalance(Base):
    __tablename__ = 'exchange_market_balances'

    __table_args__ = (
        UniqueConstraint('exchange_market_id', 'symbol',
                         name='_exchange_market_balance_exchange_market_id_n_symbol_uc'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange_market_id = Column(ForeignKey('exchange_markets.id'), nullable=False)
    symbol = Column(Enum(CurrencySymbol), index=True, nullable=False)
    address = Column(String, nullable=False)
    destination = Column(String, nullable=True)
    created_at = Column(TZDateTime, nullable=False, server_default=func.now())

    exchange = relationship('ExchangeMarket', backref=backref('balances'))


class ExchangeMarket(Base):
    __tablename__ = 'exchange_markets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(TZDateTime, nullable=False, server_default=func.now())
