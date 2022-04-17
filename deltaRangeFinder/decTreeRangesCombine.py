def findStrFile(strF, startIndex, file, line):
    index = 0
    lines = file.readlines()

    # print(strF)
    # print(line)

    index = index + 1
    if strF in line:
        return True, index
    return -1


def weightSearch(stratData, listOfReqVal):
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
            for key, value in tmpDict.items():
                if tmp < key:
                    tmp = key
            biggestWeight = tmp
            # print(tmpDict[biggestWeight][0])
            file.close()
            weightDict[stratName] = tmpDict[biggestWeight][0]
            tmpDict.clear()
    return weightDict


def weightLinesSearch(weightDict):
    weightLine = []
    for stratName in weightDict:
        i = 0
        strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
            replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")

        file = open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+")
        for line in file.readlines():
            i = i + 1
            if weightDict[stratName] in line:
                weightLine.append(i)
    return weightLine


def weightLinesDepthSearch(weightDict, weightLine):
    depthIndicator = '|'
    weightDepthIndex = []
    i = 0
    j = 0
    for stratName in weightDict:
        num = 0
        strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
            replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")

        file = open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+")
        content = file.readlines()
        t = content[weightLine[i] - 1]
        # print(t)
        # print(weightLine[i])
        num = t.count(depthIndicator)
        weightDepthIndex.append(num)
        # print(num)
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

                #print(currDe)
                lengthFeatures = len(featuresList)
                featuresList.append(content[weightLine[j] - i]
                                    .replace("|", "").replace(" ", "").replace("---", "").replace("\n", ""))
                currDe = currDe - 1
            i = i + 1
        j = j + 1
        featureListDict[stratName] = featuresList
    return featureListDict
