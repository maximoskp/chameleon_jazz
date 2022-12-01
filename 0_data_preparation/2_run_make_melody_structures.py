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
print('constructing global HMM')
globalHMM = ccc.ChameleonHMM()

for s in all_structs:
    globalHMM.add_melody_information_with_matrix( s.hmm.melody_per_chord )
    globalHMM.add_transition_information( s.hmm.transition_matrix )
    globalHMM.add_chord_distribution( s.hmm.chords_distribution )

# form groups in global HMM

print('saving globalHMM')
with open('../data/globalHMM.pickle', 'wb') as handle:
    pickle.dump(globalHMM, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% test plot
os.makedirs('../figs', exist_ok=True)
import matplotlib.pyplot as plt
plt.imshow(np.reshape(globalHMM.melody_per_chord.toarray(), (70,12*12)), cmap='gray_r')
plt.savefig('../figs/test_melperchord.png', dpi=500)

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

