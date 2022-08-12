import pandas as pd
import os.path


def csvImport(file):
    df = pd.read_csv(file, sep='\t')
    df.drop(index=df.index[0])
    BuySellPrice = df[["BuyPrice ", "SellPrice "]].copy()
    df.drop(["Quantity ", "BuyPrice ", "SellPrice ", "SellReason "], axis=1, inplace=True)
    colNames = list(df.columns)
    col_name = colNames[6]
    df[col_name] = [elem[:-2] for elem in df[col_name].values]  # udalaem % iz colNames[6]
    df[col_name] = [float(x) for x in df[col_name].values]

    return df, colNames, BuySellPrice


def checkFilesForExistence(listOfReportFiles):
    for path in listOfReportFiles:
        if os.path.exists(path):
            print(f'File {path} exists')
        elif not os.path.exists(path):
            with open(path, 'w') as file:
                print(f'Created file {path}')


