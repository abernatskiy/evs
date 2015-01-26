#!/usr/bin/python2

# Usage: mainConfig.py <evals> <indivs> <randseed> <config>

import sys
import ConfigParser
import importlib

conf = ConfigParser.RawConfigParser()
conf.optionxform = str # required to keep the uppercase-containing fields working
conf.read(sys.argv[4])

Individual = importlib.import_module('individuals.' + conf.get('classes', 'individual')).Individual
Evolver = importlib.import_module('evolvers.' + conf.get('classes', 'evolver')).Evolver
Communicator = importlib.import_module('communicators.' + conf.get('classes', 'communicator')).Communicator

floats = ['mutExploration', 'mutInsDelRatio', 'mutProbability']
ints = ['length', 'genStopAfter', 'populationSize', 'randomSeed', 'initDensity', 'beginConn', 'endConn']

def loadDict(section):
	global conf, floats, ints
	dict = {}
	for item in conf.items(section):
		if item[0] in ints:
			dict[item[0]] = int(item[1])
		elif item[0] in floats:
			dict[item[0]] = float(item[1])
		else:
			dict[item[0]] = item[1]
	return dict

indivParams = loadDict('indivParams')

evolParams = loadDict('evolParams')
evolParams['indivClass'] = Individual
evolParams['randomSeed'] = int(sys.argv[3])

comm = Communicator(sys.argv[1], sys.argv[2])
evolver = Evolver(comm, indivParams, evolParams)

evolver.logBestIndividual(filename = 'bestIndividual' + str(evolParams['randomSeed']) + '.log')
if evolParams.has_key('logEveryPopulation') and evolParams['logEveryPopulation'] == 'yes':
	evolver.logPopulation(prefix = 'seed' + str(evolParams['randomSeed']))

while True:
	### Uncommented this if you want to make a backup of every generation
	# evolver.pickleSelf()

	evolver.updatePopulation() # DO NOT EDIT

	### Leave this uncommented if you want the evolution to log the best 
	# individual and its fitness at each generation
	evolver.logBestIndividual(filename = 'bestIndividual' + str(evolParams['randomSeed']) + '.log')
	if evolParams.has_key('logEveryPopulation') and evolParams['logEveryPopulation'] == 'yes':
		evolver.logPopulation(prefix = 'seed' + str(evolParams['randomSeed']))

	### Uncomment/comment these lines to turn on/off various aspects of command line output
	evolver.printGeneration()
#	evolver.printBestIndividual()
#	evolver.printPopulation()
