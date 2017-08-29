import unittest

from hanpun import storage


class TestBaseController(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.db_session = storage.db_session

    def setUp(self):
        super().setUp()
        storage.drop_db()
        storage.init_db()

    def tearDown(self):
        super().tearDown()
        storage.drop_db()
        storage.db_session.remove()
