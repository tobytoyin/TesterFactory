# Module for manipulating files systems and creating new files

import os
from src.setup.setup_load import export_config
from src.helper import Timer


class DirSetter:
    'DirSetter is for doing stuff to the directory'

    def __init__(self):
        super().__init__()
        self.output_dir = self.create_output_dir(mk_dir=False)

    def create_output_dir(self, mk_dir=False):
        path = f"output/{self._create_pattern(create_type='dir')}"
        if mk_dir == True:
            os.mkdir(path)
            os.mkdir(f'{path}/image_testcases')  # store test image
            os.mkdir(f'{path}/image_extracted')  # store image extracted using function
            print(f">> Created folders in {path}")
        return path

    def create_output_path(self, name: str = None, ext: str = None):
        'function to help generating consistent file names. `name:str`: a file name to be created. `return`: a path to create this file'
        assert (name != None) & (ext != None), "cannot be empty"
        file_name = f"{name}_{self._create_pattern(create_type='doc')}.{ext}"
        target_path = f'{self.output_dir}/{file_name}'
        return target_path

    def _create_pattern(self, create_type=None):
        testcase_name = export_config['name']
        cur_time = Timer().now()
        if create_type == 'dir':
            return f'{cur_time} {testcase_name}'
        elif create_type == 'doc':
            return f'{testcase_name}_{cur_time}'


if __name__ == '__main__':
    pass
else:
    dir_setter = DirSetter()
    output_dir = dir_setter.output_dir
    create_output_path = dir_setter.create_output_path
