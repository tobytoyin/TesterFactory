from src.helper import print_table
from src.operation.execution import TestExecution, ValidateExecution
from src.processing.process import Process
from datetime import datetime


class MainFrame:
    """
    MainFrame is used to take a single data needed from Process and start the testing process.
    Handle logical operation of the whole framework.
    The output will then query another data needed and continue.
    Argument:
    ------
    `process_info` (A dictionary in a format)
    """

    def __init__(self, process_info, printout=False):
        self.reports = []
        self.prev = {}
        self.process = Process(
            process_info['service_info'],
            process_info['test_input'],
            process_info['bp_map'],
        )
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

            assert process.web_status == 200
            # geterator a cache for passing data
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

            # Block for manipulating iterator pointer
            self.ptr_logic_gate(cache, process_cur)

            # Debug print
            if self.printout:
                header_b = ('Blueprint fields', 'Values')
                header_c = ('Cached fields', 'Values')
                print_table(
                    cache.get_log_cache,
                    header=header_b,
                    title='Results',
                    style=('=', '-'),
                )
                print_table(
                    cache.get_cache, header=header_c, title='Cache', style=('~', '-')
                )

            if not cache.is_empty():
                self.reports.append(cache.get_log_cache)

            # store history
            self.prev.update(cache.get_cache)
            del cache
            process_cur = process_iter.i  # retreive current position

        ### process terminated ###
        process.driver.close()
        return self.get_reports

    def ptr_logic_gate(self, cache, process_cur):
        """Method for moving the ptr of the process iterator if needed"""
        ptr = None

        if 'jumpto' in cache.get_cache:
            ptr = int(cache.get_cache['jumpto'])
        elif 'skipby' in cache.get_cache:
            ptr = process_cur + int(cache.get_cache['skipby'])
        if ptr is not None:
            self.process.pointer_change(value=ptr)
        return None
