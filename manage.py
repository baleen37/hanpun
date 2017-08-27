import unittest

from manager import Manager

from hanpun import storage

manage = Manager()


@manage.command
def run():
    pass


@manage.command
def init_db():
    storage.init_db()


@manage.command
def drop_db():
    storage.drop_db()


@manage.command
def reset_db():
    storage.drop_db()
    storage.init_db()


@manage.command
def test():
    testsuite = unittest.TestLoader().discover('.', pattern='test_*.py')
    unittest.TextTestRunner().run(testsuite)


if __name__ == '__main__':
    manage.main()
