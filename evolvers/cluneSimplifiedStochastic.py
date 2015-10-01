import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Multiobjective algorithm which optimizes
     connection cost. See Clune Mouret Lipson 2013.

     Required stuff:
       evolParams['populationSize']
       evolParams['initialPopulationType']
        - can be 'random' or 'sparse'.
        If 'sparse' is chosen, the following
        method is required:
       evolParams['secondObjectiveProbability']
       evolParams['indivClass'].setValuesToZero().

     NOTE: unlike AFPO, this method does not work
     too well with probability-1 mutations'''
	def __init__(self, communicator, indivParams, evolParams):
		super(Evolver, self).__init__(communicator, indivParams, evolParams)
		if self.params['initialPopulationType'] == 'random':
			for i in xrange(self.params['populationSize']):
				indiv = self.params['indivClass'](indivParams)
				self.population.append(indiv)
		elif self.params['initialPopulationType'] == 'sparse':
		  for i in xrange(self.params['populationSize']):
				indiv = self.params['indivClass'](indivParams)
				indiv.setValuesToZero()
				indiv.mutate()
				self.population.append(indiv)
		else:
			raise ValueError('Wrong type of initial population')
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()
		paretoFront = self.findStochasticalParetoFront(lambda x: -1*x.score, lambda x: len(filter(lambda y: y!=0, x.values)))

		if self.params.has_key('printParetoFront') and self.params['printParetoFront'] == 'yes':
			for indiv in paretoFront:
				print str(indiv) + ' score: ' + str(indiv.score) + ' number of connections: ' + str(len(filter(lambda y: y!=0, indiv.values)))
			print ''

		# a useful warning
		r = float(len(paretoFront))/float(self.params['populationSize'])
		if r == 0.0:
			raise RuntimeError('No nondominated individuals!')
		if r > 0.75:
			print 'WARNING! Proportion of nondominated individuals too high (' + str(r) + ')'

		newPopulation = []
		for indiv in paretoFront:
			newPopulation.append(indiv)
		while len(newPopulation) < self.params['populationSize']:
			parent = np.random.choice(paretoFront)
			child = deepcopy(parent)
			child.mutate()
			newPopulation.append(child)
		self.population = newPopulation
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)
