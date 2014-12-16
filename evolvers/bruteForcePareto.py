from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Brute force Pareto front finder
     Not an evolutionary algorithm. Works by generating a
     population of all possible solutions using 
     indiv.setValuesToTheFirstSet() and indiv.increment(),
     then evaluating the population. In the first call of
     updatePopulation() the Pareto front which maximizes
     indiv.score and minimizes the 
     params['secondMinObj'](indiv) function.
     The population is then set to be the Pareto front.
     Subsequent calls of updatePopulation do not change it.
       Required methods and parameters:
        communicator.evaluate(population)
        evolParams['indivClass']
        evolParams['indivClass'].setValuesToTheFirstSet()
				evolParams['indivClass'].increment()
				evolParams['secondMinObj'](indiv)'''
	def __init__(self, communicator, indivParams, evolParams):
		super(Evolver, self).__init__(communicator, indivParams, evolParams)
		indiv = self.params['indivClass'](indivParams)
		indiv.setValuesToTheFirstSet()
		self.population.append(indiv)
		nextIndiv = deepcopy(indiv)
		while nextIndiv.increment():
			self.population.append(nextIndiv)
			newNextIndiv = deepcopy(nextIndiv)
			nextIndiv = newNextIndiv
		self.communicator.evaluate(self.population)

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()
		paretoFront = self.findParetoFront(lambda x: -1*x.score, self.params['secondMinObj'])
#		self.population = paretoFront
		return paretoFront
