from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from datetime import datetime

def clientInit():
    api_key = "InpLPIyMKvx0qNAeCFCCxBJczLxSU7snqfzZfGHlcriFUxlo2Sinr1JvVUKpChx1"
    api_secret = "CHmWXVTNhX4o0YL790vpKezFykXerCsCqvcrk3xiZCjzB1mCL7detkTUUpl0Hm7y"
    client = Client(api_key, api_secret)


def getDateOfTradesToReceive(stratData):
    # stratData -> 1 -> stratName -> iterate over trades -> 1 -> BuyDate \ CloseDate
    for stratName in stratData[1]:
        for trade in stratData[1][stratName]:
            #print(trade[1]['BuyDate '])
            buyDate = trade[1]['BuyDate '][:-1]
            closeDate = trade[1]['CloseDate '][:-1]

            buyDateConverted = datetime.strptime(buyDate, "%Y-%m-%d %H:%M:%S")
            closeDateConverted = datetime.strptime(closeDate, "%Y-%m-%d %H:%M:%S")
            if buyDateConverted.strftime('%M') % 5 == 0:
                numOfCline = buyDateConverted.strftime('%M')
            print(buyDateConverted.strftime('%M'))


            hours = ['19:30', '20:10', '20:30', '21:00', '22:00']
            now = datetime.datetime.strptime("20:18", "%H:%M")
            min(hours, key=lambda t: abs(now - datetime.datetime.strptime(t, "%H:%M")))
            #timeForKline =

