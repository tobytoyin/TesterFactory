from src.setup.setup_load import DataLoader
from src.processing.belt import AssemblyBelt
import pprint
from multiprocessing import Process, Manager
from src.setup.setup_load import assembler_config


pp = pprint.PrettyPrinter(indent=4)


class AssemblyLines:
    """The AssemblyLines is a multi-processing class"""

    def __init__(self):
        super().__init__()
        self.TestSet = DataLoader()
        self.testreport = Manager().dict()

    def get_lines_start(self):
        "Split test cases to #num_workers"
        workers_get_ready = self.TestSet.assign_testcase
        jobs_to_start = []

        # launch parallel jobs
        for worker_i in workers_get_ready.items():
            print(worker_i)
            process = Process(target=self._belt_unit_run, args=(worker_i,))
            jobs_to_start.append(process)
            process.start()

        # join parallel jobs
        for job in jobs_to_start:
            job.join()

    def _belt_unit_run(self, worker: tuple):
        "worker: a tuple (worker_id, dataframe)"
        # initialize value
        worker_summary = {}
        task_id = 1

        template_key = assembler_config['testcase_config']['case_template']
        for _, task_to_do in worker[1].iterrows():
            template_to_use = task_to_do[template_key]

            # create the material for process
            material_per_task = {
                'worker_testcase': task_to_do,
                'teststep': self.TestSet.teststeps_map[0][template_to_use],
                'components_lib': self.TestSet.teststeps_map[1],
            }
            #
            belt = AssemblyBelt(material_per_task=material_per_task)
            worker_summary[task_id] = belt.start()  # add to a dictionary
            del belt
            task_id += 1
        # pp.pprint(worker_summary)

        # append results into a dict with workers set
        print(f"{worker[0]} is adding results")
        self.testreport[str(worker[0])] = worker_summary
        return True