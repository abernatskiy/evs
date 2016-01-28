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

		self.setParamDefault('bruteForceChunkSize', -1)
		self.setParamDefault('paretoBreakTiesByIDs', False)
		self.setParamDefault('logParetoFrontKeepAllGenerations', False)

		if not self.params.has_key('bruteForceChunkSize') or self.params['bruteForceChunkSize'] <= 0:
			self.params['genStopAfter'] = 0
		elif self.params.has_key('genStopAfter'):
			self.params.pop('genStopAfter')

		if not self.params.has_key('secondMinObj'):
			print 'WARNING! The second objective function is undefined, falling back to constant'
			self.params['secondMinObj'] = lambda x: 0
		if not hasattr(self, '__secondObjName__'):
			self.__secondObjName__ = 'unknown'

		indiv = self.params['indivClass'](indivParams)
		indiv.setValuesToTheFirstSet()

		self.nextIndiv = self._addSpaceChunk(indiv, self.params['bruteForceChunkSize'])
		self.communicator.evaluate(self.population)

		self.paretoFront = self.findParetoFront(lambda x: -1*x.score, self.params['secondMinObj'], breakTiesByIDs=self.params['paretoBreakTiesByIDs'])
		self.paretoFront.sort(key = self.params['secondMinObj'])
		self._outputPareto()

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

	def _outputPareto(self):
		self.logSubpopulation(self.paretoFront, 'logParetoFront', 'paretoFront', genPostfix=self.params['logParetoFrontKeepAllGenerations'])
		self.printParetoFront(self.paretoFront, self.__secondObjName__, self.params['secondMinObj'])

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		if self.nextIndiv is None:
			self.done()

		self.population = []
		self.nextIndiv = self._addSpaceChunk(self.nextIndiv, self.params['bruteForceChunkSize'])
		self.communicator.evaluate(self.population)

		self.paretoFront += self.findParetoFront(lambda x: -1*x.score,
																						self.params['secondMinObj'],
																						breakTiesByIDs=self.params['paretoBreakTiesByIDs'])

		self.paretoFront = self.findParetoFront(lambda x: -1*x.score,
																						self.params['secondMinObj'],
																						breakTiesByIDs=self.params['paretoBreakTiesByIDs'],
																						population = self.paretoFront)

		self.paretoFront.sort(key = self.params['secondMinObj'])
		self._outputPareto()
