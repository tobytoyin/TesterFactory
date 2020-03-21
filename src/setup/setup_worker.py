class AssignWorkers:
    def __init__(self, testcase, num_workers):
        """AssignWorkers helps to split the dataframe to a designated number of wokers"""
        self.testcase = testcase
        self.num_workers = self._validate_workers(num_workers)

    def _validate_workers(self, num_workers):
        """return the appropriate amount of workers"""
        assert type(num_workers) is int, f"num_workers: {num_workers} is not an integer"
        assert num_workers > 0, f"num_workers: {num_workers} cannot be empty or 0"

        m = len(self.testcase)
        return num_workers if num_workers < m else m 

    def assign_workers(self):
        """
        Assign workers to the tasks
        return: 
        -----
        An assigned workers dictionary: {worker_i: task list}
        """
        workers = {}

        ### create worker's task ###
        # calculate number of task per worker
        num_task = round(len(self.testcase) / self.num_workers)

        cur = 0
        for i in range(1, self.num_workers + 1):
            if i == self.num_workers:
                workers['worker_' + str(i)] = self.testcase[cur::]
            else:
                workers['worker_' + str(i)] = self.testcase[cur : cur + num_task]
                cur += num_task
            print(f">> worker_{i} gets a job...")
        return workers

