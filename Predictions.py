import LSTM
import RF
import SVM
import KNN
import CNN
from numpy import reshape, shape, array
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from os.path import dirname, abspath
from Data_Utils import data_prep, data_reshape, stocks_dict

stocks_file = dirname(abspath(__file__)) + "/Live Data/"


def prediction_distribution(predictions: list, true_labels: list):
    if len(predictions) != len(true_labels):
        raise Exception(f"Decisions are not same length.\nPredictions length is {len(predictions)}\nLabels length is {len(true_labels)}")
    buy_total, sell_total, hold_total = 0, 0, 0
    buy, sell, hold = 0, 0, 0
    buy_fp, sell_fp, hold_fp = 0, 0, 0
    for index in range(len(predictions)):
        if true_labels[index] == 1:
            buy_total += 1
            if predictions[index] == 1:
                buy += 1
            elif predictions[index] == 0:
                hold_fp += 1
            elif predictions[index] == -1:
                sell_fp += 1
        if true_labels[index] == 0:
            hold_total += 1
            if predictions[index] == 0:
                hold += 1
            elif predictions[index] == 1:
                buy_fp += 1
            elif predictions[index] == -1:
                sell_fp += 1
        if true_labels[index] == -1:
            sell_total += 1
            if predictions[index] == -1:
                sell += 1
            elif predictions[index] == 1:
                buy_fp += 1
            elif predictions[index] == 0:
                hold_fp += 1

    if buy_total > 0:
        print(f"Correct Buy Percentage: {100 * buy / buy_total}%")
        print(f"False Positive Buy Percentage: {100 * buy_fp / buy_total}%")
        print(f"Total True Buy Decisions: {buy_total}\n")
    else:
        print("Correct Buy Percentage: N/A")
        print("False Positive Buy Percentage: N/A\n")
    if hold_total > 0:
        print(f"Correct Hold Percentage: {100 * hold / hold_total}%")
        print(f"False Positive Hold Percentage: {100 * hold_fp / hold_total}%")
        print(f"Total True Hold Decisions: {hold_total}\n")
    else:
        print("Correct Hold Percentage: N/A")
        print("False Positive Hold Percentage: N/A\n")
    if sell_total > 0:
        print(f"Correct Sell Percentage: {100 * sell / sell_total}%")
        print(f"False Positive Sell Percentage: {100 * sell_fp / sell_total}%")
        print(f"Total Sell Buy Decisions: {sell_total}\n")
    else:
        print("Correct Sell Percentage: N/A")
        print("False Positive Sell Percentage: N/A\n")


def get_features(company: str, train_size: float = None, scaled=True):
    features, labels = data_prep(company)

    prices = []
    times = []
    for day in features:
        times.append(day[0])
        prices.append(day[1])

    if train_size is None:
        train_size = (len(features) - 1) / len(features)

    if train_size == 1.0:
        X_train, y_train = features, labels
        test_times, test_prices = None, None
    else:
        X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=1-train_size, random_state=42, shuffle=False, stratify=None)
        train_times, test_times, train_prices, test_prices = train_test_split(times, prices, test_size=1-train_size, random_state=42, shuffle=False, stratify=None)

    if scaled:
        scaling = MinMaxScaler(feature_range=(-1, 1)).fit(X_train)
    if train_size == 1.0:
        if scaled:
            X_train = scaling.transform(X_train)
        X_test, y_test = None, None
    else:
        if scaled:
            X_train = scaling.transform(X_train)
            X_test = scaling.transform(X_test)
    return X_train, X_test, y_train, y_test, test_prices, test_times


def knn_predict(company: str, verbose=False, train_size=0.80, scaled=False):
    X_train, X_test, y_train, y_test, prices, times = get_features(company, train_size=train_size, scaled=scaled)
    true_labels, KNN_predictions = KNN.predict(X_train, y_train, X_test, y_test)
    accuracy = accuracy_score(true_labels, KNN_predictions)
    if verbose:
        print(f"KNN Accuracy: {accuracy * 100}%\n")
        prediction_distribution(KNN_predictions, true_labels)
    return prices, times, KNN_predictions, accuracy


def svm_predict(company: str, verbose=False, train_size=0.80, scaled=False):
    X_train, X_test, y_train, y_test, prices, times = get_features(company, train_size=train_size, scaled=scaled)
    true_labels, SVM_predictions = SVM.predict(X_train, y_train, X_test, y_test)
    accuracy = accuracy_score(true_labels, SVM_predictions)
    if verbose:
        print(f"SVM Accuracy: {accuracy * 100}%\n")
        prediction_distribution(SVM_predictions, true_labels)
    return prices, times, SVM_predictions, accuracy


def rf_predict(company: str, verbose=False, train_size: float = None, scaled=False):
    X_train, X_test, y_train, y_test, prices, times = get_features(company, train_size=train_size, scaled=scaled)
    true_labels, RF_predictions = RF.predict(X_train, y_train, X_test, y_test)
    accuracy = accuracy_score(true_labels, RF_predictions)
    if verbose:
        print(f"RF Accuracy: {accuracy * 100}%\n")
        prediction_distribution(RF_predictions, true_labels)

    return prices, times, RF_predictions, accuracy


def lstm_predict(company: str, verbose=False, train_size=0.80, scaled=False):
    X_train, X_test, y_train, y_test, prices, times = get_features(company, train_size=train_size, scaled=scaled)
    X_train, y_train, X_test, y_test = data_reshape(X_train, y_train, X_test, y_test)
    LSTM_predictions, true_labels = LSTM.predict(X_train, y_train, X_test, y_test, company)
    accuracy = accuracy_score(true_labels, LSTM_predictions)
    if verbose:
        print(f"LSTM Accuracy: {accuracy * 100}%\n")
        prediction_distribution(LSTM_predictions, true_labels)
    return prices, times, LSTM_predictions, accuracy


def cnn_predict(company: str, verbose=False, train_size=0.80, scaled=False):
    X_train, X_test, y_train, y_test, prices, times = get_features(company, train_size=train_size, scaled=scaled)
    X_train, X_test = reshape(array(X_train), (shape(X_train)[0], shape(X_train)[1], 1)), reshape(array(X_test), (shape(X_test)[0], shape(X_test)[1], 1))
    y_train, y_test = reshape(array(y_train), (shape(y_train)[0], 1, 1)), reshape(array(y_test), (shape(y_test)[0], 1, 1))
    true_labels, CNN_predictions = CNN.predict(X_train, y_train, X_test, y_test)
    true_labels = reshape(true_labels, (shape(true_labels)[0], ))
    CNN_predictions = reshape(CNN_predictions, (shape(CNN_predictions)[0], ))
    accuracy = accuracy_score(true_labels, CNN_predictions)
    if verbose:
        print(f"Training Instances: {len(X_train)}")
        print(f"Testing Instances: {len(X_test)}")
        print(f"CNN Accuracy: {accuracy * 100}%\n")
        prediction_distribution(CNN_predictions, true_labels)
    return prices, times, CNN_predictions, accuracy


if __name__ == '__main__':
    model = rf_predict
    for stock in stocks_dict:
        company_name = stocks_dict[stock]
        print(f'Company name: {company_name.title()}')
        model(company_name, verbose=True, train_size=0.50)
