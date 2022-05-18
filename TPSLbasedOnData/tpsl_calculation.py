from datetime import datetime, timedelta
import pytz
from databaseInteraction.dataReceiver import receiveData

utc = pytz.UTC


def dataPrepStratLevel(stratName, stratData, BuySellPrice, stratTPSLdata, dateFormat, tradeNumList, colNames):
    tradeData = stratData[1][stratName]
    TPSLdata = stratTPSLdata[stratName]

    return tradeData, BuySellPrice, TPSLdata, tradeNumList, colNames, dateFormat, stratName


def tpsl_StratLevel_manager(stratData, colNames, BuySellPrice):
    TPSLdata, tradeNumList = receiveData(stratData)
    dateFormat = "%Y-%m-%d %H:%M:%S"
    for stratName in stratData[1]:
        print(tpsl_TradeLevel_manager(
            *dataPrepStratLevel(stratName, stratData, BuySellPrice, TPSLdata, dateFormat, tradeNumList, colNames)))


# trade data : from strat data by stratName
# BuySellPrice : open close price by overall trade num
# TPSLdata : price action separated by strat name key which have a value of lists with prices for every minute in trade
# tradeNumList : lists num is same as strat has["Coin ", tradeNumOverall]
# colNames : list of column names in csv

def tpsl_TradeLevel_manager(tradeData, BuySellPrice, TPSLdata, tradeNumList, colNames, dateFormat, stratName):
    highestPercentOverall = 0
    lowestPercentOverall = 0
    indexDict = {}
    for trade in tradeData:
        if trade[1][colNames.index('Coin ')][:-1] not in indexDict.keys():
            if trade[1][colNames.index('Coin ')][:-1] in TPSLdata.keys():
                indexDict[trade[1][colNames.index('Coin ')][:-1]] = 0
    numOfNormalTrades = 0
    for trade in tradeData:
        overallTradeNum = tradeNumList[tradeData.index(trade)][1]
        coin = trade[1][colNames.index('Coin ')][:-1]  # coin name
        indexTrade = indexDict[coin]  # num of trade in TPSLdata dict TPSLdata->coin-> indexTrade
        openTime = trade[1][colNames.index('BuyDate ')][:-1]  # open time
        closeTime = trade[1][colNames.index('CloseDate ')][:-1]  # close time
        openPrice = BuySellPrice.loc[overallTradeNum, 'BuyPrice ']
        closePrice = BuySellPrice.loc[overallTradeNum, 'SellPrice ']
        profit = trade[1][colNames.index('Profit ')]  # profit

        if tradeCheck(TPSLdata[coin][indexTrade], openTime, closeTime, dateFormat, numOfNormalTrades):
            numOfNormalTrades += 1
            highestPercent, lowestPercent = rrCalculator(TPSLdata[coin][indexTrade], openPrice, closePrice)
            highestPercentOverall = highestPercentOverall + highestPercent
            lowestPercentOverall = lowestPercentOverall + lowestPercent
        indexDict[coin] = indexDict[coin] + 1

    print(numOfNormalTrades)
    return highestPercent/numOfNormalTrades, lowestPercent/numOfNormalTrades


def tradeCheck(priceActionData, openTime, closeTime, dateFormat, numOfNormalTrades):
    tradeDur = (datetime.strptime(closeTime, dateFormat) - datetime.strptime(openTime, dateFormat))
    openTimeDT = utc.localize(datetime.strptime(openTime, dateFormat) - timedelta(hours=4))
    closeTimeDT = utc.localize(datetime.strptime(closeTime, dateFormat) - timedelta(hours=4))
    if priceActionData is not None and len(priceActionData) >= 1:
        startData = priceActionData[0].klinevaluetimebuy
        endData = priceActionData[-1].klinevaluetimeclose
        dataDur = endData - startData
        # print('============================')
        # print(f'\n openTimeDT = {openTimeDT}'
        #       f'\n closeTimeDT = {closeTimeDT}'
        #       f'\n tradeDur = {tradeDur}'
        #       f'\n openTime Data = {startData}'
        #       f'\n closeTime Data = {endData}'
        #       f'\n dataDur = {dataDur}')
    if (closeTimeDT - openTimeDT) > timedelta(minutes=1):
        if priceActionData is not None:
            if len(priceActionData) >= 1:
                dataDur = priceActionData[-1].klinevaluetimeclose - priceActionData[0].klinevaluetimebuy
                if dataDur > tradeDur:
                    if priceActionData[0].klinevaluetimebuy <= openTimeDT and \
                            priceActionData[-1].klinevaluetimeclose >= closeTimeDT:
                        return True


def rrCalculator(priceActionData, openPrice, closePrice):
    maxH = -1
    minL = 99999
    for el in priceActionData:
        maxH = max(float(maxH), float(el.klinevaluehigh))
        minL = min(float(minL), float(el.klinevaluelow))
    highestPercent = (maxH - openPrice) / openPrice * 100
    lowestPercent = (minL - openPrice) / openPrice * 100
    #print(f'===================================='
          #f'\nhighestPercent = {highestPercent}'
          #f'\nlowestPercent = {lowestPercent}')

    return highestPercent, lowestPercent
