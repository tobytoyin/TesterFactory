from src.helper import print_table, Timer
from src.operation.exec_valid import ValidateExecution
from src.operation.exec_test import TestExecution
from src.processing.process import Process
from datetime import datetime
from multiprocessing import Lock


class MainFrame:
    """
    MainFrame is used to take a single data needed from Process and start the testing process.
    Handle logical operation of the whole framework.
    The output will then query another data needed and continue.
    Argument:
    ------
    `process_info` (A dictionary in a format)
    """

    def __init__(self, process_info, printout, printout_cache, stop_when_fail):
        self.args = {
            'printout': printout,
            'printout_cache': printout_cache,
            'stop_when_fail': stop_when_fail,
        }
        self.reports = []
        self.prev = {}
        self.process = Process(
            setup=process_info['setup'],
            test_input=process_info['test_input'],
            bp_map=process_info['bp_map'],
        )

    @property
    def get_reports(self):
        "Retrieve the testing report of a single test case"
        return self.reports

    def start(self):
        """
        Start to execute the test automation \n
        output: A list of test result dicts
        """
        ### initialize variables ###
        print_lock = Lock()
        process = self.process
        process_iter = iter(process)
        process_cur = process_iter.i
        process_max = process_iter.n
        t_start = datetime.now()
        g = 0

        ### process running ###
        while process_cur < process_max:

            assert process.web_status == 200
            # geterator a cache for passing data
            cache = next(process_iter)
            # load prev into cache
            cache.log_input(g=g)
            cache.load_prev(self.prev)
            # print(data_interface.get_blueprint_cache)

            # Block for TestExecution
            timer = Timer()
            timer.begin()
            test_exe = TestExecution(process.driver, cache)
            test_exe.execute_func(execute_for='run')
            timer.end()

            # Debugging msg
            # print("Test cache passing --->")
            # print(data_interface.get_cache)

            # Block for ValidateExecution
            valid_exe = ValidateExecution(process.driver, cache)
            if valid_exe.validate_require:
                valid_exe.execute_func(execute_for='validate')

            # Block for manipulating iterator pointer
            self.ptr_logic_gate(cache, process_cur)

            # Debug print
            if self.args['printout']:
                print_lock.acquire()
                header_b = ('Blueprint fields', 'Values')
                print_table(
                    cache.get_log_cache,
                    header=header_b,
                    title=f'Results - {test_exe.tc}',
                    style=('=', '-'),
                )
                print_lock.release()

            if self.args['printout_cache']:
                print_lock.acquire()
                header_c = ('Cached fields', 'Values')
                print_table(
                    cache.get_cache,
                    header=header_c,
                    title=f'Cache Info - {valid_exe.tc}',
                    style=('~', '-'),
                )
                print_lock.release()

            if not cache.is_empty():
                self.reports.append(cache.get_log_cache)

            # store history
            g += 1
            self.prev.update(cache.get_cache)
            try:
                if valid_exe.validate_require and self.args['stop_when_fail']:
                    assert valid_exe.terminate is False
            except AssertionError:  # Fail case will stop immediately
                print(f"> {valid_exe.tc} has been terminated")
                break
            finally:
                del cache, valid_exe, test_exe
                process_cur = process_iter.i  # retreive current position

        ### process terminated ###
        process.driver.close()
        return self.get_reports  # return a [dicts]

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
