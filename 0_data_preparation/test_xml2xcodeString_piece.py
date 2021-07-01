#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 19:28:55 2019

@author: maximoskaliakatsos-papakostas
"""

import xmlChart2String
import sys

# get number of arguments:
num_args = len(sys.argv)

if num_args <= 1:
    print('ERROR: not enough input arguments. Run as:')
    print('==========================================')
    print('python RELATIVE/PATH/TO/FILE')
    print('==========================================')
else:
    # file_name = 'Lullaby_Of_Birdland.musicxml'
    for i in range(1, len(sys.argv), 1):
        file_name = str( sys.argv[i] )
        s = xmlChart2String.chart2string( file_name )
        print('string to paste in Xcode:')
        print(s)
        print('==========================================')