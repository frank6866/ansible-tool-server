import unittest
import json
import benchmark.utils.chart_util as chart_util


class TestChartUtil(unittest.TestCase):
    def setUp(self):
        self.chart_id = 1

    def test_construct_char(self):
        data = chart_util.construct_char(self.chart_id)
        print json.dumps(data)
