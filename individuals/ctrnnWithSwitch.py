import json
from copy import deepcopy
import numpy as np

from baseIndividual import BaseIndividual
from ctrnn import Individual as ctrnnIndiv

class Individual(BaseIndividual):
	'''CTRNNs with a parallel switch that effectively
     replaces controller depending on the output of
     a special subnetwork - governing body.

     Parameter fields:
       numSensorNeurons
       numMotorNeurons
       initNumBehavioralControllers

       mutGoverning

       governingMutAddBehavioralController
       governingMutRemoveBehavioralController

       governingNumHiddenNeurons
       governingMutModifyNeuron
	     governingMutModifyConnection
       governingMutAddRemRatio

       behavioralNumHiddenNeurons
       behavioralMutModifyNeuron
	     behavioralMutModifyConnection
       behavioralMutAddRemRatio

       weightScale (default 1.0)

  '''
	def __init__(self, params):
		super(Individual, self).__init__(params)

		self.nsen = self.params['numSensorNeurons']
		self.nchan = self.params['numMotorNeurons']
		self.nopt = self.params['initNumBehavioralControllers']

		self.setParamDefault('weightScale', 1.)

		self.behavioralControllers = []
		bcparams = self._getBCParams()
		for _ in range(self.nopt):
			self.behavioralControllers.append(ctrnnIndiv(bcparams))

		gcparams = self._getGCParams()
		self.governingController = ctrnnIndiv(gcparams)

	def __str__(self):
		return str(self.id) + ' ' + json.dumps(self._getGenotypeStruct())

	def _getGenotypeStruct(self):
		genotype = {}

		genotype['numBehavioralControllers'] = self.nopt

		genotype['behavioralControllers'] = []
		for bc in self.behavioralControllers:
			genotype['behavioralControllers'].append(bc.values)

		genotype['governingController'] = self._translateGCValues(self.governingController.values)

		return genotype

	def _getBCParams(self):
		bcparams = {}
		bcparams['numSensorNeurons'] = self.params['numSensorNeurons']
		bcparams['numMotorNeurons'] = self.params['numMotorNeurons']
		bcparams['numHiddenNeurons'] = self.params['behavioralNumHiddenNeurons'] # sic!
		bcparams['mutModifyConnection'] = self.params['behavioralMutModifyConnection']
		bcparams['mutModifyNeuron'] = self.params['behavioralMutModifyNeuron']
		bcparams['mutAddRemRatio'] = self.params['behavioralMutAddRemRatio']
		bcparams['weightScale'] = self.params['weightScale']
		return bcparams

	def _getGCParams(self):
		gcparams = {}
		gcparams['numSensorNeurons'] = self.nsen + self.nchan
		gcparams['numMotorNeurons'] = self.nopt
		gcparams['numHiddenNeurons'] = self.params['governingNumHiddenNeurons']
		gcparams['mutModifyConnection'] = self.params['governingMutModifyConnection']
		gcparams['mutModifyNeuron'] = self.params['governingMutModifyNeuron']
		gcparams['mutAddRemRatio'] = self.params['governingMutAddRemRatio']
		gcparams['weightScale'] = self.params['weightScale']
		return gcparams

	def _translateGCValues(self, gcvalues):
		v = {}
		v['numHiddenNeurons'] = gcvalues['numHiddenNeurons']
		v['hiddenNeuronsParams'] = deepcopy(gcvalues['hiddenNeuronsParams'])
		v['governingNeuronsParams'] = deepcopy(gcvalues['motorNeuronsParams'])
		v['synapsesParams'] = {}
		gcsynp = deepcopy(gcvalues['synapsesParams'])
		v['synapsesParams']['hiddenToHidden'] = gcsynp['hiddenToHidden']
		v['synapsesParams']['hiddenToGoverning'] = gcsynp['hiddenToMotor']
		v['synapsesParams']['sensorToHidden'] = [ [i,j,w] for i,j,w in gcsynp['sensorToHidden'] if i<self.nsen ]
		v['synapsesParams']['trueMotorToHidden'] = [ [i-self.nsen,j,w] for i,j,w in gcsynp['sensorToHidden'] if i>=self.nsen ]
		return v

	def mutate(self):
		mutated = False
		while not mutated:
			randVal0 = np.random.random()
			if randVal0 < self.params['mutGoverning']:
				randVal1 = np.random.random()
				if randVal1 < self.params['governingMutAddBehavioralController']:
					mutated = self._addBehavioralController()
				elif randVal1 < self.params['governingMutAddBehavioralController'] + self.params['governingMutRemoveBehavioralController']:
					mutated = self._removeBehavioralController()
				else:
					mutated = self.governingController.mutate()
			else:
				bcidx = np.random.randint(self.nopt)
				mutated = self.behavioralControllers[bcidx].mutate()
		self.renewID()
		return True

	def _addBehavioralController(self):
		bcparams = self._getBCParams()
		self.behavioralControllers.append(ctrnnIndiv(bcparams))
		self.governingController._addMotorNeuron()
		self.nopt += 1

	def _removeBehavioralController(self):
		if self.nopt < 2:
			return False
		bcidx = np.random.randint(self.nopt)
		self.behavioralControllers.pop(bcidx)
		self.governingController._removeMotorNeuron(bcidx)
		self.nopt -= 1

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toFloat'].update({'mutGoverning', 'governingMutAddBehavioralController', 'governingMutRemoveBehavioralController',
		                     'governingNumHiddenNeurons', 'governingMutModifyNeuron', 'governingMutModifyConnection', 'governingMutAddRemRatio',
		                     'behavioralNumHiddenNeurons', 'behavioralMutModifyNeuron', 'behavioralMutModifyConnection', 'behavioralMutAddRemRatio'})
		t['toInt'].update({'numSensorNeurons', 'numMotorNeurons', 'initNumBehavioralControllers'})
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toFloat'].update({'weightScale'})
		return t

	def connectionCost(self, useWeights=False):
		bcweights = [ bc.connectionCost(useWeights=useWeights) for bc in self.behavioralControllers ]
		#print('bcweights = {}'.format(bcweights))
		return sum(bcweights)
#		return sum([ bc.connectionCost(useWeights=useWeights) for bc in self.behavioralControllers ])

	def setValuesToZero(self):
		for bc in self.behavioralControllers:
			bc.setValuesToZero()
