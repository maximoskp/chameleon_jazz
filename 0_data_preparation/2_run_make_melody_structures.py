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

with open('../data/all_melody_structs.pickle', 'wb') as handle:
    pickle.dump(all_structs, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% TODO: make melody-chord stats for all chords
# Run through all items in all_structs and add/append in dictionary with
# add_melody_per_chord_information 
# keys: all chords (840)
# values: distribution of piece_tonality-rPCPs of melodies in GlobalHMM melody_per_chord