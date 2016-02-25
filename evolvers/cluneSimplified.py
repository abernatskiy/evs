import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Multiobjective algorithm which optimizes
     connection cost. See Clune 2013
       evolParams['populationSize']
       evolParams['initialPopulationType']
        - can be 'random' or 'sparse'.
        If 'sparse' is chosen, the following
        method is required:
       evolParams['indivClass'].setValuesToZero().
     NOTE: unlike AFPO, this method does not work
     too well with probability-1 mutations'''
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

#		print 'Making a Pareto front'
		paretoFront = self.findParetoFront(lambda x: -1*x.score, lambda x: len(filter(lambda y: y!=0, x.values)))
#		paretoFront = self.findParetoFront(lambda x: -1*x.score, lambda x: len(filter(lambda y: y, x.mask)))

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

#		print 'Creating a new population'
		newPopulation = []
		for indiv in paretoFront:
			newPopulation.append(indiv)
		while len(newPopulation) < self.params['populationSize']:
#			print 'Adding a child'
			parent = np.random.choice(paretoFront)
#			print 'Chose a parent ' + str(parent)
			child = deepcopy(parent)
#			print 'Copying successful'
			child.mutate()
#			print 'Mutating a child'
			newPopulation.append(child)
#			print 'Appended the child to the new population'
#		print 'Made a population'
		self.population = newPopulation
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)
#		print 'Exiting updatePopulation()'
