#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 23:38:29 2021

@author: max
"""

import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle

import os
import json
import numpy as np
import matplotlib.pyplot as plt

from sklearn.manifold import TSNE

with open('data/' + os.sep + 'states_data.pickle', 'rb') as handle:
    states_data = pickle.load(handle)

with open('data/' + os.sep + 'metadata.pickle', 'rb') as handle:
    metadata = pickle.load(handle)

h_final_np = states_data['h_final_np'][:,0,:]
c_final_np = states_data['c_final_np'][:,0,:]

# plt.imshow( h_final_np )
# plt.imshow( c_final_np )

# X_embedded = TSNE(n_components=2, learning_rate='auto', init='pca', verbose=2, n_iter=3000).fit_transform(c_final_np)
overall_states = np.c_[ np.squeeze( states_data['h_final_np'] ) , np.squeeze( states_data['h_final_np'] ) ]
X_embedded = TSNE(n_components=2, init='pca', verbose=2, n_iter=3000).fit_transform(overall_states)

with open('data/' + os.sep + 'X_embedded.pickle', 'wb') as handle:
    pickle.dump(X_embedded, handle, protocol=pickle.HIGHEST_PROTOCOL)

plt.clf()
plt.scatter( X_embedded[:,0], X_embedded[:,1], alpha=0.5, s=3 )
plt.savefig( 'data/tsne0.png', dpi=500 )

# also save 3D TSNE
lstm_tsne_3D_tonalities = TSNE(n_components=3, init='pca', verbose=2, n_iter=3000).fit_transform(overall_states)
with open('data/' + os.sep + 'lstm_tsne_3D_tonalities.pickle', 'wb') as handle:
    pickle.dump(lstm_tsne_3D_tonalities, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% clustering

from sklearn.cluster import KMeans

with open('data/lstm_tsne_3D_tonalities.pickle', 'rb') as handle:
    lstm_tsne_3D_tonalities = pickle.load(handle)

clusters_info = {}

for n_clusters in range(2,20,1):
    print('running for number of clusters: ', n_clusters)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(lstm_tsne_3D_tonalities)
    clusters_info[str(n_clusters)] = {
        'id_per_point': repr(list( kmeans.labels_ )),
        'centroids': {}
    }
    centroids = kmeans.cluster_centers_
    # min and max for normalization
    val_min = np.min( centroids, axis=0 )
    val_max = np.max( centroids, axis=0 )
    diff_max_min = val_max - val_min
    x = np.add( centroids, -val_min )
    d = 1/diff_max_min
    c = np.floor( np.power( np.multiply( x, d ) , 5 )*255).astype(int)
    for i in range( n_clusters ):
        clusters_info[str(n_clusters)]['centroids'][str(i)] = repr(list(list(c)[i]))

with open('data/' + os.sep + 'clusters_lstm_3D_tonalities.pickle', 'wb') as handle:
    pickle.dump(clusters_info, handle, protocol=pickle.HIGHEST_PROTOCOL)


# %% interactive hovering

# fig,ax = plt.subplots()
# sc = plt.scatter( X_embedded[:,0], X_embedded[:,1], alpha=0.5, s=3 )

# annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
#                     bbox=dict(boxstyle="round", fc="w"),
#                     arrowprops=dict(arrowstyle="->"))

# def update_annot(ind):
#     pos = sc.get_offsets()[ind["ind"][0]]
#     annot.xy = pos
#     # text = 'lala' + str(ind)
#     metakeys = list(metadata.keys())
#     idxs = ind["ind"]
#     text = metadata[metakeys[idxs[0]]]['all']
#     # text = ''
#     # for i in idxs:
#     #     text += metadata[metakeys[i]]['all'] + '\n'
#     # text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), 
#     #                        " ".join([names[n] for n in ind["ind"]]))
#     annot.set_text(text)
#     # annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
#     annot.get_bbox_patch().set_facecolor('red')
#     annot.get_bbox_patch().set_alpha(0.4)


# def hover(event):
#     vis = annot.get_visible()
#     if event.inaxes == ax:
#         cont, ind = sc.contains(event)
#         if cont:
#             update_annot(ind)
#             annot.set_visible(True)
#             fig.canvas.draw_idle()
#         else:
#             if vis:
#                 annot.set_visible(False)
#                 fig.canvas.draw_idle()

# fig.canvas.mpl_connect("motion_notify_event", hover)

# plt.show()