# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 14:25:59 2022

@author: maximos
"""

import pickle
import os
import sys
sys.path.append('..' + os.sep +'0_data_preparation')
import computeDIC as dic
import CJ_ChartClasses as ccc
import CJ_ChartBlending as bs

# %% load pickle

with open('../data/all_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

# %%

c0 = all_structs[0]
c1 = all_structs[1]

blendsess = bs.BlendingSession(c0, c1)

# %% save pickle

with open('..' + os.sep + 'data' + os.sep + 'test_blending_session.pickle', 'wb') as handle:
    pickle.dump(blendsess, handle, protocol=pickle.HIGHEST_PROTOCOL)