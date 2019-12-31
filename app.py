from src.job_setup import Factory
from src.job_assign import Boss
from src.operation.mainframe import MainFrame


class Application:
    """Application is the Framework"""

    def __init__(self, path="C:/Users/tobyt/TestFactory/controller/controller.json"):
        self.factory = Factory(path=path)

    def test(self):
        assigned_tasks = self.factory.assigned_tasks
        job_1 = assigned_tasks['worker_1'].loc[0]
        job_1_template = job_1['template']

        process_info = {
            'service_info': self.factory.setup['service'],
            'test_input': job_1,
            'bp_map': self.factory.bp_maps[job_1_template],
        }
        return process_info


a = Application()
b = a.test()
mainframe = MainFrame(process_info=b, printout=True)
mainframe.start()

# def main(self):
#     test_cases = factory.test_inputs

#     # this should be a single DataFrame
#     assert test_cases.__class__ is pd.DataFrame, "input should be DataFrame"
