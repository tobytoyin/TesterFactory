import pandas as pd
import json


class Factory:
    def __init__(self, path='C:/USers/tobyt/TestFactory/controller/controller.json'):
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
    def flows_map(self):
        wb, sh, _ = self.book_and_sheets(book_key='flowMap')
        flows_map = {}

        for sheet in sh:
            flows_map[sheet] = pd.read_excel(wb, sheet, dtype=object)
        return flows_map

    @property
    def testcases(self):
        wb, _, tg = self.book_and_sheets(book_key='caseMap')
        testcases = pd.read_excel(wb, tg, dtype=object).dropna(how='all')
        return testcases


f = Factory()
print(f.testcases)
