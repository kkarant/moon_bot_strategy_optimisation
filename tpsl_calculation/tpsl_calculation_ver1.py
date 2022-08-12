from datetime import datetime, timedelta

import pytz
from API_DB_pipeline.db_interaction.dataReceiver import receiveData

utc = pytz.UTC


def dataPrepStratLevel(stratName, stratData, BuySellPrice, stratTPSLdata, dateFormat, tradeNumList, colNames):
    tradeData = stratData[1][stratName]
    TPSLdata = stratTPSLdata[stratName]
    return tradeData, BuySellPrice, TPSLdata, tradeNumList, colNames, dateFormat, stratName


def tpsl_StratLevel_manager(stratData, colNames, BuySellPrice):
    TPSLdata, tradeNumList = receiveData(stratData)
    tradeNumListLastNum = 0
    optimalTPSLstrat = {}
    dateFormat = "%Y-%m-%d %H:%M:%S"
    for stratName in stratData[1]:
        optimalPHighO, optimalPLowO = tpsl_TradeLevel_manager(*dataPrepStratLevel(stratName, stratData, BuySellPrice,
                                                                                  TPSLdata, dateFormat, tradeNumList,
                                                                                  colNames))
        if optimalPHighO and optimalPLowO != "err":
            optimalTPSLstrat[stratName] = [optimalPHighO, optimalPLowO]
            print(stratName)
            print(' optimal TP %.3f \n optimal SL %.3f ' % (optimalPHighO, optimalPLowO))
    return optimalTPSLstrat


# trade data : from strat data by stratName
# BuySellPrice : open close price by overall trade num
# TPSLdata : price action separated by strat name key which have a value of lists with prices for every minute in trade
# tradeNumList : lists num is same as strat has["Coin ", tradeNumOverall]
# colNames : list of column names in csv


def tpsl_TradeLevel_manager(tradeData, BuySellPrice, TPSLdata, tradeNumList,
                            colNames, dateFormat, stratName):
    highestPercentOverall = 0
    lowestPercentOverall = 0
    indexDict = {}
    for trade in tradeData:
        if trade[1][colNames.index('Coin ')][:-1] not in indexDict.keys():
            if trade[1][colNames.index('Coin ')][:-1] in TPSLdata.keys():
                indexDict[trade[1][colNames.index('Coin ')][:-1]] = 0
    numOfNormalTrades = 0
    for trade in tradeData:
        # overallTradeNum = tradeNumList[tradeData.index(trade) + tradeNumListLastNum][1]
        # print(list(filter(lambda x: x[0] == trade, tradeNumList)))
        # overallTradeNum = filter(lambda x: x[0].equals(other=trade[1]), tradeNumList)
        overallTradeNum = trade[0]
        # print(overallTradeNum)
        coin = trade[1][colNames.index('Coin ')][:-1]  # coin name
        indexTrade = indexDict[coin]  # num of trade in TPSLdata dict TPSLdata->coin-> indexTrade
        openTime = trade[1][colNames.index('BuyDate ')][:-1]  # open time
        closeTime = trade[1][colNames.index('CloseDate ')][:-1]  # close time
        openPrice = BuySellPrice.loc[overallTradeNum, 'BuyPrice ']
        closePrice = BuySellPrice.loc[overallTradeNum, 'SellPrice ']
        profit = trade[1][colNames.index('Profit ')]  # profit

        if tradeCheck(TPSLdata[coin][indexTrade], openTime, closeTime, dateFormat):
            numOfNormalTrades += 1
            highestPercent, lowestPercent = rrCalculator(TPSLdata[coin][indexTrade], openPrice, closePrice)
            highestPercentOverall = highestPercentOverall + highestPercent
            lowestPercentOverall = lowestPercentOverall + lowestPercent
        indexDict[coin] = indexDict[coin] + 1

    # print(numOfNormalTrades)
    if numOfNormalTrades >= 1:
        return highestPercentOverall / numOfNormalTrades, lowestPercentOverall / numOfNormalTrades
    else:
        return 'err', 'err'


def tradeCheck(priceActionData, openTime, closeTime, dateFormat):
    tradeDur = (datetime.strptime(closeTime, dateFormat) - datetime.strptime(openTime, dateFormat))
    openTimeDT = utc.localize(datetime.strptime(openTime, dateFormat))
    closeTimeDT = utc.localize(datetime.strptime(closeTime, dateFormat))
    if priceActionData is not None and len(priceActionData) >= 1:
        if (closeTimeDT - openTimeDT) > timedelta(minutes=1):
            if len(priceActionData) >= 1:
                lasttimedata = utc.localize(datetime.strptime(datetime.fromtimestamp(int(priceActionData[-1][1]) /
                                                                                     1000).strftime(
                    '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
                firsttimedata = utc.localize(datetime.strptime(datetime.fromtimestamp(int(priceActionData[0][1]) /
                                                                                      1000).strftime(
                    '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
                dataDur = lasttimedata - firsttimedata
                # print(openTimeDT, closeTimeDT)
                # print(firsttimedata, lasttimedata)

                if dataDur > tradeDur:
                    if firsttimedata <= openTimeDT and \
                            lasttimedata >= closeTimeDT:
                        return True


def rrCalculator(priceActionData, openPrice, closePrice):
    maxH = -1
    minL = 99999
    for el in priceActionData:
        maxH = max(float(maxH), float(el[0]))
        minL = min(float(minL), float(el[0]))
    highestPercent = (maxH - openPrice) / openPrice * 100 * 20
    lowestPercent = (minL - openPrice) / openPrice * 100 * 20
    # print(highestPercent)
    # print(lowestPercent)
    # print(f'===================================='
    # f'\nhighestPercent = {highestPercent}'
    # f'\nlowestPercent = {lowestPercent}')

    return highestPercent, lowestPercent
