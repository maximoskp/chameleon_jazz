HOW TO RUN server.py

python server.py /path/to/csv/data

HOW TO MAKE REQUESTS
to get list of data:
http://155.207.188.7:5000/songslist

to get piece by name and complexity values (rhythm and harmonic)
http://155.207.188.7:5000/songcsvcomplex?name="NAME_WITH_UNDERSCORES"&r=3&h=3

to get piece by index
http://155.207.188.7:5000/songcsv?index=10?