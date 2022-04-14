import fileImport
import regressionCalculaton
import strategyStatistics
from deltaRangeFinder.decTreeRangesCombine import weightSearch, weightLinesSearch, weightLinesDepthSearch, \
    featuresListFinder
from deltaRangeFinder.deltaFindML import decisionTree, decorator


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

    weightDict = weightSearch(stratData, listOfReqVal)  # ne rabotaet rzdelenie na zony
    print(weightDict)
    weightLine = weightLinesSearch(weightDict)
    print(weightLine)
    weightDepthIndex = weightLinesDepthSearch(weightDict, weightLine)
    print(weightDepthIndex)
    featuresListFinder(weightDepthIndex, weightLine, weightDict)


if __name__ == '__main__':
    main()

# TODO strategyDict -> [1] -> strategy name -> vse sdelki
