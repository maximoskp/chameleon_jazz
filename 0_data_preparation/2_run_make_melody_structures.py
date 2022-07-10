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
    print('Processing (' + str(i) + '/' + str(len(songs_keys)) + '): ' + songs[songs_keys[i]]['appearing_name'])
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

print('saving globalHMM')
with open('../data/globalHMM.pickle', 'wb') as handle:
    pickle.dump(globalHMM, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% test plot
os.makedirs('../figs', exist_ok=True)
import matplotlib.pyplot as plt
plt.imshow(np.reshape(globalHMM.melody_per_chord.toarray(), (70,12*12)), cmap='gray_r')
plt.savefig('../figs/test_melperchord.png', dpi=500)