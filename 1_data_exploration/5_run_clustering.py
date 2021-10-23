import numpy as np
import os
import json
import pickle
import matplotlib.pyplot as plt

# %% load 
print('loading data')
with open('../data/X_embedded.pickle', 'rb') as handle:
    X_embedded = pickle.load(handle)

with open('../data/discarded_idx.pickle', 'rb') as handle:
    discarded_idx = pickle.load(handle)

# %% clustering
print('clustering')
from sklearn.cluster import KMeans
n_clusters = 30
kmeans = KMeans(n_clusters=n_clusters, n_init=30, max_iter=1000, verbose=1)
km_labels = kmeans.fit_predict(X_embedded)
km_centers = kmeans.cluster_centers_

# %% save clusters
with open('../data/n_clusters.pickle', 'wb') as handle:
    pickle.dump(n_clusters, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/km_labels.pickle', 'wb') as handle:
    pickle.dump(km_labels, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/km_centers.pickle', 'wb') as handle:
    pickle.dump(km_centers, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% plot clusters
plt.clf()
plt.scatter( X_embedded[:,0], X_embedded[:,1], c=km_labels, alpha=0.5, s=3 )
for i,c in enumerate(km_centers):
    plt.text(c[0], c[1], 'c_'+str(i), color='red', alpha=0.5)
plt.savefig( '../data/tsne_clusters0.png', dpi=500 )