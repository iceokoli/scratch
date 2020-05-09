import json

import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler

from tensorflow.keras.layers import Dense, Dropout, LSTM, BatchNormalization
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping

from kerastuner.tuners import RandomSearch
from kerastuner.engine.hyperparameters import HyperParameters


def get_data():
    df = pd.read_csv("TSLA.csv", index_col=0)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df


def multivariate_data(
    dataset,
    target,
    start_index,
    end_index,
    history_size,
    target_size,
    step,
    single_step=False,
):

    data = []
    labels = []

    start_index = start_index + history_size
    if end_index is None:
        end_index = len(dataset) - target_size

    for i in range(start_index, end_index):
        indices = range(i - history_size, i, step)
        data.append(dataset[indices])

        if single_step:
            labels.append(target[i + target_size])
        else:
            labels.append(target[i : i + target_size])

    return np.array(data), np.array(labels)


def build_model(hp):
    model = Sequential()

    for i in range(hp.Int("n_ltsm_layers", 0, 2)):
        model.add(
            LSTM(
                hp.Int(f"layer_{i}_units", 2, 256, 4),
                input_shape=X_train.shape[1:],
                return_sequences=True,
            )
        )
        model.add(Dropout(hp.Float(f"layer_{i}_dropout", 0, 0.4, 0.1)))
        model.add(BatchNormalization())

    model.add(
        LSTM(
            hp.Int(f"final_ltsm_units", 2, 256, 4),
            input_shape=X_train.shape[1:],
            return_sequences=False,
        )
    )
    model.add(Dropout(hp.Float("final_ltsm_dropout", 0, 0.4, 0.1)))
    model.add(BatchNormalization())

    for i in range(hp.Int("n_RNN_dense_layers", 0, 2)):
        model.add(Dense(hp.Int(f"dense_layer_{i}_units", 2, 256, 4), activation="relu"))
        model.add(Dropout(hp.Float(f"dense_layer_{i}_dropout", 0, 0.4, 0.1)))

    model.add(Dense(1))

    model.compile(optimizer="adam", loss="mse")

    return model


if __name__ == "__main__":

    df = get_data()

    # Prepare the data, normalise and split
    train_index = int(np.where(df.index == "2019-01-02")[0])
    valid_index = int(np.where(df.index == "2020-01-02")[0])

    scale = MinMaxScaler()
    scale.fit(df.iloc[:train_index])
    scaled_data = scale.transform(df)

    X_train, y_train = multivariate_data(
        dataset=scaled_data,
        target=scaled_data[:, 3],
        start_index=0,
        end_index=train_index,
        history_size=20,
        target_size=5,
        step=1,
        single_step=True,
    )

    X_valid, y_valid = multivariate_data(
        dataset=scaled_data,
        target=scaled_data[:, 3],
        start_index=train_index,
        end_index=valid_index,
        history_size=20,
        target_size=5,
        step=1,
        single_step=True,
    )

    early_stop = EarlyStopping(monitor="val_loss", mode="min", verbose=1, patience=25)

    tuner = RandomSearch(
        build_model,
        objective="val_loss",
        executions_per_trial=1,
        max_trials=200,
        project_name="tuning_results",
    )

    # tuner.search_space_summary()

    tuner.search(
        X_train,
        y_train,
        batch_size=32,
        epochs=20,
        validation_data=(X_valid, y_valid),
        callbacks=[early_stop],
        verbose=2,
    )

    # tuner.get_best_models()

    best = tuner.get_best_hyperparameters()[0].values
    with open("best_param.json", "w") as f:
        json.dump(best, f)
