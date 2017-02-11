#!/usr/bin/python

# Convert an OSM file into a CSV of intersections and numbers for them
# Usage: extract_intersections.py file.osm.pbf out.csv

# Copyright (C) 2014-2017 Matthew Wigginton Conway.

from imposm.parser import OSMParser
from sys import argv
from pyproj import Proj, transform
from collections import defaultdict
import csv
import json

# define an OSM parser
class IntersectionFinder(object):
    def __init__(self, states):
        # Track all loaded nodes, with x, y, etc.
        self.nodes = {}

        self.states = states

        # track edge counts for nodes
        # we use a separate dict so that ways and nodes don't have to load in order
        self.nodeRefs = defaultdict(lambda: 0)

        # Track nodes in state-names avenues
        self.nodesInStateAvenues = defaultdict(lambda: [])

        self.wayCount = 0
        self.nodeCount = 0

    # use a coords callback because we want all intersections even if there are no tags
    def coords_callback(self, coords):
        for osmid, lon, lat in coords:
            self.nodes[osmid] = dict(osmid=osmid, lon=lon, lat=lat, ways=0, names=set())

            self.nodeCount += 1
            if self.nodeCount % 100000 == 0:
                print '%sk nodes' % (self.nodeCount / 1000)

    def ways_callback(self, ways):
        for osmid, tags, nodes in ways:
            if 'name' in tags:
                # find intersections with named drivable streets
                if 'highway' in tags and tags['highway'] not in ['footway', 'bridleway', 'steps', 'path']:
                    for node in nodes:
                        self.nodeRefs[node] += 1

                # Check if this is a state-named avenue
                lowerName = tags['name'].lower()
                for state, abbr in self.states.iteritems():
                    if lowerName.find(state) == 0 and not lowerName == 'washington boulevard': # only at beginning, dont catch GW Pkwy or C&O Canal
                        self.nodesInStateAvenues[abbr] += nodes
                        break # it can only be one state avenue

            self.wayCount += 1
            if self.wayCount % 100000 == 0:
                print '%sk ways' % (self.wayCount / 1000)


    # remove nodes that don't have more than one way
    def filter_nodes(self):
        for abbr, nodes in self.nodesInStateAvenues.iteritems():
            # should not be a concurrent modification issue, we are not adding/removing keys
            self.nodesInStateAvenues[abbr] = [n for n in nodes if self.nodeRefs[n] > 1]

    def toGeoJSON(self):
        nodes = []
        for abbr, memberNodes in self.nodesInStateAvenues.iteritems():
            for node in memberNodes:
                nodes.append((node, abbr))

        return {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [self.nodes[node]['lon'], self.nodes[node]['lat']]
                    },
                    'properties': {
                        'state': abbr
                    }
                } for node, abbr in nodes
            ]
        }

    def parse(self, filename):
        parser = OSMParser(concurrency=4, coords_callback=self.coords_callback, ways_callback=self.ways_callback)
        parser.parse(filename)

if __name__ == '__main__':
    states = dict()

    with open(argv[2]) as stateTxt:
        for line in csv.DictReader(stateTxt):
            states[line['state'].lower()] = line['abbr']

    builder = IntersectionFinder(states)

    print 'reading osm'
    builder.parse(argv[1])

    print 'filtering nodes'
    builder.filter_nodes()

    nodeCount = reduce(lambda a, b: a + len(b), builder.nodesInStateAvenues.values(), 0)
    print 'found %s avenues with %s nodes total' % (len(builder.nodesInStateAvenues), nodeCount)

    print 'writing json'
    with open(argv[3], 'w') as outfile:
        json.dump(builder.toGeoJSON(), outfile)
