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

h_final_np = states_data['h_final_np'][:,0,:]
c_final_np = states_data['c_final_np'][:,0,:]

# plt.imshow( h_final_np )
# plt.imshow( c_final_np )

X_embedded = TSNE(n_components=2, learning_rate='auto', init='pca', verbose=2, n_iter=3000).fit_transform(c_final_np)

plt.clf()
plt.scatter( X_embedded[:,0], X_embedded[:,1], alpha=0.5, s=3 )
# plt.savefig( '../data/tsne0.png', dpi=500 )

# %% interactive hovering

fig,ax = plt.subplots()
sc = plt.scatter( X_embedded[:,0], X_embedded[:,1], alpha=0.5, s=3 )

annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))

def update_annot(ind):
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    text = 'lala'
    # text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), 
    #                        " ".join([names[n] for n in ind["ind"]]))
    annot.set_text(text)
    # annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
    annot.get_bbox_patch().set_facecolor('red')
    annot.get_bbox_patch().set_alpha(0.4)


def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

plt.show()