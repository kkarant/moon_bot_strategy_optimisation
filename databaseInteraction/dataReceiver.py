from databaseInteraction.dbKlinesInfo import receiveDataFromDB, connectionDB


def receiveData(stratData):
    tradeNumList = []
    stratTPSLdata = {}
    dateFormat = "%Y-%m-%d %H:%M:%S"
    cur, conn = connectionDB()
    # for stratName in stratData[1]:
    #     # stratDict[stratName] = []
    #     if stratData[1][stratName].__len__() > 100:
    #         tradeDict = {}
    #         for trade in stratData[1][stratName]:
    #             tradeDict[trade[1]["Coin "][:-1]] = receiveDataFromDB(trade, dateFormat, cur, conn)
    #         filteredTradeDict = {k: v for k, v in tradeDict.items() if v is not None and v}
    #         stratTPSLdata[stratName] = filteredTradeDict
    tradeDict = {}
    i = 0
    for trade in stratData[1]["(strategy <d180s1 M+>) "]:
        tradeDict[trade[1]["Coin "][:-1]] = []
    for trade in stratData[1]["(strategy <d180s1 M+>) "]:
        tradeDict[trade[1]["Coin "][:-1]].append(receiveDataFromDB(trade, dateFormat, cur, conn))
        tradeNumList.append([trade[1]["Coin "][:-1], trade[0]])
    filteredTradeDict = {k: v for k, v in tradeDict.items() if v is not [None] and v}
    stratTPSLdata["(strategy <d180s1 M+>) "] = filteredTradeDict
    conn.close()
    return stratTPSLdata, tradeNumList
