from src.helper import print_table
from src.processing.assembler import Assembler
from src.operation.exec_valid import ValidateExecution
from src.operation.exec_test import TestExecution
from src.processing.cache import Cache
from src.helper import print_table
from multiprocessing import Lock
from src.setup.setup_load import assembly_config


class AssemblyBelt:
    """
    Parameters: 
    ---
    `process_bundle`: {config, worker_testcase, teststep, components_lib}

    AssemblyLine is used to take a single data needed from Process and start the testing process.
    Handle logical operation of the whole framework.
    The output will then query another data needed and continue.
    Argument:
    ------
    `process_info` (A dictionary in a format)
    """

    def __init__(
        self,
        material_per_task: dict(
            ref_testcase_id=None,
            worker_testcase=None,
            teststep=None,
            components_lib=None,
        ),
    ):
        self._testreports = []  # reports after completing a step
        self.prev = {}  # storing the previous step
        self.assembler = Assembler(
            ref_id=material_per_task['ref_testcase_id'],
            testcase=material_per_task['worker_testcase'],
            teststep=material_per_task['teststep'],
            component_map=material_per_task['components_lib'],
        )

    ### Golden Retriever ###
    def get_reports(self):
        'Retrieve the testing report for a single test case'
        return self._testreports

    def start(self):
        """Start to execute the test automation\n
        Output: 
        ----
        `self.testreports` -- [dict(),] -- A list of test result dicts
        """

        ### initialize variables ###
        assembler = self.assembler
        process_iter = iter(assembler)
        process_cur = process_iter.ptr
        process_end = process_iter.end_index
        global_step_idx = 0  # use to trace the global step regardless of the ptr

        ### Process running ###
        while process_cur < process_end:
            # TODO a webstatus assertion

            cache = assembler.new_process_initialize(
                process_iter=process_iter, global_index=global_step_idx, prev=self.prev
            )

            test_exe = TestExecution(assembler.driver, cache)
            test_exe.execute_func(execute_for='exe_teststep')

            validate_exe = ValidateExecution(assembler.driver, cache)
            if validate_exe.validate_require:
                validate_exe.execute_func(execute_for='validate')

            ## See if the pointer needs to change to change the next step starting point ##
            self._ptr_logic_gate(cache, process_cur)

            # Print Table
            self._print_table(cache=cache, print_config=assembly_config['print_table'])

            # append report
            log_cache = cache.get_cache(which_cache='log')
            if log_cache['testcase_id']:
                self._testreports.append(log_cache)

            # store history
            global_step_idx += 1
            self.prev.update(cache.get_cache(which_cache='tem'))

            # end check
            try:
                if validate_exe.validate_require and assembly_config['stop_when_fail']:
                    assert validate_exe.terminate is False
            except AssertionError:
                print(f"> {validate_exe.tc} has been terminated")
                break
            finally:
                del cache, validate_exe, test_exe
                process_cur = process_iter.ptr

        assembler.driver.close()
        return self.get_reports()

    def _ptr_logic_gate(self, cache: Cache, process_cur):
        "To determine whether point needs to change based on cache.logic"
        next_ptr = None
        tem_cache = cache.get_cache(which_cache='tem')

        if 'jumpto' in tem_cache:
            next_ptr = int(tem_cache['jumpto'])
        elif 'skipby' in tem_cache:
            next_ptr = process_cur + int(tem_cache['skipby'])
        self.assembler.ptr_change(
            new_ptr=next_ptr
        ) if next_ptr is not None else next_ptr
        return None

    def _print_table(self, cache: Cache, print_config: dict):
        print_lock = Lock()

        for cache_type, print_bool in print_config.items():
            if print_bool:
                print_lock.acquire()
                print_table(
                    cache.get_cache(which_cache=cache_type[6::]),  # name after "print_"
                    header=(f"{cache_type[6::]}_cache Fields", 'Values'),
                    title=f"{cache.ref_id} - {cache_type[6::]}",
                    style=('=', '-'),
                )
                print_lock.release()
