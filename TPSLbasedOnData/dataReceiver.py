from databaseInteraction.dbKlinesInfo import receiveDataFromDB


def receiveData(stratData):
    stratDict = {}
    dateFormat = "%Y-%m-%d %H:%M:%S"
    for stratName in stratData[1]:
        #stratDict[stratName] = []
        if stratData[1][stratName].__len__() > 10:
            for trade in stratData[1][stratName]:
                receiveDataFromDB(trade, dateFormat)
