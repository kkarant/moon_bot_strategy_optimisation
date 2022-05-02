import asyncio

from TPSLbasedOnData.dataReceiver import receiveData
from binanceApiTradeInfo.apiInitialization import clientInit, apiToDatabase
from binanceApiTradeInfo.restAPIinteraction import single_request
from databaseInteraction.dbKlinesInfo import receiveDataFromDB
from deltaRangesFinder.decTreeRangesCombine import weightSearch, weightLinesDepthSearch, \
    featuresListFinder, featuresCombineFinal, featuresFinalReport
from deltaRangesFinder.deltaFindML import decisionTree
from fileInteraction import fileImport, reportCreator
from fileInteraction.fileImport import checkFilesForExistence
from stratStatistics import regressionCalculaton, strategyStatistics
from supportingFunctions import decorator


@decorator
def main():
    repFile = 'data/dr13k.txt'
    listOfReportFiles = ["report/report.txt", "report/reportFeatures.txt", "report/reportFuncDuration.txt",
                         "report/reportRangesNotSorted.txt", "report/reportStratRangesFiveBest.txt"]
    client = clientInit()  # init of work with binance apI
    # mode = 0
    mode = 1
    checkFilesForExistence(listOfReportFiles)

    df = fileImport.csvImport(repFile)[0]  # our dataset from imported report
    colNames = fileImport.csvImport(repFile)[1]  # column name from imported file
    stratData = strategyStatistics.getStatForStrat(df, colNames)  # all trades for every strategy separated
    regrDict = regressionCalculaton.regressionValues(stratData, colNames)[0]  # regressions for every parame in strat
    listOfReqVal = regressionCalculaton.regressionValues(stratData, colNames)[1]  # list of values used in program
    stratRatioDict = strategyStatistics.strategyGetRatio(stratData)  # basic info but for every strategy by themselves

    with open("report/report.txt", "r") as file:
        lines = file.readlines()
        if lines.__len__() == 0 or str("Report for " + repFile) not in lines[0]:
            file.close()
            ratioData = strategyStatistics.getRatio(df, colNames)  # finds basic info as PnL or number of + and - trades
            reportCreator.reportCreation(repFile, stratData, regrDict, ratioData, colNames, df, listOfReqVal,
                                         stratRatioDict)

        # creates a txt report for all file and every strategy(correlation, basic stats, time in trade and so on)

    with open("report/reportFeatures.txt", "r") as file:
        lines = file.readlines()
        if lines.__len__() == 0 or str("Report for " + repFile) not in lines[0]:
            file.close()
            decisionTree(stratData, colNames)
            # TODO add if not the same reportFile then delete txt and generate new
            # generates trees, also can turn on feature of creating Jpg or TXT reports
            weightDict = weightSearch(stratData, listOfReqVal, mode)[0]
            # list of weights to find location and depth
            weightLine = weightSearch(stratData, listOfReqVal, mode)[1]
            # in which line of report there is searched weight
            weightDepthIndex = weightLinesDepthSearch(weightDict, weightLine, mode)
            # depth of lines with weights
            featureListDict = featuresListFinder(weightDepthIndex, weightLine, weightDict, mode)
            # returns dictionary with all features on the way to weights in given line (weightLine)
            # and depth (weightDepthIndex)
            # TODO SERVICE FUNCTION FOR ALL RAW FEATURES FOR SELECTED WEIGHTS
            reportCreator.featureReportCreation(repFile, weightDict, featureListDict)
            # creates txt report with features in raw format for every of 3 biggest weights in every strategy
            # TODO REMAKE OF DATA ABOUT RANGES AND TXT REPORT ABOUT IT
            rangesDictFinal = featuresCombineFinal(featuresFinalReport(featureListDict, listOfReqVal), listOfReqVal)
            # returns ranges in [$;$] format for all strategies
            reportCreator.rangesDictFinalReportCreation(repFile, rangesDictFinal)
            # creates txt report with all params ranges (not sorted)
            # TODO FINDS BEST STRATEGIES
            biggestRRList = strategyStatistics.bestStrategies(stratRatioDict, regrDict,
                                                              rangesDictFinal, stratData, listOfReqVal)[0]
            biggestRegrDictStrat = strategyStatistics.bestStrategies(stratRatioDict, regrDict,
                                                                     rangesDictFinal, stratData, listOfReqVal)[1]
            # finds five strategies with more than 400 trades and highest profit/loss ratio
            reportCreator.rangesReportFiveBestCreation(repFile, rangesDictFinal, biggestRRList,
                                                       biggestRegrDictStrat, stratRatioDict)
            # creates txt report with ranges and correlations for five strategies with highest ratio

    #apiToDatabase(stratData, client)

    receiveData(stratData)


if __name__ == '__main__':
    main()

# TODO strategyDict -> [1] -> strategy name -> vse sdelki
