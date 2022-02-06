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

import sys
sys.path.insert(1, '../0_data_preparation')
import CJ_ChartClasses as ccc

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
        unfolded_neutralized += 'chord~' + str(c.relative_root['piece_tonality']) + ':' + str(c.symbolic_type) + '@' + str(c.onset_in_measure) + ','
        if len(commasplit[1]) > 0:
            unfolded_neutralized += commasplit[1] + ','
    return unfolded_neutralized
# end neutralize_song

def remove_keyword( song, w ):
    w_split = song.split( w )
    out_song = ''
    for s in w_split:
        if ',' in s:
            comma_split = s.split(',')
            out_song += ','.join(comma_split[ 1: ])
    return out_song
# end remove_keyword

def remove_metadata(song, metadata=['section~', 'style~', 'tempo~', 'tonality~']):
    for m in metadata:
        song = remove_keyword(song, m)
    return song
# end remove_metadata

def prepare_song(s, metadata=['section~', 'style~', 'tempo~', 'tonality~'], reps=1):
    n = remove_metadata( neutralize_song( s ).split(',end,')[0], metadata=metadata )
    return 'start,' + n*reps + ',end,'
# end prepare_song

# %%

def get_metadata_from_string(s, title=''):
    # style
    styles = ''
    t = s.split('style~')
    for i in range( len(t)-1 ):
        c = t[i+1].split(',')
        if i > 0:
            styles += ', '
        styles += c[0]
    # sections
    sections = ''
    t = s.split('section~')
    for i in range( len(t)-1 ):
        c = t[i+1].split(',')
        sections += c[0]
    # tempi
    tempi = ''
    t = s.split('tempo~')
    for i in range( len(t)-1 ):
        c = t[i+1].split(',')
        if i > 0:
            tempi += ', '
        tempi += c[0]
    # tonalities
    tonalities = ''
    t = s.split('tonality~')
    for i in range( len(t)-1 ):
        c = t[i+1].split(',')
        if i > 0:
            tonalities += ', '
        tonalities += c[0]
    # time signatures
    time_sigs = []
    time_sigs_str = ''
    t = s.split('bar~')
    for i in range( len(t)-1 ):
        c = t[i+1].split(',')
        if c[0] not in time_sigs:
            if i > 0 and c[0] not in time_sigs:
                time_sigs_str += ', '
            time_sigs_str += c[0]
            time_sigs.append( c[0] )
    return {
        'title': title,
        'styles': styles,
        'sections': sections,
        'tempi': tempi,
        'tonalities': tonalities,
        'time_signatures': time_sigs,
        'all': title + '\n' + styles + '-' + sections + '\n' + tonalities + '-' + tempi + '-' + time_sigs_str
    }
# end get_metadata_from_string

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
# lstm = layers.LSTM(64, return_state=True, return_sequences=True)
# seq_out, states_h, states_c = lstm(nn_in)
# nn_out = layers.Dense(len(chars), activation="softmax")(seq_out)

d1 = layers.Dense(256, activation="selu", input_shape=[len(chars)])(nn_in)
d2 = layers.Dense(128, activation="selu")(d1)
lstm = layers.LSTM(128, return_state=True, return_sequences=True)
seq_out, states_h, states_c = lstm(d2)
d3 = layers.Dense(128, activation="selu")(seq_out)
nn_out = layers.Dense(len(chars), activation="softmax")(d3)

model = keras.Model( inputs=nn_in, outputs=[nn_out, states_h, states_c], name='lstm128' )

# model = keras.Sequential(
#     [
#         nn_in,
#         lstm,
#         nn_out,
#     ]
# )
# pass weights to new model
for i in range( len( model.layers ) - 1 ):
    model.layers[i+1].set_weights( model1.layers[i].get_weights() )

with open('..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'songslibrary.json') as json_file:
    songs = json.load(json_file)

songs_keys = list( songs.keys() )

# for the first three songs
# h_all = []
# c_all = []
sizes = []
h_final_states = []
c_final_states = []
metadata = {}
for song_idx in range(len(songs_keys)):
    print('song_idx: ' + str(song_idx) + ' / ' + str(len(songs_keys)))
    # get a piece
    # n = prepare_song(songs[songs_keys[song_idx]])
    n = prepare_song( songs[songs_keys[song_idx]],metadata=[],reps=1)
    p = n
    # get 'metadata'
    metadata[ songs_keys[song_idx] ] = get_metadata_from_string(p, title=songs_keys[song_idx])
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
        # print('step: ' + str(i) + ' / ' +str(x.shape[1]-50))
        y, h, c = model(x[:, i:i+50, :])
        # h_all.append( h )
        # c_all.append( c )
    h_final_states.append( h )
    c_final_states.append( c )

# h_np = np.array( h_all )
# c_np = np.array( c_all )
h_final_np = np.array( h_final_states )
c_final_np = np.array( c_final_states )

states_data = {
    'h_final_np': h_final_np,
    'c_final_np': c_final_np,
}

with open('data/' + os.sep + 'states_data.pickle', 'wb') as handle:
    pickle.dump(states_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('data/' + os.sep + 'metadata.pickle', 'wb') as handle:
    pickle.dump(metadata, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% 

'''
for i in range(0, c_np.shape[0]-100, 100):
    # plt.imshow(h_np[:,0,:])
    plt.imshow(c_np[i:i+100,0,:])
    plt.pause(0.1)
'''
# plt.plot(h_np[-1,0,:])
# plt.plot(c_np[-1,0,:])
