from src.helper import inline_arg_compile
from src.operation.execution import TestExecution, ValidateExecution
from src.processing.Process import Process, test_data
from datetime import datetime


class MainFrame:
    """
    MainFrame is used to take a single data needed from Process and start the testing process.
    Handle logical operation of the whole framework. 
    The output will then query another data needed and continue. 
    Argument:
    ------
    `process` (Process object)
    """

    def __init__(self, process):
        self.testing_reports = []
        self.process = process

    @property
    def get_testing_reports(self):
        "Retrieve the testing report of a single test case"
        return self.testing_reports

    def start(self):
        "Start to execute a test case"
        ### initiate variables ###
        process = self.process
        run = 0  # determine to terminate/ continue
        process_iter = iter(process)
        process_max = process_iter.n
        t_start = datetime.now()

        ### process running ###
        print("process is starting --->")
        while run < process_max:
            print(f"{run} \n")
            assert process.web_status == 200
            # geterator a cache for passing data
            data_interface = next(process_iter)
            # print(data_interface.get_blueprint_cache)

            # Block for TestExecution
            test_exe = TestExecution(process.driver, data_interface)
            test_exe.execute_func(execute_for='run')

            # Debugging msg
            # print("Test cache passing --->")
            # print(data_interface.get_cache)

            # Block for ValidateExecution
            valid_exe = ValidateExecution(process.driver, data_interface)
            valid_exe.execute_func(execute_for='validate')

            # Debugging msg
            # print("Test validate cache passing --->")
            # print(data_interface.get_cache)
            print(data_interface.get_log_cache)

            # Block for manipulating iterator pointer
            # self._inline_logic_read(
            #     test_exe, data_interface.get_blueprint_data['run_logic'])
            del data_interface
            run += 1

            ### process terminated ###
        # print(data_interface.get_testing_reports)

    def _inline_logic_read(self, test_exe, logic_list):
        """
        Read inline logic, e.g. --jumpto(Yes,3)
        Arguments: 
        ------
        `logic_list` (list of dict): list containing dictionaries with keys `['func', 'condition', 'output']`
        """
        # no inline-args to work on
        if len(logic_list) == 0:
            return None
        for arg in logic_list:  # loop each dict
            if arg['func'] == 'jumpto':
                self._jumpto_logic(test_exe, arg)

    def _jumpto_logic(self, test_exe, arg):
        element_exist = test_exe.element_exist
        # print(element_exist)
        # print(arg)
        if (element_exist == None) & (arg['condition'] == 'No'):
            self.process.pointer_change(
                switch_method='jumpto', value=arg['input'])
            print(f"pointer change to {self.process.i}")

        elif (element_exist != None) & (arg['condition'] == 'Yes'):
            self.process.pointer_change(
                switch_method='jumpto', value=arg['output'])
            print(f"pointer change to {self.process.i}")
        else:
            pass
            print("some error ")


class Error(Exception):
    pass


class WebStatusError(Error):
    """Raised when web response is not 200"""
    pass


if __name__ == '__main__':
    import os
    print(os.getcwd())
    main = MainFrame(test_data['process'])
    main.start()
