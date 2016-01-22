import numpy as np
from realVectorTunableBoundsSureMutation import Individual as RealVectorTunableBoundsSureMutation

class Individual(RealVectorTunableBoundsSureMutation):
	'''Class for evolutionary individuals described by a vector of
     real-valued weights taken from [initLowerLimit, initUpperLimit]
     of constant length, with a single-valued score represented
     by a real number.

     Unlile realVectorTunableBoundsSureMutation, this class
     keeps track of which weights are close to zero and which
     are not. Whether the weight is close to zero or not is
     determined by a reloadable member function isAZeroWeight(self, pos).
     The mutation proceeds as follows:
      - with probability of mutExploration, the mutation operator
        will attempt to change a randomly picked nonzero weight
        using the reloadable changeWeight(self, pos) function.
        If the result ends up being close to zero, the connection
        will be removed;
      - all other cases are divided between the insertions and
        deletions. Ratio of the frequencies is controlled by the
        mutInsDelRatio parameter.
     Constructor takes a dictionary with the following parameter
     fields:
       initLowerLimit, initUpperLimit
       relativeMutationAmplitude
       length                         - length of the vector
     Optional fields:
       lowerCap, upperCap
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)

		if not self.params.has_key('initProbabilityOfConnection')
			self.params['initProbabilityOfConnection'] = 1.0

		self.changeFrac = self.params['mutExploration']
		self.deleteFrac = (1.0 - self.changeFrac)/(self.params['mutInsDelRatio']+1)
		self.insertFrac = 1.0 - self.changeFrac - self.deleteFrac

		self.mask = map(lambda x: x<self.params['initProbabilityOfConnection'], np.random.random(self.params['length']))

		for pos,connExists in enumerate(self.mask):
			if not connExists:
				self.values[pos] = 0.0

	def _getRandomPosition(self, boolConnType):
		positions = []
		for pos,connExists in enumerate(self.mask):
			if connExists == boolConnType:
				positions.append(pos)
		if positions == []:
			return -1
		else:
			return np.random.choose(positions)

	def isAZeroWeight(self, pos):
		return self.values[pos] == 0.0

	def changeWeight(self, pos):
		self.values[pos] *= (1. + self.params['relativeMutationAmplitude']*np.random.standard_normal())
		self.values[pos] = np.clip(self.values[pos], self.params['lowerCap'], self.params['upperCap'])

	def _insert(self):
		insPos = self._getRandomPosition(False)
		if insPos != -1:
			self.values[insPos] = self.getAnInitialValue()
			if not self.isAZeroWeight(insPos):
				self.mask[insPos] = True
				return True
			else:
				self.values[insPos] = 0.0
		return False

	def _delete(self):
		insPos = self._getRandomPosition(True)
		if insPos != -1:
			self.mask[insPos] = False
			self.values[insPos] = 0.0
			return True
		return False

	def _change(self):
		insPos = self._getRandomPosition(True)
		if insPos != -1:
			oldVal = self.values[mutPos]
			self.changeWeight(mutPos)
			if self.isAZeroWeight(mutPos):
				self.values[mutPos] = 0.0
				self.mask[mutPos] = False
			if oldVal != self.values[mutPos]:
				return True
		return False

	def mutate(self):
		mutated = False
		randVal = np.random.random()
		if randVal < self.changeFrac:
			mutated = self._change()
		elif randVal < (self.changeFrac + self.insertFrac):
			mutated = self._insert()
		else:
			mutated = self._delete()
    if mutated:
      self.renewID()
    return mutated
