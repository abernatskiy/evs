import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Class for evolutionary individuals described by a vector of 
	floating point numbers (FPNs) in [0,1] of constant length, with 
	a single-valued score represented by a FPN. Constructor takes a 
	dictionary with the following parameter fields:
    length     - number of floating point numbers (FPNs)
    precision  - number of significant digits to keep for each FPN
    mutationProbability - probability that mutation occurs upon mutate() call
    mutationAmplitude   - coefficient in front of the Gaussian distribution 
                          giving the amplitude of the mutational change'''
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
		if np.random.random() <= self.params['mutationProbability']:                             # in the unlikely event of mutation
			self.renewID()                                                                         # the mutated individual loses parent's ID 
			position = np.random.randint(len(self.values))                                         # at the random position of its genotype
			self.values[position] += np.random.randn()*self.params['mutationAmplitude']            # normally distributed increment is introduced
			if self.values[position] < 0.0:                                                        # the result is cropped to be greater than 0 ...
				self.values[position] = 0.0
			elif self.values[position] > 1.0:                                                      # ... and less than 1 ...
				self.values[position] = 1.0
			self.values[position] = np.around(self.values[position], self.params['precision'])     # ... and contain no more decimal digits then allowed.

	def isDominatedBy(self, other):
		if self.checkIfScored() and other.checkIfScored():
			return self.score < other.score
