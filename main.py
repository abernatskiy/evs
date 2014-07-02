#!/usr/bin/python2

from individuals.trinaryVector import Individual
#from individuals.floatVector import Individual

from communicators.unixPipe import Communicator
#from communicators.textFile import Communicator

#from evolvers.hillClimber import Evolver
from evolvers.afpo import Evolver
#from evolvers.averagingAfpo import Evolver

indivParams = {'length': 8, 'precision': 4, 'mutationProbability': 0.03, 'mutationAmplitude': 0.1}
evolParams = {'indivClass': Individual, 'populationSize': 30}

comm = Communicator('evaluations.pipe', 'individuals.pipe')
#comm = Communicator('evaluations.txt', 'individuals.txt')

evolver = Evolver(comm, indivParams, evolParams)

while True:
	evolver.updatePopulation()

	# command line output
	evolver.printBestIndividual()
#	evolver.printPopulation()
	evolver.logBestIndividual()
