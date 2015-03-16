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

while True: # DO NOT EDIT
	### Leave this uncommented if you want to make a backup of every generation
	evolver.pickleSelf()

	print evolver.generation
	evolver.updatePopulation() # DO NOT EDIT

	### Leave this uncommented if you want the evolution to log the best 
	# individual and its fitness at each generation
	evolver.logBestIndividual()

	### Uncomment/comment these lines to turn on/off various aspects of 
	# command line output
	#evolver.printBestIndividual()
	#evolver.printPopulation()
