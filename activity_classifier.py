from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM, Dropout
import numpy as np
import tensorflow as tf

N_CLASSES = 18
N_FEATURES = 7
TIMESTEPS = 30
CKPT_DIR = "ckpt/checkpoints"
class ActivityClassifier:
    def __init__(self):
        #self.__create_model__(N_CLASSES,(TIMESTEPS,N_FEATURES))
        #self.__load_model__()
        self.model = load_model("checkpoint")
        self.__labels__ = {
            0:'lying',
            1:'sitting',
            2:'standing',
            3:'walking',
            4:'running',
            5:'cycling',
            6:'nordic walking',
            7:'watching TV',
            8:'computer work',
            9:'car driving',
            10:'ascending stairs',
            11:'descending stairs',
            12:'vaccm cleaning',
            13:'ironing',
            14:'folding laundry',
            15:'house cleaning',
            16:'playing soccer',
            17:'rope jumping'
        }
    def __create_model__(self,n_classes,lstm_layer_shape):  
        self.model = Sequential()
        self.model.add(LSTM(64,input_shape = lstm_layer_shape,
                       activation = 'tanh',recurrent_activation = 'sigmoid',return_sequences=True))
        self.model.add(LSTM(32))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(32,activation='relu'))
        self.model.add(Dense(n_classes, activation = 'softmax'))
    def __load_model__(self):
        self.model.load_weights(CKPT_DIR)
    def predict(self,feature_vector):
        feature_vector = np.array(feature_vector)
        feature_vector = np.reshape(feature_vector,(1,TIMESTEPS,N_FEATURES))
        prediction_vector = self.model.predict(feature_vector)
        class_id = np.argmax(prediction_vector)
        return self.__labels__[class_id]
