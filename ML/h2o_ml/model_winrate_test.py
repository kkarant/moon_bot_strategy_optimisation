import h2o
import warnings
import pandas as pd
from h2o.automl import H2OAutoML

from api_db_pipeline.db_interaction.db_interaction import dbReceiveKlines, connectionDB
from tpsl_calculation.tp_calculation_ver3 import tradeDataPrep


def h2o_train_c(TP, colNames, BuySellPrice, stratData):
    h2o.init(ip="localhost", port=54323)

    df = categorize(colNames, BuySellPrice, stratData, TP)
    data = h2o.H2OFrame(df)
    train, test, valid = data.split_frame(ratios=[.7, .15])
    x = train.columns
    y = "Profit "

    x.remove(y)
    train[y] = train[y].asfactor()
    test[y] = test[y].asfactor()
    aml = H2OAutoML(max_models=20, seed=1)
    aml.train(x=x, y=y, training_frame=train)

    m = aml.get_best_model()
    model_path = h2o.save_model(model=m, path="all_data/models", force=True)


def categorize(colNames, BuySellPrice, stratData, TP):
    warnings.simplefilter(action='ignore', category=FutureWarning)
    columns = ["Profit ", "dBTC ", "d24BTC ", "dMarket ", "dM24 ",
               "dBTC5m ", "Pump1H ", "Dump1H ", "d24h ", "d3h ", "d1h ", "d15m ", "d5m ", "d1m ", "dBTC1m "]
    df = pd.DataFrame(columns=columns)
    dateFormat = "%Y-%m-%d %H:%M:%S"
    for stratName in stratData[1]:
        for trade in stratData[1][stratName]:
            p = 0
            profit = 0
            append_data = []
            coin, openTimeDT, closeTimeDT, openPrice, closePrice, profit, optimisedName = \
                tradeDataPrep(trade, colNames, dateFormat, BuySellPrice)
            optimisedName = str("_" + trade[1]["Coin "][:-1] + "USDT")
            profit = 0
            priceActionData = dbReceiveKlines(optimisedName, openTimeDT, closeTimeDT, *connectionDB())
            for el in priceActionData:
                p_t = (float(el[0]) - float(openPrice)) / float(openPrice) * 100
                if p_t > p:
                    p = p_t
            if stratName in TP.keys():
                for el in TP[stratName]:
                    if p >= el[2]:
                        profit = int(1)
            else:
                if p >= 0.2:
                    profit = int(1)
            append_data = [profit]
            for el in ["dBTC ", "d24BTC ", "dMarket ", "dM24 ", "dBTC5m ", "Pump1H ",
                       "Dump1H ", "d24h ", "d3h ", "d1h ", "d15m ", "d5m ", "d1m ", "dBTC1m "]:
                append_data.append(trade[1][colNames.index(el)])
            append_data_pd = pd.Series(append_data, index=df.columns)
            df = df.append(append_data_pd, ignore_index=True)
    return df


def ml_accuracy(TP, colNames, BuySellPrice, stratData):
    h2o.init(ip="localhost", port=54323)
    goods = 0
    df = categorize(colNames, BuySellPrice, stratData, TP)
    df.to_csv("trainData.csv")
    data = h2o.H2OFrame(df)
    train, test, valid = data.split_frame(ratios=[.7, .15])
    x = train.columns
    y = "Profit "
    x.remove(y)
    train[y] = train[y].asfactor()
    test[y] = test[y].asfactor()

    model = h2o.load_model("all_data/models/DRF_1_AutoML_1_20220727_110304")
    preds = model.predict(test)

    predsList = h2o.as_list(preds, use_pandas=False)
    testList = h2o.as_list(test[y], use_pandas=False)
    # make plot of profit from test and preds on one plot
    i = 0
    for index in range(1, len(testList)):
        if testList[index][0] == '0':
            i += 1
            if int(predsList[index][0]) == int(testList[index][0]):
                goods += 1
    print(f'Accuracy = {goods/len(test)*100}')
