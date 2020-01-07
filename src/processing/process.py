from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.processing.caches import Cache
from src.helper import inline_arg_compile


class Process:
    def __init__(self, setup, test_input, bp_map):
        """
        Core processing for fetching data. Per blueprint task

        Parameters:
        ------
        `setup_info`: an dictionary converted from application json
        `test_input` (single Factory object): an object to keep track of data;
        `bp_map` (single Factory object): an process map mapping all testing actions for selenium to operate;
        """
        self.service_info = setup['service']
        self.additional_col = setup['caseMap']['additionalInputCol']
        self.test_input = test_input
        self.bp_map = bp_map
        self.driver = self.create_driver()
        self.tc = self.test_input['test_id']  # define unique identity

    def create_driver(self):
        """start a webdriver"""
        options = Options()
        for arg in self.service_info['options']:
            options.add_argument(arg)
        driver = webdriver.Chrome(
            'resources/webdrivers/chromedriver.exe', options=options
        )
        return driver

    def __iter__(self):
        self.i = 0
        self.n = len(self.bp_map)
        return self

    def __next__(self):
        """
        Move the pointer
        Outputs:
        ------
        `caches`: A data cache for operation as well as report storage.
        """
        # pointer move in a step of flow_map
        i = self.i

        if i <= self.n:
            cache = Cache()
            row = self.bp_map.loc[i]
            test_input = self.test_input

            ### handle data selection using key ###
            # special handling, skip
            pass_key = str(row['key']) == 'nan' or row['key'][0] == '%'
            pass_val = (
                str(row['validate_key']) == 'nan' or row['validate_key'][0] == '%'
            )

            value = 'nan' if pass_key else test_input[row['key']]
            validate_value = 'nan' if pass_val else test_input[row['validate_key']]

            # update data into DataInterface of current pointing row
            cache.data_str_load(
                run_tc=self.tc,
                run_index=row['index'],
                run_locator=row['locator'],
                run_path=row['path'],
                run_method=row['method'],
                run_logic=row['logic'],
                run_key=row['key'],
                run_value=value,
                validate_method=row['validate_method'],
                validate_key=row['validate_key'],
                validate_value=validate_value,
                validate_logic=row['validate_logic'],
            )
            ### Load additional Fields ###
            if self.additional_col:
                for add_col in self.additional_col:
                    cache.data_str_load(**{f"add_{add_col}": test_input[add_col]})

            # compile inline-logic, add into DataInterface as dict()
            logic_dict = inline_arg_compile(str(row['logic']))
            validate_logic_dict = inline_arg_compile(str(row['validate_logic']))
            cache.data_any_load(
                run_logic_fetch=logic_dict, validate_logic_fetch=validate_logic_dict
            )

            self.i += 1
            return cache
        else:
            raise StopIteration

    def pointer_change(self, value):
        """Change the ptr of the iter obj"""
        assert (value > 0) | (
            value < self.n
        ), f"value={value} out of reach: min=0, max={self.n}"
        self.i = int(value)
        return None

    @property
    def web_status(self):
        # JS object for the current web response
        js_command = '''
            return (() => {
                let e = new Response();
                return e.status;
            })();
        '''
        return self.driver.execute_script(js_command)
        # url = self.driver.current_url
        # return requests.get(url).status_code
