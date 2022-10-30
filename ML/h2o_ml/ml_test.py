import h2o
from h2o.automl import H2OAutoML
from sklearn.metrics import mean_absolute_error
from h2o.estimators import H2OGeneralizedLinearEstimator


def h2o_train():
    h2o.init(ip="localhost", port=54323)
    trades = h2o.import_file('all_data/data/2to9JULYdr.txt')
    trades = trades[:, ["Profit ", "dBTC ", "d24BTC ", "dMarket ", "dM24 ",
                        "dBTC5m ", "Pump1H ", "Dump1H ", "d24h ", "d3h ", "d1h ", "d15m ", "d5m ", "d1m ", "dBTC1m "]]
    train, test, valid = trades.split_frame(ratios=[.7, .15])
    x = trades.columns
    y = "Profit "
    x.remove(y)

    aml = H2OAutoML(max_models=20, seed=1)
    aml.train(x=x, y=y, training_frame=train)

    lb = h2o.automl.get_leaderboard(aml, extra_columns="ALL")

    m = aml.get_best_model()

    model_path = h2o.save_model(model=m, path="all_data/models", force=True)
    preds = aml.leader.predict(test)

    print(lb)
    print("========================================")
    print(preds)


def h2o_model_pred():
    h2o.init(ip="localhost", port=54323)
    trades = h2o.import_file('all_data/data/2to9JULYdr.txt')
    trades = trades[:, ["Profit ", "dBTC ", "d24BTC ", "dMarket ", "dM24 ",
                        "dBTC5m ", "Pump1H ", "Dump1H ", "d24h ", "d3h ", "d1h ", "d15m ", "d5m ", "d1m ", "dBTC1m "]]
    # Split the data into Train/Test/Validation with Train having 70% and test and validation 15% each
    train, test, valid = trades.split_frame(ratios=[.7, .15])
    model = h2o.load_model("all_data/models/StackedEnsemble_AllModels_1_AutoML_1_20220724_55651")
    perf = model.model_performance(valid)
    preds = model.predict(test)
    colsCombine_df = test["Profit "].cbind(preds)
    # make plot of profit from test and preds on one plot
    print(model.mae())
    print(colsCombine_df)

