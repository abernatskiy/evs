import json
from copy import deepcopy

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

       behavioralNumHiddenNeurons
       behavioralMutModifyNeuron
	     behavioralMutModifyConnection
       behavioralMutAddRemRatio

       governingNumHiddenNeurons
       governingMutAddBehavioralController
       governingMutRemoveBehavioralController
       governingMutModifyNeuron
	     governingMutModifyConnection
       governingMutAddRemRatio

       weightScale (default 1.0)

  '''
	def __init__(self, params):
		super(Individual, self).__init__(params)

		self.nsen = self.params['numSensorNeurons']
		self.nchan = self.params['numMotorNeurons']
		self.nopt = self.params['initNumBehavioralControllers']

		self.behavioralControllers = []
		bcparams = self._getBCParams()
		for _ in range(self.nopt):
			self.behavioralControllers.append(ctrnnIndiv(bcparams))

		gcparams = self._getGCParams()
		self.governingController = ctrnnIndiv(gcparams)

	def __str__(self):
		genotype = {}

		genotype['numBehavioralControllers'] = self.nopt

		genotype['behavioralControllers'] = []
		for bc in self.behavioralControllers:
			genotype['behavioralControllers'].append(bc.values)

		genotype['governingController'] = _translateGCValues(self.governingController.values)

		return str(self.id) + ' ' + json.dumps(genotype)

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
