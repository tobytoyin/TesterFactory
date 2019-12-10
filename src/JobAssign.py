import pandas as pd


class Boss:
    def __init__(self, test_cases, n_workers):
        """
        Arguments:
        -----
        `test_cases`: df containing all test cases scenario.    
        `n_workers`: number of workers required.
        """
        self.test_cases = test_cases
        self.n_workers = self._validate(n_workers)

    def _validate(self, n_workers):
        m = len(self.test_cases)
        assert (
            n_workers != 0 |
            n_workers != ''), "n_workers cannot be empty or 0"
        # assign the n_workers as total number of cases
        return n_workers if n_workers < m else m
