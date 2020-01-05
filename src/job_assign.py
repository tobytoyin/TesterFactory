import pandas as pd


class Boss:
    def __init__(self, test_cases, n_workers):
        """
        A Boss need to assign workers, check that task required is good. 
        Arguments:
        -----
        `test_cases`: df containing all test cases scenario
        `n_workers`: number of workers required.
        """
        self.test_cases = self._validate_tasks(test_cases)
        self.n_workers = self._validate_workers(n_workers)

    def _validate_workers(self, n_workers):
        assert type(n_workers) is int, f"n_workers={n_workers} has to be an integer > 0"
        assert n_workers > 0, f"n_workers={n_workers} cannot be empty or 0"

        m = len(self.test_cases)
        # assign the n_workers as total number of cases
        return n_workers if n_workers < m else m

    def _validate_tasks(self, test_cases):
        assert not test_cases.empty, "test_cases cannot be empty"
        assert (
            test_cases.__class__ is pd.DataFrame
        ), "test_cases needs to be a DataFrame"

        # test_cases['result'] = None
        return test_cases

    def assign(self):
        """
        Assign workers to the tasks
        return: 
        -----
        An assigned workers dictionary: {workers_i: task list}
        """
        ### initialize dict ###
        workers = {}

        ### create worker's task ###
        # calculate number of task per worker
        task_num = round(len(self.test_cases) / self.n_workers)

        cur = 0
        for i in range(1, self.n_workers + 1):
            if i == self.n_workers:
                workers['worker_' + str(i)] = self.test_cases[cur::]
            else:
                workers['worker_' + str(i)] = self.test_cases[cur : cur + task_num]
                cur += task_num
            print(f">> workers_{i} gets a job...")
        return workers

