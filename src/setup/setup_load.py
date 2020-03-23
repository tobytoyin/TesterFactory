## Use to setup testing data, config settings to Process() ##

import json
import pandas as pd
from src.helper import path_stroke_fix
from src.setup.setup_worker import AssignWorkers

path = 'C:/Users/tobyt/Projects/TestFactory'


class Loader:
    """Loader is responsible to load input files into the framework running structure"""

    def __init__(self, path):
        self.config = self._get_json(path)

    def _get_json(self, path):
        """load the json config file"""
        cur_dir = path_stroke_fix(path)
        path = f"{cur_dir}config/config.json"
        return json.load(open(path, 'r'))


class ConfigLoader(Loader):
    def __init__(self, path):
        "Child of Loader, which load the json, and export the config data"
        super().__init__(path)
        ### export configs for modules ###

    @property
    def teststep_config(self):
        """Export configs for teststeps"""
        teststep_key_names = self.config['reader_settings']['test_steps']
        return teststep_key_names

    @property
    def process_config(self):
        """Export configs for `Process` object"""
        driver_options = self.config['service']['options']
        output_col = self.config['test_cases_file']['additional_output_columns']
        process_config = {
            'assembler_config': {
                'driver_options': driver_options,
                'output_options': output_col,
                'teststep_config': self.teststep_config,
                'case_id': self.config['reader_settings']['test_case']['keys'][
                    'case_id'
                ],
            },
            'assembly_config': self.config['assembly_settings'],
        }
        return process_config


class DataLoader(Loader):
    def __init__(self, path):
        "Child of Loader, which load the json, and export the testing data"
        super().__init__(path)

    def _get_workbook(self, config_key=''):
        assert config_key != '', "config_key cannot be empty"
        location = path_stroke_fix(self.config[config_key]['path'])
        file_name = path_stroke_fix(self.config[config_key]['file_name'])[:-1]
        path = f"{location}{file_name}"
        workbook = pd.ExcelFile(path)
        return workbook

    @property
    def teststeps_map(self):
        """teststeps_map is a dictionary storing different test-steps of running test cases"""
        workbook = self._get_workbook(config_key='test_steps_file')
        teststeps_map = {}

        # set up testing_scenarios with different teststeps
        for testing_scenario in workbook.sheet_names:
            teststeps_map[testing_scenario] = pd.read_excel(
                workbook, testing_scenario, dtype=object
            )

        # setup a lookup components dataframe
        component_key = self.config['test_steps_file']['components_lib']
        component_map = teststeps_map[component_key].set_index('key')
        del teststeps_map[component_key]

        return teststeps_map, component_map

    @property
    def assign_testcase(self):
        """assign testcase to workers"""
        num_workers = self.config['service']['num_workers']
        workbook = self._get_workbook(config_key='test_cases_file')
        df = pd.DataFrame()
        for section in workbook.sheet_names:
            tem = pd.read_excel(workbook, section, dtype=object).dropna(how='all')
            tem['section'] = section  # add a column to define which section it is from
            df = df.append(tem)
            del tem

        # assign tasks to workers
        assign = AssignWorkers(df, num_workers=num_workers)
        del df

        return assign.assign_workers()


if __name__ == "__main__":
    pass
else:
    process_config = ConfigLoader(path=path).process_config
    assembler_config = process_config['assembler_config']
    assembly_config = process_config['assembly_config']
