# moon_bot_strategy_optimisation

## Introduction
Main goal of this project is correction of strategies that are given in trading terminal MOON BOT to increase their efficiency.

>  The entire subsequent process is tied to the input file, which contains market data for every trade in some specific period.
> Strategies will be optimized to the type of market, which was when
> trades in the report happened.

Based on the input file, the program will download all necessary price action data for trades, and it will be used in analysis. Source of price action data is Binance Futures API. 

    https://fapi.binance.com/fapi/v1/aggTrades

## Application output

 - First TXT file with ranges of market parameters, which are optimal
   for maximum profitability of strategies over a distance. Ranges
   creation is described here.
 - There is also created  a file with data on the optimal Take Profit
   and Stop Loss for each of the strategies separately in order to
   control risk management. TPSL calculation described here.

All these data is calculated only for strategies that have enough trade history, so that the analysis is objective and anomalies in trades do not spoil the statistics and subsequently the obtained parameters.


## Application modules
