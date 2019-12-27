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
        self._blueprint_cache = {
            'run_tc': '',
            'run_index': '',
            'run_locator': '',
            'run_path': '',
            'run_method': '',
            'run_logic': '',
            'run_logic_fetch': '',
            'run_key': '',
            'run_value': '',
            'validate_method': '',
            'validate_logic': '',
            'validate_logic_fetch': '',
            'validate_key': '',
            'validate_value': ''
        }

        ### Data structure for reporting ###
        self._log_cache = {
            'tc': '',
            'map_index': '',
            'expect': '',
            'validate_method': '',
            'actual': '',
            'result': '',
            'error_msg': '',
            'output': ''
        }

        ### Test Cache ###
        self._cache = {}

        # For assertion whether the test process pass or not?
        self._proceed = False

    @property
    def get_blueprint_cache(self):
        return self._blueprint_cache

    @property
    def get_log_cache(self):
        return self._log_cache

    @property
    def get_cache(self):
        return self._cache

    def data_str_load(self, **kwargs):
        """
        Add string-like data to `DataInterface`.
        Example:
        ------
        `data_load(key1=value1, key2=value2, ...)` loads value into `DataInterface._blueprint_cache`
        Only works when key exist in `DataInterface._blueprint_cache`
        """
        for key, value in kwargs.items():
            assert (key in self._blueprint_cache.keys()
                    ), "Key not in blueprint, use data_add_key() to add new key"
            self._blueprint_cache[key] = str(value)
        return self.get_blueprint_cache

    def data_any_load(self, **kwargs):
        """
        Add any-like data to `DataInterface`.
        """
        for key, value in kwargs.items():
            assert (key in self._blueprint_cache.keys()
                    ), "Key not in blueprint, use data_add_key() to add new key"
            self._blueprint_cache[key] = value
        return self.get_blueprint_cache

    def data_add_key(self, **args):
        """Add keys to `DataInterface`"""
        for new_key in args.items():
            assert (new_key not in self._blueprint_cache.keys()), "Repeated Key"
            self._blueprint_cache[new_key] = ''
        return self.get_blueprint_cache

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
            'actual': "ACTUAL={}",
            'result': "RESULT={}"
        }
        for key, value in kwargs.items():
            try:
                self._log_cache[key] += msg_prefix[key].format(value)
            except KeyError:
                self._log_cache[key] = value
        return self._log_cache

    def cache_add(self, **kwargs):
        """Add data to cache"""
        for key, value in kwargs.items():
            self._cache[key] = value
        return self.get_cache
