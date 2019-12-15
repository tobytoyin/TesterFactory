class DataInterface:
    def __init__(self):
        """
        `DataInterface` is a cache for storing data for this application. 
        Usage:
        ------
        `next(process)` generates a `DataInterface` object inside the `MainFrame`. 
        Data required to 1 test step is then passed to `Execution` object to retreive data for selenium usage. 
        Testing feedbacks are then passback to `DataInterface` and return to `MainFrame`.
        Finally `MainFrame` concatenate all caches and summarized into a report.
        """
        ### Data structure for running a single test process ###
        self._blueprint_data = {
            'run_tc': '',
            'run_locator': '',
            'run_path': '',
            'run_method': '',
            'run_logic': '',
            'run_key': '',
            'run_value': '',
            'validate_method': '',
            'validate_key': '',
            'validate_value': ''
        }

        ### Data structure for reporting ###
        self._log_data = {
            'tc': '',
            'expect': '',
            'result': '',
            'error_msg': '',
            'output': ''
        }

        ### Test Cache ###
        self._cache = {}

        # For assertion whether the test process pass or not?
        self._proceed = False

    @property
    def get_blueprint_data(self):
        return self._blueprint_data

    @property
    def get_log_data(self):
        return self._log_data

    @property
    def get_cache(self):
        return self._cache

    def data_load(self, **kwargs):
        """
        Add data to `DataInterface`.
        Example:
        ------
        `data_load(key1=value1, key2=value2, ...)` loads value into `DataInterface._blueprint_data`
        Only works when key exist in `DataInterface._blueprint_data`
        """
        for key, value in kwargs.items():
            assert (key in self._blueprint_data.keys()
                    ), "Key not in blueprint, use data_add() to add new key"
            self._blueprint_data[key] = str(value)
        return self.get_blueprint_data

    def data_add(self, **kwargs):
        for key, value in kwargs.items():
            self._blueprint_data[key] = value
        return self.get_blueprint_data

    def check_proceed(self, test_case=''):
        "A test case can proceed to next step"
        self._proceed = True
        return self

    def conditional_proceed(self, test_case=''):
        self.check_status = True
        self.log_input(tc=test_case,
                       result='PASS - conditional item is hidden')
        return self

    def log_input(self, **kwargs):
        """Function for adding log for each testing process"""
        msg_prefix = {
            'error_msg': "ERROR={}",
            'expect': "EXPECTED={}",
            'result': "RESULT={}"
        }
        for key, value in kwargs.items():
            try:
                self._log_data[key] += msg_prefix[key].format(value)
            except KeyError:
                self._log_data[key] = value
        return self._log_data

    def cache_add(self, **kwargs):
        """Add data to cache"""
        for key, value in kwargs.items():
            self._cache[key] = value
        return self.get_cache
