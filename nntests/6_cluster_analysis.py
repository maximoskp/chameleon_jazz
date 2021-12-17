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

# %% stats per cluster

from collections import Counter

stats_per_cluster = {}
for i in range( n_clusters ):
    stats_per_cluster[i] = {}

def get_prevalent_feature(cs):
    key = max(cs, key=cs.get)
    value = cs[key]
    if sum(cs.values()) > 0:
        value /= sum(cs.values())
    return {'key': key, 'value': value}

for ckey in list( meta_per_cluster.keys() ):
    clusters = meta_per_cluster[ ckey ]
    styles = []
    sections = []
    tempi = []
    tonalities = []
    time_signatures = []
    for c in clusters:
        styles.append(c['styles'])
        sections.append(c['sections'])
        tempi.append(c['tempi'])
        tonalities.append(c['tonalities'])
        time_signatures.extend(c['time_signatures'])
    c_styles = Counter(styles)
    c_sections = Counter(sections)
    c_tempi = Counter(tempi)
    c_tonalities = Counter(tonalities)
    c_time_signatures = Counter(time_signatures)
    stats_per_cluster[ckey]['styles'] = {'counter': c_styles, 'prevalent': get_prevalent_feature(c_styles)}
    stats_per_cluster[ckey]['sections'] = {'counter': c_sections, 'prevalent': get_prevalent_feature(c_sections)}
    stats_per_cluster[ckey]['tempi'] = {'counter': c_tempi, 'prevalent': get_prevalent_feature(c_tempi)}
    stats_per_cluster[ckey]['tonalities'] = {'counter': c_tonalities, 'prevalent': get_prevalent_feature(c_tonalities)}
    stats_per_cluster[ckey]['time_signatures'] = {'counter': c_time_signatures, 'prevalent': get_prevalent_feature(c_time_signatures)}
    # max(cs, key=cs.get)


# %% 

plt.clf()
plt.scatter( X_embedded[:,0], X_embedded[:,1], c=km_labels, alpha=0.5, s=3 )
for i,c in enumerate(km_centers):
    plt.text(c[0], c[1], 'c_'+str(i), color='red', alpha=0.5)
    plt.text(c[0], c[1]-2.5, stats_per_cluster[i]['styles']['prevalent']['key'] + ': ' + str(stats_per_cluster[i]['styles']['prevalent']['value'])[:4], color='red', alpha=0.5)
    plt.text(c[0], c[1]-5., stats_per_cluster[i]['tonalities']['prevalent']['key'] + ': ' + str(stats_per_cluster[i]['tonalities']['prevalent']['value'])[:4], color='red', alpha=0.5)
plt.savefig( 'data/tsne_clusters_info.png', dpi=500 )