from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)
from tensorflow.keras.callbacks import ModelCheckpoint

import os

import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle

with open('data/' + os.sep + 'saved_data.pickle', 'rb') as handle:
        saved_data = pickle.load(handle)

x = saved_data['x']
y = saved_data['y']
maxlen = saved_data['maxlen']
step = saved_data['step']
songs_string = saved_data['songs_string']
chars = saved_data['chars']
char2idx = saved_data['char2idx']
idx2char = saved_data['idx2char']

nn_in = keras.Input(shape=(maxlen, len(chars)))
# lstm, states_h, states_c = layers.LSTM(units=64,dropout=0.3,recurrent_dropout=0.2, return_state=True, return_sequences=True)
# lstm = layers.LSTM(64,dropout=0.3,recurrent_dropout=0.2, return_state=True, return_sequences=True)
lstm = layers.LSTM(64)
nn_out = layers.Dense(len(chars), activation="softmax")

model = keras.Sequential(
    [
        nn_in,
        lstm,
        nn_out,
    ]
)
# only for states
# model_states = keras.Model(nn_in, [lstm, states_h, states_c])

optimizer = keras.optimizers.Adam(learning_rate=0.01)
model.compile(loss="categorical_crossentropy", optimizer=optimizer)

os.makedirs( 'models/lstm128', exist_ok=True )

filepath = 'models/lstm128/lstm128_epoch{epoch:02d}_trainLoss{val_loss:.6f}.hdf5'
checkpoint = ModelCheckpoint(filepath=filepath,
                            monitor='val_loss',
                            verbose=1,
                            save_best_only=True,
                            mode='min')

filepath_current_best = 'models/lstm128/lstm128_current_best.hdf5'
checkpoint_current_best = ModelCheckpoint(filepath=filepath_current_best,
                            monitor='val_loss',
                            verbose=1,
                            save_best_only=True,
                            mode='min')

# def sample(preds, temperature=1.0):
#     # helper function to sample an index from a probability array
#     preds = np.asarray(preds).astype("float64")
#     preds = np.log(preds) / temperature
#     exp_preds = np.exp(preds)
#     preds = exp_preds / np.sum(exp_preds)
#     probas = np.random.multinomial(1, preds, 1)
#     return np.argmax(probas)

# %% 

epochs = 40
batch_size = 128

model.fit(x, y, batch_size=batch_size, epochs=epochs, validation_data=(x[:100,:,:],y[:100,:]),
        callbacks=[checkpoint, checkpoint_current_best])

# for epoch in range(epochs):
#     model.fit(x, y, batch_size=batch_size, epochs=1)
#     print()
#     print("Generating text after epoch: %d" % epoch)

#     start_index = np.random.randint(0, len(songs_string) - maxlen - 1)
#     for diversity in [0.2, 0.5, 1.0, 1.2]:
#         print("...Diversity:", diversity)

#         generated = ""
#         sentence = songs_string[start_index : start_index + maxlen]
#         print('...Generating with seed: "' + sentence + '"')

#         for i in range(400):
#             x_pred = np.zeros((1, maxlen, len(chars)))
#             for t, char in enumerate(sentence):
#                 x_pred[0, t, char2idx[char]] = 1.0
#             preds = model.predict(x_pred, verbose=0)[0]
#             next_index = sample(preds, diversity)
#             next_char = idx2char[next_index]
#             sentence = sentence[1:] + next_char
#             generated += next_char

#         print("...Generated: ", generated)
#         print()