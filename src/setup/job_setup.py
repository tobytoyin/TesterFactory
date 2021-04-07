import pandas as pd
import json
from src.job_assign import AssignWorkers
from src.excel_processing.excel_helper import create_runflow, create_testcases
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Factory:
    def __init__(
        self, path=r'C:\Users\tobyt\Projects\TestFactory\controller\controller.json'
    ):
        """
        Factory is used to setup and load all needed data from spreadsheets
        """
        self.setup = json.load(open(path, 'r'))

    def get_workbook(self, controller_key=''):
        """
        Arguments:
        -----
        --book_key: 'key of spreadsheet in controller.json

        Outputs:
        -----
        (workbook_for_testcases, workbook_for_runflow)
        """

        assert controller_key != '', "book_key cannot be empty"
        if self.setup[controller_key]['path'][-1] != '/':
            path = f"{self.setup[controller_key]['path']}/{self.setup[controller_key]['fileName']}"
        else:
            path = f"{self.setup[controller_key]['path']}{self.setup[controller_key]['fileName']}"
        workbook = pd.ExcelFile(path)
        return workbook

    @property
    def bp_maps(self):
        """bp_maps is a dictionary that allow test_case to fetch the blueprint that it needs"""
        wb = self.get_workbook(controller_key='runFlow')
        return create_runflow(wb)

    @property
    def component(self):
        component_sheet = self.setup['runFlow']['componentMasterSheetName']
        return self.bp_maps[component_sheet].set_index('key')

    @property
    def assigned_tasks(self):
        """assign workers"""
        ### initialize ###
        n_workers = self.setup['service']['workers']
        wb = self.get_workbook(controller_key='testCases')
        assign = AssignWorkers(create_testcases(wb), n_workers)
        return assign.assign()
