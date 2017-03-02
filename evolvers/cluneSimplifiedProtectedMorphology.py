import numpy as np
from copy import deepcopy
from cluneSimplified import Evolver as CluneSimplifiedEvolver

class Evolver(CluneSimplifiedEvolver):
	'''A variant of connection cost-based multiobjective selection algorithm that
     also protects morphologies while their controllers are optimized.

     The only difference in using this one is that unlike the cluneSimplified
     it always (and not for certain settings of parameters) expects all
     Individuals to be composites of two: morphology (Class0) and controller
     (Class1 in configs of the composite).

     Below is a copy of the cluneSimplified docstring.

     Multiobjective algorithm which minimizes the connection cost alongside
     with maximizing the fitness function. It is similar to the technique used
     in the 2013 Clune Mouret Lipson "The evolutionary origins of modularity"
     paper; the difference is that instead of using NSGA-II, we simply keep the
     whole Pareto front at each generation and add its offsprings to the
     population until it restores its size.

     Required parameters:
       evolParams['populationSize']
       evolParams['initialPopulationType'] - can be 'random' or 'sparse'.
         If 'sparse' is chosen, the initial population will be composed of
         individulas with all genes set to zero and mutated once. To do so,
         the algorithm will use the following method of the individual class:
           evolParams['indivClass'].setValuesToZero().
         Feel free to use it to redefine the meaning of the sparsity!
         More info on benefits of sparse initial populations can be found in
         2015 Bernatskiy Bongard "Exploiting the relationship between structural
         modularity and sparsity for faster network evolution".

     Optional parameters:
       evolParams['secondObjectiveProbability'] - if provided, connection cost
         will only be taken into account with the specified probability. If it
         is not taken into account, the algorithm will assume that the
         individual with larger fitness dominates regardless of connection cost.
         See 2013 Clune et al.
       evolParams['useMaskForSparsity'] - use mask instead of comparing the
         fields to zero to count nonzero values.
       evolParams['noiseAmplitude'] - if provided, noisy evaluations with a
			  uniformly distributed noise of given amplitude will be simulated.

     NOTE: Individual classes with surefire mutation operator are OK.'''

	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)
		for indiv in self.population:
			indiv.tsmm = 0 # time since the last morphological mutation

	def getConnectionCostFunc(self):
		self.secondObjectiveLabel = 'relative age'
		return (lambda x: float(x.tsmm) / (1 + len(filter(lambda y: y!=0, x.parts[1].values))))

	def processMutatedChild(self, child, parent):
		if child.parts[0].id != parent.parts[0].id:
			child.tsmm = -1

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()
		for indiv in self.population:
			indiv.tsmm += 1
