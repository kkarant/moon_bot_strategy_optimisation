import pandas as pd


def remake_file(file_path='all_data/data/allTradesSet.csv'):
    badCols = ['Coin ', 'BuyDate ', 'CloseDate ', 'Quantity ', 'BuyPrice ',
               'SellPrice ', 'Spent USDT ', 'Gained USDT ', 'ProfitUSDT ', 'SellReason ',
               'bvsv ', 'PriceBug ', 'Vd1m ', 'H. Vol ', 'D. Vol']
    df = pd.read_csv(file_path, sep="\t", header=None)
    df.columns = ['Coin ', 'BuyDate ', 'CloseDate ', 'Quantity ', 'BuyPrice ', 'SellPrice ', 'Spent USDT ',
                  'Gained USDT ', 'ProfitUSDT ', 'Profit ', 'ChannelName ', 'SellReason ', 'dBTC ', 'd24BTC ',
                  'dMarket ',
                  'dM24 ', 'bvsv ', 'dBTC5m ', 'Pump1H ', 'Dump1H ', 'd24h ', 'd3h ', 'd1h ', 'd15m ', 'd5m ', 'd1m ',
                  'dBTC1m ', 'PriceBug ', 'Vd1m ', 'H. Vol ', 'D. Vol']

    for col in badCols:
        df.drop(col, inplace=True, axis=1)
    df = df.dropna()
    df.drop(df.index[df['ChannelName '] == '(strategy <d180s1.2 M+ FILTERS>) '], inplace=True)
    df.drop(df.index[df['ChannelName '] == '(strategy <d120s1.2 M+ FILTERS>) '], inplace=True)
    df.drop(df.index[df['ChannelName '] == '(strategy <d120s1.5 M+ FILTERS >) '], inplace=True)
    df.drop(df.index[df['ChannelName '] == '(strategy <d150s1.2 M+ FILTERS>) '], inplace=True)
    df['Profit '] = df['Profit '].apply(lambda x: 0 if float(x[:-2]) <= 0 else 1)
    df.to_csv('all_data/data/allTradesForModel..csv', sep=",")
