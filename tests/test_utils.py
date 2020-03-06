import os
import tempfile
from unittest import TestCase

from arrayfiles import utils


class UtilsTestCase(TestCase):

    def setUp(self):
        self.fp = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.fp.close()

    def test_open(self):
        with utils.fd_open(self.fp.name, os.O_RDWR) as fd:
            self.assertIsInstance(fd, int)
