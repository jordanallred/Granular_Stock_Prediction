from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import Dropout
from numpy import ndarray, shape
from os import environ
# from keras.utils.vis_utils import plot_model
from keras.callbacks import TensorBoard
# from subprocess import call
# from datetime import datetime

environ["OMP_NUM_THREADS"] = "4"

def predict(train_features: ndarray, train_labels: ndarray, test_features: ndarray, test_labels: ndarray, company: str):
    batch_size = 256
    epochs = 10
    units = 50
    dropout = 0.10

    model = Sequential()

    if len(shape(train_features)) < 3:
        model.add(LSTM(units=units, return_sequences=True, input_shape=(train_features.shape[1], 1)))
    else:
        model.add(LSTM(units=units, return_sequences=True, input_shape=(train_features.shape[1], train_features.shape[2])))
    model.add(Dropout(dropout))
    model.add(LSTM(units=units, return_sequences=True, recurrent_dropout=True))
    model.add(Dropout(dropout))
    model.add(LSTM(units=units))
    model.add(Dropout(dropout))
    model.add(Dense(1, batch_size=batch_size))
    trainCallBack = TensorBoard(log_dir='./Graph/Train/' + company,
                                histogram_freq=0, write_graph=True, write_images=True,
                                update_freq='batch', batch_size=batch_size)

    # plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
    model.fit(train_features, train_labels, epochs=epochs, batch_size=batch_size, verbose=1,
              callbacks=[trainCallBack])
    predictions = model.predict(test_features, batch_size=batch_size)

    rounded_predictions = []
    for prediction in predictions:
        rounded_predictions.append(round(prediction[0]))

    return test_labels, rounded_predictions
