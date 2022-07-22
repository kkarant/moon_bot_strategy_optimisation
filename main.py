from tpsl_calculation.data_manager import tpsl_StratLevel_manager_v3
from tpsl_calculation.tpsl_backtest import backtest_stratLevel_manager
from binance_api.APIinteraction import clientInit, apiToDatabase
from delta_calculation.decTreeRangesCombine import weightSearch, weightLinesDepthSearch, \
    featuresListFinder, featuresCombineFinal, featuresFinalReport
from delta_calculation.deltaFindML import decisionTree
from file_interaction.reportCreator import rangesReportFiveBestCreation, rangesDictFinalReportCreation, \
    featureReportCreation, reportCreation
from file_interaction.fileImport import checkFilesForExistence, csvImport
from strategy_statistics.strategyStatistics import getStatForStrat, strategyGetRatio, getRatio, bestStrategies
from strategy_statistics.regressionCalculaton import regressionValues
from data_validation.supportingFunctions import decorator, checkEmptyFile


@decorator
def main():
    repFile = 'allData/data/dr13k.txt'
    listOfReportFiles = [repFile, "allData/report/report.txt", "allData/report/reportFeatures.txt",
                         "allData/report/reportFuncDuration.txt", "allData/report/reportRangesNotSorted.txt",
                         "allData/report/reportStratRangesFiveBest.txt", "allData/report/optimalTPSL.txt",
                         "allData/report/profitOnCalculatedTPSLRanges.txt"]
    # mode = 0
    mode = 1
    checkFilesForExistence(listOfReportFiles)

    df, colNames, BuySellPrice = csvImport(repFile)  # our dataset from imported report
    stratData: dict = getStatForStrat(df, colNames)  # all trades for every strategy separated
    regrDict, listOfReqVal = regressionValues(stratData, colNames)  # list of val used in program
    stratRatioDict = strategyGetRatio(stratData)  # basic info but for every strategy by themselves

    if checkEmptyFile("allData/report/report.txt", repFile):
        ratioData: tuple = getRatio(df, colNames)
        # finds basic info as PnL or number of + and - trades
        reportCreation(repFile, stratData, regrDict, ratioData, colNames, df, listOfReqVal,
                       stratRatioDict)

        # creates a txt report for all file and every strategy(correlation, basic stats, time in trade and so on)
    if checkEmptyFile("allData/report/reportFeatures.txt", repFile):
        decisionTree(stratData, colNames)
        # TODO add if not the same reportFile then delete txt and generate new
        # generates trees, also can turn on feature of creating Jpg or TXT reports
        weightDict: dict = weightSearch(stratData, listOfReqVal, mode)[0]
        # list of weights to find location and depth
        weightLine: dict = weightSearch(stratData, listOfReqVal, mode)[1]
        # in which line of report there is searched weight
        weightDepthIndex: dict = weightLinesDepthSearch(weightDict, weightLine, mode)
        # depth of lines with weights
        featureListDict: dict = featuresListFinder(weightDepthIndex, weightLine, weightDict, mode)
        # returns dictionary with all features on the way to weights in given line (weightLine)
        # and depth (weightDepthIndex)
        # TODO SERVICE FUNCTION FOR ALL RAW FEATURES FOR SELECTED WEIGHTS
        featureReportCreation(repFile, weightDict, featureListDict)
        # creates txt report with features in raw format for every of 3 biggest weights in every strategy
        # TODO REMAKE OF DATA ABOUT RANGES AND TXT REPORT ABOUT IT
        rangesDictFinal = featuresCombineFinal(featuresFinalReport(featureListDict, listOfReqVal), listOfReqVal)
        # returns ranges in [$;$] format for all strategies
        rangesDictFinalReportCreation(repFile, rangesDictFinal)
        # creates txt report with all params ranges (not sorted)
        # TODO FINDS BEST STRATEGIES
        biggestRRList, biggestRegrDictStrat = bestStrategies(
            stratRatioDict, regrDict, rangesDictFinal, stratData, listOfReqVal)
        # finds five strategies with more than 400 trades and highest profit/loss ratio
        rangesReportFiveBestCreation(repFile, rangesDictFinal, biggestRRList,
                                     biggestRegrDictStrat, stratRatioDict)
        # creates txt report with ranges and correlations for five strategies with highest ratio

    if checkEmptyFile("allData/report/profitOnCalculatedTPSLRanges.txt", repFile):
        backtest_stratLevel_manager(stratData, colNames, repFile)

    apiToDatabase(stratData)

    tpsl_StratLevel_manager_v3(stratData, colNames, BuySellPrice)


if __name__ == '__main__':
    main()

