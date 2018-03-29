import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''...

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

     NOTE: Individual classes with surefire mutation operator are OK.'''

	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)
		if self.params['initialPopulationType'] == 'random':
			while len(self.population) < self.params['populationSize']:
				indiv = self.getRandomIndividual()
				self.population.append(indiv)
		elif self.params['initialPopulationType'] == 'sparse':
			while len(self.population) < self.params['populationSize']:
				indiv = self.getSparseIndividual()
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
		self.paretoFront = self.getTemporalParetoFront()

		self.paretoSizeHeaderWritten = False

		self.newGenomesPerGeneration = 5

		self.epsilon = 0

	def getRandomIndividual(self):
		return self.params['indivClass'](self.indivParams)

	def getSparseIndividual(self):
		indiv = self.params['indivClass'](self.indivParams)
		indiv.setValuesToZero()
		indiv.mutate()
		return indiv

	def requiredParametersTranslator(self):
		t = super(Evolver, self).requiredParametersTranslator()
		t['toFloat'].add('secondObjectiveProbability')
		t['toString'].add('initialPopulationType')
		return t

	def getEvaluationTimeFunc(self):
		self.secondObjectiveLabel = 'simulation time'
		return lambda x: x.evaluationTime

	def getErrorFunc(self):
		return lambda x: -1.*x.score

	def getTemporalParetoFront(self):
		errorFunc = self.getErrorFunc()
		evaluationTimeFunc = self.getEvaluationTimeFunc()
		if self.paramExists('secondObjectiveProbability') and self.params['secondObjectiveProbability'] != 1.:
			return self.findStochasticalParetoFront(errorFunc, evaluationTimeFunc)
		else:
			return self.findParetoFront(errorFunc, evaluationTimeFunc)

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
		self.printParetoFront(self.paretoFront, self.secondObjectiveLabel, self.getEvaluationTimeFunc())
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

		#evt = self.getEvaluationTimeFunc()

		#maxEvalTime = max([ evt(i) for i in self.population ])
		#minEvalTime = min([ evt(i) for i in self.population ])

		newPopulation = []
		while len(newPopulation)+len(self.paretoFront) < self.params['populationSize'] - self.newGenomesPerGeneration:
			parent = np.random.choice(self.paretoFront)
			child = deepcopy(parent)
			child.mutate()
			self.processMutatedChild(child, parent)
			newPopulation.append(child)

		for _ in range(self.newGenomesPerGeneration):
			if self.params['initialPopulationType'] == 'random':
				newPopulation.append(self.getRandomIndividual())
			elif self.params['initialPopulationType'] == 'sparse':
				newPopulation.append(self.getSparseIndividual())

		self.communicator.evaluate(newPopulation)
		self.population = newPopulation + self.paretoFront

		self.population.sort(key = lambda x: x.score)
		self.paretoFront = self.getTemporalParetoFront()
