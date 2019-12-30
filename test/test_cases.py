import pandas as pd


index = pd.Index(range(0, 5))
col_1 = pd.array(range(1, 6))
col_n = pd.array(['column_1'])

real_df = pd.DataFrame(col_1, index=index, columns=col_n)
empty_df = pd.DataFrame()
fake_df = []
