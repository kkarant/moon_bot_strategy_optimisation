import fileImport
import regressionCalculaton
import strategyStatistics
from deltaRangeFinder.decTreeRangesCombine import weightSearch, weightLinesDepthSearch, \
    featuresListFinder
from deltaRangeFinder.deltaFindML import decorator
from reportCreator import featureReportCreation


@decorator
def main():
    repFile = 'data/dr11k.txt'
    df = fileImport.csvImport(repFile)[0]
    colNames = fileImport.csvImport(repFile)[1]
    ratioData = strategyStatistics.getRatio(df, colNames)
    stratData = strategyStatistics.getStatForStrat(df, colNames)
    regrDict = regressionCalculaton.regressionValues(stratData, colNames)[0]
    listOfReqVal = regressionCalculaton.regressionValues(stratData, colNames)[1]
    stratRatioDict = strategyStatistics.strategyGetRatio(stratData)

    # reportCreator.reportCreation(repFile, stratData, regrDict, ratioData, colNames, df, listOfReqVal,
    # stratRatioDict)
    # mode = 0
    mode = 1
    weightDict = weightSearch(stratData, listOfReqVal, mode)[0]
    print(weightDict)
    weightLine = weightSearch(stratData, listOfReqVal, mode)[1]
    print(weightLine)
    weightDepthIndex = weightLinesDepthSearch(weightDict, weightLine, mode)
    print(weightDepthIndex)
    featureListDict = featuresListFinder(weightDepthIndex, weightLine, weightDict, mode)
    print(featureListDict)

    featureReportCreation(repFile, weightDepthIndex, weightLine, weightDict, featureListDict)


if __name__ == '__main__':
    main()

# TODO strategyDict -> [1] -> strategy name -> vse sdelki
