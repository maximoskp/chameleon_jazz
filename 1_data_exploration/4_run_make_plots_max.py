#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 18:56:11 2021

@author: max
"""

import numpy as np
import os
import json
import pickle
import sys
from scipy import sparse
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc
import matplotlib.pyplot as plt

# %% load pickle

with open('../data/charts_with_melodies/nmf_models.pickle', 'rb') as handle:
    nmf_models = pickle.load(handle)

# %%

x = nmf_models[0]['H'][0,:]
y = nmf_models[0]['H'][1,:]
z = nmf_models[0]['H'][2,:]

ax = plt.figure().add_subplot(projection='3d')

ax.scatter3D(x,y,z,'.')