from sqlalchemy.orm import Session
from sqlalchemy.orm.scoping import ScopedSession


class BaseController():
    def __init__(self, db_session: ScopedSession):
        self.db_session = db_session
        pass
