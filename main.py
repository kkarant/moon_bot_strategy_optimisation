from datetime import datetime

import fileImport
import regressionCalculaton
import reportCreator
import strategyStatistics
from deltaRangeFinder.decTreeRangesCombine import decoder
from deltaRangeFinder.deltaFindML import dataSetForDecisionTree, decisionTree, decorator


@decorator
def main():
    repFile = 'data/dr6k.txt'
    df = fileImport.csvImport(repFile)[0]
    colNames = fileImport.csvImport(repFile)[1]
    ratioData = strategyStatistics.getRatio(df, colNames)
    stratData = strategyStatistics.getStatForStrat(df, colNames)
    regrDict = regressionCalculaton.regressionValues(stratData, colNames)[0]
    listOfReqVal = regressionCalculaton.regressionValues(stratData, colNames)[1]
    stratRatioDict = strategyStatistics.strategyGetRatio(stratData)

    reportCreator.reportCreation(repFile, stratData, regrDict, ratioData, colNames, df, listOfReqVal,
                                 stratRatioDict)

    textRep = decisionTree(stratData, colNames)
    decoder(textRep, stratData, listOfReqVal)


if __name__ == '__main__':
    main()

# TODO strategyDict -> [1] -> strategy name -> vse sdelki
