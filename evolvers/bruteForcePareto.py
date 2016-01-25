from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Brute force Pareto front finder
     Not an evolutionary algorithm. Works by generating a
     population of all possible solutions using
     indiv.setValuesToTheFirstSet() and indiv.increment(),
     then evaluating the population, then finding the
     Pareto front which maximizes indiv.score and
     minimizes the params['secondMinObj'](indiv) function.
     The Pareto front is optionally logged
     (logParetoFront=yes).
		 The number of of generations is fixed to be zero,
     so the updatePopulation() function returns False
     on the first call.
       Required methods and parameters:
        communicator.evaluate(population)
        evolParams['indivClass']
        evolParams['indivClass'].setValuesToTheFirstSet()
				evolParams['indivClass'].increment()
				evolParams['secondMinObj'](indiv)'''
	def __init__(self, communicator, indivParams, evolParams):
		super(Evolver, self).__init__(communicator, indivParams, evolParams)

		self.params['genStopAfter'] = 0

		if not self.params.has_key('secondMinObj'):
			print 'WARNING! The second objective function is undefined, falling back to constant'
			self.params['secondMinObj'] = lambda x: 0

		indiv = self.params['indivClass'](indivParams)
		indiv.setValuesToTheFirstSet()
		self.population.append(indiv)

		nextIndiv = deepcopy(indiv)
		while nextIndiv.increment():
			self.population.append(nextIndiv)
			newNextIndiv = deepcopy(nextIndiv)
			nextIndiv = newNextIndiv

		self.communicator.evaluate(self.population)

		paretoFront = self.findParetoFront(lambda x: -1*x.score, self.params['secondMinObj'])
		self.logSubpopulation(paretoFront, 'logParetoFront', 'paretoFront')
		self.printParetoFront(paretoFront, 'unknown', lambda x: 0)
