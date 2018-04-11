import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Multiobjective algorithm which minimizes the connection cost alongside
     with maximizing the fitness function. It is similar to the technique used
     in the 2013 Clune Mouret Lipson "The evolutionary origins of modularity"
     paper; the difference is that instead of using NSGA-II, we simply keep the
     whole Pareto front at each generation and add its offsprings to the
     population until it restores its size.

     Required parameters:
       evolParams['populationSize']
       evolParams['initialPopulationType'] - can be 'random' or 'sparse'.
         If 'sparse' is chosen, the initial population will be composed of
         individulas with all genes set to zero and mutated once. To do so,
         the algorithm will use the following method of the individual class:
           evolParams['indivClass'].setValuesToZero().
         Feel free to use it to redefine the meaning of the sparsity!
         More info on benefits of sparse initial populations can be found in
         2015 Bernatskiy Bongard "Exploiting the relationship between structural
         modularity and sparsity for faster network evolution".

     Optional parameters:
       evolParams['secondObjectiveProbability'] - if provided, connection cost
         will only be taken into account with the specified probability. If it
         is not taken into account, the algorithm will assume that the
         individual with larger fitness dominates regardless of connection cost.
         See 2013 Clune et al.
       evolParams['useMaskForSparsity'] - use mask instead of comparing the
         fields to zero to count nonzero values.
       evolParams['noiseAmplitude'] - if provided, noisy evaluations with a
			  uniformly distributed noise of given amplitude will be simulated.
       evolParams['newIndividualsPerGeneration'] - number of new individuals
        injected per generation. Default 0.

     NOTE: Individual classes with surefire mutation operator are OK.'''

	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)

		self.setParamDefault('newIndividualsPerGeneration', 0)
		self.newGenomesPerGeneration = self.params['newIndividualsPerGeneration']

		if self.params['initialPopulationType'] == 'random' or self.params['initialPopulationType'] == 'sparse':
			while len(self.population) < self.params['populationSize']:
				indiv = self.getNewIndividual()
				self.population.append(indiv)
		elif self.params['initialPopulationType'] == 'expandFromFile':
			if not initialPopulationFileName:
				raise ValueError('Initial population file name must be specified if initialPopulationType=expandFromFile is used')
			curPopLen = len(self.population)
			while len(self.population) < self.params['populationSize']:
				indiv = deepcopy(np.random.choice(self.population[:curPopLen]))
				indiv.mutate()
				self.population.append(indiv)
		else:
			raise ValueError('Wrong type of initial population')

		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)
		self.paretoFront = self.getCluneParetoFront()

		self.paretoSizeHeaderWritten = False

		self.epsilon = 0

	def getRandomIndividual(self):
		return self.params['indivClass'](self.indivParams)

	def getSparseIndividual(self):
		indiv = self.params['indivClass'](self.indivParams)
		indiv.setValuesToZero()
		indiv.mutate()
		return indiv

	def getNewIndividual(self):
		if self.params['initialPopulationType'] == 'random':
			return self.getRandomIndividual()
		elif self.params['initialPopulationType'] == 'sparse':
			return self.getSparseIndividual()
		else:
			raise ValueError('Wrong population type {} for a getNewIndividual() call - must be random or sparse'.format(self.params['initialPopulationType']))

	def requiredParametersTranslator(self):
		t = super(Evolver, self).requiredParametersTranslator()
		t['toFloat'].add('secondObjectiveProbability')
		t['toString'].add('initialPopulationType')
		return t

	def optionalParametersTranslator(self):
		t = super(Evolver, self).optionalParametersTranslator()
		t['toInt'].add('newIndividualsPerGeneration')
		t['toBool'].add('useMaskForSparsity')
		return t

	def getConnectionCostFunc(self):
		#if self.paramIsEnabled('useMaskForSparsity'):
		#	connectionCostFunc = lambda x: len(filter(lambda y: y, x.mask))
		#else:
		#	connectionCostFunc = lambda x: len(filter(lambda y: y!=0, x.values))
		self.secondObjectiveLabel = 'connection cost'
		return lambda x: x.connectionCost()

	def getErrorFunc(self):
		return lambda x: -1.*x.score

	def getCluneParetoFront(self):
		errorFunc = self.getErrorFunc()
		connectionCostFunc = self.getConnectionCostFunc()
		if self.paramExists('secondObjectiveProbability') and self.params['secondObjectiveProbability'] != 1.:
			return self.findStochasticalParetoFront(errorFunc, connectionCostFunc)
		else:
			return self.findParetoFront(errorFunc, connectionCostFunc)

	def logParetoSize(self, paretoFront):
		if not self._shouldIRunAPeriodicFunctionNow('logParetoSize'):
			return
		filename = 'paretoSize{}.log'.format(self.params['randomSeed'])
		if self.paretoSizeHeaderWritten:
			with open(filename, 'a') as logFile:
				logFile.write('{} {}\n'.format(self.generation, len(paretoFront)))
		else:
			with open(filename, 'w') as logFile:
				self._writeParamsToLog(logFile)
				logFile.write('# Columns: generation paretoFrontSize\n')
			self.paretoSizeHeaderWritten = True
			self.logParetoSize(paretoFront)

	def doParetoOutput(self):
		self.printParetoFront(self.paretoFront, self.secondObjectiveLabel, self.getConnectionCostFunc())
		self.logParetoFront(self.paretoFront)
		self.paretoWarning(self.paretoFront)
		self.logParetoSize(self.paretoFront)

	def processMutatedChild(self, child, parent):
		pass

	def generateLogsAndStdout(self):
		super(Evolver, self).generateLogsAndStdout()
		self.doParetoOutput()

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		evt = self.getConnectionCostFunc()
		erf = self.getErrorFunc()

		maxEvalTime = max([ evt(i) for i in self.population ])
		minEvalTime = min([ evt(i) for i in self.population ])

		newPopulation = []
		while len(newPopulation)+len(self.paretoFront) < self.params['populationSize'] - self.newGenomesPerGeneration:
#		while len(newPopulation) < self.params['populationSize'] - self.newGenomesPerGeneration:

			evtlevel = evt(np.random.choice(self.paretoFront))
			evttau = (evtlevel - minEvalTime)/(maxEvalTime - minEvalTime) if maxEvalTime!=minEvalTime else 1.0

			levelindivs = [ i for i in self.population if np.abs(evt(i)-evtlevel) <= self.epsilon ]
			levelerrs = [ erf(i) for i in levelindivs ]
			minerr = min(levelerrs)
			sumdifferr = sum([ e-minerr for e in levelerrs ])
			levelsize = len(levelindivs)

			deltaprobs = [ 1. if x==minerr else 0. for x in levelerrs ]

			maxperfid = max([ x.id for x,p in zip(levelindivs, deltaprobs) if p==1.])
			deltaprobs = [ x if i.id==maxperfid else 0. for x,i in zip(deltaprobs, levelindivs) ]

			levelprobs = [ (1.-evttau)/levelsize + evttau*d for d in deltaprobs ]
# 			levelprobs = [ (e-minerr)/sumdifferr for e in levelerrs ]
#			levelprobs = deltaprobs

			parent = np.random.choice(levelindivs, p=levelprobs)
#			print 'Among parents of performance level ' + str(evtlevel) + ' (' + str([ i.id for i in levelindivs ]) + ') id ' + str(parent.id) + ' was chosen'
#			print 'Performance levels: ' + str(levelerrs) + ' probabilities: ' + str(levelprobs)

			child = deepcopy(parent)
			child.mutate()
			self.processMutatedChild(child, parent)
			newPopulation.append(child)
#		print ''

		for _ in range(self.newGenomesPerGeneration):
			if self.params['initialPopulationType'] == 'random':
				newPopulation.append(self.getRandomIndividual())
			elif self.params['initialPopulationType'] == 'sparse':
				newPopulation.append(self.getSparseIndividual())

		self.communicator.evaluate(newPopulation)
		self.population = newPopulation + self.paretoFront

		self.population.sort(key = lambda x: x.score)
		self.paretoFront = self.getCluneParetoFront()
