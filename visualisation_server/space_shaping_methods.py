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

import math

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
    d = np.pi/2 - a1
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
        plt.plot( hh[:,0], hh[:,1], 'x' );plt.plot(hh[i1,0], hh[i1,1], 'ro');plt.plot(hh[i2,0], hh[i2,1], 'ro')
        plt.text(hh[i1,0], hh[i1,1], k[i1])
        plt.text(hh[i2,0], hh[i2,1], k[i2])
    return hh
# end nn_shaping