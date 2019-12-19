from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from selenium import webdriver
from src.processing.Process import test_data
from src.helper import inline_arg_compile
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
        self.logics = inline_arg_compile(self.blueprint_data['run_logic'])

    @property
    def _logics(self, inline_logic):
        output = []
        logics = inline_arg_compile(inline_logic)
        for logic in logics:
            output.append(logic[''])
        # TODO last activity

    def execute_func(self, execute_for='run'):
        """Execute function through string fetching"""
        assert execute_for in ['run', 'validate'], \
            "Usage: execute_for in ['run', 'validate']"
        key = f'{execute_for}_method'
        if str(self.blueprint_data[key]) == 'nan':
            return None
        func = getattr(self, self.blueprint_data[key])
        func()
        # add element into cache
        if self.element_exist is None:
            self._data_interface.cache_add(element_exist=0)
        else:
            self._data_interface.cache_add(element_exist=self.element_exist)


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
            return f'{locator} name', path, self.driver
        elif locator == 'css':
            return 'css selector', path, self.driver
        else:
            return locator, path, self.driver

    def _single_element(self):
        """Use to locate single web element"""
        locator, path, driver = self._locators()
        try:
            self.element_exist = self.driver.find_element(locator, path)
        except NoSuchElementException:
            print('no such element')
        print(self._data_interface.get_cache)

    def _group_elements(self):
        """Use to locate GROUPED web elements by INDEX"""
        locator, path, driver = self._locators()
        value = self.blueprint_data['run_value'].lower()
        choice = 0  # if entry don't have choice, assume to select first element

        if value == 'false':
            choice = int(1)
        elif value not in ['nan', 'true']:
            choice = int(value)  # specific element index

        try:
            self.element_exist = driver.find_elements(locator, path)[choice]
        except IndexError:
            # checkbox is to not click
            if choice != 1:
                self._data_interface.log_input(
                    test_case=self.tc, error_msg='web element out of reach')
        except NoSuchElementException:
            self._data_interface.log_input(
                test_case=self.tc, error_msg='web element does not exist')

    def _text_elements(self):
        """Locate GROUPED web elements by STRING"""
        locator, path, driver = self._locators()
        value = self.blueprint_data['run_value']

        # locate buttons
        buttons = driver.find_elements(locator, path)

        # element not found
        if len(buttons) == 0:
            self._data_interface.log_input(
                test_case=self.tc, error_msg='web element does not exist')

        # check button text
        # stop loading when text is found
        match = False
        for index, button in enumerate(buttons):
            if button.text == value:
                match = True
                break

        # text not found
        if not match:
            self._data_interface.log_input(
                test_case=self.tc, error_msg=f'No BUTTONS cointain {value}')
        else:
            self.element_exist = buttons[index]

    def _button_clicker(self):
        """Handle clicking button, e.g. real/ shadow button"""
        element = self.element_exist

        try:
            assert element is not None
            element.click()  # ordinary clicking
        # handle shadow button
        except ElementClickInterceptedException:
            js_command = 'arguements[0].click();'
            self.driver.execute_script(js_command, element)
        except ElementNotInteractableException:
            element.submit()
        except AssertionError:
            print("----> test: Button does not exist")

    ### Actions Block ###
    def click_button(self):
        """method = click_button"""
        self._single_element()
        if self.element_exist:
            self._button_clicker()
            self._data_interface.check_proceed()

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
