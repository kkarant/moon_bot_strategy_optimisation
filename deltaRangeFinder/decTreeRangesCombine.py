def findStrFile(strF, startIndex, file, line):
    index = 0
    lines = file.readlines()

    # print(strF)
    # print(line)

    index = index + 1
    if strF in line:
        return True, index
    return -1


def weightSearch(stratData, listOfReqVal, mode):
    weightLine = {}
    tmpList1 = []
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

            file = open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+")
            for line in file.readlines():
                i = 0
                while i < len(stratData[1][stratName]):
                    # strF = f"weights: [0.00, {i:.2f}] class: Profit"
                    # strF_2 = str("weights: [0.00, 33.00] class: Profit")
                    # result = findStrFile(strToFind[i], startIndex, file, line)[0]
                    if findStrFile(strToFind[i], startIndex, file, line) is not None \
                            and findStrFile(strToFind[i], startIndex, file, line) != -1:
                        # print("Index of found is " + str(i))
                        tmpDict[i] = [strToFind[i], findStrFile(strToFind[i], startIndex, file, line)[1]]
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
                biggestWeightsList = sorted(tmpDict.keys(), reverse=True)[:3]
                for i in biggestWeightsList:
                    tmpList1.append(tmpDict[i][0])
                weightDict[stratName] = tmpList1
                weightLine[stratName] = biggestWeightsList
                biggestWeightsList = []
                tmpDict.clear()
                tmpList1 = []
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
        if mode == 0:
            t = content[weightLine[i] - 1]
            num = t.count(depthIndicator)
            weightDepthIndex[stratName] = num
        elif mode == 1:
            k = 0
            while k < len(weightLine[stratName]):
                t = content[weightLine[stratName][k] - 1] #problem
                print(k)
                num = t.count(depthIndicator)
                tmpList1.append(num)
                k = k + 1
            weightDepthIndex[stratName] = tmpList1
        tmpList1 = []

        file.close()
        i = i + 1
    return weightDepthIndex


def featuresListFinder(weightDepthIndex, weightLine, weightDict):
    depthIndicator = '|'
    j = 0
    featureListDict = {}
    for stratName in weightDict:
        featuresList = []
        i = 1
        strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
            replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")

        file = open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+")
        content = file.readlines()
        currDe = weightDepthIndex[j] - i
        while i <= weightLine[j]:
            if content[weightLine[j] - i].count('weights') == 1:
                ...
            elif content[weightLine[j] - i].count(depthIndicator) == currDe:

                # print(currDe)
                lengthFeatures = len(featuresList)
                featuresList.append(content[weightLine[j] - i]
                                    .replace("|", "").replace(" ", "").replace("---", "").replace("\n", ""))
                currDe = currDe - 1
            i = i + 1
        j = j + 1
        featureListDict[stratName] = featuresList
    return featureListDict


def findSeveralWeightPaths():
    ...
