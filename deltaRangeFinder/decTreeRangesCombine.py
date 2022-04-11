

def findStrFile(strF, startIndex, file):
    # opening a text file
    # file1 = open(str(file), "r")
    line = ''
    listFoundStr = []
    index = 0
    for line in file:
        index = index + 1
        if line.find(strF) != -1:
            listFoundStr.append(index)
            listFoundStr.append(line.find(strF))
            return listFoundStr


def decoder(textRep, stratData, listOfReqVal):
    featuresDict = {}
    i = 0
    for val in listOfReqVal:
        featuresDict['feature_' + str(i)] = str(val)
        i = i + 1
    i = 0

    for stratName in stratData[1]:
        if stratData[1][stratName].__len__() > 10:
            startOfStratStr = 'Report for ' + stratName
            print(startOfStratStr)
            startIndex = 0
            i = 0
            j = 0
            strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
                replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")
            with open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+") as file:
                while i < stratData[1][stratName].__len__():
                    strF = "weights: [0.00, " + str(i) + ".00] class: Profit"
                    #strF = str("weights: [0.00, 33.00] class: Profit")
                    #print(f"weights: [{i:.2f}, {j:.2f}] class: Profit")

                    results = findStrFile(strF, startIndex, file)
                    if results is not None:
                        print(results)
                    i = i + 1
                i = 0
            file.close()



