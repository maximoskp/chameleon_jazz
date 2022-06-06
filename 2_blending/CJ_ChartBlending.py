# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 08:22:31 2022

@author: user
"""

import os
import numpy as np


class BlendingSession:
    def __init__(self, chart1, chart2):
        self.idiom1 = chart1
        self.idiom2 = chart2
        # keep chart names for making the blend name
        self.name_1 = self.idiom1.piece_name
        self.name_2 = self.idiom2.piece_name
        # compute property priorities for transitions in ontologies
        self.trans_ontologies_1 = self.compute_idiom_priorities( self.idiom1.chord_transitions, self.idiom2.chord_transitions )
        self.trans_ontologies_2 = self.compute_idiom_priorities( self.idiom2.chord_transitions, self.idiom1.chord_transitions )
    # end constructor
    
    def compute_idiom_priorities(self, t1, t2):
        for i in range( len( t1 ) ):
            t1[i] = self.compute_transition_priorities( t1[i], t1, t2 )
        return t1
    # end compute_idiom_priorities
    
    def compute_transition_priorities(self, trans, intra_trans, other_trans):
        # computes priorities for transition ontologies
        # trans: transitions to compute priorities for
        # idiom_trans: transition ontologies of the idiom that the trans belongs to
        # idiom_other: transition ontologies of the idiom that the trans doesn't belong to
        # HOME =================================================================
        # for each property, check how often it is used in the idioms
        for p_name in trans.properties_list:
            p = getattr( trans, p_name )
            # in case property is considered a single element
            if p['matching'] == 'chord_name' or p['matching'] == 'boolean':
                intra_idiom_count = 0
                for tr in intra_trans:
                    t = getattr( tr, p_name )
                    if p['matching'] == 'chord_name':
                        if np.array_equal( p['property'], t['property'] ):
                            intra_idiom_count = intra_idiom_count + 1
                    elif p['matching'] == 'boolean':
                        if p['property'] == t['property']:
                            intra_idiom_count = intra_idiom_count + 1
                # assign property value
                p['priority_idiom'] = intra_idiom_count/len( intra_trans )
            # in case property is an array of properties
            elif p['matching'] == 'subset_match':
                sub_intra_count = np.zeros( len(p['property']) )
                for i in range( len( p['property'] ) ):
                    for tr in intra_trans:
                        t = getattr( tr, p_name )
                        if p['property'][i] in t['property']:
                            sub_intra_count[i] = sub_intra_count[i] + 1
                # assign property value
                p['priority_idiom'] = sub_intra_count/len( intra_trans )
            else:
                print('Unknown matching type!')
        # AWAY =================================================================
        # for each property, check how often it is used in the idioms
        for p_name in trans.properties_list:
            p = getattr( trans, p_name )
            # in case property is considered a single element
            if p['matching'] == 'chord_name' or p['matching'] == 'boolean':
                other_idiom_count = 0
                for tr in other_trans:
                    t = getattr( tr, p_name )
                    if p['matching'] == 'chord_name':
                        if np.array_equal( p['property'], t['property'] ):
                            other_idiom_count = other_idiom_count + 1
                    elif p['matching'] == 'boolean':
                        if p['property'] == t['property']:
                            other_idiom_count = other_idiom_count + 1
                # assign property value
                p['priority_other'] = 1 - other_idiom_count/len( other_trans )
            # in case property is an array of properties
            elif p['matching'] == 'subset_match':
                sub_other_count = np.zeros( len(p['property']) )
                for i in range( len( p['property'] ) ):
                    for tr in other_trans:
                        t = getattr( tr, p_name )
                        if p['property'][i] in t['property']:
                            sub_other_count[i] = sub_other_count[i] + 1
                # assign property value
                p['priority_other'] = 1 - sub_other_count/len( other_trans )
            else:
                print('Unknown matching type!')
            p['priority'] = 0.5*p['priority_idiom'] + 0.5*p['priority_other']
            # print(p['priority'])
        return trans
    # end compute_transition_priorities