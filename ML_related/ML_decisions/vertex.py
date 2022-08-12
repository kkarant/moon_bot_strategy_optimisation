import requests
from google.cloud import aiplatform
from google.oauth2 import service_account


def endpoint_predict(project: str, location: str, instances: list, endpoint: str):
    aiplatform.init(project=project, location=location)

    endpoint = aiplatform.Endpoint(endpoint)

    prediction = endpoint.predict(instances=instances)
    return prediction


def readTradeFile(fileName):
    with open(fileName) as infile:
        column_names = infile.readline()
        keys = [el[:-1] for el in column_names.split("\t")]
        number_of_columns = len(keys)
        list_of_dictionaries = []
        data = infile.readlines()
        list_of_rows = []
        for row in data:
            list_of_rows.append([(el.strip()) for el in row.split("\t")])
        infile.close()
        for item in list_of_rows:
            row_as_a_dictionary = {}
            for i in range(number_of_columns):
                row_as_a_dictionary[keys[i]] = item[i]
            list_of_dictionaries.append(row_as_a_dictionary)

    return list_of_dictionaries


def live_predict():
    # credentials = service_account.Credentials.from_service_account_file\
    #                 ("D:\\ChromeDownloads\\tradepred-357807-1d8093a8e7dd.json")
    # client = aiplatform.gapic.PredictionServiceClient(credentials=credentials)

    ENDPOINT_ID = "3403489865268985856"
    PROJECT_ID = "tradepred-357807"
    REGION = "asia-northeast1"
    instance = readTradeFile("allData/data/emulator231re.csv")
    prediction = endpoint_predict(PROJECT_ID, REGION, instance, ENDPOINT_ID)
    return prediction


def winrate_test(prediction, df):
    sureTrades = 0
    zeronum = 0
    zeroaccuracy = 0
    accurate = 0
    nl = 0
    missedGoodTrades = 0
    zeroNumPred = 0
    oneNumPred = 0

    true_plus = 0
    pred_plus = 0
    true_minus = 0
    pred_minus = 0
    correct_plus = 0
    correct_minus = 0

    for index, row in df.iterrows():
        trade_pred = -1

        if float(row['Profit ']) <= 0:
            trade = 0
            true_minus += 1
        elif float(row['Profit ']) > 0:
            trade = 1
            true_plus += 1
        zero = prediction[0][index]["scores"][0]
        one = prediction[0][index]["scores"][1]

        if zero > one:
            trade_pred = 0
            pred_minus += 1
        elif zero < one:
            trade_pred = 1
            pred_plus += 1

        if trade == 0 and trade_pred == 0:
            correct_minus += 1
        if trade == 1 and trade_pred == 1:
            correct_plus += 1

        if trade_pred == 1:
            nl += float(row['Profit '])
        elif trade_pred == 0:
            nl -= 2
        elif trade_pred == -1:
            nl += float(row['Profit '])
        # realNL += float(row['Profit '])

    print(f'\nNumber of trades = {true_plus + true_minus}\n'
          f'true_plus = {true_plus}, pred_plus = {pred_plus}, plus accuracy = {pred_plus/true_plus*100}\n'
          f'true_minus = {true_minus}, pred_minus = {pred_minus}, minus accuracy = {pred_minus/true_minus*100}\n')


