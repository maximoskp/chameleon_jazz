import numpy as np
import os
import json
import pickle
import sys
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc
import matplotlib.pyplot as plt

file_name = 'experiment_blends.json'
blends = []
# # Open a file with access mode 'a' or 'w'
# file_object = open(file_name, 'w')

# %% load pickle

with open('../data/all_melody_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

with open('../data/globalHMM.pickle', 'rb') as handle:
    globalHMM = pickle.load(handle)

# %% print piece idxs

'''
# printed list at the end of the file
for i in range(len(all_structs)):
    print(str(i) + ': ' + all_structs[i].piece_name)
'''

# %% load pieces to blend

'''
34: Au Privave
44: Billie's Bounce
60: Blue Bossa
77: Cheese Cake
116: So What
130: Freddie Freeloader
133: Yesterdays
134: Cantaloupe island
157: All The Things You Are
160: Giant Steps
166: All of Me
173: Black Orpheus
204: Caravan
211: Afro Blue
233: Autumn Leaves
'''

# i1_pieces and i2_pieces should be of the same length
i1_pieces = [ 44,44,44,      60,60,60,     211,211,211,    116,116,116,    77,77,77,    204,204,204 ]
i2_pieces = [34,166,160,    77,166,160,    166,134,130,    204,173,160,   116,34,160,   157,116,160 ]

# i1_pieces = [ 211 ]
# i2_pieces = [ 134 ]

for i in range(len(i1_pieces)):
    # i1 will provide the melody and i2 the heaviest transition probabilities
    i1, i2 = i1_pieces[i], i2_pieces[i]

    s1, s2 = all_structs[i1], all_structs[i2]
    
    print(30*'-')
    print(s1.piece_name)
    print(s2.piece_name)

    # construct weighted "blended" transition matrix and get observations

    w1, w2, wGlobal = 0.0, 1.0, 0.0

    t1 = s1.hmm.transition_matrix.toarray()
    t2 = s2.hmm.transition_matrix.toarray()
    tGlobal = globalHMM.transition_matrix.toarray()
    trans_probs = (w1*t1 + w2*t2 + wGlobal*tGlobal)/(w1+w2+wGlobal)
    # zero-out t1
    # trans_probs[ t1 > 0 ] = 0
    # normalize
    for i in range(trans_probs.shape[0]):
        if np.sum( trans_probs[i,:] ) > 0:
            trans_probs[i,:] = trans_probs[i,:]/np.sum( trans_probs[i,:] )
    
    # m1 = s1.hmm.melody_per_chord.toarray()
    m2 = s2.hmm.melody_per_chord.toarray()
    mGlobal = globalHMM.melody_per_chord.toarray()
    # mel_per_chord_probs = w1*m1 + w2*m2 + wGlobal*mGlobal
    # mel_per_chord_probs = (w1+w2)*m2 + wGlobal*mGlobal
    # mel_per_chord_probs = m2
    mel_per_chord_probs = mGlobal
    for i in range(mel_per_chord_probs.shape[0]):
        if np.sum( mel_per_chord_probs[i,:] ) > 0:
            mel_per_chord_probs[i,:] = mel_per_chord_probs[i,:]/np.sum( mel_per_chord_probs[i,:] )
    
    emissions = s1.melody_information

    constraints = s1.constraints


    # apply HMM

    # pathIDXs, delta, psi, markov, obs = s1.hmm.apply_cHMM_with_constraints(trans_probs, mel_per_chord_probs, emissions, constraints, adv_exp=0.0)
    pathIDXs, delta, psi, markov, obs = s1.hmm.apply_cHMM_with_support(trans_probs, mel_per_chord_probs, emissions, constraints, tGlobal, adv_exp=0.0)

    transp_idxs = s1.transpose_idxs(pathIDXs, s1.tonality['root'])

    debug_constraints = np.array([pathIDXs,constraints])

    generated_chords = s1.idxs2chordSymbols(transp_idxs)

    generated_vs_initial = []
    for i in range(len(generated_chords)):
        generated_vs_initial.append( [constraints[i], generated_chords[i], s1.chords[i].chord_symbol] )

    new_unfolded = s1.substitute_chordSymbols_in_string( s1.unfolded_string, generated_chords )

    # costruct GJT-ready structure

    new_key = 'BL_' + s1.key + '-' + s2.key

    blended_piece = {
        new_key: {}
    }

    blended_piece[new_key]['string'] = new_unfolded
    blended_piece[new_key]['original_string'] = new_unfolded
    blended_piece[new_key]['unfolded_string'] = new_unfolded
    blended_piece[new_key]['original_string'] = new_key
    blended_piece[new_key]['appearing_name'] = 'BL_' + s1.piece_name + '-' + s2.piece_name
    blended_piece[new_key]['tonality'] = s1.tonality['symbol']

    # # Append string at the end of file
    # file_object.write(repr(blended_piece) + '\n')
    blends.append( blended_piece )

    # plot - debug

    os.makedirs('../figs', exist_ok=True)
    os.makedirs('../figs/experiment_hmm_debug', exist_ok=True)

    plt.clf()
    plt.imshow(trans_probs, cmap='gray_r')
    plt.savefig('../figs/experiment_hmm_debug/trans_probs' + s1.key.replace(' ', '_') + '-' + s2.key.replace(' ', '_') + '.png', dpi=500)

    plt.clf()
    plt.imshow(delta, cmap='gray_r')
    plt.savefig('../figs/experiment_hmm_debug/delta' + s1.key.replace(' ', '_') + '-' + s2.key.replace(' ', '_') + '.png', dpi=500)

    plt.clf()
    plt.imshow(markov, cmap='gray_r')
    plt.savefig('../figs/experiment_hmm_debug/markov' + s1.key.replace(' ', '_') + '-' + s2.key.replace(' ', '_') + '.png', dpi=500)

    plt.clf()
    plt.imshow(obs, cmap='gray_r')
    plt.savefig('../figs/experiment_hmm_debug/obs' + s1.key.replace(' ', '_') + '-' + s2.key.replace(' ', '_') + '.png', dpi=500)
# end for

# # Close the file
# file_object.close()

# %%
blends_dict = {}
for b in blends:
    blends_dict[ list(b.keys())[0] ] = list(b.values())[0]

# %%
with open(file_name, 'w') as outfile:
    json.dump(blends_dict, outfile)

# %% printed list 2022/11/13

'''
0: Come Rain Or Come Shine
1: The Best Thing For You Is me
2: Bags and Trane
3: I Remember You
4: The Very Thought Of You
5: Alice In Wonderland
6: Funkallero
7: If You Never Come To Me
8: Watch What Happens
9: Summer In Central Park
10: The Thrill Is Gone
11: High Fly
12: Backstage Sally
13: Laurie
14: Blue Silver
15: On The Street Where You Live
16: Everything I Love
17: If I Were A Bell
18: Black Narcissus
19: Polkadots And Moonbeams
20: The Core
21: Our Delight
22: Godchild
23: Wrap Your Troubles In Dreams
24: Chelsea Bridge
25: Everything Happens To Me
26: Chasin The Trane
27: The Jody Grind
28: Autumn In New York
29: This I Dig Of You
30: Imagination
31: A Flower Is A Lovesome Thing
32: Be My Love
33: Budo
34: Au Privave
35: Decision
36: Moonlight In Vermont
37: You Go To My Head
38: Georgia On My Mind
39: Wild Flower
40: Gone With The Wind
41: Four Brothers
42: catch me
43: When The Sun Comes Out
44: Billie's Bounce
45: Come Sunday
46: Dream Dancing
47: Alone Together
48: Little Waltz
49: Line For Lyons
50: The Chase
51: Don't Go To Strangers
52: Tangerine
53: Memories Of You
54: By Myself
55: Bewitched
56: Horace-Scope
57: Embraceable You
58: The Boy Next Door
59: A little tear
60: Blue Bossa
61: Blues For Wood
62: Desafinado
63: Along came Betty
64: Four
65: Bohemia After Dark
66: Well You Needn't
67: You Stepped Out Of A Dream
68: Up Jumped Spring
69: Cousin Mary
70: Monk's Mood
71: April In Paris
72: Too Close For Comfort
73: Tenor Madness
74: Trane's Blues
75: A Certain Smile
76: A Weaver Of Dreams
77: Cheese Cake
78: Four on six
79: Emily
80: Triste
81: Don't Get Around Much Anymore
82: Afternoon In Paris
83: A child is born
84: Misty
85: Freight Train
86: Day Dream
87: Everything I Have Is Yours
88: My Romanceteliko
89: Blue Moon
90: Voyage
91: Early Autumn
92: What's New
93: Taking A Chance On Love
94: There Will Never Be Another You
95: Angel Eyes
96: Blue Monk
97: Watermelon Man
98: The Song Is You
99: Ba-lue Bolivar Ba-lues-are
100: Fall
101: Lady Bird
102: Equinox
103: Lover Man
104: Birk's Works
105: Blue Daniel
106: Dig
107: All Or Nothing At All
108: One For My Baby
109: We'll Be Together Again
110: Elora
111: Feel Like Makin' Love
112: Flying Hometeliko
113: Take The A Train
114: Bernie's Tune
115: Straight No Chaser
116: So What
117: Criss Crossteliko
118: Incentive
119: All My Tomorrows
120: Eclypso
121: Willow Weep For Me
122: Barbara
123: You'd Be So Nice To Come Home To
124: Flintstones
125: Like Someone In Love
126: Bye Bye Blackbird
127: Nefertititeliko
128: April Skiesteliko
129: Skylar
130: Freddie Freeloader
131: Let's Fall In Love
132: Blame It On My Youth
133: Yesterdays
134: Cantaloupe island
135: Deep Purple
136: Hello
137: Jersey Bounce
138: The End Of A Love Affair
139: I Believe In You
140: Stormy Weather
141: Nobody Else But Me
142: Fools Rush In
143: The Sweetest Sounds
144: Gee Baby Ain't I Good To You
145: Off Minor
146: Oleo
147: Doxy
148: The Touch Of Your Lips
149: Too Marvelous For Words
150: Gentle Wind And Falling Tear
151: Dewey Square
152: Little Sunflower
153: The Summer Knows
154: Hackensack
155: What A Difference A Day Made
156: Anthropology
157: All The Things You Are
158: Darn That Dream
159: Happy Little Sunbeam
160: Giant Steps
161: Beautiful Love
162: These Foolish Things
163: You Must Believe In Spring
164: Bessie's Blues
165: I Thought About You
166: All of Me
167: It Could Happen To You
168: All God's Chillun Got Rhythm
169: Laura
170: It's Only a Paper Moon
171: Do You Know What It Means?
172: Blue And Sentimental
173: Black Orpheus
174: But Not For Me
175: I'm Old Fashioned
176: Gloria's Step
177: Do Nothin' Til You Hear From Me
178: You Do Something To Me
179: Time After Time
180: Wave
181: Sunny
182: Get Out Of Town
183: St. Thomas
184: Someday My Prince Will Come
185: Tenderly
186: I've Found A New Baby
187: Dearly Beloved
188: Cheryl
189: Favela
190: You've Changed
191: Chega De Saudade (No More Blues)
192: Who Can I Turn To
193: I Should Care
194: Song For My Father
195: Sweet Georgia Brown
196: Good Bait
197: Booker's Waltz
198: Fly Me To The Moon
199: Killer Joe
200: Old Folks
201: Down For Double
202: Diane
203: Good Morning Heartache
204: Caravan
205: East Of The Sun
206: Eighty One
207: On A Clear Day
208: A Sleepin Bee
209: Blues For Alice
210: Alfie's Theme
211: Afro Blue
212: Ask Me Now
213: Bunko
214: Epilogue
215: It Had To Be You
216: Black And Tan Fantasy
217: Jeannine
218: Bye Bye Baby
219: Long Ago And Far Away
220: Be-Bopτ
221: Bloomdidoteliko
222: Let's Cool One
223: As Time Goes By
224: A Fine Romance
225: Indiana (back home again in)
226: You Better Leave it Alone
227: Avalon
228: You And The Night And The Music
229: Yardbird Suite
230: Friday The 13th
231: Autumn In New York(D)
232: Blues In The Closet
233: Autumn Leaves
234: Satin Doll
235: Work Song
236: Love For Sale
237: In Walked Bud
238: Barbados
239: But Beautiful
240: Till There Was You
241: Hocus-Pocus
242: Where Or When
243: While We're Young
244: Bag's groove
245: They Say It's Wonderful
246: A Foggy Day
247: For Heaven's Sake
'''