from src.job_setup import Factory
from src.operation.mainframe import MainFrame
from multiprocessing import Process, Manager


class Application:
    """Application is the Framework"""

    def __init__(self, path="C:/Users/tobyt/TestFactory/controller/controller.json"):
        self.factory = Factory(path=path)
        self.reports = Manager().dict()

    def report_judgement(self):
        """Based on the results, finalized whether a cases is pass or not"""
        # if not all Pass, then Fail
        pass

    def inner_loop_for_worker(self, worker_id, worker_tasks_all):
        """Loop the test case inside a worker"""
        # default template column if needed
        template_col = self.factory.setup['caseMap']['blueprintTemplateCol']
        template_col = 'template' if template_col == '' else template_col
        result = {}

        task_id = 1
        for _, job_to_do in worker_tasks_all.iterrows():
            # process info have i-th row test case
            template_to_fetch = job_to_do[template_col]
            process_info = {
                'service_info': self.factory.setup['service'],
                'test_input': job_to_do,
                'bp_map': self.factory.bp_maps[template_to_fetch],
            }

            # run this test with the above frag of data
            mainframe = MainFrame(process_info=process_info, printout=False)
            result[task_id] = mainframe.start()
            del mainframe
            task_id += 1
            
        # append results into a dict with workers set
        print(f"{worker_id} is adding results")
        self.reports[str(worker_id)] = result
        return True

    def initialize_tasks(self):
        assigned_tasks = self.factory.assigned_tasks  # contains all workers
        services = []
        
        # launch parallel services
        for worker_id, tasks_all in assigned_tasks.items():
            process = Process(
                target=self.inner_loop_for_worker,
                args=(worker_id, tasks_all)
            )
            services.append(process)
            process.start()
        
        # joining services
        for service in services:
            service.join()

        return None

if __name__ == '__main__':
    a = Application()
    a.initialize_tasks()
    print(a.reports)
