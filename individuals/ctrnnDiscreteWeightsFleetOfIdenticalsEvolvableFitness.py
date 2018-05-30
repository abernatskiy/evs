import numpy as np
from copy import deepcopy

from ctrnnDiscreteWeightsFleetOfIdenticals import Individual as fleetIndiv

class Individual(fleetIndiv):
	'''Evolvable fitness function'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self.numFitnessParams = params['numFitnessParams']
		self.fitnessParams = np.ones(self.numFitnessParams)
		self.mutateFitnessParams()

	def setFitnessParams(self, newParams):
		self.fitnessParams = deepcopy(np.array(newParams))

	def mutateFitnessParams(self):
		i = np.random.randint(self.numFitnessParams)
		self.fitnessParams[i] = self.fitnessParams[i]*(2**np.random.choice([-1,1]))

	def _getGenotypeStruct(self):
		return {'fitnessCoefficients': self.fitnessParams, 'controller': super(Individual, self)._getGenotypeStruct()}
