from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.processing.caches import Cache
from src.helper import inline_arg_compile


class Process:
    def __init__(self, setup, test_input, bp_map, components_map):
        """
        Core processing for fetching data. Per blueprint task

        Parameters:
        ------
        `setup_info`: an dictionary converted from application json
        `test_input` (single Factory object): an object to keep track of data;
        `bp_map` (single Factory object): an process map mapping all testing actions for selenium to operate;
        """
        self.driver = self.create_driver()
        self.driver_options = setup['service']['options']
        self.additional_col = setup['caseMap']['additionalOutputCol']
        self.test_input = test_input
        self.bp_map = bp_map
        self.componenets_map = components_map
        self.test_id = self.test_input['test_id']  # define unique identity

    def __iter__(self):

        self.i = 0
        self.n = len(self.bp_map)
        return self

    def __next__(self):
        """
        Move the pointer. This also means that it moves the rows of the excel.
        Outputs:
        ------
        `caches`: A data cache for operation as well as report storage.
        """

        def _selector(from_master=False):
            if from_master:
                key = test_step['path']
                return self.componenets_map.loc[key]
            else:
                return test_step

        # pointer move in a step of flow_map
        i = self.i

        if i <= self.n:
            cache = Cache()
            test_step = self.bp_map.loc[i]
            test_data = self.test_input

            ### get locator from components_map ###
            from_master_bool = test_step['selector'] == 'master'
            source = _selector(from_master=from_master_bool)  # assign source

            ### handle data selection using key ###
            # special handling on NaN or %xxxxx test_step
            skip_step = str(test_step['key']) == 'nan' or test_step['key'][0] == '%'
            skip_validation = (
                str(test_step['validate_key']) == 'nan'
                or test_step['validate_key'][0] == '%'
            )

            # Framework treat 'nan' as skip case
            test_value = 'nan' if skip_step else test_data[test_step['key']]
            validate_value = (
                'nan' if skip_validation else test_data[test_step['validate_key']]
            )

            # update data into DataInterface of current pointing row
            cache.data_str_load(
                run_test_id=self.test_id,
                run_index=test_step['index'],
                run_locator=source['locator'],
                run_path=source['path'],
                run_method=test_step['method'],
                run_logic_str=test_step['logic'],
                run_key=test_step['key'],
                run_value=test_value,
                validate_method=test_step['validate_method'],
                validate_key=test_step['validate_key'],
                validate_value=validate_value,
                validate_logic=test_step['validate_logic'],
            )

            ### Load additional Fields ###
            if self.additional_col:
                for add_col in self.additional_col:
                    cache.data_str_load(**{f"add_{add_col}": test_data[add_col]})

            # compile inline-logic, add into DataInterface as dict()
            logic_dict = inline_arg_compile(str(test_step['logic']))
            validate_logic_dict = inline_arg_compile(str(test_step['validate_logic']))
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

    def create_driver(self):
        """start a webdriver"""
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # loop options setup
        for arg in self.driver_options:
            options.add_argument(arg)
        driver = webdriver.Chrome(
            'resources/webdrivers/chromedriver.exe', options=options
        )

        # options to avoid automation blocks
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd(
            "Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "tobyto"}}
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
