#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 10:48:54 2021

@author: max
"""

import os
import json
from collections import Counter
import numpy as np

import sys
sys.path.insert(1, '../0_data_preparation')
import CJ_ChartClasses as ccc

import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle

# from tensorflow import keras
# from tensorflow.keras import layers
# import tensorflow as tf
# physical_devices = tf.config.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)

# %% 

def neutralize_song( song ):
    unfolded_neutralized = ''
    chordsplit = song['unfolded_string'].split('chord~')
    unfolded_neutralized = chordsplit[0]
    chameleon_context = ccc.ChameleonContext()
    for i in range( len(chordsplit)-1 ):
        commasplit = chordsplit[i+1].split(',')
        cc = commasplit[0]
        c = ccc.Chord(cc)
        t = chameleon_context.tonality_from_symbol(song['tonality'])
        c.set_tonalities(piece_tonality=t, estimated_tonality=t)
        # print( str(c.relative_root['piece_tonality']) + ':' + str(c.symbolic_type) )
        unfolded_neutralized += 'chord~' + str(c.relative_root['piece_tonality']) + ':' + str(c.symbolic_type) + '@' + str(c.onset_in_measure)
        unfolded_neutralized += ',' + commasplit[1]
    return unfolded_neutralized
# end neutralize_song


# %% 

with open('..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'songslibrary.json') as json_file:
    songs = json.load(json_file)

songs_keys = list( songs.keys() )

# make string
songs_string = ''
for s in songs_keys:
    n = neutralize_song( songs[s] )
    songs_string += n

# keep unique characters
chars = sorted( list( set(songs_string) ) )
chars_count = Counter( songs_string )

# chars2int and back
char2idx = dict((c, i) for i, c in enumerate(chars))
idx2char = dict((i, c) for i, c in enumerate(chars))

# %% 

# cut the text in semi-redundant sequences of maxlen characters
maxlen = 50
step = 3
sentences = []
next_chars = []
for i in range(0, len(songs_string) - maxlen, step):
    sentences.append(songs_string[i : i + maxlen])
    next_chars.append(songs_string[i + maxlen])
print("Number of sequences:", len(sentences))

x = np.zeros((len(sentences), maxlen, len(chars)), dtype=bool)
y = np.zeros((len(sentences), len(chars)), dtype=bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char2idx[char]] = 1
    y[i, char2idx[next_chars[i]]] = 1

saved_data = {
    'x': x,
    'y': y,
    'maxlen': maxlen,
    'step': step,
    'songs_string': songs_string,
    'chars': chars,
    'char2idx': char2idx,
    'idx2char': idx2char
}

with open('data/' + os.sep + 'saved_data.pickle', 'wb') as handle:
    pickle.dump(saved_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% 

# model = keras.Sequential(
#     [
#         keras.Input(shape=(maxlen, len(chars))),
#         layers.LSTM(128),
#         layers.Dense(len(chars), activation="softmax"),
#     ]
# )
# optimizer = keras.optimizers.RMSprop(learning_rate=0.01)
# model.compile(loss="categorical_crossentropy", optimizer=optimizer)

# def sample(preds, temperature=1.0):
#     # helper function to sample an index from a probability array
#     preds = np.asarray(preds).astype("float64")
#     preds = np.log(preds) / temperature
#     exp_preds = np.exp(preds)
#     preds = exp_preds / np.sum(exp_preds)
#     probas = np.random.multinomial(1, preds, 1)
#     return np.argmax(probas)

# # %% 

# epochs = 40
# batch_size = 128

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







