import json
import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Class for continuous time-recurrent neural networks (CTRNNs)
	   represented in genome as JSON hierarchical structures.

     Constructor takes a dictionary with the following parameter
     fields:
	     numInputNeurons
	     numOutputNeurons
	     numHiddenNeurons
       mutModifyConnection
	     mutModifyNeuron
       mutAddRemRatio
	   Optional:
	     weightScale (default 1.)
	'''
	avgInDegree = 2
	stdDevCoef = 1.

	def __init__(self, params):
		super(Individual, self).__init__(params)

		self.modifyNeuronFrac = self.params['mutModifyNeuron']
		self.modifyConnFrac = self.params['mutModifyConnection']
		addRemFrac = 1.0 - self.modifyNeuronFrac - self.modifyConnFrac
		self.removeConnFrac = addRemFrac / (self.params['mutAddRemRatio']+1.)
		self.addConnFrac = addRemFrac - self.deleteFrac

		self.nsen = self.params['numSensorNeurons']
		self.nhid = self.params['numHiddenNeurons']
		self.nmot = self.params['numMotorNeurons']
		self.layerParamDict = {'sensorToHidden': (self.nsen, self.nhid),
		                       'hiddenToHidden': (self.nhid, self.nhid),
		                       'hiddenToMotor':  (self.nhid, self.nmot)}

		self.setParamDefault('weightScale', 1.)

		self.values = {}
		self.values['numHiddenNeurons'] = self.nhid
		self.values['motorNeuronParams'] = {}
		self.values['hiddenNeuronParams'] = {}
		for neuronParamName in ['initialState', 'tau', 'alpha']:
			self.values['motorNeuronParams'][neuronParamName] = [ self._getInitialNeuronParam(neuronParamName) for _ in range(self.nmot) ]
			self.values['hiddenNeuronParams'][neuronParamName] = [ self._getInitialNeuronParam(neuronParamName) for _ in range(self.nhid) ]

		self.setValuesToZero()
		for layer in self.layerParamDict.keys():
			self._eswPopulateLayer(layer)

	def _eswPopulateLayer(self, layerName):
		n,m = self.layerParamDict(layerName)
		connProb = float(Individual.avgInDegree)/float(n)
		for i in range(n):
			for j in range(m):
				r = np.random.random()
				if(r < connProb):
					w = self._getInitialConnectionWeight()
					self.values['sensorsParams'][layerName].append([i,j,w])

	def _getInitialConnectionWeight(self):
		return (2.*np.random.random()-1.)*self.params['weightScale']

	def _getModifiedConnectionWeight(self, prevWt):
		return np.random.normal(loc=prevWt, scale=Individual.stdDevCoef*prevWt)

	def _getInitialNeuronParam(self, paramType):
		# Constants for now
		constants = {'initalState': -1., 'tau': 1., 'alpha': 1.}
		return constants[paramType]

	def _getModifiedNeuronParam(self, paramType, prevVal):
		# Easiest way
		return self._getModifiedConnectionWeight(prevVal)

	def _getNumConnections(self):
		return sum([len(layerConns) for layerConns in self.values['sensorParams'].values()])

	def _getNumPossibleConnections(self):
		return self.nsen*self.nhid + self.nhid*self.nhid + self.nhid*self.nmot

	def _getNumNeuronParams(self):
		# Alphas, taus and the initial state
		return 3*(self.nhid+self.nmot)

	def __str__(self):
		print(json.dumps(self.values))

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toFloat'].update({'mutExploration', 'mutInsDelRatio'})
		t['toInt'].update({'numInputNeurons', 'numOutputNeurons', 'numHiddenNeurons'})
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toFloat'].update({'weightScale'})
		return t

	def setValuesToZero(self):
		# No idea on what to do with taus, alphas and initial states, so just resetting the connections
		# self.values['synapsesParams'] = {'sensorToHidden': [], 'hiddenToHidden': [], 'hiddenToMotor': []}
		self.values['synapsesParams'] = { layerName: [] for layerName in self.layerParamDict.keys() }

	def _addConnection(self):
		numMissingConnections = self._getNumPossibleConnections() - self._getNumConnections()
		if numMissingConnections > 0:
			makeConnectionAt = np.random.randint(numMissingConnections)
			counter = 0
			for layer,layerConns in self.values['synapsesParams'].iteritems():
				n,m = self.layerParamDict[layer]
				for i in range(n):
					for j in range(m):
						connectionExists = false
						for conn in layerConns:
							if conn[0] == i and conn[1] == j:
								connectionExists = true
						if not connectionExists:
							if counter == makeConnectionAt:
								w = self._getRandomWeight()
								self.values['synapsesParams'][layer].append([i,j,w])
								return True
							counter += 1
		else:
			return False

	def _removeConnection(self):
		numExistingConnections = self._getNumConnections()
		if numExistingConnections > 0:
			counter = 0
			removeConnectionAt = np.random.randint(numExistingConnections)
			for layer,layerConns in self.values['synapsesParams'].iteritems():
				for conn in layerConns:
					if counter == removeConnectionAt:
						self.values['synapsesParams'][layer].remove(conn)
						return True
					counter += 1
		return False

	def _modifyConnection(self):
		numExistingConnections = self._getNumConnections()
		if numExistingConnections > 0:
			counter = 0
			modifyConnectionAt = np.random.randint(numExistingConnections)
			for layer,layerConns in self.values['synapsesParams'].iteritems():
				for connPos in range(len(layerConns)):
					if counter == modifyConnectionAt:
						oldval = self.values['synapsesParams'][layer][connPos]
						newval = self._getModifiedConnectionWeight(oldval)
						self.values['synapsesParams'][layer][connPos] = newval
						return newval != oldval
					counter += 1
		return False

	def _modifyNeuron(self):
		numNeuronParams = self._getNumNeurons()
		modifyParamAt = np.random.randint(numNeuronParams)
		for group in ['motorNeuronParams', 'hiddenNeuronParams']:
			for paramName, paramVals in self.values[group]:
				for paramPos in range(len(paramVals)):
					if counter == modifyParamAt:
						oldval = self.values[group][paramName][paramPos]
						newval = self._getModifiedNeuronParam(paramName, oldval)
						self.values[group][paramName][paramPos] = newval
						return newval != oldval
					counter +=1
		return False

	def mutate(self):
		mutated = False
		while not mutated:
			randVal = np.random.random()
			if randVal < self.modifyNeuronFrac:
				mutated = self._modifyNeuron()
			elif randVal < (self.modifyNeuronFrac + self.modifyConnFrac):
				mutated = self._modifyConnection()
			elif randVal < (self.modifyNeuronFrac + self.modifyConnFrac + self.addConnFrac):
				mutated = self._addConnection()
			else:
				mutated = self._removeConnection()
		self.renewID()
		return True
