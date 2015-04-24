#!/usr/bin/python2

import pickle
import sys

with open(sys.argv[1]) as f:
	evolver = pickle.load(f)

for indiv in evolver.population:
	print 'Individual: ' + str(indiv)
	print 'Ancestry: ' + str(indiv.ancestry)
	print
