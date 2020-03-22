class Cache:
    def __init__(self):
        """
        Cache is used to store data that are needed for making one test step. 
        And returning data or results of that test step
        Usage:
        ------
        `next(process)` generates a `Cache` object inside the `MainFrame`.
        Data required to 1 test step is then passed to `Execution` object to retreive data for selenium usage.
        Testing feedbacks are then passback to `Cache` and return to `MainFrame`.
        Finally `MainFrame` concatenate all caches and summarized into a report.
        """

        ### Input - Data structure for running a single test process ###
        self._exe_cache = {
            'ref_testcase_id': None,
            'ref_testcase_section': None,
            ###
            'exe_teststep_index': None,
            'exe_teststep_selector': None,
            'exe_teststep_source': None,
            'exe_teststep_method': None,
            #'exe_teststep_logic': None,
            'exe_teststep_key': None,
            'exe_teststep_data': None,
            'exe_teststep_arg': None,
            ###
            'validate_method': None,
            'validate_key': None,
            'validate_data': None,
            'validate_arg': None,
        }

        ### Results - Data structure for test process logs ###
        self._log_cache = {
            'teststep_index': None,
            'teststep_output': None,
            ###
            'testcase_id': None,
            'testcase_section': None,
            'testcase_expect': None,
            'testcase_actual': None,
            ###
            'validate_result': None,
            'validate_method': None,
            ###
            'error_alert': None,
            'exe_global_index': None,
        }

        ### Misc Cache ###
        self._tem_cache = {'element_exist': None}
        self.prev = {}

        ### Flow Control ###
        self._proceed = False  # by default a step cannot be proceed

    ### Golden Retriever ###
    def get_cache(self, which_cache='exe'):
        return self._cache_switch(which_cache)

    @property
    def ref_id(self):
        return str(self._exe_cache['ref_testcase_id'])

    ### Flow Control Change ###
    def allow_proceed(self):
        self._proceed = True
        return self

    ### Data Interaction - with the Input ache ###
    def data_load(self, load_to='exe', **kwargs):
        """
        Add type-data to `Cache.exe_cache`

        Parameters:
        -----
        `load_to` -- 'exe' - if load to self.exe_cache; 'log' - if load to self.log_cache\n
        `kwargs` -- (data_type, value)

        Example:
        ------
        `string_data_load(load_to, key1=(data_type, value), ...)` if key is well defined (load by arguments)\n
        `string_data_load(load_to, **{key: (data_type, value)})` if one is to use looping to load data
        """
        cache = self._cache_switch(to=load_to)
        for key, tuple_val in kwargs.items():
            self._key_validation(key, cache=load_to, check_exist=True)
            if tuple_val[0] == 'string':
                cache[key] = str(tuple_val[1])
            elif tuple_val[0] == 'log':
                end_space = " " if self.log_cache[key] != None else ""
                cache[key] += str(tuple_val[1]) + end_space
            else:
                cache[key] = tuple_val[1]

        return cache

    def data_key_add(self, *args, add_to='exe'):
        """Add list of new keys to the cache"""
        cache = self._cache_switch(to=add_to)
        for new_key in args:
            self._key_validation(new_key, cache=add_to, check_exist=False)
            cache[new_key] = None

        return cache

    # ### Data Interaction - with the Output ache ###
    # def log_enter(self, testcase_id=None, **kwargs):
    #     """Adding result to the log_cache"""
    #     # initialize id for identification
    #     self._testcase_id_not_empty(testcase_id)
    #     self.log_cache['testcase_id'] = testcase_id

    #     for key, value in kwargs.items():
    #         self._key_validation(key, cache='log', check_exist=True)
    #         end_space = " " if self.log_cache[key] != None else ""
    #         self.log_cache[key] += str(value) + end_space

    #     return self.log_cache

    def backup_cache(self, prev):
        """Load a backup cache to the prev (for backtracking the previous step)"""
        self.prev.update(prev)
        return self.prev

    ### Cache validation ###
    def _key_validation(self, key, cache='exe', check_exist=True):
        """
        validate whether a key exist (check_exist = True) or not (check_exist = False)
        validate on the cache (cache='exe') or (cache='log')
        """
        validate_on = self._cache_switch(to=cache)
        cache_keys = validate_on.keys()  # retrieve the keys for comparison
        error_msg = (
            f"\"Keys: <{key}> exists in the <{cache}_cache> is {not check_exist}\""
        )
        assert (key in cache_keys) == check_exist, error_msg

    def _testcase_id_not_empty(self, testcase_id):
        assert testcase_id != None, "testcase_id is empty"

    def _cache_switch(self, to='exe'):
        "for other functions to switch between different Cache._cache"
        if to == 'exe':
            return self._exe_cache
        elif to == 'tem':
            return self._tem_cache
        elif to == 'log':
            return self._log_cache
        else:
            raise AttributeError
