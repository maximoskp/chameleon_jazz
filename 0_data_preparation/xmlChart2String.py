#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 08:00:05 2019

@author: maximoskaliakatsos-papakostas
"""

# TODO:
# 1) process polychords and print them as A|B
# 2) incorporate rehearsal marks for style and tempo changes

import music21 as m21
import sys

def fixingType(t):
    # further fixing type
    # print(t)
    # remove add
    if 'add' in t and 'add9' not in t and 'add3sus' not in t and 'addb9' not in t:
        t = t.replace( 'add' , '' )
    # replace 7add3sus4
    if '7add3sus4' == t:
        t = t.replace( '7add3sus4' , '7add3sus' )
    # replace 7sus4add3
    if '7sus4add3' == t:
        t = t.replace( '7sus4add3' , '7add3sus' )
    # remove alter
    if 'alter' in t:
        t = t.replace( 'alter' , '' )
    # replace maj7
    if 'maj' in t:
        t = t.replace( 'maj' , "Δ" )
    # replace M
    if 'M' in t:
        t = t.replace( 'M' , "Δ" )
    if "\u0394" == t:
        t = t.replace( "\u0394" , " " )
    # replace half diminished
    if '/o' == t:
        t = t.replace( '/o' , "\u00f87" )
    if '/o7' == t:
        t = t.replace( '/o7' , "\u00f87" )
    if '/o/' in t: # could have bass afterwards
        t = t.replace( '/o/' , "\u00f87/" )
    if '/o7/' in t: # could have bass afterwards
        t = t.replace( '/o7/' , "\u00f87/" )
    if 'o7-' == t: # m21 bug?
        t = t.replace( 'o7-' , "o7" )
    if 'o7-/' in t: # m21 bug?
        t = t.replace( 'o7-/' , "o7/" )
    if 'o-/' in t: # m21 bug?
        t = t.replace( 'o-/' , "o/" )
    if 'm7b5' == t:
        t = t.replace( 'm7b5' , "\u00f87" )
    if "\u00f8" == t:
        t = t.replace( "\u00f8" , "\u00f87" )
    # replace diminished
    if 'dim' in t:
        t = t.replace( 'dim' , "o" )
    # remove spaces =================================================
    t = t.replace( ' ' , '' )
    # remove pedal
    if 'pedal' in t:
        t = t.replace( 'pedal' , ' ' )
    # replace 7b9sus4
    if '7b9sus4' == t:
        t = t.replace( '7b9sus4' , '7b9sus' )
    # replace 7sus4b9
    if '7sus4b9' == t:
        t = t.replace( '7sus4b9' , '7b9sus' )
    # replace sus79
    if 'sus79' == t:
        t = t.replace( 'sus79' , '9sus' )
    # replace sus7
    if 'sus7' == t:
        t = t.replace( 'sus7' , '7sus' )
    # replace 9sus41113
    if '9sus41113' == t:
        t = t.replace( '9sus41113' , '13sus' )
    if '9sus1113' == t:
        t = t.replace( '9sus1113' , '13sus' )
    # replace #5#9
    if '#5#9' == t:
        t = t.replace( '#5#9' , '7#9#5' )
    if '7#5#9' == t:
        t = t.replace( '7#5#9' , '7#9#5' )
    # misc replacements
    if '94subtract3' == t:
        t = t.replace( '94subtract3' , '9sus' )
    if '7b5#5b9#9' == t:
        t = t.replace( '7b5#5b9#9' , '7alt' )
    if '7b94subtract3' == t:
        t = t.replace( '7b94subtract3' , '7b9sus' )
    if 'm69' == t:
        t = t.replace( 'm69' , 'm6/9' )
    if 'm#7' == t:
        t = t.replace( 'm#7' , 'mΔ7' )
    if '69' in t:
        t = t.replace( '69' , '6/9' )
    if '7#5b9' == t:
        t = t.replace( '7#5b9' , '7b9#5' )
    if '7#11b9' == t:
        t = t.replace( '7#11b9' , '7b9#11' )
    if '7#11#9' == t:
        t = t.replace( '7#11#9' , '7#9#11' )
    if '7b13b9' == t:
        t = t.replace( '7b13b9' , '7b9b13' )
    # if '+' in t:
    #     t = t.replace( '+' , '(#5)' )
    if '(7#5)' == t:
        t = t.replace( '(7#5)' , '+' )
    if '7(#5)' == t:
        t = t.replace( '7(#5)' , '+' )
    if '(#5)' == t:
        t = t.replace( '(#5)' , '+' )
    if '(#5)/' in t:
        t = t.replace( '(#5)/' , '+/' )
    if '#5' == t:
        t = t.replace( '(#5)' , '+' )
    if '#5/' in t:
        t = t.replace( '#5/' , '+/' )
    # if '7#5' == t:
    #     t = t.replace( '7#5' , '+' )
    if '#5' == t:
        t = t.replace( '#5' , '+' )
    if '7#9b9' == t:
        t = t.replace( '7#9b9' , '7b9#9' )
    if '7#9b139' == t:
        t = t.replace( '7#9b139' , '7b9#9' )
    if 'm#5' == t:
        t = t.replace( 'm#5' , 'm(#5)' )
    if '7b5b9' == t:
        t = t.replace( '7b5b9' , '7b9b5' )
    # if 'sus' in t and not ('sus4' in t or 'sus2' in t):
    #     t = t.replace( 'sus' , 'sus4' )
    if 'sus2' in t:
        t = t.replace( 'sus2' , 'sus' )
    if 'sus4' in t:
        t = t.replace( 'sus4' , 'sus' )
    if '2' == t:
        t = t.replace( '2' , 'sus' )
    # if '11' == t:
    #     t = t.replace( '11' , '9sus' )
    if '13sus4' == t:
        t = t.replace( '13sus4' , '13sus' )
    if '134subtract3' == t:
        t = t.replace( '134subtract3' , '13sus' )
    if '7b134subtract3' == t:
        t = t.replace( '7b134subtract3' , '7b13sus' )
    if 'Power' == t:
        t = t.replace( 'Power' , '5' )
    if 'power' == t:
        t = t.replace( 'power' , '5' )
    if 'b5' == t:
        t = t.replace( 'b5' , "\u03947b5" )
    if 'm9b5' == t:
        t = t.replace( 'm9b5' , "\u00f89" )
    if 'm11b5' == t:
        t = t.replace( 'm11b5' , "\u00f811" )
    if '73sus' == t:
        t = t.replace( '73sus' , '7sus' )
    if 'sus791113' == t:
        t = t.replace( 'sus791113' , '13sus' )
    if 'susb97' == t:
        t = t.replace( 'susb97' , '13sus' )
    if 'sus37' == t:
        t = t.replace( 'sus37' , '7add3sus' )
    if 'susb137' == t:
        t = t.replace( 'susb137' , '7b13sus' )
    if "m\u039479" == t:
        t = t.replace( "m\u039479" , "m\u03949" )
    # if nothing has remained, it's a major
    if "" == t:
        t = ' '
    # if t not in chord_names and t not in chords_not_found:
    #     chords_not_found.append( t )
    return t

# move bass to end
def moveBassToEnd(t):
    for root in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        if '/' + root +'b' in t:
            t = t.replace('/' + root +'b', '')
            t = t + '/' + root +'b'
        if '/' + root +'-' in t:
            t = t.replace('/' + root +'-', '')
            t = t + '/' + root +'-'
        if '/' + root +'#' in t:
            t = t.replace('/' + root +'#', '')
            t = t + '/' + root +'#'
        if '/' + root in t and '/' + root +'b' not in t and '/' + root +'-' not in t and '/' + root +'#' not in t:
            t = t.replace('/' + root, '')
            t = t + '/' + root
    return t

# typical style names
typical_style_names = {
    'Swing': 'Swing',
    'swing': 'Swing',
    'Bossa Nova': 'Bossa Nova',
    'bossa nova': 'Bossa Nova',
    'bossanova': 'Bossa Nova',
    'Bossa nova': 'Bossa Nova',
    'Bossanova': 'Bossa Nova',
    'Even 8ths': 'Even 8ths',
    'even 8ths': 'Even 8ths',
    'Even 16ths': 'Even 16ths',
    'even 16ths': 'Even 16ths',
    'Open Even 8ths': 'Open Even 8ths',
    'open even 8ths': 'Open Even 8ths',
    'Open even 8ths': 'Open Even 8ths',
    'Open even 8': 'Open Even 8ths',
    'Open Even 16ths': 'Open Even 16ths',
    'open even 16ths': 'Open Even 16ths',
    'Open even 16ths': 'Open Even 16ths',
    'Open even 16': 'Open Even 16ths',
    'modern Jazz': 'Modern Jazz',
    'Modern Jazz': 'Modern Jazz',
    'Modern jazz': 'Modern Jazz',
    'modern jazz': 'Modern Jazz',
    'modernjazz': 'Modern Jazz',
    'Modernjazz': 'Modern Jazz',
    'ModernJazz': 'Modern Jazz',
    'Medium Swing': 'Medium Swing',
    'Medium swing': 'Medium Swing',
    'medium swing': 'Medium Swing',
    'Mambo': 'Mambo',
    'mambo': 'Mambo',
    'samba': 'Samba',
    'Samba': 'Samba',
    'Open Swing': 'Open Swing',
    'open swing': 'Open Swing',
    'Open swing': 'Open Swing',
    'Afro-Cuban': 'Afro-Cuban',
    'Afro-cuban': 'Afro-Cuban',
    'afro-cuban': 'Afro-Cuban',
    'Afro Cuban': 'Afro-Cuban',
    'Afro cuban': 'Afro-Cuban',
    'afro cuban': 'Afro-Cuban',
    'New Orleans': 'New Orleans',
    'New orleans': 'New Orleans',
    'new Orleans': 'New Orleans',
    'new orleans': 'New Orleans',
    'Free': 'Free',
    'free': 'Free'
}

def chart2string( file_name, print_interim=False, chord_names=[] ):
    print('running: ' + file_name)
    # keep chord types that have not been found in the dictionary / chord_names
    chords_not_found = []
    # initialise output string
    s = ''
    # parse piece
    sm21 = m21.converter.parse(file_name)
    # supposing that there is only one part
    p = sm21.parts[0]
    # p.show('t')
    # iterate through measures
    ms = p.getElementsByClass('Measure')
    # get repeat brackets on score
    repeatBrackets = p.getElementsByClass(m21.spanner.RepeatBracket)
    # initialize measure index
    m_idx = 1
    # initialise running time signature
    running_ts = []
    # iterate through measures
    for m in ms:
        if print_interim:
            print('TMP print: bar number: ' + str(m_idx))
        '''
        # print measure symbol and print time signature
        # check if we have running signature or if it can be found in measure
        ts = m.getElementsByClass('TimeSignature')
        if running_ts == [] and len(ts) == 0:
            sys.exit('ERROR in xmlChartString.py: no initial time signature for piece')
        else:
            if len(ts) == 1:
                running_ts = str(ts[0].numerator) + '/' + str(ts[0].denominator)
            elif len(ts) > 1:
                print('WARNING in xmlChartString.py: more than 1 ts found - Keeping 1st')
                running_ts = str(ts[0].numerator) + '/' + str(ts[0].denominator)
        if print_interim:
            print('bar~' + running_ts + ',')
        s += 'bar~' + running_ts + ','
        '''
        # check for section and print section symbol
        # get rehearsal marks
        rms = m.getElementsByClass( m21.expressions.RehearsalMark )
        # check any rehearsal mark
        if len(rms) > 0:
            # for all rehearsal marks, check what they are
            for rm in rms:
                rm_type = infereRehearsalMarkType( rm.content )
                if rm_type == 'undefined':
                    if print_interim:
                        print('rm: ', rm)
                    print('rm: ', rm)
                    sys.exit('ERROR in xmlChartString.py: undefined rehearsal mark')
                elif rm_type != '':
                    if rm_type == 'tempo_tonality':
                        # split tempo from tonality
                        tempo = rm.content.split('_')[0]
                        tonality = rm.content.split('_')[1]
                        if print_interim:
                            print('tempo' + '~' + tempo + ',')
                        s += 'tempo' + '~' + tempo + ','
                        if print_interim:
                            print('tonality' + '~' + tonality + ',')
                        s += 'tonality' + '~' + tonality + ','
                    elif rm_type == 'style':
                        if print_interim:
                            print('style' + '~' + typical_style_names[rm.content] + ',')
                        s += 'style' + '~' + typical_style_names[rm.content] + ','
                    else:
                        if print_interim:
                            print(rm_type + '~' + rm.content + ',')
                        s += rm_type + '~' + rm.content + ','
        # print measure symbol and print time signature
        # check if we have running signature or if it can be found in measure
        ts = m.getElementsByClass('TimeSignature')
        if running_ts == [] and len(ts) == 0:
            sys.exit('ERROR in xmlChartString.py: no initial time signature for piece')
        else:
            if len(ts) == 1:
                running_ts = str(ts[0].numerator) + '/' + str(ts[0].denominator)
            elif len(ts) > 1:
                print('WARNING in xmlChartString.py: more than 1 ts found - Keeping 1st')
                running_ts = str(ts[0].numerator) + '/' + str(ts[0].denominator)
        if print_interim:
            print('bar~' + running_ts + ',')
        s += 'bar~' + running_ts + ','
        # iterate through chord symbols and print them with their offset
        cs = m.getElementsByClass('ChordSymbol')
        # first check for polychords - chords with same onset
        # keep all chords and their offsets in two lists
        chords = []
        offsets = []
        for c in cs:
            root, figure_type = getRootTypeFromFigure( c.figure )
            # check if chords is part of polychord
            if c.offset in offsets:
                # get index of polychord
                tmp_idx = offsets.index( c.offset )
                # construct polychord
                chords[ tmp_idx ] += '|' + (root+figure_type)
            else:
                chords.append( root+figure_type )
                offsets.append( c.offset )
            # do chord check
            if len( chord_names ) > 0:
                if figure_type not in chord_names and figure_type not in chords_not_found:
                    chords_not_found.append( figure_type )
        # print chords and offsets
        for i in range(len(chords)):
            if print_interim:
                print('chord~' + chords[i] + '@' + str(offsets[i]) + ',')
            s += 'chord~' + chords[i] + '@' + str(offsets[i]) + ','
        # check for accents
        r = getAccents( m )
        for a in r:
            if print_interim:
                print('accent@' + str(a) + ',')
            s += 'accent@' + str(a) + ','
        # check for repeat start/end
        r = checkRepeatStartEnd( m )
        if r == 'start':
            if print_interim:
                print('repeatStart,')
            s += 'repeatStart,'
        elif r == 'end':
            if print_interim:
                print('repeatEnd,')
            s += 'repeatEnd,'
        elif r == 'both':
            if print_interim:
                print('repeatStart,')
                print('repeatEnd,')
            s += 'repeatStart,' + 'repeatEnd,'
        # check for repeat version start/end
        r = checkRepeatVersionStart( m_idx , repeatBrackets )
        if r > 0:
            if print_interim:
                print('repeatVersionStart~' + str(r) + ',')
            s += 'repeatVersionStart~' + str(r) + ','
        r = checkRepeatVersionEnd( m_idx , repeatBrackets )
        if r > 0:
            if print_interim:
                print('repeatVersionEnd~' + str(r) + ',')
            s += 'repeatVersionEnd~' + str(r) + ','
        # increase measure idx
        m_idx += 1
    # add ending
    if print_interim:
        print('end')
    s += 'end'
    # check if tonality has been initialised
    try:
        tonality
    except NameError:
        print("TONALITY UNDEFINED!")
        tonality = -1
    return s, tonality, chords_not_found
# end chart2string

def getRootTypeFromFigure(f):
    # check if it comes from polychord
    if f[0] == '/':
        f = f[1:]
    # initialise type
    t = " "
    r = f
    if len(f) > 1:
        split_idx = 1
        # isolate type - remove root
        if f[1] == '#' or f[1] == 'b' or f[1] == '-':
            split_idx = 2
        t = f[split_idx:]
        r = f[:split_idx]
        if split_idx == len(f):
            t = " "
        else:
            # CAUTION: the following needs to be also applied to hidden_sequences_library.py
            # TODO: check if it works
            # print(t)
            t = moveBassToEnd(t)
            t = fixingType(t)
            # print('fixed: ', t)
            # TODO: replace type symbol
    if len(t) == 0:
        print('f: ', f)
    return r, t

def infereRehearsalMarkType( r ):
    t = 'undefined'
    if r in['A', 'B', 'C', 'D']:
        t = 'section'
    if is_number(r):
        t = 'tempo'
    # CAUTION if the following array is modified
    # make sure changes are added to typical_style_names
    if r in ['Swing', 'swing', 'Bossa Nova', 'bossa nova', 
             'bossanova', 'Bossa nova', 'Bossanova', 'even 8ths', 'Even 8ths',
             'even 16ths', 'Even 16ths',
             'Open Even 8ths', 'open even 8ths', 'Open even 8ths', 'Open even 8',
             'Open Even 16ths', 'open even 16ths', 'Open even 16ths', 'Open even 16',
             'Modern Jazz', 'modern Jazz', 'Modern jazz', 'modern jazz',
             'Medium Swing', 'Medium swing', 'medium swing',
             'modernjazz', 'Modernjazz', 'ModernJazz', 'Mambo', 'mambo',
             'Samba', 'samba',
             'Open Swing', 'open swing', 'Open swing',
             'Afro-Cuban', 'Afro-cuban', 'afro-cuban', 'Afro Cuban',
             'Afro cuban', 'afro cuban',
             'New Orleans', 'New orleans', 'new Orleans', 'new orleans',
             'Free', 'free']:
        t = 'style'
    if '_' in r:
        t = 'tempo_tonality'
    if r == '':
        t = ''
    return t
# end infereRehearsalMarkType


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
# end is_number

def getAccents( m ):
    # m: measure to check
    result = []
    # get notes in measure
    ns = m.getElementsByClass('Note')
    # iterate notes and look for accents
    for n in ns:
        # check for articulations
        artcs = n.articulations
        if len(artcs) > 0:
            # check if articulation is accent
            for a in artcs:
                if a.name == 'accent':
                    result.append( n.offset )
    return result
# end getAccents

def checkRepeatStartEnd( m ):
    # m: measure to check
    result = 'none' # means no repeat
    # get possibly repeat marks
    r = m.getElementsByClass(m21.repeat.RepeatMark)
    # check if repeat marks exist
    if len(r) > 0:
        # check if repeat mark is start, end or both
        if len(r) > 1:
            result = 'both'
        else:
            result = r[0].direction
    return result
# end checkRepeatVersionStart

def checkRepeatVersionStart( m_idx , rb ):
    # m_idx: index of measure to check
    # rb: all repeat brackets
    result = -1 # means no repeat
    # guard erroneous inclusion of two brackets
    already_found = False
    for r in rb:
        if r.getFirst().measureNumber == m_idx:
            result = r.getNumberList()
            # check if many repeat signs exist
            if len(result) > 1 or already_found:
                sys.exit('ERROR in xmlChart2String.py: more than one repeat version signs')
            else:
                result = result[0]
                already_found = True
    return result
# end checkRepeatVersionStart

def checkRepeatVersionEnd( m_idx , rb ):
    # m_idx: index of measure to check
    # rb: all repeat brackets
    result = -1 # means no repeat
    # guard erroneous inclusion of two brackets
    already_found = False
    for r in rb:
        if r.getLast().measureNumber == m_idx:
            result = r.getNumberList()
            # check if many repeat signs exist
            if len(result) > 1 or already_found:
                sys.exit('ERROR in xmlChart2String.py: more than one repeat version signs')
            else:
                result = result[0]
                already_found = True
    return result
# end checkRepeatVersionStart

def unfold_chart(s):
    # split in bar
    bars = s.split('bar')
    # repetition markers
    repStart = -1
    repEnd = -1
    repApplyAfter = -1
    i = 0
    while i < len(bars):
        b = bars[i]
        if 'repeatStart' in b:
            repStart = i
        if 'repeatVersionStart' in b:
            repEnd = i
        if 'repeatEnd' in b:
            repApplyAfter = i+1
            if repEnd == -1:
                repEnd = i
            # apply repetition
            repetition_part = bars[repStart:repEnd]
            for j in range( len(repetition_part)-1, -1, -1 ):
                r = repetition_part[j]
                bars.insert( repApplyAfter , r )
                i += 1
        i += 1
    return 'bar'.join(bars)
# end unfold_chart