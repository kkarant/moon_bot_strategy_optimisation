

def findStrFile(startOfSearchIndex, strF):
    # opening a text file
    file1 = open('report/reportDecTree.txt', "r")

    index = startOfSearchIndex


    # Loop through the file line by line
    for line in file1:
        index = index + 1
        if strF in line:
            startOfSearchIndex = index
            break

    file1.close()
    return index, startOfSearchIndex


def decoder(textRep, stratData, listOfReqVal):
    featuresDict = {}
    startEndDict = {}
    i = 0
    for val in listOfReqVal:
        featuresDict['feature_' + str(i)] = str(val)
        i = i + 1
    i = 0
    endOfStratStr = '==============================================================================='
    #endTmpIndex = 0
    for stratName in stratData[1]:
        if stratData[1][stratName].__len__() > 10:

            startOfStratStr = 'Report for ' + stratName
            #findStrFile(startTmpIndex, startOfStratStr)[1]
            startTmpIndex = findStrFile(0, startOfStratStr)[0]
            endTmpIndex = findStrFile(startTmpIndex, endOfStratStr)[0] - 2
            print(startTmpIndex)
            print(endTmpIndex)


