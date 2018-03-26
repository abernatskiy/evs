import json
import numpy as np

from ctrnnWithSwitch import Individual as ctrnnswIndiv

class Individual(ctrnnswIndiv):
	'''Array of identical CTRNNs with switches

     Parameter fields:
       all the fields of ctrnnWithSwitch
       fleetSize
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self.fleetSize = params['fleetSize']

	def _getGenotypeStruct(self):
		return [super(Individual, self)._getGenotypeStruct()]*self.fleetSize

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toInt'].update({'fleetSize'})
		return t
