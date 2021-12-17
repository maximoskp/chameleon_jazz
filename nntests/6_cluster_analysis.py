#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 10:35:57 2021

@author: max
"""

import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle

import os
# import json
import numpy as np
import matplotlib.pyplot as plt

with open('data/' + os.sep + 'X_embedded.pickle', 'rb') as handle:
    X_embedded = pickle.load(handle)

with open('data/' + os.sep + 'metadata.pickle', 'rb') as handle:
    metadata = pickle.load(handle)

with open('data/' + os.sep + 'n_clusters.pickle', 'rb') as handle:
    n_clusters = pickle.load(handle)

with open('data/' + os.sep + 'km_labels.pickle', 'rb') as handle:
    km_labels = pickle.load(handle)

with open('data/' + os.sep + 'km_centers.pickle', 'rb') as handle:
    km_centers = pickle.load(handle)

# %% meta per cluster

meta_per_cluster = {}

for i in range( n_clusters ):
    meta_per_cluster[i] = []

for i, k in enumerate( list( metadata.keys() ) ):
    meta_per_cluster[ km_labels[i] ].append( metadata[ k ] )