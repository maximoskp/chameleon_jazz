# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 08:22:31 2022

@author: user
"""

import os
import numpy as np
import sys
sys.path.append('..' + os.sep +'0_data_preparation')
import computeDIC as dic

class Transition:
    def __init__(self, c1_np, c2_np):
        # print('initialising transition with chords: ', c1_np, ' - ', c2_np)
        self.properties_list = ['from_chord_np', 'to_chord_np', 'from_rpc', 'to_rpc', 'dic_has_0', 'dic_has_1', 'dic_has_N1', 'asc_semitone_to_root', 'desc_semitone_to_root', 'semitone_to_root']
        # remember to retrive object property from string of attribute as:
        # attr = getattr( obj, STR_ATTR )
        self.from_chord_np = {
            'property': c1_np,
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'chord_name',
            'necessary': True,
        }
        self.to_chord_np = {
            'property': c2_np,
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'chord_name',
            'necessary': True
        }
        self.from_rpc = {
            'property': np.mod( c1_np[0]+c1_np[1:], 12 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'subset_match',
            'necessary': True
        }
        self.to_rpc = {
            'property': np.mod( c2_np[0]+c2_np[1:], 12 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'subset_match',
            'necessary': True,
        }
        self.dic_has_0 = {
            'property': self.compute_dic_value( c1_np, c2_np, 0 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.dic_has_1 = {
            'property': self.compute_dic_value( c1_np, c2_np, 1 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.dic_has_N1 = {
            'property': self.compute_dic_value( c1_np, c2_np, -1 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.asc_semitone_to_root = {
            'property': (11 in c1_np) and (0 in c2_np),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.desc_semitone_to_root = {
            'property': (1 in c1_np) and (0 in c2_np),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.semitone_to_root = {
            'property': ( (1 in c1_np) and (0 in c2_np) ) or ( (11 in c1_np) and (0 in c2_np) ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.blending_score = 0
    # end constructor

    def compute_dic_value(self, c1, c2, d):
        b = False
        p1 = np.mod( c1[0]+c1[1:], 12 )
        p2 = np.mod( c2[0]+c2[1:], 12 )
        v,ids = dic.computeDICfromMIDI(p1,p2)
        if v[ np.where( ids == d )[0][0] ] > 0:
            b = True
        return b
    # end compute_dic_value
# end Transition class

class BlendingSession:
    def __init__(self, chart1, chart2):
        self.idiom1 = chart1
        self.idiom2 = chart2
        self.possible_gcts_np = chart1.all_states_np
        # keep chart names for making the blend name
        self.name_1 = self.idiom1.piece_name
        self.name_2 = self.idiom2.piece_name
        # compute property priorities for transitions in ontologies
        self.trans_ontologies_1 = self.compute_idiom_priorities( self.idiom1.chord_transitions, self.idiom2.chord_transitions )
        self.trans_ontologies_2 = self.compute_idiom_priorities( self.idiom2.chord_transitions, self.idiom1.chord_transitions )
        # construct all blending diamonds - input1, input2, generic, blends
        self.blending_diamonds = self.construct_diamonds()
        # filter chords in dictionary according to generic space constraints
        # also rate blends along the process
        self.blending_diamonds = self.generic_filter_and_rate()
        # run through each diamond and keep a total of best blends
        self.best_ab_blends, self.best_ba_blends = self.select_best_blends()
        
    # end constructor
    
    def compute_idiom_priorities(self, t1, t2):
        for k in list( t1.keys() ):
            t1[k] = self.compute_transition_priorities( t1[k], t1, t2 )
        return t1
    # end compute_idiom_priorities
    
    def compute_transition_priorities(self, trans, intra_trans, other_trans):
        # computes priorities for transition ontologies
        # trans: transitions to compute priorities for
        # idiom_trans: transition ontologies of the idiom that the trans belongs to
        # idiom_other: transition ontologies of the idiom that the trans doesn't belong to
        # HOME =================================================================
        # for each property, check how often it is used in the idioms
        print('trans:', trans)
        for p_name in trans.properties_list:
            p = getattr( trans, p_name )
            # in case property is considered a single element
            if p['matching'] == 'chord_name' or p['matching'] == 'boolean':
                intra_idiom_count = 0
                for k in intra_trans.keys():
                    tr = intra_trans[k]
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
                    for k in intra_trans.keys():
                        tr = intra_trans[k]
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
                for k in other_trans.keys():
                    tr = other_trans[k]
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
                    for k in other_trans.keys():
                        tr = other_trans[k]
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
    
    def construct_diamonds(self):
        diamonds = []
        for k1 in self.trans_ontologies_1.keys():
            t1 = self.trans_ontologies_1[k1]
            for k2 in self.trans_ontologies_2.keys():
                t2 = self.trans_ontologies_2[k2]
                g = self.compute_generic_space(t1, t2)
                # a chain has two transitions, one that goes form space X to new and one from new to space Y
                diamonds.append( {'input1': t1, 'input2': t2, 'generic': g, 'ab_chains': [], 'ba_chains': [], 'ab_scores': [], 'ba_scores': []} )
        return diamonds
    # end construct_triplets
    
    def compute_generic_space(self, t1, t2):
        g = Transition( t1.from_chord_np['property'] , t1.to_chord_np['property'])
        for p_name in t1.properties_list:
            p1 = getattr( t1, p_name )
            p2 = getattr( t2, p_name )
            pg = getattr( g, p_name )
            if p1['matching'] == 'chord_name':
                if not np.array_equal( p1['property'], p2['property'] ):
                    pg['property'] = 'empty'
            elif p1['matching'] == 'boolean':
                if p1['property'] != p2['property']:
                    pg['property'] = 'empty'
            elif p1['matching'] == 'subset_match':
                pg['property'] = np.intersect1d( p1['property'], p2['property'] )
                if len( pg['property'] ) == 0:
                    pg['property'] = 'empty'
        return g
    # end compute_generic_space
    
    def generic_filter_and_rate(self):
        # iterate over all generic spaces and return dictionary elements that comply with restrictions
        dd = 0
        for d in self.blending_diamonds:
            print('dd: ', dd)
            dd += 1
            # possible chains from a to b, which will be filtered and rated (as chains) at the time they get generated
            t_ab = []
            t_ba = []
            # keep all scores
            ab_scores = []
            ba_scores = []
            # construct all possible ab chains
            for c in self.possible_gcts_np:
                # A->B chains =====================================================================
                # form both components of the chain
                ab_1_transition = Transition( d['input1'].from_chord_np['property'] , c )
                ab_2_transition = Transition( c , d['input2'].to_chord_np['property'] )
                # check generic space of each component
                ab_1_gen_check = self.check_generic_constraints( ab_1_transition , d['generic'] )
                ab_2_gen_check = self.check_generic_constraints( ab_2_transition , d['generic'] )
                # keep only chains that have both transitions valid
                if ab_1_gen_check and ab_2_gen_check:
                    ab_1_transition = self.rate_blend(ab_1_transition , d['input1'], d['input2'])
                    ab_2_transition = self.rate_blend(ab_2_transition , d['input1'], d['input2'])
                    t_ab.append( [ab_1_transition, ab_2_transition] )
                    ab_scores.append( ab_1_transition.blending_score + ab_2_transition.blending_score )
                # B->A chains =====================================================================
                # form both components of the chain
                ba_1_transition = Transition( d['input2'].from_chord_np['property'] , c )
                ba_2_transition = Transition( c , d['input1'].to_chord_np['property'] )
                # check generic space of each component
                ba_1_gen_check = self.check_generic_constraints( ba_1_transition , d['generic'] )
                ba_2_gen_check = self.check_generic_constraints( ba_2_transition , d['generic'] )
                # keep only chains that have both transitions valid
                if ba_1_gen_check and ba_2_gen_check:
                    ba_1_transition = self.rate_blend(ba_1_transition , d['input1'], d['input2'])
                    ba_2_transition = self.rate_blend(ba_2_transition , d['input1'], d['input2'])
                    t_ba.append( [ba_1_transition, ba_2_transition] )
                    ba_scores.append( ba_1_transition.blending_score + ba_2_transition.blending_score )
            # append to the diamond structure
            print('--------- ab: ', len(t_ab))
            print('--------- ba: ', len(t_ba))
            d['ab_chains'] = t_ab
            d['ab_scores'] = ab_scores
            d['ba_chains'] = t_ba
            d['ba_scores'] = ba_scores
        return self.blending_diamonds
    # end generic_filter_and_rate
    
    def rate_blend(self, b, i1, i2):
        # initiase a score of zero
        s = 0
        for p_name in b.properties_list:
            # get blend property
            pb = getattr( b, p_name )
            # get properties of inputs
            pi1 = getattr( i1, p_name )
            pi2 = getattr( i2, p_name )
            if pb['matching'] == 'chord_name':
                if np.array_equal( pb['property'] , pi1['property'] ):
                    # get half reward from each input
                    s = s + pi1['priority']/2
                if np.array_equal( pb['property'] , pi2['property'] ):
                    # get half reward from each input
                    s = s + pi2['priority']/2
            elif pb['matching'] == 'boolean':
                if pb['property'] == pi1['property']:
                    s = s + pi1['priority']/2
                if pb['property'] != pi2['property']:
                    s = s + pi2['priority']/2
            elif pb['matching'] == 'subset_match':
                inclusion = np.isin( pi1['property'] , pb['property'] )
                if np.any( inclusion ):
                    s = s + np.sum( pi1['priority'][inclusion] )/(2*np.sum(inclusion))
                inclusion = np.isin( pi2['property'] , pb['property'] )
                if np.any( inclusion ):
                    s = s + np.sum( pi2['priority'][inclusion] )/(2*np.sum(inclusion))
        b.blending_score = s
        return b
    # end rate_blend
    
    def check_generic_constraints(self, t, g):
        # assume it satisfies generic space constraints
        b = True
        for p_name in t.properties_list:
            # get generic space property
            pg = getattr( g, p_name )
            # check if generic space has a restriction for this property
            if pg['property'] is not 'empty':
                # get transition property
                pt = getattr( t, p_name )
                if pt['matching'] == 'chord_name':
                    if not np.array_equal( pt['property'] , pg['property'] ):
                        b = False
                        break
                elif pt['matching'] == 'boolean':
                    if pt['property'] != pg['property']:
                        b = False
                        break
                elif pt['matching'] == 'subset_match':
                    if not np.all( np.isin( pg['property'] , pt['property'] ) ):
                        b = False
                        break
        return b;
    # end check_generic_constraints
    
    def select_best_blends(self):
        print('selecting best blends')
        # list of best blended transitions and their rates
        best_ab_blends = []
        best_ab_scores = []
        best_ba_blends = []
        best_ba_scores = []
        # iterate through diamonds and keep the single best blend from each
        for d in self.blending_diamonds:
            # get maximum score index
            # A->B chains =======================================================
            if len( d['ab_scores'] ) > 0:
                idx = np.argmax( d['ab_scores'] )
                best_ab_blends.append( d['ab_chains'][idx] )
                best_ab_scores.append( d['ab_scores'][idx] )
            # B->A chains =======================================================
            if len( d['ba_scores'] ) > 0:
                idx = np.argmax( d['ba_scores'] )
                best_ba_blends.append( d['ba_chains'][idx] )
                best_ba_scores.append( d['ba_scores'][idx] )
        # sort blends based on their scores
        # A->B chains =======================================================
        best_ab_scores = np.array( best_ab_scores )
        idxs_ab = np.argsort( -best_ab_scores )
        best_ab_scores = best_ab_scores[idxs_ab]
        best_ab_blends = [best_ab_blends[i] for i in idxs_ab]
        # B-> chains =======================================================
        best_ba_scores = np.array( best_ba_scores )
        idxs_ba = np.argsort( -best_ba_scores )
        best_ba_scores = best_ba_scores[idxs_ba]
        best_ba_blends = [best_ba_blends[i] for i in idxs_ba]
        return best_ab_blends, best_ba_blends
    # end select_best_blends
# end BlendingSession class