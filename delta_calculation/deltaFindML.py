import os
import shutil
from io import StringIO

import pandas as pd
import pydotplus
from IPython.display import Image
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_graphviz, export_text

from strategy_statistics.strategyStatistics import timeInTradeCalc
from supportingFunctions import decorator


def getProfit(stratData, stratName):  # execution  time OK
    tempListOProfit = []
    classification = []
    el = 0
    while el < stratData[1][stratName].__len__():  # el is number of trades in strategy
        tProfit = int(stratData[1][stratName][el][1][6])
        # tempListOProfit.append(tProfit)
        if tProfit > 0.5:
            classification.append('Profit')
        elif tProfit < 0.5:
            classification.append('Loss')
        el = el + 1
    return tempListOProfit, classification


def dataSetInsert(stratData, stratName, val, colNames):
    # returns dataframe with 1 col of time ans 2nd col of val values
    # tempListOProfit = getProfit(stratData, stratName)[0]
    classification = getProfit(stratData, stratName)[1]
    valList = []
    timeList = []
    el = 0
    index = colNames.index(val)
    while el < stratData[1][stratName].__len__():
        # тут по порядку для каждой сделки все данные listOfReqVal
        valList.append(stratData[1][stratName][el][1][int(index)])
        timeList = timeInTradeCalc(stratData, colNames)[1][stratName]
        el = el + 1
    el = 0
    dfDict = {str(val): valList, 'tradeTime': timeList, 'classification': classification}
    df = pd.DataFrame(dfDict)
    return df


# SVC algorithm - too slow, not for out situation def analysisSCV(stratData, colNames):
# listOfReqVal = ['dBTC ',
# 'd24BTC ', 'dMarket ', 'dM24 ', 'bvsv ', 'dBTC5m ', 'Pump1H ', 'Dump1H ', 'd24h ', 'd3h ', 'd1h ', 'd15m ', 'd5m ',
# 'd1m ', 'dBTC1m ', 'Vd1m ']
#
#     for stratName in stratData[1]:
#         for val in listOfReqVal:
#             df = dataSetInsert(stratData, stratName, val, colNames)
#             training_set, test_set = train_test_split(df, test_size=0.2, random_state=1)
#             X_train = training_set.iloc[:, 0:2].values
#             Y_train = training_set.iloc[:, 2].values
#             X_test = test_set.iloc[:, 0:2].values
#             Y_test = test_set.iloc[:, 2].values
#
#             classifier = SVC(kernel='rbf', random_state=1)
#             classifier.fit(X_train, Y_train)
#
#             Y_pred = classifier.predict(X_test)
#             test_set["Predictions"] = Y_pred
#
#             le = LabelEncoder()
#             Y_train = le.fit_transform(Y_train)
#             classifier = SVC(kernel='rbf', random_state=1)
#             classifier.fit(X_train, Y_train)
#
#             plt.figure(figsize=(7, 7))
#             X_set, y_set = X_train, Y_train
#             X1, X2 = np.meshgrid(np.arange(start=X_set[:, 0].min() - 1, stop=X_set[:, 0].max() + 1, step=0.01),
#                                  np.arange(start=X_set[:, 1].min() - 1, stop=X_set[:, 1].max() + 1, step=0.01))
#             plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape), alpha=0.75,
#                          cmap=ListedColormap(('black', 'white')))
#             plt.xlim(X1.min(), X1.max())
#             plt.ylim(X2.min(), X2.max())
#             for i, j in enumerate(np.unique(y_set)):
#                 plt.scatter(X_set[y_set == j, 0], X_set[y_set == j, 1], c=ListedColormap(('red', 'orange'))(i), label=j)
#             plt.title(str(val))
#             plt.xlabel('Value of ' + str(val))
#             plt.ylabel('Time')
#             plt.legend()
#             plt.show()


def dataSetForDecisionTree(stratData, stratName, listOfReqVal, colNames):
    valList = []
    valDict = {}
    el = 0
    classification = getProfit(stratData, stratName)[1]

    for val in listOfReqVal:
        index = colNames.index(val)
        while el < stratData[1][stratName].__len__():
            # тут по порядку для каждой сделки все данные listOfReqVal
            valList.append(stratData[1][stratName][el][1][int(index)])
            el = el + 1
        el = 0
        valDict[str(val)] = valList
        valList = []
    valDict['classification'] = classification
    df = pd.DataFrame(valDict)
    return df


def decisionTreeVisualisation(stratName, listOfReqVal, clf):
    dot_data = StringIO()
    export_graphviz(clf, out_file=dot_data,
                    filled=True, rounded=True,
                    special_characters=True, feature_names=listOfReqVal, class_names=['0', '1'])
    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
    strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
        replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")
    fileName = 'DecisionTree' + strName + '.png'
    graph.write_png(fileName)
    Image(graph.create_png())

    dst_dir = 'decisionTreeReports'
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    try:
        os.remove(dst_dir + "/" + fileName)
    except OSError as e:
        print("Error: %s : %s" % (fileName, e.strerror))

    shutil.move(fileName, dst_dir)


# def decisionTreeVisu(stratName, listOfReqVal, clf, X, y):
#
#     viz = dtreeviz(clf, X, y,
#                    target_name="target",
#                    feature_names=listOfReqVal)
#     print(viz)

def decisionTreeTextReport(clf, stratName):
    textReport = export_text(clf, show_weights=True)
    strName = str(stratName).replace(" ", "").replace("(", "").replace(")", "").replace(">", ""). \
        replace("<", "").replace("-", "_minus").replace("+", "_plus").replace("st", "St")
    with open('allData/decisionTreeTextReport/reportDecTree' + str(strName) + '.txt', "w+") as file:
        file.truncate()
        file.writelines(textReport)
        file.write('\n')
    file.close()
    return file


@decorator
def decisionTree(stratData, colNames):
    listOfReqVal = ['dBTC ', 'd24BTC ', 'dMarket ', 'dM24 ', 'bvsv ', 'dBTC5m ', 'Pump1H ', 'Dump1H ', 'd24h ', 'd3h ',
                    'd1h ', 'd15m ', 'd5m ', 'd1m ', 'dBTC1m ', 'Vd1m ']

    for stratName in stratData[1]:
        if stratData[1][stratName].__len__() > 10:
            df = dataSetForDecisionTree(stratData, stratName, listOfReqVal, colNames)
            X = df[listOfReqVal]  # Features
            y = df['classification']  # Target variable
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
            clf = DecisionTreeClassifier()
            # Train Decision Tree Classifer
            clf = clf.fit(X_train, y_train)
            # Predict the response for test dataset
            y_pred = clf.predict(X_test)
            # print("For strategy {0} accuracy: {1:.2f}".format(stratName, metrics.accuracy_score(y_test, y_pred)))
            # decisionTreeVisualisation(stratName, listOfReqVal, clf)
            textRep = decisionTreeTextReport(clf, stratName)
        # else:
        # print(f"Not enough data for {stratName}")
