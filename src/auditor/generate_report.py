# Helps to turn log data into a dataframe
from src.helper import Timer
import pandas as pd
from src.setup.setup_load import export_config
from src.setup.setup_dir import output_dir, create_output_path


class Examiner:
    def __init__(self, testreport):
        self._testreport = testreport

    # def _export_csv(self, name):
    #     outputfile = create_output_path(name=name)

    def create_log_csv(self):
        "Create a dataframe like testreport for process"
        examine_list = []
        # First layer loop {'worker_n': tasks}
        for worker_id, tasks in self._testreport.items():
            # Second layer loop {'task_id': list of validation}
            for task_id, log_list in tasks.items():
                # Third layer loop: [list of validation]
                for log_item in log_list:
                    tem = pd.Series({'worker_id': worker_id, 'worker_task_id': task_id})
                    tem = tem.append(pd.Series(log_item))
                    examine_list.append(tem)
                    del tem
        col_names = list(examine_list[0].keys())
        df = pd.DataFrame(examine_list, columns=col_names)
        df.to_csv(create_output_path(name='logs', ext='csv'))
