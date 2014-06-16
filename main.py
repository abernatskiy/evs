#!/usr/bin/python2

from individuals.trinaryVector import Individual
from communicators.unixPipe import Communicator
from evolvers.hillClimber import Evolver

indivParams = {'length': 12, 'precision': 4, 'mutationProbability': 0.03, 'mutationAmplitude': 0.1}
evolParams = {'populationSize': 3} # pack all Evolver constructor's arguments into this structure

comm = Communicator('evaluations.pipe', 'individuals.pipe')
evolver = Evolver(comm, Individual, indivParams, evolParams)

import time

while True:
	evolver.updatePopulation()
	evolver.printBestIndividual()
#	time.sleep(0.1)
