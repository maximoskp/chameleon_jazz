#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 11:41:46 2022

@author: konstantinosvelenis
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

i = 77
s = ccc.Chart( songs[songs_keys[i]] )

print( 'size of object: ' + str(len(pickle.dumps(s, -1))) )