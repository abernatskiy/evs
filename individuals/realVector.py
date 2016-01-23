import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Base class for real-valued vectors. Do not use, inherit.'''
	def fromStr(self, representation):
		vals = map(float, representation.split())
		self.id = int(vals[0])
		self.values = vals[1:]

	def setValuesToZero(self): # for sparse-first search and certain brute force approaches
		self.values = np.zeros(self.params['length'], dtype=np.int)
		self.renewID()
