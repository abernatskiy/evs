import json

from ctrnn import Individual as ctrnnIndiv

class Individual(ctrnnIndiv):
	'''Array of identical CTRNNs

     Parameter fields:
       all the fields of ctrnnWithSwitch
       fleetSize
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self.fleetSize = params['fleetSize']

	def _getGenotypeStruct(self):
		return [self.values]*self.fleetSize

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toInt'].update({'fleetSize'})
		return t
