import numpy as np
from copy import deepcopy

from ctrnnDiscreteWeightsFleetOfIdenticals import Individual as fleetIndiv

class Individual(fleetIndiv):
	'''Evolvable fitness function'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self.numFitnessParams = params['numFitnessParams']
		self.fitnessParams = self._getInitialFitnessParams()

	def _getInitialFitnessParams(self):
		return 2.**np.random.randint(-4, 5, size=self.numFitnessParams)

	def _getUltimateFitnessParams(self):
		return np.zeros(self.numFitnessParams)

	def setFitnessParams(self, newParams):
		self.fitnessParams = deepcopy(np.array(newParams))
		self.renewID()

	def getFitnessParams(self):
		return tuple(self.fitnessParams)

	def hideFitnessParams(self):
		self._hiddenFitnessParams = self.fitnessParams
		self.fitnessParams = self._getUltimateFitnessParams()

	def showFitnessParams(self):
		self.fitnessParams = self._hiddenFitnessParams

	def mutateFitnessParams(self):
		i = np.random.randint(self.numFitnessParams)
		self.fitnessParams[i] = self.fitnessParams[i]*(2.**np.random.choice([-1,1]))
		self.renewID()

	def _getGenotypeStruct(self):
		return {'fitnessCoefficients': list(self.fitnessParams), 'controller': super(Individual, self)._getGenotypeStruct()}

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toInt'].update(['numFitnessParams'])
		return t
