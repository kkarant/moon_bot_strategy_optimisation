
def findStrFile(strF, startIndex, file):
    index = 0
    lines = file.readlines()
    for line in lines:
        # print('in', line, sep='\n')
        # print('To', strF, sep='\n')
        # print(strF in line)

        index = index + 1
        if line.__contains__(strF):
            return index
    return -1


def decoder(stratData, listOfReqVal):
    featuresDict = {}
    i = 0
    for val in listOfReqVal:
        featuresDict['feature_' + str(i)] = str(val)
        i = i + 1

    for stratName in stratData[1]:
        if stratData[1][stratName].__len__() > 10:
            print(stratName)
            startIndex = 0
            strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
                replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")

            # with open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+") as file:
            file = open('decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "r+")
            for line in file.readlines():
                i = 0
                while i < len(stratData[1][stratName]) + 1:
                    strF = f"weights: [0.00, {i:.2f}] class: Profit"
                    # strF_2 = str("weights: [0.00, 33.00] class: Profit")
                    # print(f"weights: [{i:.2f}, {j:.2f}] class: Profit")
                    # print(strF)
                    results = findStrFile(strF, startIndex, file)
                    if results is not None and results != -1:
                        print("Index of found " + strF + " is " + str(results))
                    i = i + 1
            file.close()



