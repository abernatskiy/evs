import json
import numpy as np

from ctrnnDiscreteWeightsFleetOfIdenticals import Individual as Fleet

class Individual(Fleet):
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self.minTime = 2.028959000152416
		self.timeMultiplier = 1.5

		self.timeDegree = 0

		self.mutTimeIncrease = 0.05
		self.mutTimeDecrease = 0.05

		self.maxTimeDegree = 8

		self.evaluationTime = self.minTime

	def __str__(self):
		return str(self.id) + ' ' + json.dumps({'evaluationTime': self.evaluationTime, 'controller': self._getGenotypeStruct()})

	def _getTime(self):
		return self.minTime*self.timeMultiplier**self.timeDegree

	def mutate(self):
		self.renewID()
		r = np.random.random()
		if r < self.mutTimeIncrease:
			if self.timeDegree < self.maxTimeDegree:
				self.timeDegree += 1
				self.evaluationTime = self._getTime()
				return True
			else:
				return self.mutate()
		elif r < self.mutTimeIncrease + self.mutTimeDecrease:
			if self.timeDegree > 0:
				self.timeDegree -= 1
				self.evaluationTime = self._getTime()
				return True
			else:
				return self.mutate()
		else:
			return super(Individual, self).mutate()
