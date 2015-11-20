#!/usr/bin/python2

import sys
import pickle

if len(sys.argv) == 2:
	file = open(sys.argv[1], 'r')
else:
	raise ValueError('Specify backup filename')

evolver = pickle.load(file)
file.close()

evolver.recover()
evolver.generateLogsAndStdout()

while True:
	evolver.updatePopulation()
	evolver.pickleSelf()
	evolver.generateLogsAndStdout()
