from sqlalchemy import Column, Date, func, Integer, String, event

from mangus.common.datetime import TZDateTime
from mangus.models.base import Base


class ExchangeMarket(Base):
    __tablename__ = 'exchange_markets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(TZDateTime, nullable=False, server_default=func.now())
