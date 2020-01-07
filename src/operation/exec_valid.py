from src.operation.execution import Execution
import re


class ValidateExecution(Execution):
    """
    Child-class of `Execution()` for validating testing outputs
    """

    def __init__(self, driver, cache):
        super().__init__(driver, cache)
        # self.cache = cache.get_cache
        # self.bp_cache = cache.get_bp_cache
        self.s_cache = cache.get_cache
        self.terminate = True
        self.result = 'Fail'

    @property
    def validate_value(self):
        """Retrieve the value to validate for"""
        return self.bp_cache['validate_value']

    @property
    def validate_require(self):
        return self.bp_cache['validate_method'] != 'nan'

    @property
    def logic_args(self):
        """Retrieve inline args and inputs for validation"""
        return self.bp_cache['validate_logic_fetch']

    ### helper ###
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
        cached = self.s_cache['text']
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
        assert (
            self.s_cache != {}
        ), "Cannot conduct validation without checking a specific elements previously"
        element_exist = self.s_cache['element_exist']
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

        self.cache.log_input(
            validate_method=f"checkout-validation BY:{how}",
            expect=f"{validate_key} {placeholder}={validate_value}",
            actual=f"{validate_key} {placeholder}={tp if validate_value == 'Yes' else tn}",
            result=self.result,
        )

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

        ### Log result ###
        self.cache.log_input(
            expect=f"Redirect ({how}) to '{redirect_to}'",
            actual=f"Redirect ({how}) to '{current_url}'",
            result=self.result,
        )

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

        self.cache.log_input(
            validate_method=f'text-validation BY:{how}',
            expect=f'"{compare_with}" IS {placeholder} IN SCRAPPED TEXT',
            actual=f'"{compare_with}" IS {actual_placeholder} IN "{scrapped_text}"',
            result=self.result,
        )
