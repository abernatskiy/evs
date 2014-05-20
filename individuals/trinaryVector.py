import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Class for evolutionary individuals described by a vector of 
	numbers taken from {-1,0,1} of constant length, with 
	a single-valued score represented by a FPN. Constructor takes a 
	dictionary with the following parameter fields
	  length     - length of the vector
	  mutationProbability - probability that mutation occurs upon mutate() call
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
		if np.random.random() <= self.params['mutationProbability']:                             # in the unlikely event of mutation
			self.renewID()                                                                         # the mutated individual loses parent's ID 
			position = np.random.randint(len(self.values))                                         # at the random position of its genotype
			self.values[position] = np.random.random_integers(-1, 1)                               # value of the trinary number is changed randomly

	def isDominatedBy(self, other):
		if self.checkIfScored() and other.checkIfScored():
			return self.score < other.score
