import pandas as pd
import json


class Factory:
    def __init__(self, path='C:/USers/tobyt/TestFactory/controller/controller.json'):
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
        assert (book_key != ''), "book_key cannot be empty"
        if self.setup[book_key]['path'][-1] != '/':
            path = f"{self.setup[book_key]['path']}/{self.setup[book_key]['fileName']}"
        else:
            path = f"{self.setup[book_key]['path']}{self.setup[book_key]['fileName']}"
        wb = pd.ExcelFile(path)
        sh = wb.sheet_names
        tg = self.setup[book_key]['sheetName']
        return wb, sh, tg

    @property
    def flow_maps(self):
        wb, sh, _ = self.book_and_sheets(book_key='flowMap')
        flow_maps = {}

        for sheet in sh:
            flow_maps[sheet] = pd.read_excel(wb, sheet, index_col='index')
        return flow_maps

    @property
    def test_inputs(self):
        wb, _, tg = self.book_and_sheets(book_key='caseMap')
        test_inputs = pd.read_excel(wb, tg, dtype=str).dropna(how='all')
        return test_inputs
