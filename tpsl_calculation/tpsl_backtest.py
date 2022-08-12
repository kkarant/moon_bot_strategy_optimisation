import math


def findStrFile(strF, line, startIndex):
    if strF in line:
        return startIndex
    return -1


def paramsCollector(startIndex, lines):
    paramsList = []
    paramsDict = {}
    lines = lines[startIndex + 1:]
    for line in lines:
        if "====================================" not in line:
            if "for" in line:
                param = ""
                for element in range(4, len(line)):
                    if line[element] != "r":
                        param = str(param) + str(line[element])
                    else:
                        break
                if param == 'dMa':
                    param = 'dMarket '

                paramsList.append(param[:-1])
                for element in range(4 + len(param), len(line)):
                    if line[element] == "[":
                        rangeEl = line[element:]
                        values = [float(x) for x in rangeEl[:-1].replace("[", "").replace("]", "").split(", ")]
                paramsDict[param] = values
        else:
            return paramsDict


def receiveOptimisedDeltaFromReport(file, stratData):
    stratDeltasStart = {}
    paramsDict = {}
    startIndex = 0
    with open(file, "r+") as file:
        lines = file.readlines()
        for line in lines:
            for stratName in stratData[1]:
                if str(stratName)[:-1] in line:
                    stratDeltasStart[stratName] = startIndex
            startIndex = startIndex + 1
    for el in stratDeltasStart.keys():
        paramsDict[el] = paramsCollector(stratDeltasStart[el], lines)
    return paramsDict


def receiveOptimisedTPSLFromReport(file, stratData):
    tpslValuesDict = {}
    startIndex = 0
    with open(file, "r+") as file:
        lines = file.readlines()
        for line in lines:
            for stratName in stratData[1]:
                if str(stratName)[:-1] in line:
                    if startIndex != -1:
                        optimalTP = lines[startIndex + 1].replace(" optimal TP ", "")
                        optimalSL = lines[startIndex + 2].replace(" optimal SL ", "")
                        tpslValuesDict[stratName] = [optimalTP[:-2], optimalSL[:-2]]
            startIndex = startIndex + 1
    return tpslValuesDict


def paramsRangesNormalise(paramMin, paramMax, param, stratName):
    dictparamRanges = {'dBTC ': [-5, 5],
                       'd24BTC ': [-10, 10],
                       'Pump1H ': [0, 1000],
                       'Dump1H ': [0, 1000],
                       'd24h ': [0, 100],
                       'd5m ': [0, 100],
                       'dBTC1m ': [0, 100],
                       'd3h ': [0, 20],
                       'd15m ': [0, 20],
                       'd1m ': [0, 20]
                       }

    dictDiffM = {'dMarket -': [-10, 0],
                 'dMarket +': [0, 10],
                 'dM24 -': [-10, 0],
                 'dM24 +': [0, 10]}
    if math.isnan(paramMin):
        if str(param + '-') in dictDiffM.keys() or str(param + '+') in dictDiffM.keys():
            if '-' in stratName:
                paramMin = dictDiffM[str(param + '-')][0]
            elif '+' in stratName:
                paramMin = dictDiffM[str(param + '+')][0]
        if str(param) in dictparamRanges.keys():
            paramMin = dictparamRanges[str(param)][0]

    if math.isnan(paramMax):
        if str(param + '-') in dictDiffM.keys() or str(param + '+') in dictDiffM.keys():
            if '-' in stratName:
                paramMax = dictDiffM[str(param + '-')][1]
            elif '+' in stratName:
                paramMax = dictDiffM[str(param + '+')][1]
        if str(param) in dictparamRanges.keys():
            paramMax = dictparamRanges[str(param)][1]

    return paramMin, paramMax


def backtest_stratLevel_manager(stratData, colNames, repFile):
    paramsDict = receiveOptimisedDeltaFromReport("all_data/report/reportRangesNotSorted.txt", stratData)
    # print(paramsDict)
    tpslValuesDict = receiveOptimisedTPSLFromReport("all_data/report/optimalTPSL.txt", stratData)
    # print(tpslValuesDict)
    file = open("all_data/report/profitOnCalculatedTPSLRanges.txt", "w")
    file.write(f"Report for {repFile}")
    for stratName in stratData[1]:
        overallprofit = 0
        overallprofitotSorted = 0
        plusCount = 0
        minusCount = 0
        if stratName in paramsDict.keys() and stratName in tpslValuesDict.keys():
            if paramsDict[stratName] is not None and tpslValuesDict[stratName] is not None:
                for trade in stratData[1][stratName]:
                    coinNotOK = 0
                    for param in paramsDict[stratName].keys():
                        paramVal = trade[1][colNames.index(param)]
                        paramMin, paramMax = paramsRangesNormalise(paramsDict[stratName][param][0],
                                                                   paramsDict[stratName][param][1], param, stratName)
                        # paramMin = paramsDict[stratName][param][0]
                        # paramMax = paramsDict[stratName][param][1]
                        # print(paramVal, paramMin, paramMax)
                        if param != 'bvsv ':
                            if paramMin <= float(paramVal) or float(paramVal) <= paramMax:
                                pass
                            else:
                                coinNotOK = 1
                    if coinNotOK != 1:
                        if float(trade[1][colNames.index('Profit ')]) > 6:
                            plusCount = plusCount + 1
                        else:
                            minusCount = minusCount + 1
                        overallprofit = overallprofit + float(trade[1][colNames.index('Profit ')])
                    overallprofitotSorted = overallprofitotSorted + float(trade[1][colNames.index('Profit ')])
                calculatedprofit = plusCount * float(tpslValuesDict[stratName][0]) \
                                   + minusCount * float(tpslValuesDict[stratName][1])

                file.write(f"\n====================================")
                file.write(f'\nFor {stratName} '
                           f'\nProfit(from report) = {round(overallprofit)}, '
                           f'\ncalculated profit = {round(calculatedprofit)}')
