import numpy as np
from ctrnn import Individual as ctrnnIndividual

class Individual(ctrnnIndividual):
	'''Class for continuous time-recurrent neural networks (CTRNNs)
	   represented in genome as JSON hierarchical structures.
     Unlike in ctrnn.py, weights take only discrete values of
     (+-)weightScale*2^k, where k in an integer.

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
	def _getInitialConnectionWeight(self):
		return np.random.choice([-1.,1.])*self.params['weightScale']

	def _getModifiedConnectionWeight(self, prevWt):
		modificationType = np.random.choice(['decrease', 'increase', 'flipSign'])
		if modificationType == 'decrease':
			return prevWt/2.
		elif modificationType == 'increase':
			return prevWt*2.
		elif modificationType == 'flipSign':
			return -1.*prevWt
