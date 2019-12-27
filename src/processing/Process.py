from selenium import webdriver
from src.processing.DataInterface import DataInterface
from src.Factory import Factory
from src.helper import inline_arg_compile


class Process:
    def __init__(self, driver, test_input, flow_map):
        # , driver, data_interface,
        """
        Core processing for fetching data 

        Parameters:
        ------
        `driver` (Selenium object): a selenium driver object; 
        `test_input` (single Factory object): an object to keep track of data;
        `flow_map` (Factory object): an process map mapping all testing actions for selenium to operate;
        """
        self.driver = driver
        self.test_input = test_input
        self.flow_map = flow_map

        # define unique identity
        self.tc = self.test_input['test_id']

        self.special_regex = r"(->|nan)"

    def __iter__(self):
        self.i = 0
        self.n = len(self.flow_map)
        return self

    def __next__(self):
        """
        Move the pointer
       Outputs:
       ------
       `data_interface`: A data cache for operation as well as report storage.
       """
        # pointer move in a step of flow_map
        i = self.i

        if i <= self.n:
            data_interface = DataInterface()
            row = self.flow_map.loc[i]

            ### handle data selection using key ###
            # special handling, skip
            pass_key = str(row['key']) == 'nan' or row['key'][0] == '%'
            pass_val = str(row['validate_key']) == 'nan' or row['validate_key'][0] == '%'

            value = 'nan' if pass_key else self.test_input[row['key']]
            validate_value = 'nan' if pass_val else self.test_input[row['validate_key']]

            # update data into DataInterface of current pointing row
            data_interface.data_str_load(
                run_tc=self.tc,
                run_locator=row['locator'], run_path=row['path'], run_method=row['method'],
                run_logic=row['logic'], run_key=row['key'], run_value=value,
                validate_method=row['validate_method'], validate_value=validate_value,
                validate_logic=row['validate_logic'])

            # compile inline-logic, add into DataInterface as dict()
            logic_dict = inline_arg_compile(str(row['logic']))
            validate_logic_dict = inline_arg_compile(
                str(row['validate_logic']))
            data_interface.data_any_load(
                run_logic_fetch=logic_dict, validate_logic_fetch=validate_logic_dict)

            self.i += 1
            return data_interface
        else:
            raise StopIteration

    def pointer_change(self, switch_method='next', value=1):
        if switch_method == 'jumpto':
            self.i = int(value)
        return self

    @property
    def web_status(self):
        # JS object for the current web response
        js_command = """
            return (() => {
                let e = new Response();
                return e.status;
            })();
        """
        return self.driver.execute_script(js_command)


f = Factory()
case = 2
t = f.test_inputs
template = t['template'][case]
a = f.flow_maps[template]
driver = webdriver.Chrome('resources/webdrivers/chromedriver.exe')
p = Process(driver, t.loc[case], a)
# it = iter(p)
# n = next(it)

test_data = {
    'driver': driver,
    'f': f,
    'flow_maps': a,
    'test_inputs': t,
    'process': p
    # 'data_interface': n
}
