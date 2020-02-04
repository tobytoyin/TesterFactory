from src.operation.execution import Execution
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys


class TestExecution(Execution):
    """
    Sub-class of `Execution()` for executing testing steps
    """

    def __init__(self, driver, cache):
        super().__init__(driver, cache)

    @property
    def logic_args(self):
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

        if value in ['false', 'no']:
            choice = int(1)
        elif value not in ['nan', 'true', 'yes']:
            choice = int(value)  # specific element index

        try:
            self.element_exist = driver.find_elements(locator, path)[choice]
        except IndexError:
            # checkbox is to not click
            if choice != 1:
                self.cache.log_input(error_msg='web element out of reach')
        except NoSuchElementException:
            self.cache.log_input(error_msg='web element does not exist')

    def _text_elements(self):
        """Locate GROUPED web elements by STRING"""
        locator, path, driver = self._locators()
        value = self.bp_cache['run_value']

        # locate buttons
        buttons = driver.find_elements(locator, path)

        # element not found
        if len(buttons) == 0:
            self.cache.log_input(error_msg='web element does not exist')

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
            self.cache.log_input(error_msg=f'No BUTTONS cointain {value}')
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
        except (ElementClickInterceptedException, ElementNotInteractableException):
            js_command = 'arguments[0].click();'
            driver.execute_script(js_command, element)
        # except ElementNotInteractableException:
        #     element.submit()
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
        sleep(1)  # ?
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
        print("checkout start")
        locator, path, driver = self._locators()
        how = self._logic_setup(default='checkout')
        checkout_list = driver.find_elements(locator, path)  # This should be a []
        checkout_num = len(checkout_list)

        ### conduct Checkout ###
        if checkout_num != 0:
            self.element_exist = checkout_list

        ### run inline ###
        if 'checkout' not in how:
            key = how[0]
            attr = self._logic_attr(key, 'all')
            gate = (
                self.bp_cache['run_value']
                if attr['condition'] == 'Key'
                else attr['condition']
            )

            # possible cases that run this logic
            yes_exist = gate == 'Yes' and checkout_num != 0
            no_not_exist = gate == 'No' and checkout_num == 0
            print(f"> gate={gate}, len={checkout_num}")

            if yes_exist or no_not_exist:  # value = Yes & Exist ==> jump
                self.cache.cache_add(**{key: attr['input']})
        print("checkout done")

    def click_button(self):
        """
        method = click_button
        logic: {
            '--click': Ordinary click, 
            '--submit': Form submission click
        }
        """
        self._single_element()
        how = self._logic_setup(default="click")

        try:
            if 'click' in how:
                self._button_clicker()
            elif 'submit' in how: 
                self._button_clicker()
                sleep(5)
            self.cache.check_proceed()
        except NoSuchElementException:
            pass

    def click_checkbox(self):
        """Click a CHECKBOX"""
        print("> click checkbox")
        self._group_elements()
        try:
            self._button_clicker()
            sleep(0.5)
        # if self.element_exist:
        #     self._button_clicker()
        #     time.sleep(0.5)
        except NoSuchElementException:
            pass
        print("> click None")
        
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
        prev = self.cache._prev
        # check if this counter_name already exist in cache
        new_counter = counter_name not in self.cache._prev
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
            self.cache.cache_add(**{counter_name: count}, jumpto=goto)
        # action for existing counter
        else:
            # a completed counter -> skip
            if int(prev[counter_name] == 0):
                pass
            # reduce count value
            else:
                count = int(prev[counter_name]) - 1
                self.cache.cache_add(**{counter_name: count}, jumpto=goto)

    def date_picker(self):
        """Pick update from DATEPICKER using date format"""
        self._single_element()
        element = self.element_exist

        if self.element_exist:
            locator, path, driver = self._locators()
            value = self.bp_cache['run_value']
            js_template = 'document.{method}("{path}").value = "{value}";'
            js_command = ''
            self.element_exist.send_keys(value, Keys.TAB)
            sleep(1)
            # print(value)

            # # js get id
            # if locator == 'id':
            #     js_command = js_template.format(method='getElementById', path=path, value=value)
            # # css query
            # elif locator == 'css selector':
            #     js_command = js_template.format(method='querySelector', path=path, value=value)
            # # execute command
            # driver.execute_script(js_command)
            # self.element_exist.submit()

    def screencap(self, file_name):
        """Take a full screenshot"""
        if file_name == '':
            file_name = self.bp_cache['run_value']
        img_where = '/'
        sleep(0.5)
        img_name = f'{img_where}{self.tc}_{file_name}.png'
        self.cache.log_input(tc=self.tc, output=f'IMAGE:{img_name}')

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
                self.cache.log_input(
                    error_msg=f"UNKNOWN EXPRESSION: %inner_tag OR %inner_tag%attr%attr_val OR empty"
                )
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
                text_list = [
                    tag.get_text() for tag in soup.find_all(soup_tag, soup_dict)
                ]

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
        self.cache.log_input(tc=self.tc, output=output)
        self.cache.cache_add(text=output)  # add to cache for validation if needed

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

            sleep(1)
            self.driver_wait.until(EC.frame_to_be_available_and_switch_to_it)
            driver.switch_to.default_content()
            driver.switch_to.frame(path)

        ### GOTO BACK ###
        elif 'back' in goto:
            print("> Returning to last page...")
            driver.back()

        ### Unknown args ###
        else:
            self.cache.log_input(error_msg=f"UNKNOWN ARGS: {goto}")

    def unload_file(self):
        """upload a file to UPLOAD"""
        from os import getcwd

        self._single_element()
        file_location = getcwd() + '\\resources\\input\\' + self.bp_cache['run_value']
        element = self.element_exist
        element.send_keys(file_location)

    def waiting(self):
        """Force webdriver to wait for n-seconds"""
        ### initiate ###
        val = self._logic_setup(default='default')

        if 'default' in val:
            sec = 5
        # arg --for
        elif 'for' in val:
            sec = int(self._logic_attr(logic_name='for', attr='condition'))
        sleep(sec)
