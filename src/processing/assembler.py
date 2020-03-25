### The module is to maintain the pointer of the test scenario in 1 test case ###
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from src.processing.cache import Cache
from src.helper import inline_arg_compile
from src.setup.setup_load import assembler_config


class Assembler:
    def __init__(self, testcase, teststep, component_map):
        """
        Parameter: 
        -----
        `assembler_config`: dict of configs data. Controlled in `setup_load.py`
        `testcase`: a single testcase 
        `teststep`: a single teststep to complete the `testcase`
        `component_map`: a dict to lookup defined common components
        """
        self.driver = self._create_driver()
        self.testcase = testcase
        self.teststep = teststep
        self.component_map = component_map

    def __iter__(self):
        self.ptr = 0
        self.end_index = len(self.teststep)
        return self

    def __next__(self):
        """Looping operator for running a test scenario
        Output:
        -----
        `caches`: 
        """
        ### helper functions ###
        def _source_location(lookup_component=False):
            """
            Find the source for webdriver
            `lookup_component`: False - inputs is the source, True - inputs is the key to the source
            """
            if lookup_component:
                return self.component_map.loc[cur_teststep[keys['source']]]
            else:
                return cur_teststep

        def _define_test_data(handle_for_key=None):
            # run a special symbol rules on a specific columns
            assert handle_for_key != None, "Pick a Key"
            assert handle_for_key in [
                keys['data_key'],
                keys['validate_data_key'],
            ], "Incorrect key"

            ## Determine Logics #
            nan_skip = str(cur_teststep[handle_for_key]) == 'nan'
            sym_skip = str(cur_teststep[handle_for_key]).startswith(symbols['skip_sym'])

            ## Logical Outcome ##
            skip_step = nan_skip or sym_skip

            # reference key to fetch the value
            lookup_key = cur_teststep[handle_for_key]
            return 'null' if skip_step else self.testcase[lookup_key]

        ptr = self.ptr

        # Set up Keys in the TestStepFile#
        keys = assembler_config['teststep_config']['keys']
        symbols = assembler_config['teststep_config']['symbols']

        # conduct a looping
        if ptr <= self.end_index:
            cache = Cache()
            cur_teststep = self.teststep.loc[ptr]

            ## 1. Check if the source is from component_map or from the data ##
            lookup_to_map = cur_teststep[keys['selector']] == symbols['lookup_sym']
            cur_teststep = _source_location(lookup_component=lookup_to_map)

            ## 2. Load addition column into the Cache ##
            additional_outputs = assembler_config['output_options']
            if additional_outputs:
                for add_col in additional_outputs:
                    cache.data_key_add(f'add_{add_col}', add_to='exe')
                    cache.data_load(
                        load_to='exe',
                        **{f'add_{add_col}': ('string', self.testcase[add_col])},
                    )

            ## 3. Compile inline-logic and add them as _args dict ##
            test_logic = inline_arg_compile(str(cur_teststep[keys['test_logic']]))
            validate_logic = inline_arg_compile(
                str(cur_teststep[keys['validate_logic']])
            )

            ## 4. Load data into the Cache of current step ##
            cache.data_load(
                load_to='exe',
                ref_testcase_id=(
                    'string',
                    self.testcase[assembler_config['testcase_config']['case_id']],
                ),
                ref_testcase_section=('string', self.testcase['section']),
                exe_teststep_index=('string', cur_teststep[keys['step_index']]),
                exe_teststep_selector=('string', cur_teststep[keys['selector']]),
                exe_teststep_source=('string', cur_teststep[keys['source']]),
                exe_teststep_method=('string', cur_teststep[keys['test_method']]),
                exe_teststep_key=('string', cur_teststep[keys['data_key']]),
                exe_teststep_data=(
                    'string',
                    _define_test_data(handle_for_key=keys['data_key']),
                ),
                exe_teststep_arg=('dict', test_logic),
                validate_method=('string', cur_teststep[keys['validate_method']]),
                validate_key=('string', cur_teststep[keys['validate_data_key']]),
                validate_data=(
                    'string',
                    _define_test_data(handle_for_key=keys['validate_data_key']),
                ),
                validate_arg=('dict', validate_logic),
            )

            self.ptr += 1
            return cache
        else:
            raise StopIteration

    def new_process_initialize(self, process_iter=None, global_index=None, prev=None):
        "Starting procedure for starting a new teststep (i to n)"
        cache: Cache = process_iter.__next__()
        cache.data_load(load_to='log', global_index=('any', global_index))
        cache.backup_cache(prev)
        return cache

    def ptr_change(self, new_ptr):
        "Change the ptr of the iterator to a new value"
        valid_ptr = (new_ptr >= 0) or (new_ptr < self.end_index)
        assert (
            valid_ptr
        ), f"value: {new_ptr} is out of reach: min=0, max={self.end_index}"
        self.ptr = int(new_ptr)
        return None

    def _create_driver(self):
        """start a webdriver"""
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # loop options setup
        for arg in assembler_config['driver_options']:
            options.add_argument(arg)
        driver = webdriver.Chrome(
            'resources/webdrivers/chromedriver.exe', options=options
        )

        # options to avoid automation blocks
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd(
            "Network.setExtraHTTPHeaders",
            {"headers": {"User-Agent": "cacbjiik maximus"}},
        )
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
            },
        )
        return driver
