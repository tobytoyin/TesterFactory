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
    `cache` (Process object, iterator): A set of data for selenium to work on.

    Error Handling:
    ------
    Errors will be treated as exception and reported in testing log
    """

    def __init__(self, driver, cache):

        # WebDriver Setup
        self.driver = driver
        self.driver.implicitly_wait(10)
        self.driver_wait = WebDriverWait(self.driver, 10)

        # Caches
        self._cache = cache
        self.bp_cache = self._cache.get_bp_cache

        # Values that commonly used
        self.tc = self.bp_cache['run_tc']  # test case id
        self.element_exist = None  # determine whether a web-element exist or not
        # self.logics = inline_arg_compile(self.bp_cache['run_logic'])

    ##### FUNCTIONS THAT VARY BY CHILD_CLASS #####
    def _logic_setup(self, default=''):
        """Setup for the inline-logic: setup default value if not logic"""
        assert default != '', "args--default requires a value"

        # from child TestExecution
        if self.__class__ is TestExecution:
            logic_list = self.run_logic_list
        # from child ValidateExecution
        elif self.__class__ is ValidateExecution:
            logic_list = self.validate_logic_list

        # if the logic list is empty, add the default value in list.
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

    ##### EXECUTION FUNCTION #####
    def execute_func(self, execute_for='run'):
        """Trigger function through string in the blueprint"""
        assert execute_for in {'run', 'validate'}, "Usage: execute_for in {'run', 'validate'}"
        # retrieve whether current cache is passing testing step or validating step function
        key = f'{execute_for}_method'
        if str(self.bp_cache[key]) == 'nan':
            return None  # break, no func to execute
        func = getattr(self, self.bp_cache[key])
        func()

        ### add element into cache ###
        if self.element_exist is None:
            self._cache.cache_add(element_exist=0)
        else:
            self._cache.cache_add(element_exist=self.element_exist)

        ### add identification to log_cache when Validation###
        # tc -- id for test case data
        # map_index -- id for execution logic row
        if execute_for == 'validate':
            self._cache.log_input(tc=self.tc, map_index=self.bp_cache['run_index'])


class TestExecution(Execution):
    """
    Sub-class of `Execution()` for executing testing steps
    """

    def __init__(self, driver, cache):
        super().__init__(driver, cache)
        # the logic to be triggered
        self.run_logic_list = list(self.run_args.keys())

    @property
    def run_args(self):
        """Retrieve inline args and input for running"""
        return self.bp_cache['run_logic_fetch']

    ### Preparation Functions ###

    def _locators(self):
        """Fix name for selenium and provide a path for that locator
        Outputs:
        ------
        `(locator, path)` --
        """
        path = self.bp_cache['run_path']
        locator = self.bp_cache['run_locator'].lower()
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
            print('> LOCATOR: NO SUCH ELEMENT.')

    def _group_elements(self):
        """Use to locate GROUPED web elements by INDEX"""
        locator, path, driver = self._locators()
        value = self.bp_cache['run_value'].lower()
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
                self._cache.log_input(error_msg='web element out of reach')
        except NoSuchElementException:
            self._cache.log_input(error_msg='web element does not exist')

    def _text_elements(self):
        """Locate GROUPED web elements by STRING"""
        locator, path, driver = self._locators()
        value = self.bp_cache['run_value']

        # locate buttons
        buttons = driver.find_elements(locator, path)

        # element not found
        if len(buttons) == 0:
            self._cache.log_input(error_msg='web element does not exist')

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
            self._cache.log_input(error_msg=f'No BUTTONS cointain {value}')
        else:
            self.element_exist = buttons[index]

    ### Logic behind performing actions. Generalized different cases with similar behaviours ###
    def _button_clicker(self):
        """Handle clicking button, e.g. real/ shadow button"""
        element = self.element_exist
        driver = self.driver

        try:
            assert element is not None
            element.click()  # ordinary clicking
        # handle shadow button
        except ElementClickInterceptedException:
            js_command = 'arguments[0].click();'
            driver.execute_script(js_command, element)
        except ElementNotInteractableException:
            element.submit()
        except AssertionError:
            print("> LOCATOR: Button does not exist")

    def _input_writer(self):
        """Inject run_value into input fields"""
        # initiate
        input_value = self.bp_cache['run_value']
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
        how = self._logic_setup(default='accept')
        alert_box = self.driver.switch_to.alert_box

        # default is accept
        if 'accept' in how:
            alert_box.accept()
        elif 'reject' in how:
            alert_box.reject()
        time.sleep(1)  # ?
        return None

    def checkout(self):
        """
        Check out whether a web-element should exist or not
        args:
        ------
        `--jumpto(value={Yes, No, Key}, i={0,1,..., n-th})` -- i-th determines which the exact ptr should be. \n
        `--skipby(value={Yes, No, Key}, d={1,2,...})` -- d-th determines the relative position ptr should skip. \n
        If value = Yes, and checkout element exist, jumpto i-th row of the blueprint \n
        If value = No, and checkout element NOT exist, jumpto i-th row of the blueprint \n
        If value = Key, it will lookup the {Yes, No} in run_value and apply the above conditions.
        """
        ### initiate ###
        locator, path, driver = self._locators()
        how = self._logic_setup(default='checkout')
        checkout_list = driver.find_elements(locator, path)  # This should be a []
        checkout_num = len(checkout_list)

        ### conduct Checkout ###
        if checkout_num != 0:
            self.element_exist = checkout_list

        ### run inline ###
        if any(k in ['jumpto', 'skipby'] for k in how):
            key = 'jumpto' if 'jumpto' in how else 'skipby'
            attr = self._logic_attr(key, 'all')
            gate = self.bp_cache['run_value'] if attr['condition'] == 'Key' else attr['condition']

            # possible cases that run this logic
            yes_exist = gate == 'Yes' and checkout_num != 0
            no_not_exist = gate == 'No' and checkout_num == 0
            print(f"> gate={gate}, len={checkout_num}")

            if yes_exist or no_not_exist:  # value = Yes & Exist ==> jump
                self._cache.cache_add(**{key: attr['input']})

    def click_button(self):
        """method = click_button"""
        self._single_element()
        try:
            self._button_clicker()
            self._cache.check_proceed()
        except NoSuchElementException:
            pass
        # if self.element_exist:
        #     self._button_clicker()
        #     self._cache.check_proceed()

    def click_checkbox(self):
        """Click a CHECKBOX"""
        self._group_elements()
        try:
            self._button_clicker()
            time.sleep(0.5)
        # if self.element_exist:
        #     self._button_clicker()
        #     time.sleep(0.5)
        except NoSuchElementException:
            pass

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

    def counter(self):
        """Counter on the looping"""
        # trigger this counter
        counter_name = f'counter_{self.bp_cache["run_index"]}'
        prev = self._cache._prev
        # check if this counter_name already exist in cache
        new_counter = counter_name not in self._cache._prev
        how = self._logic_setup(default='default')

        # initialize counter value
        if 'set' in how:
            attr = self._logic_attr(logic_name='set', attr='all')
            goto = attr['condition']
            count = int(attr['input'])
        elif 'default' in how:
            goto = 0
            count = 1

        # action for new_counter
        if new_counter:
            count -= 1
            self._cache.cache_add(**{counter_name: count}, jumpto=goto)
        # action for existing counter
        else:
            # a completed counter -> skip
            if int(prev[counter_name] == 0):
                pass
            # reduce count value
            else:
                count = int(prev[counter_name]) - 1
                self._cache.cache_add(**{counter_name: count}, jumpto=goto)

    def date_picker(self):
        """Pick update from DATEPICKER using date format"""
        self._single_element()
        element = self.element_exist

        if self.element_exist():
            locator, path, driver = self._locators()
            value = self.bp_cache['run_value']
            js_template = 'document.{method}("{path}").value = "{value}";'.format(path=path, value=value)

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
            file_name = self.bp_cache['run_value']
        img_where = '/'
        time.sleep(0.5)
        img_name = f'{img_where}{self.tc}_{file_name}.png'
        self._cache.log_input(tc=self.tc, output=f'IMAGE:{img_name}')

    def write_input(self):
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
        args = self.bp_cache['run_key']
        naming = ''
        have_name = self._logic_setup(default='nameless')
        text = ''

        ### define variable naming ###
        if 'name' in have_name:
            # retreive and set variable naming
            naming = self._logic_attr(logic_name='name', attr='condition')
        varname = f"{'<' + naming + '>' if naming != '' else ''}"

        if self.element_exist:
            # define expression components
            comp = args.split('%')
            comp.remove('')

            ### Input validation ###
            if len(comp) > 3:
                # Incorrect syntax (too many components)
                self._cache.log_input(
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

        output = f"TEXT{varname}:{text}"
        self._cache.log_input(tc=self.tc, output=output)
        self._cache.cache_add(text=output)  # add to cache for validation if needed

    def goto(self):
        "webdriver goto a specific object"
        ### initiate ###
        goto = self._logic_setup(default='url')
        locator, path, driver = self._locators()

        ### GOTO URL ###
        if 'url' in goto:
            url = self.bp_cache['run_value']
            assert url[0:4] == 'http', "'url' should start with 'http' or 'https'"
            driver.get(url)
            print(f"> {self.tc} travelling to: '{url}'")

        ### GOTO iFRAME ###
        elif 'iframe' in goto:
            assert path != '', "'--iframe' requires a 'path'"

            time.sleep(1)
            self.driver_wait.until(EC.frame_to_be_available_and_switch_to_it)
            driver.switch_to.default_content()
            driver.switch_to.frame(path)

        ### GOTO BACK ###
        elif 'back' in goto:
            print("> Returning to last page...")
            driver.back()

        ### Unknown args ###
        else:
            self._cache.log_input(error_msg=f"UNKNOWN ARGS: {goto}")

    def unload_file(self):
        """upload a file to UPLOAD"""
        from os import getcwd
        self._single_element()
        file_location = getcwd() + '\\resources\\input\\' + \
            self.bp_cache['run_value']
        element = self.element_exist
        element.send_keys(file_location)

    def driver_wait(self):
        """Force webdriver to wait for n-seconds"""
        ### initiate ###
        val = self._logic_setup(default='default')

        if 'default' in val:
            sec = 5
        elif 'for' in val:
            sec = int(self._logic_attr(logic_name='for', attr='condition'))
        time.sleep(sec)


class ValidateExecution(Execution):
    """
    Child-class of `Execution()` for validating testing outputs
    """

    def __init__(self, driver, cache):
        super().__init__(driver, cache)
        self.cache = cache.get_cache
        self.bp_cache = cache.get_bp_cache
        # the validate logic to be triggered
        self.validate_logic_list = list(self.validate_args.keys())
        self.terminate = True
        self.result = 'Fail'

    @property
    def validate_value(self):
        """Retrieve the value to validate for"""
        return self.bp_cache['validate_value']

    @property
    def validate_args(self):
        """Retrieve inline args and inputs for validation"""
        return self.bp_cache['validate_logic_fetch']

    def is_good(self):
        """The case is good and pass the testing"""
        self.terminate = False
        self.result = 'Pass'
        return None

    def _text_compare(self):
        """
        Compare text match with the one scrapped
        """
        ### initiate ###
        compare_with = self.validate_value
        cached = self._cache.get_cache['text']
        how = self._logic_setup(default='strict')

        ### Load info from cache-text ###
        load_regex = r'TEXT(?:\<(\w*)\>)?:(.*)'
        naming, scrapped_text = re.search(load_regex, cached).groups()
        # join '|' as whitespace
        scrapped_text = " ".join(scrapped_text.split('|'))

        ### TEXT Comparison ###
        # text = 'nan' skip checking
        if compare_with == 'nan':
            match = None
        # --loose compare
        elif 'loose' in how:
            match = re.search(rf"({compare_with})", scrapped_text)
        # strict compare
        else:
            match = re.search(rf"^\s?({compare_with})\s?$", scrapped_text)

        return match, naming, scrapped_text, compare_with

    ### Set of functions for validation ###
    def checkout_validate(self):
        """
        validate whether a `checkout` element should be exist or not \n

        args:
        -----
        `--exist` -- (default) The elements should exist\\ not \n
        `--enable` -- The elements should exist & enabled\\ disabled \n

        Sheet-value:
        -----
        (for `--exist`):\n
        Yes -- The elements should exist \n
        No  -- The elements should not exist \n

        (for `--enable`):\n
        Yes -- The elements should exist & enabled \n
        No  -- The elements should not exist & disabled\n

        Output:
        ------
        Pass -- Element exist & check-for Yes; or Element not exist & check-for No \n
        Fail -- Element exist & check-for No; or Element not exist & check-for Yes \n
        """
        ### initiate ###
        assert self.cache != {}, "Cannot conduct validation without checking a specific elements."
        element_exist = self.cache['element_exist']
        how = self._logic_setup(default='exist')
        validate_key = self.bp_cache['validate_key']
        validate_value = self.bp_cache['validate_value']
        placeholder = 'EXIST'
        tp = tn = None

        # default lookup
        if 'exist' in how:
            tp = (validate_value == 'Yes') & (element_exist != 0)  # true positive
            tn = (validate_value == 'No') & (element_exist == 0)  # true negative
        # lookup if the element is enable
        elif 'enable' in how:
            placeholder = 'ENABLE'
            # element should exist
            if element_exist != 0:
                # find whether all elements have is_enabled
                enable_li = [el.is_enabled() for el in element_exist]
                # find the set and test if the set contain False
                have_disabled = False in set(enable_li)
                # result
                tp = (validate_value == 'Yes') & (have_disabled is False)
                tn = (validate_value == 'No') & (have_disabled is True)

        ### Debugging value ###
        # print(f"Element exist: {element_exist}")
        # print(f"Validate value: {validate_value}")

        ### validation ###
        if tp or tn:
            self.is_good()
        else:
            pass

        self._cache.log_input(
            validate_method=f"checkout-validation BY:{how}",
            expect=f"{validate_key} {placeholder}={validate_value}",
            actual=f"{validate_key} {placeholder}={tp if validate_value == 'Yes' else tn}",
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
        if 'contain' in how:
            tp = re.search(redirect_to, current_url)
        elif 'strict' in how:
            tp = redirect_to == current_url

        if tp:
            self.is_good()
        else:
            pass

        ### Log result ###
        self._cache.log_input(
            expect=f"Redirect ({how}) to '{redirect_to}'",
            actual=f"Redirect ({how}) to '{current_url}'",
            result=self.result)

    def text_validate(self):
        """
        Verify whether a text exist/ not exist
        args:
        -----
        `--without` -- Text should NOT match \n
        `--loose` -- Match by occurrence instead of exact match.
        """
        match, naming, scrapped_text, compare_with = self._text_compare()
        how = self._logic_setup(default='with')
        placeholder = ''
        actual_placeholder = ''

        ### verification ###
        tp = not bool(match) if 'without' in how else bool(match)

        # Pass - Text not exist and expect not to exist
        if tp and 'without' in how:
            self.is_good()
            placeholder = actual_placeholder = 'NOT'
        elif tp and 'with' in how:
            self.is_good()
        elif (not tp) and ('without' in how):
            placeholder = 'NOT'
        elif (not tp) and ('with' in how):
            actual_placeholder = 'NOT'

        self._cache.log_input(
            validate_method=f'text-validation BY:{how}',
            expect=f'"{compare_with}" IS {placeholder} IN SCRAPPED TEXT',
            actual=f'"{compare_with}" IS {actual_placeholder} IN "{scrapped_text}"',
            result=self.result
        )
