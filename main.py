#!/usr/bin/python2

from individuals.floatVector import Individual
from communicators.unixPipe import Communicator
from evolvers.hillClimber import Evolver

indivParams = {'length': 10, 'noOfDigits': 5, 'mutationProbability': 0.05, 'mutationAmplitude': 0.1}
evolParams = {'populationSize': 3} # pack all Evolver constructor's arguments into this structure

comm = Communicator('evaluations.pipe', 'individuals.pipe')
evolver = Evolver(comm, Individual, indivParams, evolParams)

while True:
	evolver.updatePopulation()
	evolver.printBestIndiv()
