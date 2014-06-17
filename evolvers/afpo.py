from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''AFPO (Age-Fitness Pareto Optimization) - evolutionary algorithm
     which uses age of individuals to maintain diversity. The age is
     defined as the number of generations this individual has spent
     within the population. Less fit individual is considered to be
     as valuable as the more fit one if it is younger. Required
     methods and parameters, aside from the common set:
       evolParams['populationSize']'''
	def __init__(self, communicator, indivParams, evolParams):
		super(Evolver, self).__init__(communicator, indivParams, evolParams)
		self.indivParams = indivParams
		for i in xrange(self.params['populationSize']):
			indiv = self.params['indivClass'](indivParams)
			indiv.age = 0
			self.population.append(indiv)
		self.communicator.evaluate(self.population)

	def updatePopulation(self):
		# forming offsprings
		newPopulation = deepcopy(self.population)
		for newIndiv in newPopulation:
			if newIndiv.mutate():
				newIndiv.age = 0
		# adding one new, completely random individual
		indiv = self.params['indivClass'](self.indivParams)
		indiv.age = 0
		newPopulation.append(indiv)
		
		self.communicator.evaluate(newPopulation)
		self.population += newPopulation
		# uniquifying the new population
		newPopulation = []
		for indiv in self.population:
			if indiv not in newPopulation:
				newPopulation.append(indiv)
		# taking the tail
		self.population = sorted(newPopulation, key = lambda x: (x.score, -x.age))
		self.population = self.population[-self.params['populationSize']:]

		for indiv in self.population:
			indiv.age += 1

	def printBestIndividual(self):
		bestIndiv = self.population[-1]
		print 'Best individual: ' + str(bestIndiv) + ' score: ' + str(bestIndiv.score) + ' age: ' + str(bestIndiv.age)

	def printPopulation(self):
		print '----------'
		for indiv in self.population:
			print str(indiv) + ' score: ' + str(indiv.score) + ' age: ' + str(indiv.age)
		print ''
