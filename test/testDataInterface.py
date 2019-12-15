import unittest
import os
from src.DataInterface import DataInterface


class TestDataInterface(unittest.TestCase):
    def test_update(self):
        ds = DataInterface()
        with self.assertRaises(AssertionError) as cm:
            ds.data_load(non_key='some_value')


if __name__ == "__main__":
    unittest.main()
