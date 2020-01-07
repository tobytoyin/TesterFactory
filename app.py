from src.job_setup import Factory
from src.operation.mainframe import MainFrame
from multiprocessing import Process, Manager
import pandas as pd
from src.helper import print_table


class Application:
    """Application is the Framework"""

    def __init__(self, app_path="C:/Users/tobyt/Projects/TestFactory", **kwargs):
        self.app_path = app_path
        self.factory = Factory(path=f'{app_path}/controller/controller.json')
        self.reports = Manager().dict()
        self.data = self.factory.setup
        # others
        for key, value in kwargs.items():
            setattr(self, key, value)

    def inner_loop_for_worker(self, worker_id, worker_tasks_all):
        """Loop the test case inside a worker"""
        # default template column if needed
        template_col = self.data['caseMap']['blueprintTemplateCol']
        template_col = 'template' if template_col == '' else template_col
        result = {}

        # arguments for mainframe
        try:
            printout = bool(self.printout)
        except AttributeError:
            printout = False
        try:
            printout_cache = bool(self.printout_cache)
        except AttributeError:
            printout_cache = False
        try:
            stop_when_fail = bool(self.stop_when_fail)
        except AttributeError:
            stop_when_fail = True

        task_id = 1
        for _, job_to_do in worker_tasks_all.iterrows():
            # process info have i-th row test case
            template_to_fetch = job_to_do[template_col]

            process_info = {
                'setup': self.data,  # is the json setup
                'test_input': job_to_do,  # is the test load
                'bp_map': self.factory.bp_maps[template_to_fetch],
            }

            # run this test with the above frag of data
            mainframe = MainFrame(
                process_info=process_info,
                printout=printout,
                printout_cache=printout_cache,
                stop_when_fail=stop_when_fail,
            )
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
                target=self.inner_loop_for_worker, args=(worker_id, tasks_all)
            )
            services.append(process)
            process.start()

        # joining services
        for service in services:
            service.join()

    def test_tasks(self):
        assigned_tasks = self.factory.assigned_tasks  # contains all workers
        services = []
        for worker_id, tasks_all in assigned_tasks.items():
            report = self.inner_loop_for_worker(worker_id, tasks_all)
            services.append(report)

    def create_csv(self):
        ### function to use in df before exporting csv
        def _report_judgement():
            """Based on the results, finalized whether a cases is pass or not"""
            # if not all Pass, then Fail
            tc_unique = df['tc'].unique()
            print(tc_unique)
            out_li = []

            # Loop every unique workers result and judge the case
            for tc_to_judge in tc_unique:
                tem = df.loc[df['tc'] == tc_to_judge]
                final_result = 'Fail' if 'Fail' in tem['result'].values else 'Pass'

                # input to result
                out = {
                    'tc': tc_to_judge,
                    'map_index': 'END',
                    'result': final_result,
                    'g': 'END',
                }
                # add other fields
                diff = set(tem).difference(set(out))
                for d in diff:
                    out[d] = tem[d].unique()[0]

                print_table(out, title=f"Final result of {tc_to_judge}")

                out_li.append(out)
                del out, tem, final_result

            # summary = df.append(out_li, ignore_index=True)
            summary = pd.DataFrame(out_li)
            return summary

        validation_series_li = []  # for create dataframe

        # First layer loop {'worker_n': tasks}
        for worker_id, tasks in self.reports.items():
            # Second layer loop {'task_id': list of validation}
            for task_id, validation_list in tasks.items():
                # Third layer loop: [list of validation]
                for validation_item in validation_list:
                    tem = pd.Series({'worker_id': worker_id, 'worker_task_id': task_id})
                    tem = tem.append(pd.Series(validation_item))
                    validation_series_li.append(tem)
                    del tem

        ### Final reporting format ###
        path = self.data['output']['path']
        filename = self.data['output']['fileName']
        summaryname = self.data['output']['summaryName']
        col_names = list(validation_series_li[0].keys())

        df = pd.DataFrame(validation_series_li, columns=col_names)
        df.to_csv(f'{self.app_path}/{path}/{filename}')
        summary = _report_judgement()
        summary.to_csv(f'{self.app_path}/{path}/{summaryname}')
        return None


if __name__ == '__main__':
    a = Application(printout=False)
    a.initialize_tasks()
    a.create_csv()
