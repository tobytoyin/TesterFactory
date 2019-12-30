import unittest
from test.test_cases import real_df, fake_df, empty_df  # include different test cases
from src.job_assign import Boss
import pandas as pd

class TestBoss(unittest.TestCase):
    def test_n_workers_input(self):
        # test the n_workers assertion
        fail_case = [-1, 0, True, False, '1', 'hello', 3.1453]
        pass_case = [1, 3, 10, 22] 
        # false positive
        for f in fail_case:
            with self.assertRaises(AssertionError, msg="Failed: non int type injection"):
                boss = Boss(real_df, f) 
        # true positive
        for p in pass_case:
            try:
                boss = Boss(real_df, p)
            except AssertionError:
                raise ValueError("Correct value got rejected")

if __name__ == "__main__":
    unittest.main()
