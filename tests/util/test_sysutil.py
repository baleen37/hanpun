import unittest

from hanpun.utils import sysutil


class TestSysutil(unittest.TestCase):
    def test_is_unittest(self):
        self.assertTrue(sysutil.is_unittest('unittest aa bb cc ss dd'.split()))
        self.assertTrue(sysutil.is_unittest('python -m unittest discover -s aa bb cc ss dd'.split()))
        self.assertTrue(
            sysutil.is_unittest('python -m unittest discover -s //dev/hanpun -t /dev/hanpun -p test_*.py '.split()))
        self.assertFalse(sysutil.is_unittest('uwsgi aa bb cc ss dd'.split()))

    def test_is_unittest2(self):
        print('hi')
        self.assertTrue(sysutil.is_unittest('unittest aa bb cc ss dd'.split()))
        self.assertTrue(sysutil.is_unittest('python -m unittest discover -s aa bb cc ss dd'.split()))
        self.assertTrue(
            sysutil.is_unittest('python -m unittest discover -s //dev/hanpun -t /dev/hanpun -p test_*.py '.split()))
        self.assertFalse(sysutil.is_unittest('uwsgi aa bb cc ss dd'.split()))
