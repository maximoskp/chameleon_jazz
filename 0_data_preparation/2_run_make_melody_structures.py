# -*- coding: utf-8 -*-
"""
Created on Sun Sep 19 07:53:07 2021

@author: user
"""

import numpy as np
import os
import json
import CJ_ChartClasses as ccc
import pickle
import pandas as pd
from scipy import sparse


# load all piece
with open('..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'songsmelodieslibrary.json') as json_file:
    songs = json.load(json_file)

songs_keys = list( songs.keys() )

# %% run example

i = 0
s = ccc.Chart( songs[songs_keys[i]] )

print( 'size of object: ' + str(len(pickle.dumps(s, -1))) )

# %% run for all pieces

all_structs = [s]*len( songs_keys )
# all_structs = []

for i in range( len( songs_keys ) ):
    print('Processing (' + str(i+1) + '/' + str(len(songs_keys)) + '): ' + songs[songs_keys[i]]['appearing_name'])
    # all_structs.append( ccc.Chart( songs[songs_keys[i]] ) )
    all_structs[i] = ccc.Chart( songs[songs_keys[i]] )
    # print( 'size of object: ' + str(len(pickle.dumps(all_structs, -1))) )

# %% save pickle
print('saving all_structs')
with open('../data/all_melody_structs.pickle', 'wb') as handle:
    pickle.dump(all_structs, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% global HMM
print('constructing global and partial HMMs')
globalHMM = ccc.ChameleonHMM()

# harmonic styles
stylesHMM = {
    'harmonic': {},
    'genre': {}
}

for s in all_structs:
    globalHMM.add_melody_information_with_matrix( s.hmm.melody_per_chord )
    globalHMM.add_transition_information( s.hmm.transition_matrix )
    globalHMM.add_chord_distribution( s.hmm.chords_distribution )
    # harmonic styles
    if s.harmonic_style is not None:
        if s.harmonic_style not in stylesHMM['harmonic'].keys():
            tmpHMM = ccc.ChameleonHMM()
        else:
            tmpHM = stylesHMM['harmonic'][s.harmonic_style]
        tmpHMM.add_melody_information_with_matrix( s.hmm.melody_per_chord )
        tmpHMM.add_transition_information( s.hmm.transition_matrix )
        tmpHMM.add_chord_distribution( s.hmm.chords_distribution )
        stylesHMM['harmonic'][s.harmonic_style] = tmpHMM
    if s.genre_style is not None:
        if s.genre_style not in stylesHMM['genre'].keys():
            tmpHMM = ccc.ChameleonHMM()
        else:
            tmpHMM = stylesHMM['genre'][s.genre_style]
        tmpHMM.add_melody_information_with_matrix( s.hmm.melody_per_chord )
        tmpHMM.add_transition_information( s.hmm.transition_matrix )
        tmpHMM.add_chord_distribution( s.hmm.chords_distribution )
        stylesHMM['genre'][s.genre_style] = tmpHMM


# fill-in new chords with their rpcp
if len(globalHMM.all_chord_states) == 0:
    globalHMM.initialize_chord_states()
mGlobal = globalHMM.melody_per_chord.toarray()
for i in range( mGlobal.shape[0] ):
    if np.sum( mGlobal[i,:] ) == 0:
        mGlobal[i,:] = globalHMM.chord_state2rpcp( globalHMM.all_chord_states[i] )
globalHMM.melody_per_chord = sparse.csr_matrix(mGlobal)

# in styles
for style_type in ['harmonic', 'genre']:
    for k in stylesHMM[style_type].keys():
        tmp_hmm = stylesHMM[style_type][k]
        if len(tmp_hmm.all_chord_states) == 0:
            tmp_hmm.initialize_chord_states()
        mStyle = tmp_hmm.melody_per_chord.toarray()
        for i in range( mStyle.shape[0] ):
            if np.sum( mStyle[i,:] ) == 0:
                mStyle[i,:] = tmp_hmm.chord_state2rpcp( tmp_hmm.all_chord_states[i] )
        tmp_hmm.melody_per_chord = sparse.csr_matrix(mStyle)

print('saving globalHMM')
with open('../data/globalHMM.pickle', 'wb') as handle:
    pickle.dump(globalHMM, handle, protocol=pickle.HIGHEST_PROTOCOL)

print('saving stylesHMM')
with open('../data/stylesHMM.pickle', 'wb') as handle:
    pickle.dump(stylesHMM, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% test plot
'''
os.makedirs('../figs', exist_ok=True)
import matplotlib.pyplot as plt
plt.imshow(np.reshape(globalHMM.melody_per_chord.toarray(), (70,12*12)), cmap='gray_r')
plt.savefig('../figs/test_melperchord.png', dpi=500)
'''
# %% print debug markov - collect all songs per chord
songs_per_chord = {}

for s in all_structs:
    s.hmm.debug_print(filename='debug_hmm/' + s.piece_name.replace(' ','_') + '.txt')
    for c in s.chords:
        if c.chord_state not in songs_per_chord.keys():
            songs_per_chord[ c.chord_state ] = []
        if s.piece_name not in songs_per_chord[ c.chord_state ]:
            songs_per_chord[ c.chord_state ].append( s.piece_name )
# songs_per_chord for excel
spc_excel = {
    'chords': list( songs_per_chord.keys() ),
    'songs': list( songs_per_chord.values() )
}
df = pd.DataFrame( spc_excel )
df.to_excel('../data/songs_per_chord.xlsx')

globalHMM.debug_print(filename='debug_hmm/global.txt')

