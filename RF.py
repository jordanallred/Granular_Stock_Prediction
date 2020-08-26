from sklearn.ensemble import RandomForestClassifier
from numpy import ndarray
# from sklearn.tree import export_graphviz
# from os import environ
# import pydot
import time

# os.environ["PATH"] += os.pathsep + 'C:\\Users\\Jordan Allred\\Anaconda3\\Library\\bin\\graphviz\\'

feature_names = [
    'Time',
    'Price',
    'Volume',
    '1-minute Percent Change',
    '5-minute Percent Change',
    '15-minute Percent Change',
    '30-minute Percent Change',
    '60-minute Percent Change'
]

target_names = [
    'Buy',
    'Hold',
    'Sell'
]


def predict(train_features: ndarray, train_labels: ndarray, test_features: ndarray, test_labels: ndarray):
    classifier = RandomForestClassifier(n_estimators=25)
    start = time.time()
    classifier.fit(train_features, train_labels.ravel())
    end = time.time()
    # print('Train time: ' + str(end - start))
    '''
    estimator = classifier.estimators_[5]
    export_graphviz(estimator,
                    out_file='tree.dot',
                    feature_names=feature_names,
                    class_names=target_names,
                    rounded=True, proportion=False,
                    precision=2, filled=True)
    # (graph,) = pydot.graph_from_dot_file('tree.dot')
    # graph.write_png('tree.png')
    '''
    start = time.time()
    predictions = classifier.predict(test_features)
    end = time.time()
    # print('Test time: ' + str(end - start))
    rounded_predictions = []
    for prediction in predictions:
        rounded_predictions.append(round(prediction))
    return test_labels, rounded_predictions
