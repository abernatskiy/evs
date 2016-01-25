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
		if not hasattr(self, '__secondObjName__'):
			self.__secondObjName__ = 'unknown'

		self.setParamDefault('bruteForceChunkSize', -1)
		self.setParamDefault('paretoBreakTiesByIDs', False)

		indiv = self.params['indivClass'](indivParams)
		indiv.setValuesToTheFirstSet()

		self.nextIndiv = self._addSpaceChunk(indiv, self.params['bruteForceChunkSize'])
		self.communicator.evaluate(self.population)

		self.paretoFront = self.findParetoFront(lambda x: -1*x.score, self.params['secondMinObj'], breakTiesByIDs=self.params['paretoBreakTiesByIDs'])
		self.logSubpopulation(self.paretoFront, 'logParetoFront', 'paretoFront')
		self.printParetoFront(self.paretoFront, self.__secondObjName__, self.params['secondMinObj'])

	def _addSpaceChunk(self, initIndiv, chunkSize):
		self.population.append(initIndiv)
		nextIndiv = deepcopy(initIndiv)

		i = 1

		while nextIndiv.increment():
			if chunkSize > 0 and i%chunkSize == 0:
				return nextIndiv
			self.population.append(nextIndiv)
			newNextIndiv = deepcopy(nextIndiv)
			nextIndiv = newNextIndiv

			i += 1

		return None
