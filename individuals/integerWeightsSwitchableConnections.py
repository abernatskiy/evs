import numpy as np
from realWeightsSwitchableConnections import Individual as RealWeightsSwitchableConnections

def inclusiveRange(lval, uval):
	return map(float, xrange(int(lval), int(uval)+1))

class Individual(RealWeightsSwitchableConnections):
	'''Class for evolutionary individuals described by a vector of
     integer-valued weights taken from [initLowerLimit, initUpperLimit]
     of constant length, with a single-valued score represented
     by a real number. The integers are internally represented as
     floating point numbers. This may reflect on the Individuals'
     string representations.

     This class keeps track of which weights are zero and which
     are not using a member function isAZeroWeight(self, pos). This
     information is stored at self.map for use in mutation and
     connection cost compuatations.

     The mutation proceeds as follows:
      - with probability of mutExploration, the mutation operator
        will to attempt increase a randomly picked nonzero weight
        by a number randomly selected from
        [-mutationAmplitude, -mutationAmplitude+1, ... , mutationAmplitude]
        If the result ends up being a zero, the connection
        is removed. If the result cannot be changed in the selected
        direction due to limits (lowerCap, upperCap), no change is
        made but the whole mutation process is restarted from scratch.
      - all other cases are divided between the insertions and
        deletions. Ratio of the frequencies is controlled by the
        mutInsDelRatio parameter.
     Constructor takes a dictionary with the following parameter
     fields:
       length
       initLowerLimit, initUpperLimit
       mutExploration
       mutInsDelRatio
     Optional fields:
       mutationAmplitude (default 1)
       initProbabilityOfConnection (default 1)
       lowerCap, upperCap (default -Inf, Inf)
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)

		if not self.params.has_key('mutationAmplitude'):
			self.params['mutationAmplitude'] = 1.0

		self._ensureParamIntegerness('initLowerLimit')
		self._ensureParamIntegerness('initUpperLimit')
		self._ensureParamIntegerness('lowerCap')
		self._ensureParamIntegerness('upperCap')
		self._ensureParamIntegerness('mutationAmplitude')

	def _ensureParamIntegerness(self, paramName):
		if not self.params[paramName].is_integer():
			raise ValueError(paramName + ' should be an integer (is ' + str(self.params[paramName]))

	def isAZeroWeight(self, pos):
		# Redefining to safeguard against possible forgetful alterations of the parent class
		return self.values[pos] == 0.0

	def changeWeight(self, pos):
		self.values[pos] += np.random.choice(inclusiveRange(-1.*self.params['mutationAmplitude'], self.params['mutationAmplitude']))
		self.values[mutPos] = np.clip(self.values[mutPos], self.params['lowerCap'], self.params['upperCap'])

	def getAnInitialValue(self):
		return np.random.choice(inclusiveRange(self.params['initLowerLimit'], self.params['initUpperLimit']))
