# Create a distance table
# usage: intersections.json http://my.osrm.server/

from sys import argv
import requests
import json
import csv

path, infile, host, outfile = argv

intersections = None

with open(infile) as inf:
    intersections = json.load(inf)

coords = []
for intersection in intersections['features']:
    coords.append(','.join(map(str, intersection['geometry']['coordinates'])))

url = host + 'table/v1/car/' + ';'.join(coords)
res = requests.get(url)
resJson = res.json()

if not 'durations' in resJson:
    print resJson

matrix = resJson['durations']

with open(outfile, 'w') as outCsv:
    writer = csv.writer(outCsv)
    writer.writerows(matrix)
