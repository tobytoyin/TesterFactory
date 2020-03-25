from src.setup.setup_load import DataLoader
from src.processing.assembler import Assembler
from src.processing.belt import AssemblyBelt
from src.processing.lines import AssemblyLines
import os
from src.operation.exec_test import TestExecution
from src.operation.exec_valid import ValidateExecution
from src.setup.setup_load import assembly_config
import pprint

pp = pprint.PrettyPrinter(indent=4)

if __name__ == '__main__':
    a = AssemblyLines()
    a._get_lines_ready()

# app_path = os.getcwd()

# loader: DataLoader = DataLoader(app_path)
# process_bundle = {
#     'config': assembly_config,
#     'worker_testcase': loader.assign_testcase['worker_1'].iloc[0],
#     'teststep': loader.teststeps_map[0]['test_checkout'],
#     'components_lib': loader.teststeps_map[1],
# }

# assembly_line = AssemblyBelt(process_bundle=process_bundle)
# reports = assembly_line.start()
# pp.pprint(reports)

# iterator = iter(process)

# pp = pprint.PrettyPrinter(indent=2)
# # pp.pprint(cache._exe_cache)
# # pp.pprint(cache._log_cache)


# ### initialize variables ###
# prev = {}
# global_step_idx = 0  # use to trace the global step regardless of the ptr

# cache = process.new_process_initialize(
#     process_iter=iterator, g=global_step_idx, prev=prev
# )

# test_exe = TestExecution(process.driver, cache)
# test_exe.execute_func(execute_for='exe_teststep')

#             # validate_exe = ValidateExecution(process.driver, cache)
#             # if validate_exe.validate_require:
#             #     validate_exe.execute_func(execute_for='validate')

#             ## See if the pointer needs to change to change the next step starting point ##
#             # self._ptr_logic_gate(cache, process_cur)

#             # append report
# log_cache = cache.get_cache(which_cache='log')
# pp.pprint(log_cache)
# pp.pprint(cache.get_cache(which_cache='tem'))
#             if log_cache['test_id']:
#                 self._testreports.append(log_cache)

#             # store history
#             global_step_idx += 1
# prev.update(cache.get_cache(which_cache='tem'))

#             # end check
#             try:
#                 if (
#                     validate_exe.validate_require
#                     and self.assembly_config['stop_when_fail']
#                 ):
#                     assert validate_exe.terminate is False
#             except AssertionError:
#                 print(f"> {validate_exe.test_id} has been terminated")
#                 break
#             finally:
#                 del cache, validate_exe, test_exe
#                 process_cur = process_iter.end_index

#             process.driver.close()
#             return self.get_reports
