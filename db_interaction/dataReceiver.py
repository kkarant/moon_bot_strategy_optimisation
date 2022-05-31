from db_interaction.dbKlinesInfo import receiveDataFromDB, connectionDB
from supportingFunctions import decorator


def receiveData(stratData):
    tradeNumList = []
    stratTPSLdata = {}
    dateFormat = "%Y-%m-%d %H:%M:%S"
    cur, conn = connectionDB()
    stratList = ["(strategy <d180s1 M+>) "]
    for stratName in stratList:
        tradeDict = {}
        for trade in stratData[1][stratName]:
            tradeDict[trade[1]["Coin "][:-1]] = []
        for trade in stratData[1][stratName]:
            tradeDict[trade[1]["Coin "][:-1]].append(receiveDataFromDB(trade, dateFormat, cur, conn))
            tradeNumList.append([trade[1], trade[0]])
        stratTPSLdata[stratName] = tradeDict
    conn.close()
    return stratTPSLdata, tradeNumList
