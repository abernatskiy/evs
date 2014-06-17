import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Class for evolutionary individuals described by a vector of 
     numbers taken from {-1,0,1} of constant length, with 
     a single-valued score represented by a FPN. Constructor takes a 
     dictionary with the following parameter fields
       length     - length of the vector
       mutationProbability - probability that mutation occurs upon 
                             mutate() call (for each value)
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self.values = np.random.random_integers(-1, 1, size=self.params['length'])

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
				newValues.append(np.random.random_integers(-1, 1))
				if val != newValues[-1]:
					mutated = True
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
