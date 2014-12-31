import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class ProportionalEvolver(BaseEvolver):
	'''Evolutionary algorithm in which every 
     inidividual of the next generation is a 
     mutant of an individual of the current 
     generation, selected at random with 
     probability propotional to its fitness.'''
	def updatePopulation(self):
		weights = np.array(map(lambda x: x.score, self.population), dtype=np.float)
		weights = weights/weights.sum()
		newPopulation = []
		while len(newPopulation < self.params['populationSize']):
			parent = np.random.choice(self.population, weights)
			child = deepcopy(parent)
			child.mutate()
			newPopulation.append(child)
		self.population = newPopulation
		
