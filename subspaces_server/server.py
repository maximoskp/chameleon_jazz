from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import json
import os
import csv
import sys
import pandas as pd
import re
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc
sys.path.append('..' + os.sep +'3_harmonization')
import blending_styles_module as bsm
sys.path.append('..' + os.sep +'3_harmonization')
import aux_output as aux_output
import music21
from music21 import converter, stream, meter, key, chord, harmony, pitch, layout, expressions, note


# Open necessary pickles and jsons
with open('../data/all_melody_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)
with open('songnames.json') as json_file:
    songs_with_melodies = json.load(json_file)
with open('../data/stylesHMM.pickle', 'rb') as handle:
    stylesHMM = pickle.load(handle)

# Load the chord symbol mapping from the provided JSON
with open('../data/json_files/type2pcs_dictionary.json', 'r') as json_file:
    chord_mapping = json.load(json_file)

api = Flask(__name__)
CORS(api)

cors = CORS(api, resources={r"/api/*": {"origins": "*"}})

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

@api.route("/")
def index():
    return render_template("index.html")
    
songs_with_melodies_names = [struct.piece_name for struct in all_structs]
harmonic_context = list(stylesHMM[list(stylesHMM.keys())[0]].keys())
genre_style = list(stylesHMM[list(stylesHMM.keys())[1]].keys())
names_in_list = all_structs[0].metadata.index.tolist()
names_in_list_test = all_structs[12].piece_name

@api.route('/stylesHMM', methods=['GET'])
def get_stylesHMM():
    # example run: http://localhost:5000/stylesHMM
    stylesHMM_keys = {
        "harmonic": harmonic_context,
        "genre": genre_style
    }
    return jsonify(stylesHMM_keys)
# end stylesHMM

@api.route('/songsnameslist', methods=['GET'])
def get_songslist():
    # example run: http://localhost:5000/songsnameslist
    return jsonify(songs_with_melodies_names)
# end songsnameslist

@api.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('static/xml/', filename)

@api.route('/receive-user-option', methods=['POST'])
def receive_user_option():
    if request.method == 'POST':

        data = request.data.decode("utf-8")  # Decode the incoming data

        jsondata = json.loads(data)

        # Open a file for writing (use a context manager to ensure the file is properly closed)
        with open("debug_output.txt", "w") as debug_file:
            # Use the print function to write the variable's value to the file
            print(jsondata["song_name"], file=debug_file)
            print(songs_with_melodies, file=debug_file)
        try: 
            matching_index = songs_with_melodies.index(jsondata["song_name"])
            print(f"Index of: {matching_index}")
        except ValueError:
            print("'PARA VER AS MENINAS' not found in the list")

        song_name_underscore = jsondata["song_name"].replace(" ", "_")
        # Replace single quotes with underscores if they are not adjacent to underscores
        if "'" in song_name_underscore and ("_'" not in song_name_underscore) and ("'_") not in song_name_underscore:
            song_name_underscore = song_name_underscore.replace("'", "_")

        song_name_underscore = song_name_underscore.replace("'", "")
        song_name_underscore = song_name_underscore.replace("-", "_")
        print(song_name_underscore)

        # Assuming the directory path is Documents/repos/chameleon_jazz/data/Songs/Library_melodies
        directory_path = "../data/Songs/Library_melodies"

        # Construct the full filename by joining song_name_underscore with ".xml"
        filename_to_search = f"{song_name_underscore}.mxl"

        # Construct the full path of the file
        full_path_to_search = os.path.join(directory_path, filename_to_search)

        string_split = jsondata["blending_characteristic"].split(": ")
        piece_idx = matching_index
        style_type = string_split[0]
        style_subtype = string_split[1]

        b, s = bsm.blend_piece_with_style( piece_idx, style_type, style_subtype )

        # Get the first key dynamically
        first_key = list(b.keys())[0]

        # Access the 'string' value
        string_value = b[first_key]["string"]

        pattern = r"chord~(.*?)@"

        result = re.findall(pattern, string_value)
        # print("result:", result)
        # Check if the file exists
        if os.path.exists(full_path_to_search):
            # # Assuming the full path to the XML file is stored in full_path_to_search
            score = converter.parse(full_path_to_search)
            # print(f"Found: {full_path_to_search}")
            # #score = converter.parse(full_path_to_search)

            # # Function to print all chords in a measure
            # def print_chords(measure):
            #     for element in measure:
            #         if 'ChordSymbol' in element.classes:
            #             root_note = 'C'
            #             chord_type = 'dominant-seventh'  # 7 (dominant seventh)
            #             added_tone = 'M3'  # major third
            #             suspended_note = 'D'  # 2nd or 4th

            #             # Create a ChordSymbol object with the specified components
            #             new_chord_symbol = harmony.ChordSymbol(f'{root_note}{chord_type}{added_tone}({suspended_note})')

            #             # Replace the original chord symbol with the new chord symbol
            #             measure.replace(element, new_chord_symbol)

            #             # print(element)

            # def get_chord_pitches(chord_symbol):
            #     # Extract the root and extended type from the chord symbol
            #     if len(chord_symbol) > 1 and chord_symbol[1] in ('b', '#'):
            #         root = chord_symbol[:1]
            #         extended_type = chord_symbol[2:]
            #     else:
            #         root = chord_symbol[0]
            #         extended_type = chord_symbol[1:]
            #     # print("Root is: ", root)
            #     # print("Extended type is: ", extended_type)
                
    

            #     # Check if the root is in the mapping
            #     if extended_type in chord_mapping:
            #         # Get the extended type pitches from the mapping
            #         extended_type_intervals = chord_mapping[extended_type].get("extended_type", [])

            #         # Map the extended type intervals to pitches
            #         pitches = [pitch.Pitch(root + "4").transpose(interval) for interval in extended_type_intervals]

            #         # Convert pitches to strings
            #         pitch_strings = [str(p) for p in pitches]

            #         return pitch_strings

            #     else:
            #         print(f"Root note '{extended_type}' not found in the mapping.")
            #         return []
            

            # # Example usage:
            # resulting_pitches = []
            # for element in result:
            #     resulting_pitches.append(get_chord_pitches(element))
            
            # c = []
            # csymbol = []
            # for element in resulting_pitches:
            #     print("Element: ",element)
            #     c.append(chord.Chord(element))
                
            # for element in c :
            #     csymbol.append(harmony.chordSymbolFigureFromChord(element, True))    
            # # print(c)
            # print("csymbol is: ",csymbol)
            # replacement_chords = csymbol
            # Iterator for replacement chords
            replacement_iterator = iter(result)
            
            # Iterate through measures in the first part of the score
            for measure in score.parts[0].getElementsByClass('Measure'):

                for element in measure:
                    #print(element)
                    if isinstance(element, harmony.ChordSymbol):
                        try:
                            new_chord_symbol = next(replacement_iterator)
                            n = measure.getElementAtOrBefore(element.offset, classList=(note.Note, note.Rest, chord.Chord))
                            print("new_chord_symbol:", new_chord_symbol, n)
                            n.lyric = new_chord_symbol                            
                        except StopIteration:
                            break

               

            def generate_xml(sc, fileName="test_xml.xml", destination="/Users/maximoskaliakatsos-papakostas/Documents/python/miscResults/"):
                mf = music21.musicxml.m21ToXml.GeneralObjectExporter(sc)
                mfText = mf.parse().decode('utf-8')
                f = open(destination + fileName, 'w')
                f.write(mfText.strip())
                f.close()

            def generate_midi(sc, fileName="test_midi.mid", destination="/Users/maximoskaliakatsos-papakostas/Documents/python/miscResults/"):
                # we might want the take the name from uData information, e.g. the uData.input_id, which might preserve a unique key for identifying which file should be sent are response to which user
                mf = music21.midi.translate.streamToMidiFile(sc)
                mf.open(destination + fileName, 'wb')
                mf.write()
                mf.close()

            # Specify the filename for the new score
            output_filename = song_name_underscore + "_blended_with_" + style_subtype
            generate_xml(score, output_filename + '.xml', "static/xml/")
            generate_midi(score, output_filename + '.mid', "static/midi/")
            # Save the altered score to a MusicXML file
            
            

        else:
            print(f"File not found: {full_path_to_search}")


        # print(b)
        # print(s)
        

        return s

if __name__ == '__main__':
    # api.run()
    # api.run(host='0.0.0.0', port=5000, debug=True)
    api.run(ssl_context=('/home/maximos/Documents/SSL_certificates/server.crt', '/home/maximos/Documents/SSL_certificates/server.key'), host='0.0.0.0', port=5001, debug=True)
