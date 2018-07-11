import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver
from ageFunction import chooseTupleRandomly

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
		currentFitnessVariants = chooseTupleRandomly(fitnessVariants, size=self.params['fitnessGroupsNumber'])

		counter = 0
		for fvi in range(self.params['fitnessGroupsNumber']):
			for _ in range(self.params['populationSize']/self.params['fitnessGroupsNumber']):
				self.population[counter].setFitnessParams(currentFitnessVariants[fvi])
				counter += 1
		while counter < self.params['populationSize']:
			self.population[counter].setFitnessParams(currentFitnessVariants[-1])
			counter += 1

		self.communicator.evaluate(self.population) # will be repeated at the first update

	def requiredParametersTranslator(self):
		t = super(Evolver, self).requiredParametersTranslator()
		t['toInt'].add('fitnessParamsUpdatePeriod')
		t['toInt'].add('fitnessGroupsNumber')
		t['toInt'].add('populationSize')
		return t

	def optionalParametersTranslator(self):
		t = super(Evolver, self).optionalParametersTranslator()
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

	def getUltimateErrorFunc(self):
		return lambda x: -1.*x.scores[0]

	def getCurrentErrorFunc(self):
		return lambda x: -1.*x.scores[1]

	def getCluneParetoFront(self, subpop):
		raise NotImplementedError

	def generateLogsAndStdout(self):
		super(Evolver, self).generateLogsAndStdout()

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		print('updatePopulation called, pre-update done...')

		if self.generation % self.params['fitnessParamsUpdatePeriod'] == 0:
			print('Ultimate update attempted')
			self._updatePopulationOfFitnessVariants()
		else:
			print('Simple update attempted')
			self._updatePopulationsWithinFitnessVariants()

	def _findBestErrorsForVariants(self, errorFunc):
		fitnessVariantsDB = { indiv.getFitnessParams(): [] for indiv in self.population } # automatic uniquification here
		for indiv in self.population:
			fitnessVariantsDB[indiv.getFitnessParams()].append(errorFunc(indiv))

		fitnessVariantsFitnesses = { fp: min(ev) for fp, ev in fitnessVariantsDB.items() } # proportionality gets awkward if fitness is often zero...
		return fitnessVariantsFitnesses

	def _findFitnessVariantsElite(self, curIndivs, fitnessVariant, bestError):
		numIndivs = len(curIndivs)
		fitnessVariantElite = [ indiv for indiv in curIndivs if self.getCurrentErrorFunc()(indiv)==bestError ]
		ultimateFitnessElite = [ indiv for indiv in curIndivs if indiv.isAChampion() ]
		# We want to keep the best individual according to the current fitness and the veteran that got the fitness variant through the ultimate update.
		# Problem is, they might be the same individual! Or the veteran might not exist yet
		newIndivs = [ fitnessVariantElite[0] ]
		if len(ultimateFitnessElite)>0 and ultimateFitnessElite[0].id!=fitnessVariantElite[0].id:
			newIndivs.append(ultimateFitnessElite[0])
		return newIndivs

	def _updatePopulationsWithinFitnessVariants(self):
		self.communicator.evaluate(self.population)

		newPopulation = []

		fitnessVariantsErrors = self._findBestErrorsForVariants(self.getCurrentErrorFunc())
		for vf, be in fitnessVariantsErrors.items():
			curIndivs = [ indiv for indiv in self.population if indiv.getFitnessParams()==vf ]
			numIndivs = len(curIndivs)
			# Elite is made through a special reloadable method
			newIndivs = self._findFitnessVariantsElite(curIndivs, vf, be)
			# The rest of the population are offspring copied with errors
			weights = [ RELATIVE_FITNESS_EPSILON - self.getCurrentErrorFunc()(indiv) for indiv in curIndivs ]
			while len(newIndivs) < numIndivs:
				child = deepcopy(chooseTupleRandomly(curIndivs, weights=weights))
				child.mutate()
				newIndivs.append(child)

			newPopulation.extend(newIndivs)

		self.population = newPopulation

	def _updatePopulationOfFitnessVariants(self):
		self.communicator.evaluate(self.population)

		fitnessVariantsErrors = self._findBestErrorsForVariants(self.getUltimateErrorFunc())
		print('fitness variants errors: {}'.format(repr(fitnessVariantsErrors)))
		minUltimateError = min(fitnessVariantsErrors.values())
		print('min ultimate error: {}'.format(minUltimateError))
		bestFitnessVariants = list({ fp for fp, mev in fitnessVariantsErrors.items() if mev == minUltimateError })
		print('best fitness variants: {}'.format(bestFitnessVariants))

		# marking the future elite of ultimate fitness
		for fp, mev in fitnessVariantsErrors.items():
			for indiv in self.population:
				if indiv.getFitnessParams() == fp and self.getUltimateErrorFunc()(indiv) == mev:
					indiv.markAsChampion()
					break

		# doing the selection on the fitness variants
		newPopulation = []
		newFitnessVariants = []
		ngroups = self.params['fitnessGroupsNumber']
		exitFlag = False
		for i in range(ngroups):
			if i == 0: # AFPO-to-be
				dummyIndiv = self.getNewIndividual()
				newVariant = dummyIndiv.getFitnessParams()
				newFitnessVariants.append(newVariant)

				print('i=0: adding new fitness variant {}'.format(newVariant))

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

				print('i={}: adding elite fitness variant {}'.format(i, eliteVariant))

				for indiv in self.population:
					if indiv.getFitnessParams() == eliteVariant:
						newPopulation.append(indiv)
						if len(newPopulation) >= self.params['populationSize']:
							exitFlag = True
							break

			else:
				weights = [ ULTIMATE_FITNESS_EPSILON - x for x in fitnessVariantsErrors.values() ]
				normalizingCoefs = 1./sum(weights)
				parent = chooseTupleRandomly(fitnessVariantsErrors.keys(), weights=weights)
				dummyIndiv = self.getNewIndividual()
				dummyIndiv.setFitnessParams(parent)
				dummyIndiv.mutateFitnessParams()
				child = dummyIndiv.getFitnessParams()
				newFitnessVariants.append(child)

				print('i={}: adding mutated fitness variant {} with parent {}'.format(i, child, parent))

				for indiv in self.population:
					if indiv.getFitnessParams() == parent:
						newIndividual = deepcopy(indiv)
						newIndividual.setFitnessParams(child)
						newPopulation.append(newIndividual)
						if len(newPopulation) >= self.params['populationSize']:
							exitFlag = True
							break

			if exitFlag:
				break

		self.population = newPopulation
