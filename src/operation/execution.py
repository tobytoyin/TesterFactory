from selenium.webdriver.support.ui import WebDriverWait


class Execution:
    """
    Set of functions to use selenium webdriver

    Arguments:
    ------
    `driver` (Selenium webdriver): A predefined webdriver;
    `cache` (Process object, iterator): A set of data for selenium to work on.

    Error Handling:
    ------
    Errors will be treated as exception and reported in testing log
    """

    def __init__(self, driver, cache):

        # WebDriver Setup
        self.driver = driver
        self.driver.implicitly_wait(10)
        self.driver_wait = WebDriverWait(self.driver, 20)

        # Caches
        self.cache = cache
        # self.bp_cache = self.cache.get_bp_cache
        self.bp_cache = self.cache.get_cache(which_cache='exe')

        # Values that commonly used
        self.tc = self.bp_cache['ref_testcase_id']  # test case id
        self.element_exist = None  # determine whether a web-element exist or not

    ##### FUNCTIONS THAT VARY BY CHILD_CLASS #####
    def _logic_setup(self, default=''):
        """Setup for the inline-logic: setup default value if not logic"""
        assert default != '', "args--default requires a value"
        logic_list = list(self.logic_args.keys())  # retrieve child's list
        if not logic_list:
            logic_list.append(default)
        return logic_list

    def _logic_attr(self, logic_name='', attr='all'):
        """
        Retreive the attributes of a specific logic \n
        Inputs:
        -----
        `logic_name='func_name'` -- the logic name of which one wants to retreive \n
        `attr='all'` -- 'all': retreive the dictionary of values;
                'key': retreive a particular value from {'condition', 'input'}
        """
        assert logic_name != '', "'logic_name' must not be empty for retrieval"
        if attr == 'all':
            return self.logic_args[logic_name]
        else:
            return self.logic_args[logic_name][attr]

    ##### EXECUTION FUNCTION #####
    def execute_func(self, execute_for='exe_teststep'):
        """Trigger function through string in the blueprint"""
        assert execute_for in {
            'exe_teststep',
            'validate',
        }, "Usage: execute_for in {'exe_teststep', 'validate'}"
        # retrieve whether current cache is passing testing step or validating step function
        key = f'{execute_for}_method'
        bp_cache = self.bp_cache

        # Break and skip condition
        empty_func_cond = str(bp_cache[key]) == 'nan'
        if empty_func_cond:
            return None  # break, no func to execute
        func = getattr(self, bp_cache[key])
        func()

        ### add element into cache ###
        if self.element_exist is None:
            self.cache.data_load(load_to='tem', element_exist=('any', 0))
        else:
            self.cache.data_load(
                load_to='tem', element_exist=('any', self.element_exist)
            )

        ### add identification to log_cache when Validation###
        # tc -- id for test case data
        # map_index -- id for execution logic row
        if execute_for == 'validate':
            self.cache.data_load(
                load_to='log',
                testcase_id=('string', self.tc),
                testcase_section=('string', bp_cache['ref_testcase_section']),
                teststep_index=('string', bp_cache['exe_teststep_index']),
            )

            # add "add_" additional fields
            for item in bp_cache.keys():
                if "add_" in item:
                    self.cache.data_load(
                        load_to='log', **{item: ('string', bp_cache[item])}
                    )
