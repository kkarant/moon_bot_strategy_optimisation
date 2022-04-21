from datetime import datetime


def averageTime(lst):  # returns seconds
    tm = datetime(10, 1, 1, 0, 0, 0)
    for el in lst:
        tm = tm + el
    # print(tm)
    # print(tm.second + tm.minute*60 + tm.hour*3600)
    # print(len(lst))
    return (tm.second + tm.minute * 60 + tm.hour * 3600) / len(lst)


def getStatForStrat(df, columns):
    col_name = columns[7]
    strategyNames = list(df[col_name].unique())
    # print(strategyNames)

    strategyDict = {}
    index = columns.index('ChannelName ')
    # print(index)
    for row in df.iterrows():
        # print(row[1])
        if row[1][index] not in strategyDict:
            strategyDict[row[1][index]] = []
        strategyDict[row[1][index]].append(row)

    return strategyNames, strategyDict


def getRatio(df, columns) -> tuple:
    col_name = columns[6]
    plusCount = 0
    minusCount = 0
    sumForAverage_minus = 0
    sumForAverage_plus = 0
    real_pnl = 0
    for val in df.loc[:, col_name]:
        if val > 0.5:
            plusCount = plusCount + 1
            sumForAverage_plus = sumForAverage_plus + val
        elif val < 0.5:
            minusCount = minusCount + 1
            sumForAverage_minus = sumForAverage_minus + val
        real_pnl = real_pnl + val

    average_plus = sumForAverage_plus / float(plusCount)
    average_minus = sumForAverage_minus / float(minusCount)
    statistical_pnl = average_plus * plusCount + average_minus * minusCount

    return average_plus, average_minus, plusCount, minusCount, statistical_pnl, real_pnl


def strategyGetRatio(strategyDict):
    stratRatioDict = {}
    plusCount = 0
    minusCount = 0
    sumMinus = 0
    sumPlus = 0
    real_pnl = 0
    temp = []
    el = 0
    for stratName in strategyDict[1]:
        while el < (strategyDict[1][stratName]).__len__():
            tProfit = float(strategyDict[1][stratName][el][1][6])
            if tProfit > 0.5:
                plusCount = plusCount + 1
                sumPlus = sumPlus + tProfit
            elif tProfit < 0.5:
                minusCount = minusCount + 1
                sumMinus = sumMinus + tProfit
            real_pnl = real_pnl + tProfit
            el = el + 1
        el = 0
        if plusCount >= 1 and minusCount >= 1:
            averagePlus = sumPlus / float(plusCount)
            averageMinus = sumMinus / float(minusCount)
        else:
            averagePlus = 0
            averageMinus = 1

        temp.append(real_pnl)
        temp.append(plusCount)
        temp.append(minusCount)
        temp.append(sumPlus)
        temp.append(sumMinus)
        temp.append(averagePlus)
        temp.append(averageMinus)
        plusCount = 0
        minusCount = 0
        sumMinus = 0
        sumPlus = 0
        real_pnl = 0
        stratRatioDict[stratName] = temp
        temp = []

    # for stratName in stratRatioDict:
    # if stratRatioDict[stratName].__len__() > 1:
    # print(stratRatioDict[stratName])
    return stratRatioDict


def timeInTradeCalc(strategyDict, colNames):
    openTimeCol = colNames.index('BuyDate ')
    closeTimeCol = colNames.index('CloseDate ')
    tempList = []
    tempListForData = []
    strategyDictTimeAverage = {}
    strategyDictTimeData = {}
    el = 0
    for stratName in strategyDict[1]:
        while el < (strategyDict[1][stratName]).__len__():
            openTime = strategyDict[1][stratName][el][1][openTimeCol][:-1]
            closeTime = strategyDict[1][stratName][el][1][closeTimeCol][:-1]
            openTimeConverted = datetime.strptime(openTime, "%Y-%m-%d %H:%M:%S")
            closeTimeConverted = datetime.strptime(closeTime, "%Y-%m-%d %H:%M:%S")

            time_interval = closeTimeConverted - openTimeConverted
            tempList.append(time_interval)
            tempListForData.append(time_interval.seconds)

            # print('openTime = ' + str(openTimeConverted) + '\ncloseTime = ' + str(closeTimeConverted) +
            # '\ntradeTime = ' + str(time_interval))
            el = el + 1
        averageList = averageTime(tempList)

        # print(averageList)
        strategyDictTimeAverage[stratName] = averageList
        strategyDictTimeData[stratName] = tempListForData
        tempListForData = []
        tempList = []
        el = 0

    return strategyDictTimeAverage, strategyDictTimeData


def bestStrategies(stratRatioDict, regrDict, rangesDictFinal, stratData, listOfReqVal):
    stratWHighestRRList = []
    rrRatioTmp = {}
    biggestRegrDict = {}
    biggestRegrDictStrat = {}
    for stratName in rangesDictFinal:
        if len(stratData[1][stratName]) > 200:
            rrRatioTmp[stratName] = (stratRatioDict[stratName][5] / stratRatioDict[stratName][6])

    biggestRRList = sorted(rrRatioTmp.values(), reverse=False)[:5]
    for stratName in rangesDictFinal:
        if len(stratData[1][stratName]) > 200:
            for el in biggestRRList:
                if rrRatioTmp[stratName] == el:
                    stratWHighestRRList.append(stratName)

    for stratName in stratWHighestRRList:
        i = 0
        while i < len(regrDict[stratName]):
            if regrDict[stratName][i] > 0.1 or regrDict[stratName][i] < -0.1:
                biggestRegrDict[listOfReqVal[i]] = regrDict[stratName][i]
            i = i + 1
        biggestRegrDictStrat[stratName] = biggestRegrDict
        biggestRegrDict = {}
    # print(biggestRRList)
    # print(stratWHighestRRList)
    # print(biggestRegrDictStrat)
    return biggestRRList, biggestRegrDictStrat
# TODO сделать такой счетчик но и для плюс минус сделок иф профит меньше нуля то туда добавляем время и наоборот
