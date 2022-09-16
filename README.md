# moon_bot_strategy_optimisation
Main goal of this project is analysis and corrections of strategies that are given in trading terminal MOON BOT.

It is especially focused on Drops and MoonShot strategies. 
As input we give txt file with report from some period of trading history. It must contain all fields connected with profit of trade, market variables (deltas, etc.)

The entire subsequent process is tied to the input file. Based on the transactions it contains,
API queries are generated for historical data on the Binance exchange. 
Data received via api is stored in a local postgres database or on a remote Amazon RDS database. 
So far, the option with a local database is used, since speed is still a priority, and the amount of data is significant.

Having received all the data necessary for the analysis, the analysis process itself starts. 

Its result is text files with Ranges of market parameters, which are optimally adjusted for maximum profitability of strategies over a distance. A file is also created with data on the optimal Take Profit (closing in plus) and Stop Loss (closing in minus) for each of the strategies separately in order to comply with risk management.
All these data are calculated only for strategies that have enough data so that the analysis is objective and anomalous transactions do not spoil the statistics and subsequently the parameters obtained.


More about analysis modules:

-api_db_pipeline

&nbsp;&nbsp;&nbsp;&nbsp;   -binance_api - requests from the binance exchange, their layout, ordering and optimization
  
&nbsp;&nbsp;&nbsp;&nbsp;   -db_interaction - queries from the database, adding to the database, checking data integrity
  
-ML_related - training of AutoML models, model predictions (local and remote on Vertex AI)

-file_interaction - open input file, generate text reports

-market_analysis_module

&nbsp;&nbsp;&nbsp;&nbsp;   -delta_calculation - calculation of market parameter ranges using the Decision Tree Classifier algorithm. Then the processing of the trees &nbsp;&nbsp;&nbsp;&nbsp;   and the derivation of the optimal ranges from them.
  
&nbsp;&nbsp;&nbsp;&nbsp;   -strategy_statistics base strategy statistics from input file for human evaluation
  
-service_functions - Service functions to evaluate the performance of functions, as well as some pydantic validators (in development)

-tpsl_calculoation - Calculation of optimal take profits and stop losses using self-written logic based on the classification of each transaction and the price          behavior in it. The analysis is carried out from the particular (1 transaction) to the general. That is, the decision is made on the basis of where the largest        number of deals could close in plus in this strategy. For this, data on the price movement during the transaction received from the Binance exchange are used.
