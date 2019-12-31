from src.job_setup import Factory
from src.operation.mainframe import MainFrame
import multiprocessing


class Application:
    """Application is the Framework"""

    def __init__(self, path="C:/Users/tobyt/TestFactory/controller/controller.json"):
        self.factory = Factory(path=path)

    def inner_loop_for_worker(self, worker_tasks_all):
        """Loop the test case inside a worker"""
        # default template column if needed
        template_col = self.factory.setup['caseMap']['blueprintTemplateCol']
        template_col = 'template' if template_col == '' else template_col
        result = {}

        for i, job_to_do in worker_tasks_all.iterrows():
            print(job_to_do['index'])
            # process info have i-th row test case
            template_to_fetch = job_to_do[template_col]
            process_info = {
                'service_info': self.factory.setup['service'],
                'test_input': job_to_do,
                'bp_map': self.factory.bp_maps[template_to_fetch],
            }

            # run this test with the above frag of data
            mainframe = MainFrame(process_info=process_info, printout=False)
            result = mainframe.start()
        return result

    def initialize_tasks(self):
        assigned_tasks = self.factory.assigned_tasks  # contains all workers

        ### async ###
        # for task in .values():
        output = self.inner_loop_for_worker(assigned_tasks['worker_2'])
        print(output)


a = Application()
loop_list = a.initialize_tasks()
