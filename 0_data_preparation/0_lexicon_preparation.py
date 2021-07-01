#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 10:51:44 2019

@author: maximoskaliakatsos-papakostas
"""

import music21 as m21
import os
import numpy as np
import json

cwd = os.getcwd()

folder_name = '..' + os.sep + 'data' + os.sep + 'Lexikon'
file_name = 'Lexikon.mxl'

# load file
s = m21.converter.parse( folder_name + os.sep + file_name )
# iterate through parts and fill the dictionary
type2pcs_dictionary = {}
for p in s.parts:
    # get first measure to obtain chord pc
    m = p.getElementsByClass('Measure')
    # get extended chord from 1st measure
    c = m[0].getElementsByClass('Chord')
    if len(c.pitches) > 0:
        pcs = []
        for pitch in c.pitches:
            pcs.append( int( np.mod(pitch.midi , 12 ) ) )
        tmp_type_name = p.partName
        if len(tmp_type_name) == 1:
            tmp_type_name = " "
        else:
            # check if polychord lower
            if tmp_type_name[0] == '/':
                tmp_type_name = '/' + tmp_type_name[2:]
            else:
                tmp_type_name = tmp_type_name[1:]
        
        # modes are not necessary in new version
        tmp_dic = {"extended_type": pcs}
        '''
        # get modes from next measures
        for i in range(5):
            c = m[1+i].getElementsByClass('Chord')
            if len(c) > 0:
                pcs = []
                for pitch in c.pitches:
                    pcs.append( int( np.mod(pitch.midi , 12 ) ) )
                tmp_dic['modes'].append(pcs)
            else:
                break;
        '''
        type2pcs_dictionary[ tmp_type_name ] = tmp_dic
        # print( tmp_type_name + ': ' + repr(tmp_dic['extended_type']) + ' - ' + repr(tmp_dic['modes']) )
        print( tmp_type_name + ': ' + repr(tmp_dic['extended_type']) )

with open( folder_name + os.sep + 'type2pcs_dictionary.json', 'w') as f:
    json.dump(type2pcs_dictionary, f)

print('number of types: ', len( list(type2pcs_dictionary.keys()) ))