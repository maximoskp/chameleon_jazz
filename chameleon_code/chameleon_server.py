import os
import glob
from flask import Flask, render_template, request, send_file, redirect, jsonify
import json
cwd = os.getcwd()
import sys
import pickle
# import datetime
# use folders of generation functions
sys.path.insert(0, cwd + '/CM_generate')
sys.path.insert(0, cwd + '/CM_auxiliary')
sys.path.insert(0, cwd + '/CM_NN_VL')
import CM_GN_harmonise_melody as hrm
import CM_user_output_functions as uof
import zipfile
import shutil
import numpy as np

__author__ = 'maxk'

# global harmonisation variables
idiom_name = 'BachChorales'
useGrouping = False
request_code = " "
name_suffix = " "
voiceLeading = "NoVL"
mode_in = 'Auto'

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=['POST'])
def upload():
    # use globals
    global useGrouping
    global request_code
    global idiom_name
    global name_suffix
    global voiceLeading
    global mode_in
    # print('request: ', request)
    if len(request.files.getlist("file")) < 1:
        return
    target = os.path.join(APP_ROOT, 'server_input_melodies/')
    
    # request_code = datetime.datetime.now().strftime("%I_%M_%S%p_%b_%d_%Y")
    # idiom_name = 'BachChorales'
    # useGrouping = True
    if not os.path.isdir(target):
        os.mkdir(target)
    
    # initialise a subfolder name for melodic inputs
    sub_target = 'melodies_'+request_code
    # make a folder to include input melodies
    if not os.path.isdir(target+sub_target):
        os.mkdir(target+sub_target)
    target = target+sub_target+'/'

    # initialise a subfolder for hamonised output IF many requests are given
    output = 'server_harmonised_output/'
    static_output_1 = 'static/harmonisations'
    static_output_2 = 'templates/static/harmonisations'

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)

        # parent_dir = os.path.abspath(os.path.join(cwd, os.pardir))
        melodyFolder = target
        # melodyFolder = cwd + '/input_melodies/'
        melodyFileName = filename

        # TODO: makei it properly - this is a temporary vl fix
        tmp_vl_string = 'simple'
        if voiceLeading == 'NoVL':
            print(voiceLeading)
            tmp_vl_string = 'simple'
        elif voiceLeading == 'BBVL':
            print(voiceLeading)
            tmp_vl_string = 'bidirectional_bvl'
        else:
            print('Unknown VL option!')
        # set mode_in
        m, idiom = hrm.harmonise_melody_with_idiom(melodyFolder, melodyFileName, idiom_name,targetFolder=output, mode_in=mode_in, use_GCT_grouping=useGrouping, voice_leading=tmp_vl_string, logging=False)
    
    # the output name as produced by chameleon
    initial_output_file_name = m.name+'_'+idiom_name+'.xml'
    # change the name by adding the code
    output_file_name = m.name+name_suffix+'.xml'
    # output_file_name = m.name+'_'+idiom_name+'_'+'grp'+str(int(useGrouping))+'_'+request_code+'.xml'
    os.rename('server_harmonised_output/'+initial_output_file_name, 'server_harmonised_output/'+output_file_name)
    output_file_with_path = 'server_harmonised_output/'+output_file_name

    # also write midi
    midi_name = m.name+name_suffix+'.mid'
    # midi_name = m.name+'_'+idiom_name+'_'+'grp'+str(int(useGrouping))+'_'+request_code+'.mid'
    output_path = os.path.join(APP_ROOT, 'server_harmonised_output/')
    uof.generate_midi(m.output_stream, fileName=midi_name, destination=output_path)
    output_midi_with_path = output_path+'/'+midi_name

    # copy to static folders for playback/display
    shutil.copy2(output_file_with_path, static_output_1)
    shutil.copy2(output_file_with_path, static_output_2)
    # also midi
    shutil.copy2(output_midi_with_path, static_output_1)
    shutil.copy2(output_midi_with_path, static_output_2)

    # prepare response
    #tmp_json = {}
    #tmp_json['initial_output_file_name'] = initial_output_file_name
    #return jsonify(tmp_json)
    return send_file(filename_or_fp=output_file_with_path, attachment_filename=output_file_name, as_attachment=True)
    #return 'file uploaded successfully'

@app.route("/get_idiom_names", methods=['POST'])
def get_idiom_names():
    #get all Idioms
    list_all = glob.glob('static/trained_idioms/*.pickle')
    list_bl = glob.glob('static/trained_idioms/bl_*.pickle')
    idiom_names_list = [item for item in list_all if item not in list_bl]
    # idiom_names_list = glob.glob('static/trained_idioms/*.pickle')
    allIdioms = {}
    for i in range( len( idiom_names_list ) ):
        ##########Check here#################
        # idiomName = idiom_names_list[i].split('\\')[-1].split('.')[0] #for Windows
        idiomName = idiom_names_list[i].split(os.sep)[-1].split('.')[0] #for Linux, Mac
        ####################################
        with open(idiom_names_list[i], 'rb') as fp:
            anIdiom = pickle.load(fp)
        # gather all modes
        allModes = list(iter(anIdiom.modes.keys()))
        # append mode name for each found mode
        mode_names = {}
        mode_names['[0 2 4 5 7 9 11]'] = 'Major/Ionian'
        mode_names['[0 2 3 5 7 8 10]'] = 'Minor/Aeolian'
        mode_names['[0 2 3 5 7 9 10]'] = 'Dorian'
        mode_names['[0 1 3 5 7 8 10]'] = 'Phrygian'
        mode_names['[0 2 4 5 7 9 10]'] = 'Mixolydian'
        mode_names['[0 2 4 6 7 9 11]'] = 'Lydian'
        mode_names['[0 1 4 5 7 8 10]'] = 'Phrygian dominant/Hijaz maqam'
        mode_names['[0 2 4 6 7 9 10]'] = 'Acoustic/Lydian dominant'
        mode_names['[0 2 3 6 7 8 11]'] = 'Hungarian minor/Gypsy minor'
        mode_names['[0 2 4 6 8 10]'] = 'Wholetone'
        mode_names['[0 1 2 3 4 5 6 7 8 9 10 11]'] = 'Chromatic'
        mode_names['[0 2 3 6 7 8 10]'] = 'Hungarian Gypsy'
        mode_names['[0 2 3 6 7 9 10]'] = 'Romanian Minor/Ukranian Dorian'
        mode_names['[0 1 3 4 6 7 9 10]'] = 'Octatonic H-W'
        mode_names['[0 2 3 5 6 8 9 11]'] = 'Octatonic W-H'
        for i in range(0,len(allModes)):
            if allModes[i] in list( mode_names.keys() ):
                allModes[i] = mode_names[allModes[i]] + ' - ' + allModes[i]
        # append 'Auto' - not necessary now
        #allModes = ['Auto'] + allModes       
        #append to the dictionary 
        allIdioms[idiomName] = allModes
        
    # return response
    return jsonify(allIdioms)

@app.route("/set_parameters", methods=['POST'])
def set_grouping():
    print('inside set_grouping')
    data = request.get_data()
    dat_json = json.loads(data.decode('utf-8'))
    # use globals
    global useGrouping
    global request_code
    global idiom_name
    global name_suffix
    global voiceLeading
    global mode_in
    useGrouping = dat_json['useGrouping']
    request_code = dat_json['clientID']
    idiom_name = dat_json['idiom_name']
    mode_in = dat_json['mode_name']
    voiceLeading = dat_json['voiceLeading']
    # set mode_in
    name_suffix = '_'+idiom_name+'_'+'grp'+str(int(useGrouping))+'_'+voiceLeading+'_'+request_code
    print('useGrouping: ', useGrouping)
    print('request_code: ', request_code)
    print('idiom_name: ', idiom_name)
    print('mode_in: ', mode_in)
    # prepare response
    tmp_json = {}
    tmp_json['success'] = True
    tmp_json['name_suffix'] = name_suffix
    return jsonify(tmp_json)

def check_harmonisation_mismatches(m):
    mismatches = False
    num_mismatches = 0
    for p in m.phrases:
        for s in p.melody_chord_segments:
            # get chord gct
            g = s.gct_chord
            # get chord pcs
            c_pcs = np.mod( g[0]+g[1:] , 12 )
            # get melody pcs
            m_pcs = s.relative_pcs
            # check if intersection is empty
            if np.intersect1d( c_pcs , m_pcs ).size < 1:
                mismatches = True
                num_mismatches = num_mismatches + 1
    return mismatches, num_mismatches

@app.route("/set_params_and_run", methods=['POST'])
def set_grouping_2():
    print('inside set_grouping_2')
    data = request.get_data()
    dat_json = json.loads(data.decode('utf-8'))
    # use globals
    global useGrouping
    global request_code
    global idiom_name
    global name_suffix
    global voiceLeading
    global mode_in
    #useGrouping = dat_json['useGrouping']
    useGrouping = False
    request_code = dat_json['clientID']
    idiom_name = dat_json['idiom_name']
    mode_in = dat_json['mode_name']
    voiceLeading = dat_json['voiceLeading']
    melody_idx = dat_json['melody_idx']
    # set mode_in
    name_suffix = '_'+idiom_name+mode_in+'_'+'grp'+str(int(useGrouping))+'_'+voiceLeading+'_'+request_code
    print('useGrouping: ', useGrouping)
    print('request_code: ', request_code)
    print('idiom_name: ', idiom_name)
    print('mode_in: ', mode_in)
    # prepare response
    tmp_json = {}
    tmp_json['success'] = True
    tmp_json['name_suffix'] = name_suffix

    # running harmonisation
    target = os.path.join(APP_ROOT, 'server_input_melodies/')
    if not os.path.isdir(target):
        os.mkdir(target)
    # initialise a subfolder for hamonised output IF many requests are given
    output = 'server_harmonised_output/'
    static_output_1 = 'static/harmonisations'
    static_output_2 = 'templates/static/harmonisations'
    # run on existing melody
    # __bug__fix__
    # filename = 'melody' + melody_idx + '.xml'
    filename = 'melody' + melody_idx + '.mxl'
    destination = "/".join([target, filename])
    melodyFolder = target
    melodyFileName = filename
    # TODO: makei it properly - this is a temporary vl fix
    tmp_vl_string = 'simple'
    if voiceLeading == 'NoVL':
        print(voiceLeading)
        tmp_vl_string = 'simple'
    elif voiceLeading == 'BBVL':
        print(voiceLeading)
        tmp_vl_string = 'bidirectional_bvl'
    else:
        print('Unknown VL option!')
    # set mode_in
    m, idiom = hrm.harmonise_melody_with_idiom(melodyFolder, melodyFileName, idiom_name,targetFolder=output, mode_in=mode_in, use_GCT_grouping=useGrouping, voice_leading=tmp_vl_string, logging=False)
    # check whether there are chord/melody mismatches
    mismatches, num_mismatches = check_harmonisation_mismatches(m)
    tmp_json['mismatches'] = mismatches
    tmp_json['num_mismatches'] = num_mismatches
    print('mismatches: ', mismatches, ' - num_mismatches: ', num_mismatches)
    # the output name as produced by chameleon
    initial_output_file_name = m.name+'_'+idiom_name+'.xml'
    # change the name by adding the code
    output_file_name = m.name+name_suffix+'.xml'
    # output_file_name = m.name+'_'+idiom_name+'_'+'grp'+str(int(useGrouping))+'_'+request_code+'.xml'
    os.rename('server_harmonised_output/'+initial_output_file_name, 'server_harmonised_output/'+output_file_name)
    output_file_with_path = 'server_harmonised_output/'+output_file_name

    # also write midi
    midi_name = m.name+name_suffix+'.mid'
    # midi_name = m.name+'_'+idiom_name+'_'+'grp'+str(int(useGrouping))+'_'+request_code+'.mid'
    output_path = os.path.join(APP_ROOT, 'server_harmonised_output/')
    uof.generate_midi(m.output_stream, fileName=midi_name, destination=output_path)
    output_midi_with_path = output_path+'/'+midi_name

    # copy to static folders for playback/display
    shutil.copy2(output_file_with_path, static_output_1)
    shutil.copy2(output_file_with_path, static_output_2)
    # also midi
    shutil.copy2(output_midi_with_path, static_output_1)
    shutil.copy2(output_midi_with_path, static_output_2)

    return jsonify(tmp_json)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8896, debug=True)
