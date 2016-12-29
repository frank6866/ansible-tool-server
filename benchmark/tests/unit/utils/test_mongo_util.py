import unittest

import benchmark.utils.mongo_util as mongo_util


class TestProcessUtil(unittest.TestCase):
    def setUp(self):
        self.ip = "10.0.246.132/24"
        self.time_str = "2016-12-28-22-05-03"
        self.test_result = {"ip": self.ip,
                            "time_str": self.time_str}

    def tearDown(self):
        pass

    def test_insert_test_result(self):
        mongo_util.insert_test_result(self.test_result)

    def test_truncate_test_results(self):
        mongo_util.truncate_test_results()



