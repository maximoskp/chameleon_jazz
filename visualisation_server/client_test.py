import requests
import json

response = requests.get("http://localhost:5000/songslist")
names = response.json()
print('list: ', names)

response = requests.get("http://localhost:5000/songcsv?name=" + names[10])
songcsv = response.json()
print('songcsv: ', songcsv)