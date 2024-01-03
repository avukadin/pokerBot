from keras.models import Sequential
from keras.layers import Dense
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
import csv
from keras.layers import BatchNormalization
from keras.layers import Activation

from keras.callbacks import Callback, ModelCheckpoint
from enum import Enum
from ml.params import (
    HS_SAMPLE_PREDICTION_PATH,
    MOVE_SAMPLE_PREDICTION_PATH,
    BATCH_SIZE,
    EPOCHS,
    HS_TRAIN_DATA_PATH,
    MOVE_TRAIN_DATA_PATH,
    HS_MODEL_PATH,
    MOVE_MODEL_PATH
)

class Models(Enum):
    HAND_STRENGTH = 0
    MOVE_PREDICTION = 1

MODEL_TO_TRAIN = Models.MOVE_PREDICTION

PREDICTION_PATH = HS_SAMPLE_PREDICTION_PATH if MODEL_TO_TRAIN == Models.HAND_STRENGTH else MOVE_SAMPLE_PREDICTION_PATH
TRAIN_DATA_PATH = HS_TRAIN_DATA_PATH if MODEL_TO_TRAIN == Models.HAND_STRENGTH else MOVE_TRAIN_DATA_PATH
MODEL_PATH = HS_MODEL_PATH if MODEL_TO_TRAIN == Models.HAND_STRENGTH else MOVE_MODEL_PATH

class DataGenerator:
    def __init__(self, X, y, batch_size):
        self.batch_size = batch_size
        self.n_samples = len(X) 
        self.X = X
        self.y = y

    def generate(self):
        while True:
            for i in range(0, len(self.X), self.batch_size):
                X_batch = self.X[i:i + self.batch_size]
                y_batch = self.y[i:i + self.batch_size]
                yield np.array(X_batch), np.array(y_batch)

class SaveCSVOutput(Callback):

    def __init__(self, X, y, batch_size):
        super().__init__()
        self.X = X[0:500]
        self.y = y[0:500]
        self.batch_size = batch_size

    def on_epoch_end(self, epoch, logs=None):
        predictions = self.model.predict(self.X, batch_size=self.batch_size)

        if MODEL_TO_TRAIN == Models.MOVE_PREDICTION:
            predictions = np.argmax(predictions, axis=1)
            actual = np.argmax(self.y, axis=1)
        elif MODEL_TO_TRAIN == Models.HAND_STRENGTH:
            predictions = [round(p[0], 2) for p in predictions]
            actual = self.y
        else:
            raise Exception("Invalid model type")

        csv_data = {'actual': actual, 'predicted': predictions}
        with open(PREDICTION_PATH, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_data.keys())
            writer.writeheader()
            for i in range(len(csv_data['actual'])):
                writer.writerow({'actual': csv_data['actual'][i], 'predicted': csv_data['predicted'][i]})
        print(f"Saved predictions to {PREDICTION_PATH}")

def get_train_validation_split():
    print("Loading Data...")
    with open(TRAIN_DATA_PATH, 'rb') as file:
        data = pickle.load(file)
    print("Done")

    X, y = data['input'], data['output']
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.05)
    print("Train size: ", len(X_train), "Val size: ", len(X_val))

    train_generator = DataGenerator(X_train, y_train, BATCH_SIZE)
    val_generator = DataGenerator(X_val, y_val, BATCH_SIZE)

    return train_generator, val_generator

def new_model(input_dim:int):
    model = Sequential()
    model.add(Dense(64, input_dim=input_dim))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(Dense(64))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    if MODEL_TO_TRAIN == Models.HAND_STRENGTH:
        model.add(Dense(1, activation='sigmoid'))
    elif MODEL_TO_TRAIN == Models.MOVE_PREDICTION:
        model.add(Dense(4, activation='softmax'))
    else:
        raise Exception("Invalid model type")
    return model

def train():
    train_generator, val_generator = get_train_validation_split()
    input_shape = len(train_generator.X[0])
    model = new_model(input_shape)

    if MODEL_TO_TRAIN == Models.HAND_STRENGTH:
        loss_function = 'mean_squared_error'
    elif MODEL_TO_TRAIN == Models.MOVE_PREDICTION:
        loss_function = 'categorical_crossentropy'
    else:
        raise Exception("Invalid model type")

    checkpoint = ModelCheckpoint(
        MODEL_PATH,                 # Path to save the model
        monitor='val_loss',         # Metric to monitor
        verbose=1,                  # Verbosity mode
        save_best_only=True,        # Save only the best model
        mode='min'                  # Save the model with the minimum validation loss
    )

    model.compile(loss=loss_function, optimizer='adam')
    csv_callback = SaveCSVOutput(val_generator.X, val_generator.y, BATCH_SIZE)

    model.fit(
        train_generator.generate(),
        steps_per_epoch=train_generator.n_samples // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=val_generator.generate(),
        validation_steps=val_generator.n_samples // BATCH_SIZE,
        callbacks=[csv_callback, checkpoint]
    )

train()
