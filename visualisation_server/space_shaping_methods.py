#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 22:42:51 2022

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
from matplotlib.gridspec import GridSpec
import math
from sklearn.decomposition import NMF
# just for loading mnist
import tensorflow as tf
from tensorflow import keras

def NMF_preprocessing(x, d):
    model = NMF(n_components=d, init='random', random_state=0)
    W = model.fit_transform(x)
    H = model.components_
    return W
# end NMF_preprocessing

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return np.array([qx, qy])
# end rotate

def angle_stretch(x , i1, i2):
    a1 = math.atan2( x[i1,1], x[i1,0] )
    a2 = math.atan2( x[i2,1], x[i2,0] )
    rand_mult = 0.001
    if a1 < a2:
        a1,a2 = a2,a1
    while abs(a1-a2) < 0.001:
        r = np.random.rand( x.shape[0] )
        x[:,1] = x[:,1] + rand_mult*r
        a1 = math.atan2( x[i1,1], x[i1,0] )
        a2 = math.atan2( x[i2,1], x[i2,0] )
        rand_mult += 0.001
    d = np.pi - a1
    # print('i1', i1)
    # print('i2', i2)
    # print('a1', a1)
    # print('a2', a2)
    # print('d', d)
    for i in range( x.shape[0] ):
        a = math.atan2( x[i,1], x[i,0] )
        x[i,:] = rotate( [0,0], x[i,:] , (d+a2)*(a-a2)/(a1-a2) - a2 )
    return x
# end angle_stretch

def differential_plotting(h, i1, i2, k=None, alpha=1.0, stretch=True, plot=True):
    # make axis multiplier
    w = np.c_[ h[i1,:] , h[i2,:] ]
    # make reduction
    hh = h@w
    # print('hh[i1,:]', hh[i1,:])
    # print('hh[i2,:]', hh[i2,:])
    if stretch:
        hh = angle_stretch( hh, i1, i2 )
    if plot:
        plt.clf()
        plt.plot( hh[:,0], hh[:,1], 'x' );plt.plot(hh[i1,0], hh[i1,1], 'ro');plt.plot(hh[i2,0], hh[i2,1], 'ro', alpha=alpha)
        if k is not None:
            plt.text(hh[i1,0], hh[i1,1], str(k[i1]))
            plt.text(hh[i2,0], hh[i2,1], str(k[i2]))
    return hh
# end differential_plotting

def nn_shaping( piece_name1, piece_name2, tonality=True, plot=False, nonnegativity=False, stretch=True ):
    datapath = '../nntests_tonefree/data/'
    if tonality:
        datapath = '../nntests/data/'
    with open(datapath + 'states_data.pickle', 'rb') as handle:
        states_data = pickle.load(handle)
    with open(datapath + 'metadata.pickle', 'rb') as handle:
        metadata = pickle.load(handle)
    # get states combined
    h = np.c_[ np.squeeze( states_data['h_final_np'] ) , np.squeeze( states_data['h_final_np'] ) ]
    if nonnegativity:
        h -= np.min(h)
    # get piece name keys
    k = list( metadata.keys() )
    # get piece indexes
    i1 = k.index( piece_name1 )
    i2 = k.index( piece_name2 )
    hh = differential_plotting( h, i1, i2, k=k, alpha=1.0, stretch=True, plot=True )
    return hh
# end nn_shaping

def mnist_example_save():
    mnist = keras.datasets.mnist
    (X_train_full, y_train_full), (X_test, y_test) = mnist.load_data()
    x_mnist = np.reshape(X_test, (10000, 784))
    h_mnist = NMF_preprocessing(x_mnist, 10)
    y_mnist = y_test
    if not os.path.exists('data'):
        os.makedirs('data')
    with open('data/' + os.sep + 'x_mnist.pickle', 'wb') as handle:
        pickle.dump(x_mnist, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('data/' + os.sep + 'h_mnist.pickle', 'wb') as handle:
        pickle.dump(h_mnist, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('data/' + os.sep + 'y_mnist.pickle', 'wb') as handle:
         pickle.dump(y_mnist, handle, protocol=pickle.HIGHEST_PROTOCOL)
# end mnist_example_save

def mnist_shaping( digit1, digit2, plot=True, stretch=True ):
    datapath = 'data/'
    with open(datapath + 'x_mnist.pickle', 'rb') as handle:
        x_mnist = pickle.load(handle)
    with open(datapath + 'h_mnist.pickle', 'rb') as handle:
        h_mnist = pickle.load(handle)
    with open(datapath + 'y_mnist.pickle', 'rb') as handle:
        y_mnist = pickle.load(handle)
    # get piece indexes
    where1 = np.where( digit1 == y_mnist )[0]
    i1 = where1[ np.random.randint(0,where1.size) ]
    where2 = np.where( digit2 == y_mnist )[0]
    i2 = where2[ np.random.randint(0,where2.size) ]
    hh = differential_plotting( h_mnist, i1, i2, k=y_mnist, alpha=1.0, stretch=True, plot=False )
    # plot
    fig = plt.figure(constrained_layout=True, figsize=(4, 6))
    gs = GridSpec(nrows=3, ncols=2, figure=fig)
    ax1 = fig.add_subplot(gs[:2, :])
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax2 = fig.add_subplot(gs[2, 0])
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax3 = fig.add_subplot(gs[2, 1])
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax1.plot( hh[:,0], hh[:,1], 'kx', alpha=0.3);ax1.plot(hh[i1,0], hh[i1,1], 'ro');ax1.plot(hh[i2,0], hh[i2,1], 'ro')
    k = y_mnist
    ax1.text(hh[i1,0], hh[i1,1], str(k[i1]))
    ax1.text(hh[i2,0], hh[i2,1], str(k[i2]))
    ax2.imshow( np.reshape( x_mnist[i1,:] , (28,28) ), cmap='gray_r')
    ax3.imshow( np.reshape( x_mnist[i2,:] , (28,28) ), cmap='gray_r')
    plt.show()
    # plt.clf()
    # plt.subplot(3,2,1)
    # plt.plot( hh[:,0], hh[:,1], 'x');plt.plot(hh[i1,0], hh[i1,1], 'ro');plt.plot(hh[i2,0], hh[i2,1], 'ro', alpha=0.5)
    # k = y_mnist
    # if k is not None:
    #     plt.text(hh[i1,0], hh[i1,1], str(k[i1]))
    #     plt.text(hh[i2,0], hh[i2,1], str(k[i2]))
    # plt.subplot(3,2,5)
    # plt.imshow( np.reshape( x_mnist[i1,:] , (28,28) ), cmap='gray_r')
    # plt.subplot(3,2,6)
    # plt.imshow( np.reshape( x_mnist[i2,:] , (28,28) ), cmap='gray_r')
    return hh
# end nn_shaping