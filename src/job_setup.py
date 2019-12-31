import pandas as pd
import json
from src.job_assign import Boss


class Factory:
    def __init__(self, path):
        """
        Factory is used to setup and load all needed data from spreadsheets
        """
        self.setup = json.load(open(path, 'r'))

    def book_and_sheets(self, book_key=''):
        """
        Arguments:
        -----
        --book_key: 'key of spreadsheet in controller.json

        Outputs:
        -----
        (workbook, sheetnames, core_sheet)
        """
        assert book_key != '', "book_key cannot be empty"
        if self.setup[book_key]['path'][-1] != '/':
            path = f"{self.setup[book_key]['path']}/{self.setup[book_key]['fileName']}"
        else:
            path = f"{self.setup[book_key]['path']}{self.setup[book_key]['fileName']}"
        wb = pd.ExcelFile(path)
        sh = wb.sheet_names
        tg = self.setup[book_key]['sheetName']
        return wb, sh, tg

    @property
    def bp_maps(self):
        """bp_maps is a dictionary that allow test_case to fetch the blueprint that it needs"""
        wb, sh, _ = self.book_and_sheets(book_key='flowMap')
        bp_maps = {}

        for sheet in sh:
            bp_maps[sheet] = pd.read_excel(wb, sheet)
        return bp_maps

    @property
    def test_inputs(self):
        wb, _, tg = self.book_and_sheets(book_key='caseMap')
        test_inputs = pd.read_excel(wb, tg, dtype=str).dropna(how='all')
        return test_inputs

    @property
    def assigned_tasks(self):
        """assign workers"""
        ### initialize ###
        service = self.setup['service']
        boss = Boss(self.test_inputs, service['workers'])
        return boss.assign()

