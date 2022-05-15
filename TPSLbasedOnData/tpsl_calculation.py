from datetime import datetime, timedelta

from databaseInteraction.dataReceiver import receiveData


def dataPrepStratLevel(stratName, stratData, BuySellPrice, stratTPSLdata, dateFormat, tradeNumList, colNames):

    tradeData = stratData[1][stratName]
    TPSLdata = stratTPSLdata[stratName]

    return tradeData, BuySellPrice, TPSLdata, tradeNumList, colNames, dateFormat, stratName


def tpsl_StratLevel_manager(stratData, colNames, BuySellPrice):
    TPSLdata, tradeNumList = receiveData(stratData)
    dateFormat = "%Y-%m-%d %H:%M:%S"
    stratNameTm = ["(strategy <d180s1 M+>) "]
    #for stratName in stratData[1]:
    for stratName in stratNameTm:
        tpsl_TradeLevel_manager(
            *dataPrepStratLevel(stratName, stratData, BuySellPrice, TPSLdata, dateFormat, tradeNumList, colNames))


# trade data : from strat data by stratName
# BuySellPrice : open close price by overall trade num
# TPSLdata : price action separated by strat name key which have a value of lists with prices for every minute in trade
# tradeNumList : lists num is same as strat has["Coin ", tradeNumOverall]
# colNames : list of column names in csv

def tpsl_TradeLevel_manager(tradeData, BuySellPrice, TPSLdata, tradeNumList, colNames, dateFormat, stratName):
    print(len(TPSLdata))
    indexDict = {}
    for trade in tradeData:
        if trade[1][colNames.index('Coin ')][:-1] not in indexDict.keys():
            if trade[1][colNames.index('Coin ')][:-1] in TPSLdata.keys():
                indexDict[trade[1][colNames.index('Coin ')][:-1]] = 0
    for trade in tradeData:
        overallTradeNum = tradeNumList[tradeData.index(trade)][1]
        coin = trade[1][colNames.index('Coin ')][:-1]  # coin name
        indexTrade = indexDict[coin]  # num of trade in TPSLdata dict TPSLdata->coin-> indexTrade
        openTime = trade[1][colNames.index('BuyDate ')][:-1]  # open time
        closeTime = trade[1][colNames.index('CloseDate ')][:-1]  # close time
        openPrice = BuySellPrice.loc[overallTradeNum, 'BuyPrice ']
        closePrice = BuySellPrice.loc[overallTradeNum, 'SellPrice ']
        profit = trade[1][colNames.index('Profit ')]  # profit
        # print(f'Overall Trade num: {overallTradeNum}'
        #       f'\n coin name = {coin}'
        #       f'\n openTime = {openTime}'
        #       f'\n closeTime = {closeTime}'
        #       f'\n openPrice = {openPrice}'
        #       f'\n closePrice = {closePrice}'
        #       f'\n profit = {profit}')
        tradeCheck(TPSLdata[coin][indexTrade], openTime, closeTime, dateFormat)
           # for el in TPSLdata:
               # print(TPSLdata[el])
        indexDict[coin] = indexDict[coin] + 1


def tradeCheck(priceActionData, openTime, closeTime, dateFormat):
    tradeDur = (datetime.strptime(closeTime, dateFormat) - datetime.strptime(openTime, dateFormat))
    if priceActionData is not None:
        print('============================')
        print(f'\n openTime = {openTime}'
              f'\n closeTime = {closeTime}'
              f'\ntradeDur = {tradeDur}')

        startData = priceActionData[0].klinevaluetimebuy
        endData = priceActionData[-1].klinevaluetimeclose
        print(f'\n openTime Data = {startData}'
              f'\n closeTime Data = {endData}'
              f'\ndataDur = {endData - startData}')
    if (datetime.strptime(closeTime, dateFormat) - datetime.strptime(openTime, dateFormat)) > timedelta(minutes=1):
        if priceActionData is not None:
            if len(priceActionData) >= 1:
                return True
