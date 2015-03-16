#!/usr/bin/python2

from individuals.trinaryVectorSureMutation import Individual
from communicators.textFileOutputOnly import Communicator
from evolvers.proportionalEvolver import Evolver

import sys

if len(sys.argv) != 4:
	print 'Usage: generateGenomes.py <randomSeed> <sampleSize> <outputFilename>'
	sys.exit(1)

try:
	randseed = int(sys.argv[1])
	popsize = int(sys.argv[2])
except ValueError:
	print 'Usage: generateGenomes.py <randomSeed> <sampleSize> <outputFilename>'
	sys.exit(1)

indivParams = {'length': 12}
evolParams = {'indivClass': Individual, \
              'populationSize': popsize, \
              'randomSeed': randseed}

comm = Communicator('evaluations.txt', sys.argv[3])

evolver = Evolver(comm, indivParams, evolParams)
