#!/usr/bin/python2

# from individuals.trinaryVector import Individual
from individuals.floatVector import Individual

from communicators.unixPipe import Communicator

# from evolvers.hillClimber import Evolver
from evolvers.afpo import Evolver

indivParams = {'length': 12, 'precision': 4, 'mutationProbability': 0.03, 'mutationAmplitude': 0.1}
evolParams = {'indivClass': Individual, 'populationSize': 3}
comm = Communicator('evaluations.pipe', 'individuals.pipe')

evolver = Evolver(comm, indivParams, evolParams)

while True:
	evolver.updatePopulation()

	# command line output
	evolver.printBestIndividual()
#	evolver.printPopulation()
	evolver.logBestIndividual()
