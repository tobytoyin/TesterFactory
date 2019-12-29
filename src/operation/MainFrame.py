from src.helper import inline_arg_compile, print_table
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

    def __init__(self, process, printout=False):
        self.reports = []
        self.prev = {}
        self.process = process
        self.printout = printout

    @property
    def get_reports(self):
        "Retrieve the testing report of a single test case"
        return self.reports

    def start(self):
        "Start to execute a test case"
        ### initialize variables ###
        process = self.process
        process_iter = iter(process)
        process_cur = process_iter.i
        process_max = process_iter.n
        t_start = datetime.now()

        ### process running ###
        while process_cur < process_max:
            print(f"PTR @ {process_cur}==========")
            assert process.web_status == 200
            # geterator a cache for passing data
            ptr = None
            cache = next(process_iter)
            # load prev into cache
            cache.load_prev(self.prev)
            # print(data_interface.get_blueprint_cache)

            # Block for TestExecution
            test_exe = TestExecution(process.driver, cache)
            test_exe.execute_func(execute_for='run')

            # Debugging msg
            # print("Test cache passing --->")
            # print(data_interface.get_cache)

            # Block for ValidateExecution
            valid_exe = ValidateExecution(process.driver, cache)
            valid_exe.execute_func(execute_for='validate')

            # Debugging msg
            # print("Test validate cache passing --->")
            # print(data_interface.get_cache)

            # Block for manipulating iterator pointer
            if 'jumpto' in cache.get_cache:
                ptr = int(cache.get_cache['jumpto'])
            elif 'skipby' in cache.get_cache:
                ptr = process_cur + int(cache.get_cache['skipby'])
            if ptr is not None:
                self.process.pointer_change(value=ptr)

            # Debug print
            if self.printout:
                header_b = ('Blueprint fields', 'Values')
                header_c = ('Cached fields', 'Values')
                print_table(cache.get_log_cache, header=header_b, title='Results', style=('=', '-'))
                print_table(cache.get_cache, header=header_c, title='Cache', style=('~', '-'))
                print('\n')

            # self._inline_logic_read(
            #     test_exe, data_interface.get_blueprint_data['run_logic'])
            if not cache.is_empty():
                self.reports.append(cache.get_log_cache)
            # store history
            self.prev.update(cache.get_cache)
            del cache
            process_cur = process_iter.i  # retreive current position

        ### process terminated ###
        print(self.get_reports)


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
