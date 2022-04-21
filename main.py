import fileImport
import regressionCalculaton
import reportCreator
import strategyStatistics
from deltaRangeFinder.decTreeRangesCombine import weightSearch, weightLinesDepthSearch, \
    featuresListFinder, featuresFinalReport, featuresCombineFinal
from deltaRangeFinder.deltaFindML import decorator, decisionTree


@decorator
def main():
    repFile = 'data/dr13k.txt'
    df = fileImport.csvImport(repFile)[0]
    colNames = fileImport.csvImport(repFile)[1]
    ratioData = strategyStatistics.getRatio(df, colNames)
    stratData = strategyStatistics.getStatForStrat(df, colNames)
    regrDict = regressionCalculaton.regressionValues(stratData, colNames)[0]
    listOfReqVal = regressionCalculaton.regressionValues(stratData, colNames)[1]
    stratRatioDict = strategyStatistics.strategyGetRatio(stratData)

    # reportCreator.reportCreation(repFile, stratData, regrDict, ratioData, colNames, df, listOfReqVal,
    # stratRatioDict)

    # decisionTree(stratData, colNames)
    # mode = 0
    mode = 1
    weightDict = weightSearch(stratData, listOfReqVal, mode)[0]
    # print(weightDict)
    weightLine = weightSearch(stratData, listOfReqVal, mode)[1]
    # print(weightLine)
    weightDepthIndex = weightLinesDepthSearch(weightDict, weightLine, mode)
    # print(weightDepthIndex)
    featureListDict = featuresListFinder(weightDepthIndex, weightLine, weightDict, mode)
    # print(featureListDict)

    rangesDictFinal = featuresCombineFinal(featuresFinalReport(featureListDict, listOfReqVal), listOfReqVal)
    # reportCreator.featureReportCreation(repFile, weightDict, featureListDict)
    # reportCreator.rangesDictFinalReportCreation(repFile, rangesDictFinal)
    strategyStatistics.bestStrategies(stratRatioDict, regrDict, rangesDictFinal, stratData, listOfReqVal)

    biggestRRList = strategyStatistics.bestStrategies(stratRatioDict, regrDict,
                                                      rangesDictFinal, stratData, listOfReqVal)[0]

    biggestRegrDictStrat = strategyStatistics.bestStrategies(stratRatioDict, regrDict,
                                                             rangesDictFinal, stratData, listOfReqVal)[1]

    reportCreator.rangesReportFiveBestCreation(repFile, rangesDictFinal, biggestRRList, biggestRegrDictStrat)

if __name__ == '__main__':
    main()

# TODO strategyDict -> [1] -> strategy name -> vse sdelki
