# Helps to turn log data into a dataframe
from src.helper import Timer
import pandas as pd
from src.setup.setup_load import export_config
from src.setup.setup_dir import output_dir, create_output_path


class Examiner:
    def __init__(self, testreport):
        self._testreport = testreport
        self.log_df: pd.DataFrame = None

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

        # print(examine_list)
        col_names = list(examine_list[0].keys())
        self.log_df = pd.DataFrame(examine_list, columns=col_names)
        self.log_df.to_csv(create_output_path(name='logs', ext='csv'))

    def _hierarchical_result(self):
        'Generating a summary based on the level of hierarchy as a passing point'
        # IDEA: Allow users to generate a customer hierachy inside the section level and above the test_id level

        # generate unique values of hierarchy levels
        ref_id_unique = self.log_df['testcase_id'].unique()
        section_unique = self.log_df['testcase_section'].unique()
