import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

RELATIVE_FITNESS_EPSILON = 1.

def chooseTupleRandomly(iterableTuple, size=None, weights=None):
	tupleList = list(iterableTuple)
	numTuples = len(tupleList)
	if weights is None:
		normalized_p = None
	else:
		norm = sum(weights)
		normalized_p = [ x/norm for x in weights ]
	idxs = np.random.choice(range(numTuples), size=size, p=normalized_p)
	if size is None:
		return tupleList[idxs]
	else:
		return [ tupleList[i] for i in idxs ]

class Evolver(BaseEvolver):
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName=None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)
		self.setParamDefault('initialPopulationType', 'random')

		while len(self.population) < self.params['populationSize']:
			indiv = self.getNewIndividual()
			self.population.append(indiv)

		fitnessVariants = { indiv.getFitnessParams() for indiv in self.population }
		initialFitnessVariant = chooseTupleRandomly(fitnessVariants) # picking one!

		for indiv in self.population:
			indiv.age = 0
			indiv.setFitnessParams(initialFitnessVariant)

		self.communicator.evaluate(self.population)

	def requiredParametersTranslator(self):
		t = super(Evolver, self).requiredParametersTranslator()
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

	#def getConnectionCostFunc(self):
	#	self.secondObjectiveLabel = 'connection cost'
	#	return lambda x: x.connectionCost()

	def getUltimateErrorFunc(self):
		return lambda x: -1.*x.scores[0]

	def getCurrentErrorFunc(self):
		return lambda x: -1.*x.scores[1]

	def getAgeFunc(self):
		return lambda x: x.age

	def generateLogsAndStdout(self):
		super(Evolver, self).generateLogsAndStdout()

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		print('updatePopulation called, pre-update done...')

		# Pareto front of the ultimate fitness vs the age is the elite
		self._newPopulation = self.findParetoFrontManyObjectives([self.getUltimateErrorFunc(), self.getAgeFunc()])
		print('Elite from ultimate fitness: ' + ' '.join(map(str, [ (i.id, self.getUltimateErrorFunc()(i), self.getAgeFunc()(i)) for i in self._newPopulation ])))

		# However, the selection within each lineage is guided by the current fitness
		ages = [ self.getAgeFunc()(indiv) for indiv in self._newPopulation ]
		lineages = [ [ indiv for indiv in self.population if self.getAgeFunc()(indiv)==a ] for a in ages ]
		print('Found {} Pareto-optimal lineages, sizes {}'.format(len(lineages), [ len(la) for la in lineages ]))

		# Both in its elitistic...
		for la in lineages:
			self._addLineageEliteToNewPopulation(la)

		print('Added lineage elites. Total elite size is {} ({} of population size)'.format(len(self._newPopulation), float(len(self._newPopulation))/self.params['populationSize']))
		if(len(self._newPopulation)>=self.params['populationSize']):
			raise ValueError('Elite size is no less than population size, exiting')

		# ...and non-elitistic behavior
		while len(self._newPopulation)<self.params['populationSize']-1:
			la = chooseTupleRandomly(lineages)
			self._addLineageOffspringToNewPopulation(la)

		# Finally, we need to increase age of existing lineages and add some new blood
		for indiv in self._newPopulation:
			indiv.age += 1
		self._newPopulation.append(self.getNewIndividual())
		self._newPopulation[-1].age = 0
		print('Added a new lineage starting with individual {}'.format(self._newPopulation[-1].id))

		self.population = self._newPopulation

		self.communicator.evaluate(self.population)

	def _addLineageEliteToNewPopulation(self, lineage):
		bestCurrentError = min([ self.getCurrentErrorFunc()(indiv) for indiv in lineage ])
		bestIndivs = sorted([ indiv for indiv in lineage if self.getCurrentErrorFunc()(indiv)==bestCurrentError ], key=lambda x: x.id, reverse=True)
		bestIndiv = bestIndivs[0]
		print('Considering the elite indiv of lineage {}. Best error based on current func is {}. There are {} indivs with this error'.format(self.getAgeFunc()(lineage[0]), bestCurrentError, len(bestIndivs)))

		currentEliteIDs = [ indiv.id for indiv in self._newPopulation ]
		if bestIndiv.id in currentEliteIDs:
			print('Not adding the best indiv {}, it is already in the elite'.format(bestIndiv.id))
		else:
			self._newPopulation.append(bestIndiv)
			print('Added lineage best indiv {} to the elite'.format(bestIndiv.id))

	def _addLineageOffspringToNewPopulation(self, lineage):
		weights = [ RELATIVE_FITNESS_EPSILON+self.getCurrentErrorFunc()(indiv) for indiv in lineage ]
		newIndiv = deepcopy(chooseTupleRandomly(lineage, weights=weights))
		if newIndiv.mutate():
			self._newPopulation.append(newIndiv)
			print('Added new offspring {} of lineage {}'.format(newIndiv.id, self.getAgeFunc()(lineage[0])) )
