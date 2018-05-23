import json
import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Class for continuous time-recurrent neural networks (CTRNNs)
	   represented in genome as JSON hierarchical structures.

     Constructor takes a dictionary with the following parameter
     fields:
	     numSensorNeurons
	     numHiddenNeurons
	     numMotorNeurons
       mutModifyConnection
	     mutModifyNeuron
       mutAddRemRatio
	   Optional:
	     weightScale (default 1.)
	   Note: a hidden bias neuron is always automatically added, so
	   for the purpose of computing the number of connections the
	   number is increased by 1.
	'''
	avgInDegree = 2
	stdDevCoef = 1.

	def __init__(self, params):
		super(Individual, self).__init__(params)

		self.modifyNeuronFrac = self.params['mutModifyNeuron']
		self.modifyConnFrac = self.params['mutModifyConnection']
		addRemFrac = 1.0 - self.modifyNeuronFrac - self.modifyConnFrac
		self.removeConnFrac = addRemFrac / (self.params['mutAddRemRatio']+1.)
		self.addConnFrac = addRemFrac - self.removeConnFrac

		self.nsen = self.params['numSensorNeurons']
		self.nhid = self.params['numHiddenNeurons']
		self.nmot = self.params['numMotorNeurons']
		self.layerParamDict = {'sensorToHidden': (self.nsen, self.nhid+1),
		                       'hiddenToHidden': (self.nhid+1, self.nhid+1),
		                       'hiddenToMotor':  (self.nhid+1, self.nmot)} # Remember: there is a hidden bias neuron added automatically!

		self.setParamDefault('weightScale', 1.)

		self.values = {}
		self.values['numHiddenNeurons'] = self.nhid
		self.values['motorNeuronsParams'] = {}
		self.values['hiddenNeuronsParams'] = {}
		for neuronParamName in ['initialState', 'tau', 'alpha']:
			self.values['motorNeuronsParams'][neuronParamName] = [ self._getInitialNeuronParam(neuronParamName) for _ in range(self.nmot) ]
			self.values['hiddenNeuronsParams'][neuronParamName] = [ self._getInitialNeuronParam(neuronParamName) for _ in range(self.nhid) ]

		self.setValuesToZero()
		for layer in self.layerParamDict.keys():
			self._eswPopulateLayer(layer)

	def _eswPopulateLayer(self, layerName):
		n,m = self.layerParamDict[layerName]
		connProb = float(Individual.avgInDegree)/float(n)
#		print("Populating layer " + layerName + ": n=" + str(n) + " m=" + str(m) + " p=" + str(connProb))
		for i in range(n):
			for j in range(m):
				r = np.random.random()
#				print('i={} j={} r={}'.format(i,j,r))
				if(r < connProb):
					w = self._getInitialConnectionWeight()
					self.values['synapsesParams'][layerName].append([i,j,w])
#					print('Added connection: ' + str(self.values['synapsesParams'][layerName][-1]))

	def _getInitialConnectionWeight(self):
		return (2.*np.random.random()-1.)*self.params['weightScale']

	def _getModifiedConnectionWeight(self, prevWt):
		return np.random.normal(loc=prevWt, scale=Individual.stdDevCoef*np.abs(prevWt))

	def _getInitialNeuronParam(self, paramType):
		# Constants for now
		constants = {'initialState': -1., 'tau': 1., 'alpha': 1.}
		return constants[paramType]

	def _getModifiedNeuronParam(self, paramType, prevVal):
		# Easiest way
		return np.abs(self._getModifiedConnectionWeight(prevVal)) if paramType=='tau' else self._getModifiedConnectionWeight(prevVal)

	def _getNumConnections(self):
		return sum([ len(layerConns) for layerConns in self.values['synapsesParams'].values() ])

	def _getNumPossibleConnections(self):
		return sum([ n*m for n,m in self.layerParamDict.values() ])

	def _getNumNeuronsParams(self):
		# Alphas, taus and the initial state
		return 3*self._getNumNeurons()

	def _getNumNeurons(self):
		return self.nhid+self.nmot

	def _getGenotypeStruct(self):
		return self.values

	def __str__(self):
		return str(self.id) + ' ' + json.dumps(self._getGenotypeStruct())

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toFloat'].update({'mutModifyConnection', 'mutModifyNeuron', 'mutAddRemRatio'})
		t['toInt'].update({'numSensorNeurons', 'numMotorNeurons', 'numHiddenNeurons'})
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
						connectionExists = False
						for conn in layerConns:
							if conn[0] == i and conn[1] == j:
								connectionExists = True
						if not connectionExists:
							if counter == makeConnectionAt:
								w = self._getInitialConnectionWeight()
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
			# print("Modifying connection param " + str(modifyParamAt) + " out of " + str(numNeuronsParams))
			for layer,layerConns in self.values['synapsesParams'].iteritems():
				for connPos in range(len(layerConns)):
					if counter == modifyConnectionAt:
						# print('Modifying connection at ' + str(layer) + ', position ' + str(connPos))
						oldval = self.values['synapsesParams'][layer][connPos][2]
						newval = self._getModifiedConnectionWeight(oldval)
						self.values['synapsesParams'][layer][connPos][2] = newval
						return newval != oldval
					counter += 1
		return False

	def _modifyNeuron(self):
		numNeuronsParams = self._getNumNeuronsParams()
		modifyParamAt = np.random.randint(numNeuronsParams)
		# print("Modifying neuron param " + str(modifyParamAt) + " out of " + str(numNeuronsParams))
		counter = 0
		for group in ['motorNeuronsParams', 'hiddenNeuronsParams']:
			for paramName, paramVals in self.values[group].iteritems():
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

	def _addMotorNeuron(self):
		for neuronParamName in ['initialState', 'tau', 'alpha']:
			self.values['motorNeuronsParams'][neuronParamName].append(self._getInitialNeuronParam(neuronParamName))
		self.nmot += 1

	def _removeMotorNeuron(self, idx):
		for neuronParamName in ['initialState', 'tau', 'alpha']:
			self.values['motorNeuronsParams'][neuronParamName].pop(idx)

		connsToRemove = []
		for i,conn in enumerate(self.values['synapsesParams']['hiddenToMotor']):
			if conn[1] == idx:
				connsToRemove.append(i)
		# The following line simply removes the connections by indices
		# FIXME: probably can be replaces with one line of list comprehension
		self.values['synapsesParams']['hiddenToMotor'] = [ i for j, i in enumerate(self.values['synapsesParams']['hiddenToMotor']) if j not in connsToRemove ]

		self.nmot -= 1

	def connectionCost(self, useWeights=False):
		if useWeights:
			return sum([ sum([ np.abs(w) for _,_,w in conns ]) for conns in self.values['synapsesParams'] ])
		else:
			return sum([ len(x) for x in self.values['synapsesParams'].values() ])

