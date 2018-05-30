import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

ULTIMATE_FITNESS_EPSILON = 1.
RELATIVE_FITNESS_EPSILON = 1.

class Evolver(BaseEvolver):
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName=None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)
		self.setParamDefault('initialPopulationType', 'random')

		while len(self.population) < self.params['populationSize']:
			indiv = self.getNewIndividual()
			self.population.append(indiv)

		fitnessVariants = { indiv.getFitnessParams() for indiv in self.population }
		currentFitnessVariants = list(np.random.choice(fitnessVariants, size=self.params['fitnessGroupsNumber']))

		for indiv in self.population:
			indiv.setFitnessParams(np.random.choice(currentFitnessVariants))

	def requiredParametersTranslator(self):
		t = super(Evolver, self).requiredParametersTranslator()
		t['toInt'].add('fitnessParamsUpdatePeriod')
		t['toInt'].add('fitnessGroupsNumber')
		return t

	def optionalParametersTranslator(self):
		t = super(Evolver, self).requiredParametersTranslator()
		t['toString'].add('initialPopulationType')
		return t

	def getRandomIndividual(self):
		return self.params['indivClass'](self.indivParams)

	def getSparseIndividual(self):
		indiv = self.params['indivClass'](self.indivParams)
		indiv.setValuesToZero()
		indiv.mutate()
		return indiv

	def getNewIndividual(self):
		if self.params['initialPopulationType'] == 'random':
			return self.getRandomIndividual()
		elif self.params['initialPopulationType'] == 'sparse':
			return self.getSparseIndividual()
		else:
			raise ValueError('Wrong population type {} for a getNewIndividual() call - must be random or sparse'.format(self.params['initialPopulationType']))

	def getConnectionCostFunc(self):
		self.secondObjectiveLabel = 'connection cost'
		return lambda x: x.connectionCost()

	def getErrorFunc(self):
		return lambda x: -1.*x.score

	def getCluneParetoFront(self, subpop):
		raise NotImplementedError

	def generateLogsAndStdout(self):
		super(Evolver, self).generateLogsAndStdout()

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		if self.generation % self.params['fitnessParamsUpdatePeriod'] == 0:
			self._updatePopulationOfFitnessVariants()
		else:
			self._updatePopulationsWithinFitnessVariants()

	def _findBestErrorsForVariants(self):
		fitnessVariantsDB = { indiv.getFitnessParams(): [] for indiv in self.population } # automatic uniquification here
		for indiv in self.population:
			fitnessVariantsDB[indiv.getFitnessParams()].append(self.getErrorFunc()(indiv))

		fitnessVariantsFitnesses = { fp: min(ev) for fp, ev in fitnessVariantsDB.items() } # proportionality gets awkward if fitness is often zero...
		return fitnessVariantsFitnesses

	def _updatePopulationsWithinFitnessVariants(self):
		self.communicator.evaluate(self.population)

		newPopulation = []

		fitnessVariantsErrors = self._findBestErrorsForVariants()
		for indiv in self.population:
			if fitnessVariantsErrors[indiv.getFitnessParams()] == self.getErrorFunc()(indiv):
				newPopulation.append(indiv)

		while len(newPopulation) < self.params['populationSize']:
			tournament = np.random.choice(self.population, size=2)
			if tournament[0].getFitnessParams() != tournament[1].getFitnessParams():
				continue
			winner = deepcopy(np.random.choice(tournament, weights=[ RELATIVE_FITNESS_EPSILON-1.*self.getErrorFunc()(par) for par in tournament ]))
			winner.mutate()
			newPopulation.append(winner)

	def _updatePopulationOfFitnessVariants(self):
		for indiv in self.population:
			indiv.hideFitnessParams()
		self.communicator.evaluate(self.population)
		for indiv in self.population:
			indiv.showFitnessParams()

		fitnessVariantsErrors = self._findBestErrorsForVariants()
		minUltimateError = min(fitnessVariantsFitnesses.values())
		bestFitnessVariants = { fp for fp, mev in fitnessVariantsFitnesses if mev == minUltimateError }

		newPopulation = []
		newFitnessVariants = []
		ngroups = self.params['fitnessGroupsNumber']
		exitFlag = False
		for i in range(ngroups):
			if i == 0: # AFPO-to-be
				dummyIndiv = self.getNewIndividual()
				newVariant = dummyIndiv.getFitnessParams()
				newFitnessVariants.append(newVariant)

				for i in range(self.params['populationSize']/ngroups):
					newIndiv = deepcopy(np.random.choice(self.population)) # not dependent on fitness, maybe fix
					newIndiv.setFitnessParams(newVariant)
					newPopulation.append(newIndiv)
					if len(newPopulation) >= self.params['populationSize']:
						exitFlag = True
						break

			elif i < len(bestFitnessVariants)+1:
				eliteVariant = bestFitnessVariants[i-1]
				newFitnessVariants.append(eliteVariant)

				for indiv in self.population:
					if indiv.getFitnessParams() == eliteVariant:
						newPopulation.append(indiv)
						if len(newPopulation) >= self.params['populationSize']:
							exitFlag = True
							break

			else:
				parent = np.random.choice(fitnessVariantsErrors.keys(), weights=[ ULTIMATE_FITNESS_EPSILON-1.*x for x in fitnessVariantsErrors.values() ])
				dummyIndiv = self.getNewIndividual()
				dummyIndiv.setFitnessParams(parent)
				dummyIndiv.mutateFitnessParams()
				child = dummyIndiv.getFitnessParams()
				newFitnessVariants.append(child)

				for indiv in self.population:
					if indiv.getFitnessParams() == parent:
						newIndividual = deepcopy(indiv)
						newIndividual.setFitnessParams(child)
						newPopulation.append(newIndiv)
						if len(newPopulation) >= self.params['populationSize']:
							exitFlag = True
							break

			if exitFlag:
				break
