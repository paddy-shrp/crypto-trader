import keras
import tensorflow as tf
from tensorflow import keras
from keras.layers import Input, Dense, Dropout, Concatenate

TRADER_FEATURE_COUNT = 7
HISTORICAL_FEATURE_COUNT = 900

class TraderModel(keras.Model):
    def __init__(self):
        
        # Define the input layers
        trader_input = Input(shape=(TRADER_FEATURE_COUNT,))
        historical_input = Input(shape=(HISTORICAL_FEATURE_COUNT,))

        # Historical Branch
        historical_branch = Dense(128, activation='relu')(historical_input)
        historical_branch = Dropout(0.3)(historical_branch)
        historical_branch = Dense(96, activation='relu')(historical_branch)
        historical_branch = Dropout(0.3)(historical_branch)
        historical_branch = Dense(32, activation='relu')(historical_branch)
        historical_branch = Dropout(0.1)(historical_branch)
        historical_branch = Dense(2, activation='softmax')(historical_branch)

        # Combine Branches
        combined_branches = Concatenate()([trader_input, historical_branch])

        # Trader Branch
        trader_branch = Dense(16, activation='relu')(combined_branches)
        trader_branch = Dropout(0.3)(trader_branch)
        trader_branch = Dense(16, activation='relu')(trader_branch)
        trader_branch = Dropout(0.3)(trader_branch)
        trader_branch = Dense(8, activation='relu')(trader_branch)

        output = Dense(3, activation='softmax')(trader_branch)
        super().__init__(inputs=[trader_input, historical_input], outputs=output)
        self.compile(
            loss=tf.keras.losses.Huber(), 
            optimizer="adam", 
            metrics=["accuarcy"]
        )
 
    def calculate(self, trader_data, historical_data):
        trader_data = tf.reshape(trader_data, (1, -1))
        historical_data = tf.reshape(historical_data, (1, -1))
        return self([trader_data, historical_data]).numpy()
    

class TraderModelSimplified(keras.Model):
    def __init__(self):
        trader_historical_input = Input(shape=(TRADER_FEATURE_COUNT + HISTORICAL_FEATURE_COUNT,))

        trader_branch = Dense(128, activation='relu')(trader_historical_input)
        trader_branch = Dropout(0.3)(trader_branch)
        trader_branch = Dense(96, activation='relu')(trader_branch)
        trader_branch = Dropout(0.3)(trader_branch)
        trader_branch = Dense(32, activation='relu')(trader_branch)
        trader_branch = Dropout(0.1)(trader_branch)
        output = Dense(3, activation='softmax')(trader_branch)

        super().__init__(inputs=trader_historical_input, outputs=output)
        self.compile(
            loss=tf.keras.losses.Huber(), 
            optimizer="adam", 
            metrics=["accuarcy"]
        )
