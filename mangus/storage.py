from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker

from mangus import config
from mangus.models.base import Base
from mangus.models.exchange import ExchangeMarket

engine = create_engine(config.DB_URL)

db_session = scoped_session(sessionmaker(bind=engine))


def import_modules():
    import importlib
    from mangus import models
    for m in models.__all__:
        importlib.import_module('mangus.models.' + m, __name__)


def init_db():
    import_modules()
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)


def drop_db():
    import_modules()
    Base.metadata.bind = engine
    Base.metadata.drop_all(engine)


def insert_initial_values(*args, **kwargs):
    print(f'insert_initial_values')
    db_session.add(ExchangeMarket(name='bitfinex'))
    db_session.add(ExchangeMarket(name='bithumb'))
    db_session.add(ExchangeMarket(name='coinone'))
    db_session.commit()


event.listen(ExchangeMarket.__table__, 'after_create', insert_initial_values)
