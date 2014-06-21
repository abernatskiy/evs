import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Class for evolutionary individuals described by a vector of 
     floating point numbers (FPNs) in [0,1] of constant length, with 
     a single-valued score represented by a FPN. Constructor takes a 
     dictionary with the following parameter fields:
       length     - number of floating point numbers (FPNs)
       precision  - number of significant digits to keep for each FPN
       mutationProbability - probability that mutation occurs upon 
                             mutate() call (for each value)
       mutationAmplitude   - coefficient in front of the Gaussian distribution 
                             xgiving the amplitude of the mutational change'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self.values = np.random.random_sample(self.params['length'])
		self.values = np.around(self.values, self.params['precision'])

	def __str__(self):
		representation = str(self.id)
		for value in self.values:
			representation += ' '
			representation += str(value)
		return representation

	def setEvaluation(self, scoreStr):
		valueStrings = scoreStr.split()
		if self.checkID(int(valueStrings[0])):
			self.score = float(valueStrings[1])

	def mutate(self):
		newValues = []
		mutated = False
		for val in self.values:
			if np.random.random() <= self.params['mutationProbability']:
				mutated = True
				newValues.append(val + np.random.randn()*self.params['mutationAmplitude'])
				if newValues[-1] < 0.0:
					newValues[-1] = 0.0
				if newValues[-1] > 1.0:
					newValues[-1] = 1.0
			else:
				newValues.append(val)
		if mutated:
			self.renewID()
			self.values = np.array(newValues)
			return True
		else:
			return False

	def isDominatedBy(self, other):
		if self.checkIfScored() and other.checkIfScored():
			return self.score < other.score
