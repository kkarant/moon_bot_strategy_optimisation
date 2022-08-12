from datetime import datetime

import requests

from service_functions.supportingFunctions import decorator


def test_request_corect_price():
    responseSpot = requests.get(f"https://api.binance.com/api/v3/klines?symbol=ZILUSDT&interval=1m&limit=10")
    date = datetime.fromtimestamp(responseSpot.json()[0][0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Spot {date}"
          f"\n High = {responseSpot.json()[0][2]}"
          f"\n Low = {responseSpot.json()[0][3]}")
    responseFutures = requests.get(f"https://fapi.binance.com/fapi/v1/klines?symbol=ZILUSDT&interval=1m&limit=10")
    date = datetime.fromtimestamp(responseFutures.json()[0][0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Futures {date}"
          f"\nHigh = {responseFutures.json()[0][2]}"
          f"\n Low = {responseFutures.json()[0][3]}")
    responseMark = requests.get(f"https://fapi.binance.com/fapi/v1/markPriceKlines?symbol=ZILUSDT&interval=1m&limit=10")
    date = datetime.fromtimestamp(responseMark.json()[0][0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Mark {date}"
          f"\nHigh = {responseMark.json()[0][2]}"
          f"\n Low = {responseMark.json()[0][3]}")
    responseIndex = requests.get(f"https://fapi.binance.com/fapi/v1/indexPriceKlines?pair=ZILUSDT&interval=1m&limit=10")
    date = datetime.fromtimestamp(responseIndex.json()[0][0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Index {date}"
          f"\nHigh = {responseIndex.json()[0][2]}"
          f"\n Low = {responseIndex.json()[0][3]}")


@decorator
def test_request_aggTrades():
    symbol = 'RUNEUSDT'
    startTime = int(datetime.strptime('2022-04-18 23:29:51', "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
    endTime = int(datetime.strptime('2022-04-18 23:33:53', "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
    payload = {'symbol': symbol, 'startTime': startTime, 'endTime': endTime}
    response = requests.get(f"https://fapi.binance.com/fapi/v1/aggTrades", params=payload)
    tradepriceAction = []
    TPSLCalculator(select_price(response.json(), tradepriceAction), 8.30500000)
    print(tradepriceAction)


def select_price(responseJSON, tradepriceAction):
    for el in responseJSON:
        tradepriceAction.append([el["p"], el["T"]])

    return tradepriceAction


def TPSLCalculator(tradepriceAction, openPrice):
    maxH = -1
    minL = 99999
    for el in tradepriceAction:
        maxH = max(float(maxH), float(el[0]))
        minL = min(float(minL), float(el[0]))
    highestPercent = (maxH - openPrice) / openPrice * 100
    lowestPercent = (minL - openPrice) / openPrice * 100
    print(highestPercent)
    print(lowestPercent)

# RUNE 	Buy 2022-04-18 23:29:51 	close 2022-04-18 23:33:53  buy	8.30500000 sell	8.32500000
# GET /fapi/v1/aggTrades
# response
# [
#   {
#     "a": 26129,         // Aggregate tradeId
#     "p": "0.01633102",  // Price
#     "q": "4.70443515",  // Quantity
#     "f": 27781,         // First tradeId
#     "l": 27781,         // Last tradeId
#     "T": 1498793709153, // Timestamp
#     "m": true,          // Was the buyer the maker?
#   }
# ]
# parameters
# symbol	STRING	YES
# fromId	LONG	NO	ID to get aggregate trades from INCLUSIVE.
# startTime	LONG	NO	Timestamp in ms to get aggregate trades from INCLUSIVE.
# endTime	LONG	NO	Timestamp in ms to get aggregate trades until INCLUSIVE.
# limit	    INT	    NO	Default 500; max 1000.
