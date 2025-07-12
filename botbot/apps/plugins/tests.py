 # -*- coding: utf-8 -*-
import datetime

from django.test import TestCase
from datetime import datetime, timezone
from . import utils


class UtilsTestCase(TestCase):
    def test_nano_timestamp(self):
        timestamp = '2014-01-27T16:35:53.123456789Z'
        py_date = utils.convert_nano_timestamp(timestamp)
        self.assertEqual(py_date,
                         datetime.datetime(2014, 1, 27, 16, 35,
                                           53, 123456, tzinfo=datetime.UTC))

    def test_short_nano_timestamp(self):
        timestamp = '2014-01-27T16:35:53.1234Z'
        py_date = utils.convert_nano_timestamp(timestamp)
        self.assertEqual(py_date,
                         datetime.datetime(2014, 1, 27, 16, 35, 
                                           53, 123400, tzinfo=datetime.UTC))