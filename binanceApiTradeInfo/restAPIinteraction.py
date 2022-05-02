from datetime import datetime

import requests

from databaseInteraction.dbKlinesInfo import checkIfTableExist, dbAddKline
from supportingFunctions import decorator


@decorator
def single_request(symbol, interval, startTime, endTime) -> dict:
    responseList = {}
    response = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&"
                            f"startTime={startTime}&endTime={endTime}")
    num = 0
    #if response.status_code == 200:
    print(response.json()[0])

    for el in response.json():
        responseList[num] = [el[0], el[2], el[3], el[6]]
        num = num + 1

    return responseList


def apiCallsManager(coinListTransformed):
    for coin in coinListTransformed:
        checkIfTableExist(coin)
    for coin in coinListTransformed:
        symbol = str(coin + "USDT")
        for el in coinListTransformed[coin]:
            startUnix = int(datetime.timestamp(el[0]) * 1000)
            closeUnix = int(datetime.timestamp(el[1]) * 1000)
            print(symbol + " | " + str(startUnix) + " == " + str(closeUnix))
            response = single_request(symbol, "1m", startUnix, closeUnix)
            for num in response:
                dbAddKline(symbol, response[num])


