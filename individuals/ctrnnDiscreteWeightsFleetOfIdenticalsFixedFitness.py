import numpy as np

from ctrnnDiscreteWeightsFleetOfIdenticalsEvolvableFitness import Individual as fleetIndiv

class Individual(fleetIndiv):
	'''Non-evolvable fitness function that seems evolvable'''
	def _getInitialFitnessParams(self):
		return np.ones(self.numFitnessParams)

	def mutateFitnessParams(self):
		pass
