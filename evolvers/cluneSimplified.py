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

     NOTE: Individual classes with surefire mutation operator are OK.'''

	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)
		if self.params['initialPopulationType'] == 'random':
			while len(self.population) < self.params['populationSize']:
				indiv = self.params['indivClass'](indivParams)
				self.population.append(indiv)
		elif self.params['initialPopulationType'] == 'sparse':
			while len(self.population) < self.params['populationSize']:
				indiv = self.params['indivClass'](indivParams)
				indiv.setValuesToZero()
				indiv.mutate()
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

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		if self.paramIsEnabled('useMaskForSparsity'):
			connectionCostFunc = lambda x: len(filter(lambda y: y, x.mask))
		else:
			connectionCostFunc = lambda x: len(filter(lambda y: y!=0, x.values))

		if self.paramIsNonzero('secondObjectiveProbability'):
			paretoFront = self.findStochasticalParetoFront(lambda x: -1*x.score, connectionCostFunc)
		else:
			paretoFront = self.findParetoFront(lambda x: -1*x.score, connectionCostFunc)

		self.printParetoFront(paretoFront, 'connection cost', connectionCostFunc)
		self.logParetoFront(paretoFront)
		self.paretoWarning(paretoFront)

		newPopulation = []
		while len(newPopulation)+len(paretoFront) < self.params['populationSize']:
			parent = np.random.choice(paretoFront)
			child = deepcopy(parent)
			child.mutate()
			newPopulation.append(child)
		self.communicator.evaluate(newPopulation)
		self.population = paretoFront + newPopulation
		if self.paramExists('noiseAmplitude'):
			self.noisifyAllScores()
		self.population.sort(key = lambda x: x.score)
