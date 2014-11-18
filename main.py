#!/usr/bin/python2

######## CLASSES LOADING SECTION ########

# EVolutionary Server uses three classes named Individual, Communicator and Evolver. 
# Choose implemetations of these classes by commenting/uncommenting the 
# lines below. Make sure that only one line is uncommented for each of the
# three classes.

# Any combinations of implementations of the three classes are allowed in 
# the current version.

# Docs are available for every implementation at docs/<implementation name>.
# For example, documentation for the implmentation of the class Individual 
# imported from individuals.trinaryVector resides at docs/individuals.trinaryVector

### Class Individual implementats an evolutionary individual (aka genome, aka 
# candidate solution). Available options:

from individuals.trinaryVector import Individual  # Vector of numbers from {-1,0,1}
#from individuals.floatVector import Individual   # Vector of floating point values of fixed decimal precision

### Class Communicator implements the method for supplying the individuals 
# to the client and getting back the evaluations. Available options:

from communicators.unixPipe import Communicator   # Communicates with the client through a pair of named UNIX pipes
#from communicators.textFile import Communicator  # Communicates with the client through a pair of text files

### Class Evolver handles selection of the fittest and generation of new 
# individuals. See docs/evolvers.* for descriptions. Available options:

#from evolvers.hillClimber import Evolver
#from evolvers.afpo import Evolver                 # recommended
#from evolvers.averagingAfpo import Evolver
#from evolvers.doubtfulAfpo import Evolver
from evolvers.mdpea import Evolver

############ PARAMS SECTION #############

### Specify the parameters to be used by Individual (indivParams) and 
# Evolver (evolParams) classes.

# Required parameters vary by implementation, the parameters which are 
# not required are ignored. For example, the individuals.floatVector 
# implemetation of the class Individual requires the 'precision' 
# parameter, while for the individuals.trinaryVector 
# implementation this parameter is ignored (if it is present in indivParams). 

# For complete lists of the parameters required by each implementation, 
# see the implementation docs (docs/individuals.* and docs/evolvers.*)

# DO NOT EDIT the 'indivClass' parameter form evolParams - it is required to 
# pass the class Individual to the class Evolver

# Useful values:
# For k=0 connections between inputs and outputs are direct and there are 
# four weights. For other k's:
# k		4k		4k+k^2
# 1		4			5
# 2		8			12
# 3		12		21
#	4		16		32
#	5		20		45
#	6		24		60

indivParams = {'length': 4, 'precision': 4, 'mutationProbability': 0.03, 'mutationAmplitude': 0.1}

import sys

evolParams = {'indivClass': Individual, 'populationSize': 30, 'printParetoFront': True, 'randomSeed': int(sys.argv[1]), 'genStopAfter': 50}

### Specify the arguments of the Communicator constructor. Typically those 
# would be the addresses (in a general sense) associated with the 
# communication channels between the server and the client

comm = Communicator('evaluations.pipe', 'individuals.pipe') # for communicators.unixPipe
#comm = Communicator('evaluations.txt', 'individuals.txt')  # for communicators.textFile

evolver = Evolver(comm, indivParams, evolParams) # DO NOT EDIT 

while True: # DO NOT EDIT
	### Uncommented this if you want to make a backup of every generation
	# evolver.pickleSelf()

	evolver.updatePopulation() # DO NOT EDIT

	### Leave this uncommented if you want the evolution to log the best 
	# individual and its fitness at each generation
	evolver.logBestIndividual()

	### Uncomment/comment these lines to turn on/off various aspects of 
	# command line output
	#evolver.printBestIndividual()
	#evolver.printPopulation()
