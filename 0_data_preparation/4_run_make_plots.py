#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 18:56:11 2021

@author: max
"""

import numpy as np
import os
import json
import CJ_ChartClasses as ccc
import pickle

# %% load 

with open('../data/section_names.pickle', 'rb') as handle:
    section_names = pickle.load(handle)

with open('../data/section_features.pickle', 'rb') as handle:
    section_features = pickle.load(handle)

# %% plot sections

from sklearn.manifold import TSNE

X_embedded = TSNE(n_components=2, learning_rate='auto', init='random').fit_transform(section_features)