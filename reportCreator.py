import strategyStatistics


def reportModulesStrFind(strFirstLine):
    string1 = strFirstLine

    file1 = open("report/report.txt", "r")
    flag = 0
    index = 0

    for line in file1:
        index = index + 1
        if string1 in line:
            flag = 1
            break
    if flag == 0:
        # print('String', string1, 'Not Found')
        file1.close()
        return 1
    else:
        # print('String', string1, 'Found In Line', index)
        file1.close()
        return 0
    # closing text file


def reportSourceFileName(rfile):
    string1 = str(rfile)

    file1 = open("report/report.txt", "r")
    flag = 0
    index = 0

    for line in file1:
        index = index + 1
        if string1 in line:
            flag = 1
            break
    if flag == 0:
        # print('String', string1, 'Not Found')
        file1.close()
        return 1
    else:
        # print('String', string1, 'Found In Line', index)
        file1.close()
        return 0
    # closing text file


def timeInTradeCalcprint(strategyDictTime, file):
    file.write('\n===================================================')
    file.write('\nAverage time in trade stats for strategies')
    for stratName in strategyDictTime:
        file.write('\nFor strategy ' + str(stratName) + 'average time for trade is '
                   + ("%.2f" % (strategyDictTime[stratName] / 60.0))
                   + ' min (' + "%.2f" % strategyDictTime[stratName] + ') sec ')


def reportCreation(rfile, stratData, regrDict, ratioData, colNames, df, listOfReqVal, stratRatioDict):
    if reportSourceFileName(rfile):
        with open("report/report.txt", "w") as file:
            file.write('Report for ' + str(rfile))

    file = open("report/report.txt", "a")
    if reportModulesStrFind('Overall stats for strategy'):
        file.write('\n===================================================')
        file.write('\nOverall stats for strategy')
        file.write('\n')
        file.write('\nAverage plus is: ' + str('{0:.2f}'.format(ratioData[0])) + '\nAverage minus is: '
                   + (str('{0:.2f}'.format(ratioData[1])))
                   + '\nProfit/loss ratio is: ' + str('{0:.2f}'.format(ratioData[0] / ratioData[1]))
                   + '\nWhile there is: ' + str('{0:.2f}'.format(ratioData[2])) + ' profit trades, and: '
                   + str('{0:.2f}'.format(ratioData[3])) + ' loss trades'
                   + '\ncalculated statistical realized PnL(%) is: ' + str('{0:.2f}'.format(ratioData[4])) + '%' +
                   '\nReal PnL(%) is: ' + str('{0:.2f}'.format(ratioData[5])) + '%' +
                   '\n\n***PnL(%) statistics are correct only with same order size in every trade***')

    if reportModulesStrFind('Statistics about frequency of strategies'):
        file.write('\n===================================================')
        file.write('\n Statistics about frequency of strategies')
        file.write('\n')
        file.write(str(df[str(str(colNames[7]))].value_counts()))

    if reportModulesStrFind('Average time in trade stats for strategies'):
        timeInTradeCalcprint(strategyStatistics.timeInTradeCalc(stratData, colNames)[0], file)

    if reportModulesStrFind('Overall stats for each strategy'):
        # 'real_pnl', 'plusCount', 'minusCount', 'sumPlus', 'sumMinus', 'averagePlus', 'averageMinus'
        file.write('\n===================================================')
        file.write('\n Overall stats for each strategy')
        for stratName in stratRatioDict:
            file.write('\n')
            file.write('\nOverall stats for strategy ' + str(stratName))
            file.write(
                '\nTotal trades = ' + str(stratRatioDict[stratName][1] + stratRatioDict[stratName][2]) +
                '\nAverage plus is: ' + str('{0:.2f}'.format(stratRatioDict[stratName][5])) + '\nAverage minus is: '
                + (str('{0:.2f}'.format(stratRatioDict[stratName][6])))
                + '\nProfit/loss ratio is: ' + str(
                    '{0:.2f}'.format(stratRatioDict[stratName][5] / stratRatioDict[stratName][6]))
                + '\nWhile there is: ' + str('{0:.2f}'.format(stratRatioDict[stratName][1])) + ' profit trades, and: '
                + str('{0:.2f}'.format(stratRatioDict[stratName][2])) + ' loss trades'
                + '\nReal PnL(%) is: ' + str('{0:.2f}'.format(stratRatioDict[stratName][0])) + '%')

    if reportModulesStrFind('Correlation stats for strategies'):
        file.write('\n===================================================')
        file.write('\nCorrelation stats for strategies')
        file.write('\n')
        for stratName in regrDict:
            file.write('\n')
            file.write('\nCorrelations for strategy ' + str(stratName))
            i = 0
            if regrDict[stratName].__len__() == 0:
                file.write('    Not Enough data')
            elif stratData[1][stratName].__len__() < 10:
                file.write('    Not enough trades for real corr')
            else:
                for el in listOfReqVal:
                    currEl = regrDict[stratName][listOfReqVal.index(el)]
                    if currEl > 0.18 or currEl < -0.18:
                        file.write('\nparameter: ' + str(el) + ' is ' + '{0:.2f}'.format(currEl))
                        i = i + 1
                if i == 0:
                    file.write('    Not Enough data ')
    file.close()


def featureReportCreation(rfile, weightDict, featureListDict):
    with open("report/reportFeatures.txt", "w") as file:
        file.write('Report for ' + str(rfile))
    file = open("report/reportFeatures.txt", "a")
    for stratName in featureListDict:
        i = 0
        file.write('\nReport for ' + stratName)
        while i < len(weightDict[stratName]):
            file.write('\nfor ' + weightDict[stratName][i])
            file.write('\nfeatures: ')
            for el in featureListDict[stratName][1]:
                file.write('\t\n' + el)
            i = i + 1
    file.close()


def rangesDictFinalReportCreation(rfile, rangesDictFinal):
    with open("report/reportRangesNotSorted.txt", "w") as file:
        file.write('Report for ' + str(rfile))

    file = open("report/reportRangesNotSorted.txt", "a")
    for stratName in rangesDictFinal:
        file.write("\n====================================")
        file.write("\nRanges for strategy " + stratName)
        for el in rangesDictFinal[stratName]:
            file.write("\n" + el)
    file.close()


def rangesReportFiveBestCreation(rfile, rangesDictFinal, biggestRRList, biggestRegrDictStrat, stratRatioDict):
    i = 0
    with open("report/reportStratRangesFiveBest.txt", "w") as file:
        file.write('Report for ' + str(rfile))

    file = open("report/reportStratRangesFiveBest.txt", "a")
    for stratName in biggestRegrDictStrat:
        file.write("\n====================================")
        file.write("\nRanges for strategy " + stratName + " with ratio = {0:.2f}".format(biggestRRList[i]))
        file.write('\nTotal trades = ' + str(stratRatioDict[stratName][1] + stratRatioDict[stratName][2]))
        for el in rangesDictFinal[stratName]:
            file.write("\n" + el)
            if len(biggestRegrDictStrat[stratName]) > 0:
                for val in biggestRegrDictStrat[stratName]:
                    if val in el:
                        file.write(", correlation is {0:.2f}".format(biggestRegrDictStrat[stratName][val]))

        i = i + 1
    file.close()
