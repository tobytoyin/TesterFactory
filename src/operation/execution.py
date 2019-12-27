from src.processing.Process import test_data
from src.helper import inline_arg_compile
from src.util_driver import full_screenshot
import time
import re
# driver = webdriver.Chrome()
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup


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
        self.driver_wait = WebDriverWait(self.driver, 10)
        self._data_interface = data_interface
        self.blueprint_cache = self._data_interface.get_blueprint_cache
        self.tc = self.blueprint_cache['run_tc']
        self.element_exist = None  # determine whether a web-element exist or not
        self.logics = inline_arg_compile(self.blueprint_cache['run_logic'])

    def _logic_setup(self, default=''):
        """Setup for the inline-logic: setup default value if not logic"""
        assert default != '', "args--default requires a value"

        # from child TestExecution
        if self.__class__ is TestExecution:
            logic_list = self.run_logic_list
        # from child ValidateExecution
        elif self.__class__ is ValidateExecution:
            logic_list = self.validate_logic_list

        if not logic_list:
            return default
        else:
            # by args value
            return logic_list[0]

    def _logic_attr(self, logic_name='', attr='all'):
        """
        Retreive the attributes of a specific logic \n
        logic_name -- the logic name of which one wants to retreive \n
        attr -- 'all': retreive the dictionary of values;
                'key': retreive a particular value
        """
        assert logic_name != '', "'logic_name' must not be empty for retrieval"

        # from child TestExecution
        if self.__class__ is TestExecution:
            if attr == 'all':
                return self.run_args[logic_name]
            else:
                return self.run_args[logic_name][attr]
        # from child ValidateExecution
        elif self.__class__ is ValidateExecution:
            if attr == 'all':
                return self.validate_args[logic_name]
            else:
                return self.validate_args[logic_name][attr]

    def execute_func(self, execute_for='run'):
        """Execute function through string fetching"""
        assert execute_for in ['run', 'validate'], \
            "Usage: execute_for in ['run', 'validate']"
        key = f'{execute_for}_method'
        if str(self.blueprint_cache[key]) == 'nan':
            return None
        func = getattr(self, self.blueprint_cache[key])
        func()

        ### add element into cache ###
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
        # the logic to be triggered
        self.run_logic_list = list(self.run_args.keys())

    @property
    def run_args(self):
        """Retrieve inline args and input for running"""
        return self.blueprint_cache['run_logic_fetch']

    ### Preparation Functions ###

    def _locators(self):
        """Fix name for selenium and provide a path for that locator
        Outputs:
        ------
        `(locator, path)` --
        """
        path = self.blueprint_cache['run_path']
        locator = self.blueprint_cache['run_locator'].lower()
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

    def _group_elements(self):
        """Use to locate GROUPED web elements by INDEX"""
        locator, path, driver = self._locators()
        value = self.blueprint_cache['run_value'].lower()
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
                    tc=self.tc, error_msg='web element out of reach')
        except NoSuchElementException:
            self._data_interface.log_input(
                tc=self.tc, error_msg='web element does not exist')

    def _text_elements(self):
        """Locate GROUPED web elements by STRING"""
        locator, path, driver = self._locators()
        value = self.blueprint_cache['run_value']

        # locate buttons
        buttons = driver.find_elements(locator, path)

        # element not found
        if len(buttons) == 0:
            self._data_interface.log_input(
                tc=self.tc, error_msg='web element does not exist')

        # check button text
        # stop loading when text is found
        match = False
        for index, button in enumerate(buttons):

            ### debugging ###
            print(f"Button{index} Name: {button.text}")

            if button.text == value:

                ### debugging ###
                print(f"====>{button.text} == {value}")

                match = True
                break

        # text not found
        if not match:
            self._data_interface.log_input(
                tc=self.tc, error_msg=f'No BUTTONS cointain {value}')
        else:
            self.element_exist = buttons[index]

    ### Logic behind performing actions. Generalized different cases with similar behaviours ###
    # def _button_dec(self, func):
    #     """Handle clicking button, e.g. real/ shadow button"""
    #     def wrapper():
    #         self._single_element()
    #         if self.element_exist:
    #             func()
    #             self._data_interface.check_proceed()

    #     return wrapper

    def _button_clicker(self):
        """Handle clicking button, e.g. real/ shadow button"""
        element = self.element_exist
        driver = self.driver

        try:
            assert element is not None
            element.click()  # ordinary clicking
        # handle shadow button
        except ElementClickInterceptedException:
            js_command = 'arguements[0].click();'
            driver.execute_script(js_command, element)
        except ElementNotInteractableException:
            element.submit()
        except AssertionError:
            print("----> test: Button does not exist")

    def _input_writer(self):
        """Inject run_value into input fields"""
        # initiate
        input_value = self.blueprint_cache['run_value']
        element = self.element_exist
        driver = self.driver

        # don't type anything if value is 'nan'
        if input_value == 'nan':
            input_value = ''

        # inject value by trying different methods
        try:
            element.send_keys(input_value)
        # input fields is likely to be a span fields rather than input box
        except ElementNotInteractableException:
            js_command = f'arguments[0].innerText = {input_value};'
            driver.execute_script(js_command, element)

    ### Actions Block ###
    def click_alert(self):
        """
        Click something on the ALERT BOX (default=accept)
        inline-log:
        ------
        `--accept` -- accept ALERT BOX
        `--reject` -- reject ALERT BOX
        """
        self.driver_wait.until(EC.alert_is_present())
        logic_fetch = self.blueprint_cache['run_logic_fetch']

        alert_box = self.driver.switch_to.alert_box

        # default is accept
        if not logic_fetch:
            alert_box.accept()
            time.sleep(1)  # ?
            return None

        # by inline values
        if 'accept' in logic_fetch.keys():
            alert_box.accept()
        elif 'reject' in logic_fetch.keys():
            alert_box.reject()
        time.sleep(1)  # ?
        return None

    def checkout(self):
        """Check out whether a web-element should exist or not"""
        locator, path, driver = self._locators()
        checkout_list = driver.find_elements(locator, path)
        print(f"---> checkout: {path}")
        if len(checkout_list) != 0:
            self.element_exist = checkout_list

    def click_button(self):
        """method = click_button"""
        self._single_element()
        if self.element_exist:
            self._button_clicker()
            self._data_interface.check_proceed()

    def click_checkbox(self):
        """Click a CHECKBOX"""
        self._group_elements()
        if self.element_exist:
            self._button_clicker()
            time.sleep(0.5)

    def click_radio(self):
        """Click a RADIO button"""
        self._group_elements()
        element = self.element_exist

        if element:
            self._button_clicker()

    def click_named_button(self):
        """Click a BUTTON WITH NAME"""
        self._text_elements()
        if self.element_exist:
            self._button_clicker()

    def date_picker(self):
        """Pick update from DATEPICKER using date format"""
        self._single_element()
        element = self.element_exist

        if self.element_exist():
            locator, path, driver = self._locators()
            value = self.blueprint_cache['run_value']
            js_template = 'document.{method}("{path}").value = "{value}";'.format(
                path=path, value=value)

            # js get id
            if locator == 'id':
                js_command = js_template.format(method='getElementById')
            # css query
            elif locator == 'css':
                js_command = js_template.format(method='querySelector')
            # execute command
            driver.execute_script(js_command, element)

    def screencap(self, file_name):
        """Take a full screenshot"""
        if file_name == '':
            file_name = self.blueprint_cache['run_value']
        img_where = '/'
        time.sleep(0.5)
        img_name = f'{img_where}{self.tc}_{file_name}.png'
        self._data_interface.log_input(
            tc=self.tc, output=f'IMAGE:{img_name}')

    def input(self):
        """Input value into INPUT FIELDS"""
        self._single_element()
        if self.element_exist:
            self._input_writer()

    # def goto_frame(self):
    #     """Goto a iFRAME"""
    #     locator, path, driver = self._locator()

    #     time.sleep(1)
    #     self.wait.until(EC.frame_to_be_available_and_switch_to_it)
    #     driver.switch_to.default_content()
    #     driver.switch_to.frame(path)

    def scrap(self):
        """
        Scrap some info from a particular tag
        """
        ### initiate ###
        self._single_element()
        args = self.blueprint_cache['run_key']
        naming = ''
        have_name = self._logic_setup(default='nameless')
        text = ''

        ### define variable naming ###
        if have_name == 'name':
            # retreive and set variable naming
            naming = self._logic_attr(logic_name=have_name, attr='condition')
        msg = f"{'<' + naming + '>' if naming != '' else ''}"

        if self.element_exist:
            # define expression components
            comp = args.split('%')
            comp.remove('')

            ### Input validation ###
            if len(comp) > 3:
                # Incorrect syntax (too many components)
                self._data_interface.log_input(
                    tc=self.tc,
                    error_msg=f"UNKNOWN EXPRESSION: %inner_tag OR %inner_tag%attr%attr_val OR empty")
                print(f"> ERROR: {args} is an unknown syntax")
                return None 

            ### Scrapping start ###
            soup_tag = comp[0]
            inner_html = self.element_exist.get_attribute('innerHTML')
            soup = BeautifulSoup(inner_html, features='html.parser')
            if len(comp) == 3:
                # Syntax looks like (%tag%attr%attr_val): Narrowly extracting specific text
                # Syntax for BS4, e.g. span, {'class': 'some-class-val'}
                # Use when a single innerHTML has multiple elements inside, e.g. div ~ {#span1, #span2, ...}
                soup_dict = {comp[1]: comp[2]}
                text_list = [tag.get_text() for tag in soup.find_all(soup_tag, soup_dict)]

            elif len(comp) == 1:
                # Syntax looks like (%tag): Broadly extracting all text
                # Use to find text inside to whole innerHTML
                text_list = [tag.get_text() for tag in soup.find_all(soup_tag)]
            elif len(comp) == 0:
                # No inputs, Use to find text inside the whole HTML
                text_list = [self.element_exist.text]

            # Result formatting
            text = '|'.join(text_list)
        else:
            # web-element does not exist
            print("> Element does not exist...")
            pass
            
        self._data_interface.log_input(
            tc=self.tc, output=f"TEXT{msg}:{text}")


            

        


    def goto(self):
        "webdriver goto a specific object"
        ### initiate ###
        goto = self._logic_setup(default='url')
        locator, path, driver = self._locators()

        ### GOTO URL ###
        if goto == 'url':
            url = self.blueprint_cache['run_value']
            assert url[0:4] == 'http', "'url' should start with 'http' or 'https'"
            driver.get(url)
            print(f"> {self.tc} travelling to: '{url}'")

        ### GOTO iFRAME ###
        elif goto == 'iframe':
            assert path != '', "'--iframe' requires a 'path'"

            time.sleep(1)
            self.driver_wait.until(EC.frame_to_be_available_and_switch_to_it)
            driver.switch_to.default_content()
            driver.switch_to.frame(path)

        ### GOTO BACK ###
        elif goto == 'back':
            print("> Returning to last page...")
            driver.back()

        ### Unknown args ###
        else:
            self._data_interface.log_input(
                tc=self.tc, error_msg=f"UNKNOWN ARGS: {goto}")

    def unload_file(self):
        """upload a file to UPLOAD"""
        from os import getcwd
        self._single_element()
        file_location = getcwd() + '\\resources\\input\\' + \
            self.blueprint_cache['run_value']
        element = self.element_exist
        element.send_keys(file_location)

    def wait(self):
        """Force webdriver to wait for n-seconds"""
        ### initiate ###
        val = self._logic_setup(default='default')

        if val == 'default':
            sec = 5
        elif val == 'for':
            sec = int(self._logic_value(logic_name='for')['condition'])
        time.sleep(sec)


class ValidateExecution(Execution):
    """
    Child-class of `Execution()` for validating testing outputs
    """

    def __init__(self, driver, data_interface):
        super().__init__(driver, data_interface)
        self.cache = data_interface.get_cache
        self.blueprint_cache = data_interface.get_blueprint_cache
        # the validate logic to be triggered
        self.validate_logic_list = list(self.validate_args.keys())
        self.terminate = True
        self.result = 'Fail'

    @property
    def validate_value(self):
        """Retrieve the value to validate for"""
        return self.blueprint_cache['validate_value']

    @property
    def validate_args(self):
        """Retrieve inline args and inputs for validation"""
        return self.blueprint_cache['validate_logic_fetch']

    def is_good(self):
        """The case is good and pass the testing"""
        self.terminate = False
        self.result = 'Pass'
        return None

    ### Set of functions for validation ###
    def checkout_validate(self):
        """
        validate whether a `checkout` element should be exist or not \n

        Sheet-value:
        -----
        Yes -- The element should exist \n
        No  -- The element should not exist \n

        Output:
        ------
        Pass -- Element exist & check-for Yes; or Element not exist & check-for No \n
        Fail -- Element exist & check-for No; or Element not exist & check-for Yes \n
        """

        element_exist = self.cache['element_exist']
        validate_key = self.blueprint_cache['validate_key']
        validate_value = self.blueprint_cache['validate_value']
        tp = (validate_value == 'Yes') & (element_exist != 0)  # true positive
        tn = (validate_value == 'No') & (element_exist == 0)  # true negative

        ### Debugging value ###
        print(f"Element exist: {element_exist}")
        print(f"Validate value: {validate_value}")

        ### validation ###
        if tp | tn:
            self.is_good()
        else:
            pass

        self._data_interface.log_input(
            tc=self.tc,
            expect=f"{validate_key} exists={validate_value}",
            actual=f"{validate_key} exists ?? TODO MSG",
            result=self.result)

    def redirect_validate(self):
        """
        Validate whether the browser redirect to an expected url \n
        Check for exact URL match by default \n

        Sheet-value:
        -----
        (string) -- The url to validate for \n

        inline-logic:
        -----
        `--contain` -- Validate for URL containing the (string) rather than exact match \n

        Output:
        ------
        Pass -- Element redirect to destinated URL/ destinated URL with (string) \n
        Fail -- Element not redirect to destinated URL/ destinated URL not having (string) \n
        """
        ### initiate ###
        current_url = self.driver.current_url
        redirect_to = self.validate_value
        tp = None  # pass case

        # validate not needed
        if redirect_to == 'nan':
            self.is_good()
            print("> test not needed")
            return None

        how = self._logic_setup(default='strict')
        if how == 'contain':
            tp = re.search(redirect_to, current_url)
        elif how == 'strict':
            tp = redirect_to == current_url

        if tp:
            self.is_good()
        else:
            pass

        ### Log result ###
        self._data_interface.log_input(
            tc=self.tc,
            expect=f"Redirect ({how}) to '{redirect_to}'",
            actual=f"Redirect ({how}) to '{current_url}'",
            result=self.result)

    # def checkout_disable(self):
    #     """val

    # # # testing
    # # test_exe = TestExecution(test_data['driver'], test_data['data_interface'])
    # # test_exe.checkout()
