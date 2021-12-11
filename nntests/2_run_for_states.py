import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow import keras
import os
import json
import numpy as np
import matplotlib.pyplot as plt

# load model
model1 = keras.models.load_model( 'models/lstm128/lstm128_current_best.hdf5' )

# only for states
# model_states = keras.Model(nn_in, [lstm, states_h, states_c])

# optimizer = keras.optimizers.Adam(learning_rate=0.01)
# model.compile(loss="categorical_crossentropy", optimizer=optimizer)

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

# create new model but keep weights
nn_in = keras.Input(shape=(maxlen, len(chars)))
lstm = layers.LSTM(128, return_state=True, return_sequences=True)
seq_out, states_h, states_c = lstm(nn_in)
nn_out = layers.Dense(len(chars), activation="softmax")(seq_out)

model = keras.Model( inputs=nn_in, outputs=[nn_out, states_h, states_c], name='lstm128' )

# model = keras.Sequential(
#     [
#         nn_in,
#         lstm,
#         nn_out,
#     ]
# )
# pass weights to new model
model.layers[1].set_weights( model1.layers[0].get_weights() )
model.layers[2].set_weights( model1.layers[1].get_weights() )

with open('..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'songslibrary.json') as json_file:
    songs = json.load(json_file)

songs_keys = list( songs.keys() )

# for the first three songs
h_all = []
c_all = []
sizes = []
h_final_states = []
c_final_states = []
for song_idx in range(3):
    print('song_idx: ' + str(song_idx))
    # get a piece
    p = songs[songs_keys[song_idx]]['unfolded_string']
    # transform it
    x = np.zeros((1, len(p), len(chars)), dtype=bool)
    sizes.append( len(p) )
    for t, char in enumerate(p):
        x[0, t, char2idx[char]] = 1
    
    # get it through the system
    # y = model.predict(x[:,:50,:])
    # y, h, c = model(x[:,:50,:])
    # h_all = []
    # c_all = []
    for i in range( x.shape[1]-50 ):
        print('step: ' + str(i) + ' / ' +str(x.shape[1]-50))
        y, h, c = model(x[:, i:i+50, :])
        h_all.append( h )
        c_all.append( c )
    h_final_states.append( h )
    c_final_states.append( c )

h_np = np.array( h_all )
c_np = np.array( c_all )
h_final_np = np.array( h_final_states )
c_final_np = np.array( c_final_states )

# %% 

for i in range(0, c_np.shape[0]-100, 100):
    # plt.imshow(h_np[:,0,:])
    plt.imshow(c_np[i:i+100,0,:])
    plt.pause(0.1)

# plt.plot(h_np[-1,0,:])
# plt.plot(c_np[-1,0,:])