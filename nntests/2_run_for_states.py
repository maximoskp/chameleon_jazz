import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle
import tensorflow as tf
from tensorflow import keras
import os
import json
import numpy as np

# load model
model = keras.models.load_model( 'models/lstm128/lstm128_current_best.hdf5' )

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

with open('..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'songslibrary.json') as json_file:
    songs = json.load(json_file)

songs_keys = list( songs.keys() )

# get a piece
p = songs[songs_keys[0]]['unfolded_string']
# transform it
x = np.zeros((1, len(p), len(chars)), dtype=bool)
for t, char in enumerate(p):
    x[0, t, char2idx[char]] = 1

# get it through the system
y = model.predict(x[:,:50,:])
print(model.layers[0].states[0].get_value())