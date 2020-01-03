class Cache:
    def __init__(self):
        """
        `Cache` is a cache for storing data for this application.
        Usage:
        ------
        `next(process)` generates a `Cache` object inside the `MainFrame`.
        Data required to 1 test step is then passed to `Execution` object to retreive data for selenium usage.
        Testing feedbacks are then passback to `Cache` and return to `MainFrame`.
        Finally `MainFrame` concatenate all caches and summarized into a report.
        """

        ### Data structure for running a single test process ###
        self._bp_cache = {
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
            'validate_value': '',
        }

        ### Data structure for runtime log ###
        self._log_cache = {
            'tc': '',
            'map_index': '',
            'expect': '',
            'actual': '',
            'result': '',
            'validate_method': '',
            'error_msg': '',
            'output': '',
            'g': '',
        }

        ### Test Cache ###
        self._cache = {}
        self._prev = {}

        # For assertion whether the test process pass or not?
        self._proceed = False

    @property
    def get_bp_cache(self):
        return self._bp_cache

    @property
    def get_log_cache(self):
        return self._log_cache

    @property
    def get_cache(self):
        return self._cache

    def data_str_load(self, **kwargs):
        """
        Add string-like data to `Cache`.
        Example:
        ------
        `data_load(key1=value1, key2=value2, ...)` loads value into `Cache._bp_cache`
        Only works when key exist in `Cache._bp_cache`
        """
        for key, value in kwargs.items():
            assert (
                key in self._bp_cache.keys()
            ), "Key not in blueprint, use data_add_key() to add new key"
            self._bp_cache[key] = str(value)
        return self.get_bp_cache

    def data_any_load(self, **kwargs):
        """
        Add any-like data to `Cache`.
        """
        for key, value in kwargs.items():
            assert (
                key in self._bp_cache.keys()
            ), "Key not in blueprint, use data_add_key() to add new key"
            self._bp_cache[key] = value
        return self.get_bp_cache

    def data_add_key(self, **args):
        """Add keys to `Cache`"""
        for new_key in args.items():
            assert new_key not in self._bp_cache.keys(), "Repeated Key"
            self._bp_cache[new_key] = ''
        return self.get_bp_cache

    def check_proceed(self, test_case=''):
        "A test case can proceed to next step"
        self._proceed = True
        return self

    def conditional_proceed(self, test_case=''):
        self.check_status = True
        self.log_input(tc=test_case, result='PASS - conditional item is hidden')
        return self

    def log_input(self, **kwargs):
        """Function for adding log for each testing process"""
        for key, value in kwargs.items():
            if key == 'tc':
                self._log_cache[key] = value
            else:
                self._log_cache[key] += f"{value}"
        return self.get_log_cache

    def cache_add(self, **kwargs):
        """Add data to cache"""
        for key, value in kwargs.items():
            self._cache[key] = value
        return self.get_cache

    def load_prev(self, prev):
        self._prev.update(prev)
        return None

    def is_empty(self):
        return self.get_log_cache['tc'] == ''
