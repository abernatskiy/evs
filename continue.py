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
if hasattr(evolver, 'stateType'):
	if evolver.stateType == 'before_evaluation':
		evolver.updatePopulation()
		evolver.saveAfterEvaluation()
		evolver.logBestIndividual()
		evolver.printBestIndividual()
		evolver.printPopulation()
	elif evolver.stateType == 'after_evaluation':
		pass
	else:
		raise ValueError('Wrong value of the state type string, cannot continue')
else:
	print 'Recovering from a backup made by old (pre-1.1-r2) EVS. Everything should be fine, just letting you know.'

while True:
	print evolver.generation
	evolver.saveBeforeEvaluation()
	evolver.updatePopulation()
	evolver.saveAfterEvaluation()
	evolver.logBestIndividual()
	evolver.printBestIndividual()
	evolver.printPopulation()
