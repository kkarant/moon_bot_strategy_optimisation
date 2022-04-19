def findStrFile(strF, startIndex, file, line):
    index = 0
    lines = file.readlines()

    # print(strF)
    # print(line)

    index = index + 1
    if strF in line:
        return True, index
    return -1


def get_key(val, dict):
    for key, value in dict.items():
         if val == value:
             return key


def weightSearch(stratData, listOfReqVal, mode):
    weightLine = {}
    tmpList1 = {}
    biggestWeightsList = []
    weightDict = {}
    featuresDict = {}
    i = 0
    for val in listOfReqVal:
        featuresDict['feature_' + str(i)] = str(val)
        i = i + 1

    for stratName in stratData[1]:
        if stratData[1][stratName].__len__() > 10:
            # print(stratName)
            tmpDict = {}
            startIndex = 0
            strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
                replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")

            item = [item for item in range(0, len(stratData[1][stratName]))]
            numList = [float(i) for i in item]
            strToFind = ["weights: [0.00, {0:.2f}] class: Profit".format(i) for i in numList]
            # print(strToFind)
            lineIndex = 0
            file = open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+")
            for line in file.readlines():
                i = 0
                lineIndex = lineIndex + 1
                while i < len(stratData[1][stratName]):
                    # strF = f"weights: [0.00, {i:.2f}] class: Profit"
                    # strF_2 = str("weights: [0.00, 33.00] class: Profit")
                    # result = findStrFile(strToFind[i], startIndex, file, line)[0]
                    if findStrFile(strToFind[i], startIndex, file, line) is not None \
                            and findStrFile(strToFind[i], startIndex, file, line) != -1:
                        # print("Index of found is " + str(i))
                        tmpDict[lineIndex] = [strToFind[i], i]
                    i = i + 1
            tmp = -1
            if mode == 0:
                tmp = -1
                for key, value in tmpDict.items():
                    if tmp < key:
                        tmp = key
                biggestWeight = tmp

                weightDict[stratName] = tmpDict[biggestWeight][0]
                weightLine[stratName] = biggestWeight
                tmpDict.clear()
            elif mode == 1:
                biggestWeightsListOfStrNum = []
                biggestWeightsListOfStr = []
                tmpList11 = {}
                for key in tmpDict:
                    tmpList11[key] = tmpDict[key][1]  # num str -- weights value
                    tmpList1[key] = tmpDict[key][0]  # num str -- str weights
                biggestWeightsList = sorted(tmpList11.values(), reverse=True)[:3]
                for i in biggestWeightsList:
                    biggestWeightsListOfStrNum.append(get_key(i, tmpList11))
                    biggestWeightsListOfStr.append(tmpList1[get_key(i, tmpList11)])
                weightDict[stratName] = biggestWeightsListOfStr  # weights str as in file
                weightLine[stratName] = biggestWeightsListOfStrNum  # lines in which we found str
                biggestWeightsList = []
                tmpDict.clear()
                tmpList11.clear()
                tmpList1.clear()
                biggestWeightsListOfStrNum = []
            file.close()
    return weightDict, weightLine


# def weightLinesSearch(weightDict, mode):
#
#     for stratName in weightDict:
#         i = 0
#         k = 0
#         strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
#             replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")
#
#         file = open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+")
#         for line in file.readlines():
#             i = i + 1
#             if mode == 0:
#                 if weightDict[stratName] in line:
#                     weightLine.append(i)
#             elif mode == 1:
#                 while k < len(weightDict[stratName]):
#                     if weightDict[stratName][k] in line:
#                         weightLine.append(weightDict[stratName][k])
#                     k = k + 1
#     return weightLine


def weightLinesDepthSearch(weightDict, weightLine, mode):
    tmpList1 = []
    depthIndicator = '|'
    weightDepthIndex = {}
    i = 0
    j = 0
    for stratName in weightDict:
        num = 0
        strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
            replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")

        file = open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+")
        content = file.readlines()
        if len(content) > 11:
            if mode == 0:
                t = content[weightLine[stratName] - 1]
                num = t.count(depthIndicator)
                weightDepthIndex[stratName] = num
            elif mode == 1:
                k = 0
                while k < len(weightLine[stratName]):
                    t = content[weightLine[stratName][k] - 1]  # problem
                    # print(weightLine[stratName][k] - 1)
                    num = t.count(depthIndicator)
                    tmpList1.append(num)
                    k = k + 1
                weightDepthIndex[stratName] = tmpList1
            tmpList1 = []

        file.close()
        i = i + 1
    return weightDepthIndex


def featuresListFinder(weightDepthIndex, weightLine, weightDict, mode):
    depthIndicator = '|'
    featureListDict = {}
    featuresDict = {}
    for stratName in weightDict:

        i = 1
        strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
            replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")

        file = open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+")
        content = file.readlines()
        if stratName in weightDepthIndex.keys():
            if mode == 0:
                featuresList = []
                currDe = weightDepthIndex[stratName] - i
                if weightLine[stratName] > 2:
                    while i <= weightLine[stratName]:
                        if content[weightLine[stratName] - i].count('weights') == 1:
                            ...
                        elif content[weightLine[stratName] - i].count(depthIndicator) == currDe:
                            featuresList.append(content[weightLine[stratName] - i]
                                                .replace("|", "").replace(" ", "").replace("---", "").replace("\n", ""))
                            currDe = currDe - 1
                        i = i + 1
                featureListDict[stratName] = featuresList
            elif mode == 1:
                elNum = 0
                for el in weightDepthIndex[stratName]:
                    featuresList = []
                    i = 1
                    currDe = el - i
                    if weightLine[stratName][elNum] > 2:
                        while i <= weightLine[stratName][elNum]:
                            if content[weightLine[stratName][elNum] - i].count('weights') == 1:
                                ...
                            elif content[weightLine[stratName][elNum] - i].count(depthIndicator) == currDe\
                                    and content[weightLine[stratName][elNum] - i].count(depthIndicator) != el:
                                # print(currDe)
                                # print('found ' + str(content[weightLine[stratName][elNum] - i]) + ' in line '
                                #      + str(weightLine[stratName][elNum] - i) + ' currDe = ' + str(currDe))
                                featuresList.append(content[weightLine[stratName][elNum] - i]
                                                    .replace("|", "").replace(" ", "").replace("---", "").replace("\n", ""))
                                currDe = currDe - 1
                            i = i + 1
                        elNum = elNum + 1
                        featuresDict[elNum] = featuresList
                    else:
                        featuresDict[elNum] = "wrong lines"
                featureListDict[stratName] = featuresDict
                featuresDict = {}
            else:
                featureListDict[stratName] = "No depth for this strategy"
    return featureListDict

