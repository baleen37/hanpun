import pytz
from sqlalchemy import types
from sqlalchemy.types import TypeDecorator

tz = pytz.timezone('Asia/Seoul')


class TZDateTime(TypeDecorator):
    impl = types.DateTime

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.astimezone(tz)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=pytz.utc).astimezone(tz)
