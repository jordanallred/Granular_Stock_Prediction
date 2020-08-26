from numpy import ndarray
from sklearn.neighbors import KNeighborsClassifier


def predict(train_features: ndarray, train_labels: ndarray, test_features: ndarray, test_labels: ndarray):
    classifier = KNeighborsClassifier()
    classifier.fit(train_features, train_labels)
    predictions = classifier.predict(test_features)
    rounded_predictions = []
    for prediction in predictions:
        rounded_predictions.append(round(prediction))

    return test_labels, rounded_predictions
