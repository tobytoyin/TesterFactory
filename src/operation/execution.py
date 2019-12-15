from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from src.processing.Process import test_data
# driver = webdriver.Chrome()


class Execution:
    """
    Set of functions to use selenium webdriver

    Arguments:
    ------
    `driver` (Selenium webdriver): A predefined webdriver;
    `data_interface` (Process object, iterator): A set of data for selenium to work on.

    Error Handling:
    ------
    Errors will be treated as exception and reported in testing log
    """

    def __init__(self, driver, data_interface):
        self.driver = driver
        self.driver.implicitly_wait(10)
        self._data_interface = data_interface
        self.blueprint_data = self._data_interface.get_blueprint_data
        self.tc = self.blueprint_data['run_tc']
        self.element_exist = None  # determine whether a web-element exist or not

    def execute_func(self, execute_for='run'):
        """Execute function through string fetching"""
        assert execute_for in ['run', 'validate'], \
            "Usage: execute_for in ['run', 'validate']"
        key = f'{execute_for}_method'
        if str(self.blueprint_data[key]) == 'nan':
            return None
        func = getattr(self, self.blueprint_data[key])
        func()


class TestExecution(Execution):
    """
    Sub-class of `Execution()` for executing testing steps
    """

    def __init__(self, driver, data_interface):
        super().__init__(driver, data_interface)

    ### Preparation Functions ###
    def _locators(self):
        """Fix name for selenium and provide a path for that locator
        Outputs:
        ------
        `(locator, path)` --
        """
        path = self.blueprint_data['run_path']
        locator = self.blueprint_data['run_locator'].lower()
        if locator in ['class', 'tag']:
            return f'{locator} name', path
        elif locator == 'css':
            return 'css selector', path
        else:
            return locator, path

    def _single_element(self):
        """Use to locate single web element"""
        locator, path = self._locators()
        try:
            self.element_exist = self.driver.find_element(locator, path)
            self._data_interface.cache_add(element_exist=self.element_exist)
        except NoSuchElementException:
            self._data_interface.cache_add(element_exist=0)
            print('no such element')
        print(self._data_interface.get_cache)

    def _group_elements(self):
        """Use to locate more web elements"""
        locator, path = self._locators()

    def goto_url(self):
        "webdriver goto a destinated url"
        url = self.blueprint_data['run_value']
        assert url[0:4] == 'http'
        self.driver.get(url)
        print(f"{self.tc} travelling to: '{url}'")

    def checkout(self):
        """Check out whether a web-element should exist or not"""
        locator, path = self._locators()
        checkout_list = self.driver.find_elements(locator, path)
        print(f"---> checkout: {path}")
        if len(checkout_list) != 0:
            self.element_exist = checkout_list
            self._data_interface.cache_add(element_exist=checkout_list)
        else:
            self._data_interface.cache_add(element_exist=None)

    def click_button(self):
        self._single_element()
        print("Testing---> success")


class ValidateExecution(Execution):
    """
    Sub-class of `Execution()` for validating testing outputs
    """

    def __init__(self, driver, data_interface):
        super().__init__(driver, data_interface)
        self.cache = data_interface.get_cache
        self.blueprint_data = data_interface.get_blueprint_data
        self.terminate = True

    @property
    def validate_value(self):
        return self.blueprint_data['validate_value']

    def checkout_exist(self):
        """validate whether a `checkout` element should be exist or not"""
        element_exist = self.cache['element_exist']
        validate_key = self.blueprint_data['validate_key']
        validate_value = self.blueprint_data['validate_value']
        tp = (validate_value == 'Yes') & (
            element_exist is not None)  # true positive
        tn = (validate_value == 'No') & (
            element_exist is not None)  # true negative

        ### validation ###
        if tp | tn:
            self.terminate = False
        else:
            pass

        self._data_interface.log_input(
            test_case=self.tc,
            expect=f"{validate_key} exists={validate_value}",
            result=f"{validate_key} exists ?? TODO MSG"
        )

    # # testing
    # test_exe = TestExecution(test_data['driver'], test_data['data_interface'])
    # test_exe.checkout()
