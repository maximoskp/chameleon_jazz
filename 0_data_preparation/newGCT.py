# -*- coding: utf-8 -*-
"""
Created on Wed May 26 18:22:46 2021

@author: KonGiannos
"""

from itertools import permutations
import numpy as np

def HARM_findPitchClassesfromChord(chord):
    modChord = [i % 12 for i in chord] #modulo 12 to chord list to take the pitch classes
    return modChord

def HARM_takeOnlyUniqueValues(modChord):
    # remove duplicates and preserve order
    m = []
    for e in modChord:
        if e not in m:
            m.append(e)
    return m

def last_element_sum(m,candidates,consWeights):
    chord = []
    cons = []
    for i in range(len(candidates)):
        for j in m:
            if (j not in candidates[i]):
                r=0
                for k in range(len(candidates[i])):
                    interval = (j-candidates[i][k])%12
                    r += consWeights[interval]
                queue = [x for x in candidates[i]] 
                queue.append(j)
                chord.append(queue)
                cons.append(r)
    candidate_locations = np.where( np.min(cons) == cons )[0]
    candidates = []
    for i in candidate_locations:
        candidates.append(chord[i])
    return  candidates, candidate_locations

#stack_of_thirds = [0,7,5,1,1,3,2,2,2,2,4,6]
#quartal = [0,3,2,1,1,1,1,2,2,2,1,1] ????
#wholetone = [0,3,1,3,1,3,1,3,2,3,2,3]
#atonal = [0,1,1,1,1,1,1,2,2,2,2,2]

def GCT_sum_all_from_root(m,consWeights=[0,7,5,1,1,2,3,1,2,2,4,6]):
    m = HARM_findPitchClassesfromChord(m) #midi-pitch modulo 12
    m = HARM_takeOnlyUniqueValues(m) #Remove duplicates
    if (len(m)==1): #case for singletons (set with one pitch)
        gct = [m[0]%12]
        ties = False
    else: #cases for sets with more than one element
        cons = []
        pairs = list(permutations(m,2))
        for i in range(len(pairs)): #consonance rating for each ordered pair
            interval = (pairs[i][1] - pairs[i][0])%12
            r = consWeights[interval]
            cons.append(r)
        candidate_locations = np.where( np.min(cons) == cons )[0] #find the pairs with smallest rating
        candidates = []
        for i in candidate_locations:
            candidates.append( pairs[i] )
        '''candidates = [[i] for i in m]'''
        #!!!define a function and call it on repeat
        while len(candidates[0])!=len(m):
            #sum of all ratings for all possible distances before the assigned pitch
            candidates, candidate_locations = last_element_sum(m,candidates,consWeights)
        ties = False
        if len(candidates)>1: #there are several optimal ways to arrange the pitches
            candidates = [candidates[0]] #pick the first
            ties = True    
        root = candidates[0][0] #assign the first pitch as root
        chord = [(x-root)%12 for x in candidates[0]] #subtract root for the set to start with 0
        for k in range(len(chord)-1): #add extensions in increasing order and in several octaves
            while (chord[k+1]<chord[k]):
                chord[k+1] += 12
        gct = [root,chord]
    return gct,ties

def GCT_in_key(m,k=0):
    gct = GCT_sum_all_from_root(m)[0]
    gct[0] = (gct[0] - k)%12
    final_gct = gct
    return final_gct