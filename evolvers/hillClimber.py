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
		for newIndiv in newPopulation:
			newIndiv.mutate()
		self.communicator.evaluate(newPopulation)
		self.population += newPopulation
		self.population.sort()
		# uniquifying the new population
		newPopulation = []
		for indiv in self.population:
			if indiv not in newPopulation:
				newPopulation.append(indiv)
		self.population = newPopulation
		# taking the tail
		self.population = self.population[-self.params['populationSize']:]

	def printBestIndiv(self):
		bestIndiv = self.population[-1]
		print 'Best individual: ' + str(bestIndiv) + ' score: ' + str(bestIndiv.score)

	def printPopulation(self):
		for indiv in self.population:
			print str(indiv) + ' score: ' + str(indiv.score)
		print ''
