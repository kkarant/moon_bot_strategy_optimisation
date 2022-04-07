import os

import pandas as pd


# def findLastFile():
# tmp = 0
# lastFile = 'NaN'
# lastFileTime = 'NaN'
# for root, dirs, files in os.walk('data/'):
#     for file in files:
#         if file.endswith('.txt'):
#             tmp = os.path.getctime('data/' + file)
#             if tmp > os.path.getctime('data/' + file):
#                 lastFile = os.path.splitext(file.name)[0]
#                 lastFileTime = os.path.getctime('data/' + file)
#
# return lastFile, lastFileTime
#


def csvImport(file):
    df = pd.read_csv(file, sep='\t')
    df.drop(index=df.index[0])
    df.drop(["Quantity ", "BuyPrice ", "SellPrice ", "SellReason "], axis=1, inplace=True)
    colNames = list(df.columns)
    col_name = colNames[6]
    # df[col_name] = list(map(lambda x: x[:-2], df[col_name].values))
    el = 0
    df[col_name] = [elem[:-2] for elem in df[col_name].values]  # udalaem % iz colNames[6]
    df[col_name] = [float(x) for x in df[col_name].values]
    # print(colNames)

    return df, colNames

