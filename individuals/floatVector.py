import numpy as np

currentID = 0

class Individual:
	'''Class for evolutionary individuals described by a vector of 
	floating point numbers (FPNs) in [0,1] of constant length, with 
	a single-valued score represented by a FPN. Constructor takes a 
	dictionary with the following parameter fields:
    length     - number of floating point numbers (FPNs)
    noOfDigits - number of significant digits to keep for each FPN
    mutationProbability - probability that mutation occurs upon mutate() call
    mutationAmplitude   - coefficient in front of the Gaussian distribution 
                          giving the amplitude of the mutational change'''
	def __init__(self, params):
		self.renewID()
		self.params = params
		self.values = np.random.random_sample(self.params['length'])
		self.values = np.around(self.values, self.params['noOfDigits'])

	def __str__(self):
		representation = str(self.id)
		for value in self.values:
			representation += ' '
			representation += str(value)
		return representation

	def __repr__(self):
		return self.__str__()

	def __lt__(self, other):
		return self.isDominatedBy(other)

	def renewID(self):
		global currentID
		self.id = currentID
		currentID = currentID + 1

	def setEvaluation(self, scoreStr):
		valueStrings = scoreStr.split()
		if self.id != int(valueStrings[0]):
			raise ValueError('Wrong ID - setEvaluation() got an argument which is not an evaluation of this controller')
		else:
			self.score = float(valueStrings[1])

	def mutate(self):
		if np.random.random() <= self.params['mutationProbability']:
			self.renewID()
			position = np.random.randint(len(self.values))
			self.values[position] += np.random.randn()*self.params['mutationAmplitude']
			if self.values[position] < 0.0:
				self.values[position] = 0.0
			elif self.values[position] > 1.0:
				self.values[position] = 1.0
			self.values[position] = np.around(self.values[position], self.params['noOfDigits'])

	def isDominatedBy(self, other):
		if not hasattr(self, 'score') or not hasattr(other, 'score'):
			raise ValueError('One of the compared individuals is unscored')
		return self.score < other.score
