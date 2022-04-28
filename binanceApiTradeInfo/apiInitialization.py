from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager, exceptions
from datetime import datetime, timedelta
from calendar import monthrange

# import BinanceAPIException, BinanceRequestException, NotImplementedException
from databaseInteraction.dbKlinesInfo import dbAddKline, dbInit


def clientInit():
    api_key = "InpLPIyMKvx0qNAeCFCCxBJczLxSU7snqfzZfGHlcriFUxlo2Sinr1JvVUKpChx1"
    api_secret = "CHmWXVTNhX4o0YL790vpKezFykXerCsCqvcrk3xiZCjzB1mCL7detkTUUpl0Hm7y"
    client = Client(api_key, api_secret)
    res = client.get_exchange_info()
    print(client.response.headers)
    return client


def getKlinesScript(coinName, buy, close, client):
    dataFromKlines = []
    klines = client.get_historical_klines(coinName, Client.KLINE_INTERVAL_1MINUTE, str(buy), str(close))
    # print(klines)
    for el in klines:
        dataFromKlines = [el[2], el[3], el[0], el[6]]
        dbAddKline(coinName, dataFromKlines)

    print(coinName)
    print(dataFromKlines)

    return dataFromKlines


def getDateOfTradesToReceive(stratData, client):
    # stratData -> 1 -> stratName -> iterate over trades -> 1 -> BuyDate \ CloseDate
    tmpList = []
    tradeInfoList = []
    tradesInfoDict = {}
    optimisedCoins = {}
    dateFormat = "%Y-%m-%d %H:%M:%S"
    if client.get_system_status()["status"] == 0:
        for stratName in stratData[1]:
            for trade in stratData[1][stratName]:
                buyDate = trade[1]['BuyDate '][:-1]
                closeDate = trade[1]['CloseDate '][:-1]
                coinName = str(trade[1]['Coin '][:-1])
                buyDateConverted = datetime.strptime(buyDate, dateFormat)
                closeDateConverted = datetime.strptime(closeDate, dateFormat)

                tmpBuyDate = datetime.strptime(str(buyDateConverted)[:-2] + "00", dateFormat)
                tmpCloseDate = closeDateConverted + timedelta(minutes=1)
                tmpCloseDate = datetime.strptime(str(tmpCloseDate)[:-2] + "00", dateFormat)
                # print('Original buy date: ' + buyDateConverted.strftime(dateFormat)
                #       + ', converted to: ' + str(tmpBuyDate))
                # print('Original close date: ' + closeDateConverted.strftime(dateFormat)
                #       + ', converted to: ' + str(tmpCloseDate))
                # if coinName in coinsDict:
                #     if coinsDict[coinName][0] == tmpBuyDate:
                #         if coinsDict[coinName][1] == tmpCloseDate:
                #             ...
                # else:
                #     getKlinesScript(tmpBuyDate, tmpCloseDate, trade, client, coinsDict, coinName)
                tmpList.append(coinName)
                tmpList.append(tmpBuyDate)
                tmpList.append(tmpCloseDate)
                tradeInfoList.append(tmpList)
                tmpList = []

                if coinName not in optimisedCoins:
                    optimisedCoins[coinName] = [tmpBuyDate, tmpCloseDate]
                elif coinName in optimisedCoins:
                    if tmpBuyDate < optimisedCoins[coinName][0]:
                        optimisedCoins[coinName][0] = tmpBuyDate
                    if tmpCloseDate > optimisedCoins[coinName][1]:
                        optimisedCoins[coinName][1] = tmpCloseDate

            tradesInfoDict[stratName] = tradeInfoList
            tradeInfoList = []
        # print(optimisedCoins)
        # dbInit(optimisedCoins)
        for coin in optimisedCoins:
            buy = optimisedCoins[coin][0]
            close = optimisedCoins[coin][1]
            coinName = str(coin) + "USDT"
            getKlinesScript(coinName, buy, close, client)

    else:
        print('system maintenance')
        return 1
