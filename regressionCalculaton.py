import numpy as np
from scipy.stats import pearsonr


def zeroElimination(list):
    for i in range(len(list)):
        if list[i] == 0:
            list[i] = 0.0001


def regressionValues(strategyDict, columns):
    listOfReqVal = ['dBTC ', 'd24BTC ', 'dMarket ', 'dM24 ', 'bvsv ', 'dBTC5m ', 'Pump1H ', 'Dump1H ', 'd24h ', 'd3h ',
                    'd1h ', 'd15m ', 'd5m ', 'd1m ', 'dBTC1m ', 'Vd1m ']
    tempListOFprofit = []
    tempListSecondParamValForStrat = []
    tempListSecondParamValForEl = []
    tempCorrValList = []
    profitDict = {}
    secondparamDict = {}
    corrDict = {}
    el = 0
    # i = 0
    for stratName in strategyDict[1]:
        # this for is needed to iterate over every strategy
        # in it we calculate regression for this strategies
        while el < strategyDict[1][stratName].__len__():  # el is number of trades in strategy
            tempListOFprofit.append(int(strategyDict[1][stratName][el][1][6]))
            # we add the value of profit of every
            # trade (num of trade is el) of the strategy we are currently on
            # (strategy name iterates on first for by stratName value)
            el = el + 1
        # i = i + 1
        # service check of list
        # print(' Num of str: ' + str(i) + ' | Num of elem in list: ' + str(el)
        #      + ' | list: ' + str(listOfprofit)
        # regrassion calculations
        el = 0

        for val in listOfReqVal:
            while el < strategyDict[1][stratName].__len__():
                index = columns.index(val)
                # тут по порядку для каждой сделки все данные listOfReqVal
                tempListSecondParamValForEl.append(strategyDict[1][stratName][el][1][int(index)])
                el = el + 1
            el = 0
            tempListSecondParamValForStrat.append(tempListSecondParamValForEl)
            tempListSecondParamValForEl = []

        secondparamDict[stratName] = tempListSecondParamValForStrat  # list with all the market data from log file
        profitDict[stratName] = tempListOFprofit  # data for regression calculation
        tempListSecondParamValForStrat = []
        tempListOFprofit = []

    for stratName in strategyDict[1]:
        Y = np.array(profitDict[stratName])  # Y -  dependent variables whose values are to be predicted
        for el in listOfReqVal:  # параметры рынка
            X = np.array(secondparamDict[stratName][listOfReqVal.index(el)])
            # X : numpy array or sparse matrix of shape [n_samples,n_features]
            if 0 in X:
                zeroElimination(X)
            if X.__len__() < 1:
                tmcor = 'Not enough data'
                tempCorrValList.append(tmcor)
            elif X.__len__() > 1:
                tmcor = pearsonr(X, Y)
                tempCorrValList.append(tmcor[0])
            tmcor = []
            # print(tmcor[1])
        corrDict[stratName] = tempCorrValList
        tempCorrValList = []

    # for stratName in strategyDict[1]:
    #     print('\nCorrelations for strategy ' + str(stratName))
    #     if corrDict[stratName].__len__() == 0:
    #         print('Not Enough data')
    #     else:
    #         for el in listOfReqVal:
    #             print('parameter: ' + str(el) + ' is ' + '{0:g}'.format(corrDict[stratName][listOfReqVal.index(el)]))

    # print('\n')

    return corrDict, listOfReqVal

# TODO
#   X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
#                 # X_train = X_train.reshape(-1, 1)
#                 # y_train = y_train.reshape(-1, 1)
#                 # regressor = LinearRegression()
#                 # regressor.fit(X_train, y_train)
#             #y_pred = regressor.predict(X_test)
#             #df_pred = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
#             #print(df_pred)
#             # Y_pred = linearRegression.predict(X)  # make predictions\


# TODO How to print graph
#     # plt.scatter(X, Y)
#     # plt.plot(X, Y_pred, color='red')
#     # plt.title('Strategy ' + str(stratName) + ', regression for ' + str(el))
#     # plt.xlabel('profit')
#     # plt.ylabel(el)
#     # plt.show()
#     # print(profitDict[stratName]) np.array(
#     # print(secondparamDict[stratName][el])
