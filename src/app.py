from src.generate_data import Factory
from src.job_assign import Boss
import pandas as pd


class Application:
    """Application is the Framework"""

    def __init__(self, path):
        path = "C:/USers/tobyt/TestFactory/controller/controller.json"
        self.factory = Factory(path=path)
        self.boss = Boss()

    @property
    def setup(self):
        return self.factory.setup

    def main(self):
        test_cases = factory.test_inputs

        # this should be a single DataFrame
        assert test_cases.__class__ is pd.DataFrame, "input should be DataFrame"


boss = Boss()
