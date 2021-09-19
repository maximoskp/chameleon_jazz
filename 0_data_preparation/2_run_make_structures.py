# -*- coding: utf-8 -*-
"""
Created on Sun Sep 19 07:53:07 2021

@author: user
"""

import numpy as np
import os
import json
import CJ_ChartClasses as ccc

# load all piece
with open('..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'songslibrary.json') as json_file:
    songs = json.load(json_file)

songs_keys = list( songs.keys() )

i = 10
s = ccc.Chart( songs[songs_keys[i]] )