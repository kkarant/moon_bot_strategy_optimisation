# moon_bot_strategy_optimisation

# Introduction
Main goal of this project is correction of strategies that are given in trading terminal MOON BOT to increase their efficiency.

>  The entire subsequent process is tied to the input file, which contains market data for every trade in some specific period.
> Strategies will be optimized to the type of market, which was when
> trades in the report happened.

Based on the input file, the program will download all necessary price action data for trades, and it will be used in analysis. Source of price action data is Binance Futures API. 

    https://fapi.binance.com/fapi/v1/aggTrades

# Output

 - First TXT file with ranges of market parameters, which are optimal
   for maximum profitability of strategies over a distance. Ranges
   creation is described here.
 - There is also created  a file with data on the optimal Take Profit
   and Stop Loss for each of the strategies separately in order to
   control risk management. TPSL calculation described here.

All these data is calculated only for strategies that have enough trade history, so that the analysis is objective and anomalies in trades do not spoil the statistics and subsequently the obtained parameters.


# Modules



## api_db_pipeline

 - **binance_api** - requests from the Binance exchange, their layout, ordering and optimization.
- **db_interaction** - queries from the database, adding to the database, checking data integrity.
  
## ml_related (additional functionality)
- ML models training, predictions, accuracy tests (local AutoML or  Vertex AI).

## file_interaction 
- generation of reports and import file manipulations

## market_analysis_module
### delta_calculation 
calculation of market parameters ranges using the [Decision Tree Classifier](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html) algorithm. 

![Decision tree for one strategy](https://github.com/kkarant/moon_bot_strategy_optimisation/blob/df377cb44da295c10d5312da76c364fe23c482d1/all_data/report/photo_2022-08-12_18-37-05.jpg)

Every block has its color which varies from red (most negative trades) to blue (most profit trades) and the first row in every block is a column from input data from which we cut some values. And in value line we see [negative trade, positive trade] statistics which pass value cut from first row. 

**After creating this decision trees in TXT format, delta_calculation module parse files and is trying to find a path from top to bottom with the largest number of profitable trades while maintaining the minimum number of negative ones.**
  
### strategy_statistics 
Basic strategy statistics from input file for human interest. Contains data about number of positive and negative trades, average duration, average minus/plus, overall P&L and as outcome can create top of strategies which worked the best in the range of input set.
  
### tpsl_calculoation
 Calculation of optimal take profits and stop losses using self-written logic. 
- **Overall logic**                                                                                                                                                         
TP and SL analysis starts from collecting info for every trade that system thinks is not anomaly. This trade info contains optimal TP and SL for one current trade. Then the algorithm goes to strategy level and creates overall time-series statistics for TP (or SL). This statistics has a length of n seconds, and the n is a length which covers 90% of trades which happened in this strategy. On a length of n seconds, we create 10 sec chunks which summarize the overall value of TP (or SL) which happened in it and divides the value by the number of trades, so it becomes average. 
**And then an algorithm ruled by frequency of closes and average TP (or SL) values decides which value of TP (or SL) should be set from trade open and how it should change with time.**
![Example of TP ](https://github.com/kkarant/moon_bot_strategy_optimisation/blob/456db963f622ef776e4d312a031ada3bad581881/all_data/report/tslalgo.jpg)     
X =timescale (n = 600s), Y = % of profit with x20 leverage.
Red lines mean time ranges of certain TP values, which are displayed as orange crosses.
- **Input for trade analysis (TP or SL)**                                                                                                                                   
Input: entry price, entry time, price action data from the exchange.
The data from the source gives the average price of transactions in intervals of several hundred milliseconds. The interval between the data unit is not constant as the trading on some coins is not so active, but in the vast majority they are constant and not intermittent.

- **Take profit**                                                                                                                                                           
Trades are loaded from the database. We get a list of objects [TIMESTAMP, PRICE]. From the field with the price, we form a signal (roughly speaking, a chart), on which, using the find_peaks function from the SciPy library, we find the peaks of this signal. In the search parameters, we set the condition so that they are not too close to each other.
The resulting peaks are then sorted so that the first one is the largest (we do not swap them, but delete all the peaks before the largest), we also remove duplicates and peaks that are below 3% (20 shoulder) (this is a conditional value, unconditioned by anything, set according to the logic of that the price likes to walk in the range near the entrance, and 3% is just such a range, and in theory profit is missed).
For each remaining peak, we fix the time when it occurred. Time means the number of seconds from the beginning of the trade to the peak, since this measurement format is objective.

- **Stop loss**                                                                                                                                                          
To begin with, as in the calculation of the take, we find the peaks in the chart. But upside down. At the exit - bottom points. Then they go through a sorting process. It consists in classifying bottom points on W & WO. (W-with return, WO - without return).
That is, for each bottom from the list of bottoms, we must determine the maximum that comes after it. We are looking for a maximum in the range from the bottom, which we are now analyzing to the next one, and if there is none, then until the end of the transaction.
If after the onset of the bottom there is a rebound that reaches the conditional point of 3% profit (the same flat level at the entrance that I wrote about earlier), then the bottom is classified as W. If this does not happen, the bottom is recorded as WO. As a result, for the trade we have a list of the approximate form [„W”, „WO”, „WO”, „W”] or [„WO”, „W”]. This entry is further parsed using match case (python 3.10) as a pattern. But before that, there is another important point.
Calculating a specific value is possible only in some patterns, which I call basic. Any other combination (usually longer and more complex) should be broken down into several basic patterns. Usually we get several variations on how a complex pattern can be composed from basic ones. They all need to be solved (calculate), and then find the best one.
It's easier with basic patterns. They can be: W, WO, multipleW, multipleWO, WO|W, WO|multipleW, multipleWO|W, multipleWO|multipleW,
W|WO, W|multipleWO, multipleW|WO, multipleW|multipleWO.
Each of them either has its own formula, or is reduced using other basic patterns. For example, multipleWO|W. We first simplify the first half through an algorithm for such a case, then the general data can be reduced to an answer using a formula in the WO|W pattern.
