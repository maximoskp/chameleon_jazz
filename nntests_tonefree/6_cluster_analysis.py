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
import xlsxwriter

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

from collections import Counter, OrderedDict

stats_per_cluster = {}
for i in range( n_clusters ):
    stats_per_cluster[i] = {}

def get_prevalent_feature(cs):
    key = max(cs, key=cs.get)
    value = cs[key]
    if sum(cs.values()) > 0:
        value /= sum(cs.values())
    return {'key': key, 'value': value}

styles_all = []
sections_all = []
tempi_all = []
tonalities_all = []
time_signatures_all = []

for ckey in list( meta_per_cluster.keys() ):
    clusters = meta_per_cluster[ ckey ]
    titles = []
    styles = []
    sections = []
    tempi = []
    tonalities = []
    time_signatures = []
    for c in clusters:
        titles.append(c['title'])
        styles.append(c['styles'])
        styles_all.append(c['styles'])
        sections.append(c['sections'])
        sections_all.append(c['sections'])
        tempi.append(c['tempi'])
        tempi_all.append(c['tempi'])
        tonalities.append(c['tonalities'])
        tonalities_all.append(c['tonalities'])
        time_signatures.extend(c['time_signatures'])
        time_signatures_all.extend(c['time_signatures'])
    c_styles = Counter(styles)
    c_sections = Counter(sections)
    c_tempi = Counter(tempi)
    c_tonalities = Counter(tonalities)
    c_time_signatures = Counter(time_signatures)
    stats_per_cluster[ckey]['titles'] = titles
    stats_per_cluster[ckey]['styles'] = {'counter': c_styles, 'prevalent': get_prevalent_feature(c_styles)}
    stats_per_cluster[ckey]['sections'] = {'counter': c_sections, 'prevalent': get_prevalent_feature(c_sections)}
    stats_per_cluster[ckey]['tempi'] = {'counter': c_tempi, 'prevalent': get_prevalent_feature(c_tempi)}
    stats_per_cluster[ckey]['tonalities'] = {'counter': c_tonalities, 'prevalent': get_prevalent_feature(c_tonalities)}
    stats_per_cluster[ckey]['time_signatures'] = {'counter': c_time_signatures, 'prevalent': get_prevalent_feature(c_time_signatures)}
    # max(cs, key=cs.get)

# counters for all
styles_counter = Counter( styles_all )
sections_counter = Counter( sections_all )
tempi_counter = Counter( tempi_all )
tonalities_counter = Counter( tonalities_all )
time_signatures_counter = Counter( time_signatures_all )

# %% 

from copy import deepcopy

def stats_in_string(c_in, t=None, n=None):
    # c_in is a counter object
    # t is the total occurances counter for normalizing results, if necessary
    # n is the number of clusters
    c = deepcopy(c_in)
    s = []
    # c = OrderedDict(c.most_common())
    m = sum(c.values())
    for k in c.keys():
        if t is not None:
            if n is not None:
                # s.append( str(k) + ':' + str( c[k]/(t[k]/n) )[:4]  )
                c[k] = c[k]/(t[k]/n)
            else:
                # s.append( str(k) + ':' + str( c[k]/t[k] )[:4]  )
                c[k] = c[k]/t[k]
        else:
            # s.append( str(k) + ':' + str(c[k]/m)[:4]  )
            c[k] = c[k]/m
    c = OrderedDict(c.most_common())
    for k in c.keys():
        s.append( str(k) + ':' + str(c[k])[:4]  )
    return ', '.join(s)

# %%

workbook = xlsxwriter.Workbook('data/tsne_clusters.xlsx')
worksheet = workbook.add_worksheet()

worksheet.write('A1', 'Cluster ID')
worksheet.write('B1', 'Titles')
worksheet.write('C1', 'Styles')
worksheet.write('D1', 'Sections')
worksheet.write('E1', 'Tempi')
worksheet.write('F1', 'Tonalities')
worksheet.write('G1', 'Time Signatures')

num_clusters = len( list( stats_per_cluster.keys() ) )

for i in range( num_clusters ):
    worksheet.write('A'+str(i+2), str(i))
    worksheet.write('B'+str(i+2),', '.join( stats_per_cluster[i]['titles']))
    worksheet.write('C'+str(i+2), stats_in_string( stats_per_cluster[i]['styles']['counter'], styles_counter, num_clusters) )
    worksheet.write('D'+str(i+2), stats_in_string( stats_per_cluster[i]['sections']['counter'], sections_counter, num_clusters) )
    worksheet.write('E'+str(i+2), stats_in_string( stats_per_cluster[i]['tempi']['counter'], tempi_counter, num_clusters) )
    worksheet.write('F'+str(i+2), stats_in_string( stats_per_cluster[i]['tonalities']['counter'], tonalities_counter, num_clusters) )
    worksheet.write('G'+str(i+2), stats_in_string( stats_per_cluster[i]['time_signatures']['counter'], time_signatures_counter, num_clusters) )

workbook.close()

# %% 

plt.clf()
plt.scatter( X_embedded[:,0], X_embedded[:,1], c=km_labels, alpha=0.5, s=3 )
for i,c in enumerate(km_centers):
    plt.text(c[0], c[1], 'c_'+str(i), color='red', alpha=0.5)
plt.savefig( 'data/tsne_clusters_in_excel.png', dpi=500 )