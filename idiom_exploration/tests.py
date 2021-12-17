#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 14:17:59 2021

@author: max
"""

import music21 as m21
import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle

import os
# import json
import numpy as np
import matplotlib.pyplot as plt

import CM_TR_TrainingIdiom_class as trc
import CM_TonalityGrouping_classes as tgr
import GCT_functions as gct
import CM_Misc_Aux_functions as msf
import harmonisation_printer as hpr
import Grouping_functions as gfn

with open('../data/idioms/' + os.sep + 'mainChords.pickle', 'rb') as handle:
    mainChords = pickle.load(handle)

# %% 

modes = mainChords.modes
m = modes[ list(modes.keys())[0] ]

cadences = m.cadences
interm_cads = cadences['intermediate']
final_cads = cadences['final']

# %% 

import idiom_printer as ipr

ipr.print_cadences(m, 'data/cads')
ipr.print_gcts(m, 'data/gcts')
ipr.print_markov(m, 'data/markov')