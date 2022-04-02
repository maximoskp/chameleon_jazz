#HOW TO RUN server.py
python server.py /path/to/csv/data
#specifically on chameleon:
python server.py /media/datadisk/gjt_data/generated_csvs

#HOW TO MAKE REQUESTS
#to get list of data:
http://155.207.188.7:5000/songslist

#to get piece by name and complexity values (rhythm and harmonic)
http://155.207.188.7:5000/songcsvcomplex?name=NAME_WITH_UNDERSCORES&r=3&h=3
# examples
http://155.207.188.7:5000/songcsvcomplex?name=ALL_THE_THINGS_YOU_ARE&r=3&h=3
http://155.207.188.7:5000/songcsvcomplex?name=ALL_OF_ME&r=1&h=2
http://155.207.188.7:5000/songcsvcomplex?name=GIANT_STEPS&r=4&h=5

#to get piece by index
http://155.207.188.7:5000/songcsv?index=10?