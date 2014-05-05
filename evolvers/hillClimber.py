from copy import deepcopy

class Evolver:
	'''Evolver with constant population size which does 
	not use anything besides mutations to achieve variation'''
	def __init__(self, communicator, indivClass, indivParams, evolParams):
		self.communicator = communicator
		self.params = evolParams
		self.population = []
		for i in xrange(evolParams['populationSize']):
			indiv = indivClass(indivParams)
			self.population.append(indiv)
		self.communicator.evaluate(self.population)

	def updatePopulation(self):
		newPopulation = deepcopy(self.population)
		self.communicator.evaluate(newPopulation)
		self.population += newPopulation
		self.population.sort()
		self.population = self.population[self.params['populationSize']:]

	def printBestIndiv(self):
		bestIndiv = self.population[-1]
		print 'Best individual: ' + str(bestIndiv) + ' score: ' + str(bestIndiv.score)
