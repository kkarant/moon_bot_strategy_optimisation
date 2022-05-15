from datetime import datetime, timedelta

from databaseInteraction.dataReceiver import receiveData


def tpslPredictManager(stratData, colNames, BuySellPrice):
    stratTPSLdata, tradeNumList = receiveData(stratData)
    # print(stratTPSLdata)
    dateFormat = "%Y-%m-%d %H:%M:%S"
    for stratName in stratTPSLdata:
        analysisData = stratTPSLdata[stratName]
        tradeIterationTS(analysisData, stratData, stratName, colNames, tradeNumList, BuySellPrice, dateFormat)


def tradeIterationTS(analysisData, stratData, stratName, colNames, tradeNumList, BuySellPrice, dateFormat):
    TpSLList = []
    indexDict = {}
    minusCoins = {}
    # print(tradeNumList)

    for trade in stratData[1][stratName]:
        if trade[1][colNames.index('Coin ')][:-1] not in indexDict.keys():
            if trade[1][colNames.index('Coin ')][:-1] in analysisData.keys():
                indexDict[trade[1][colNames.index('Coin ')][:-1]] = 0
                minusCoins[trade[1][colNames.index('Coin ')][:-1]] = 0

    for trade in stratData[1][stratName]:
        overallTradeNum = tradeNumList[stratData[1][stratName].index(trade)][1]
        coin = trade[1][colNames.index('Coin ')][:-1]  # coin name
        indexTrade = indexDict[coin]

        openTime = trade[1][colNames.index('BuyDate ')][:-1]  # open time
        closeTime = trade[1][colNames.index('CloseDate ')][:-1]  # close time
        openPrice = BuySellPrice.loc[overallTradeNum, 'BuyPrice ']
        closePrice = BuySellPrice.loc[overallTradeNum, 'SellPrice ']
        profit = trade[1][colNames.index('Profit ')]  # profit

        minusCoins = minusCoinsCounter(coin, profit, minusCoins)

        print(f'For {coin} open Price = {openPrice}, close Price = {closePrice}, '
              f'trade len ={datetime.strptime(closeTime, dateFormat) - datetime.strptime(openTime, dateFormat)}'
              f'openTime = {openTime}, closeTime = {closeTime}')

        if coin in analysisData.keys():
            if len(analysisData[coin]) >= 1:
                if analysisData[coin][indexTrade] is not None:
                    if tradeIsNormal(openTime, closeTime, dateFormat, minusCoins, coin, len(stratData[1][stratName])):
                        if (res := optimalTSLtrade(analysisData[coin][indexTrade], profit, openPrice, closePrice)) != 1:
                            TpSLList.append(res)
        indexDict[coin] = indexDict[coin] + 1

    optimalTSLstrat(TpSLList, stratData, stratName)


def minusCoinsCounter(coin, profit, minusCoins) -> dict:
    if profit < 0:
        minusCoins[coin] += 1
    if profit > 0:
        minusCoins[coin] -= 1
    return minusCoins


def tradeIsNormal(openTime, closeTime, dateFormat, minusCoins, coin, lenStratData):
    if (datetime.strptime(closeTime, dateFormat) - datetime.strptime(openTime, dateFormat)) > timedelta(minutes=1):
        return True


def optimalTSLtrade(analysisData, profit, openPrice, closePrice):
    minutePriceAction = {}
    print('==============================================')
    print(f'Open price = {openPrice} close price = {closePrice}')
    print(f'profit= {profit}')
    # print(analysisData)

    for el in analysisData:
        if el.klinevaluetimebuy not in minutePriceAction:
            minutePriceAction[el.klinevaluetimebuy] = [float(el.klinevaluehigh), float(el.klinevaluelow)]
    highestPrice = 0
    lowestPrice = 5000

    for minute in minutePriceAction:
        # print(minutePriceAction[minute])
        highestPrice = max(minutePriceAction[minute][0], highestPrice)
        lowestPrice = min(minutePriceAction[minute][1], lowestPrice)

    if highestPrice != 50000 and lowestPrice != 0:
        highestPercent = (highestPrice - openPrice) / openPrice * 100 * 20
        lowestPercent = (lowestPrice - openPrice) / openPrice * 100 * 20
        realPercent = (closePrice - openPrice) / openPrice * 100 * 20

        print(f'For highest price = {highestPrice}, profit = {highestPercent},'
              f'\nFor lowest price = {lowestPrice}, profit = {lowestPercent}, '
              f'\nreal profit  = {realPercent}')
        return [highestPercent, highestPrice, lowestPercent, lowestPrice]

    else:
        print(f'Error, no data')
        return 1


def optimalTSLstrat(TpSLList, stratData, stratName):
    overallHighpercent = 0
    overallLowpercent = 0
    print(len(stratData[1][stratName]))
    for el in TpSLList:
        if el[0] < 50:
            overallHighpercent += el[0]
        if el[2] > -50:
            overallLowpercent += el[2]

    tmpTake = overallHighpercent / len(TpSLList)
    tmpStop = overallLowpercent / len(TpSLList)
    print(f'optimal take = {tmpTake}, optimal stop = {tmpStop}')
