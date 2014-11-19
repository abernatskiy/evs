class BaseCommunicator(object):
	'''Base class for communicators. Provides 
     a method for generic population evaluation.'''
	def __init__(self):
		self.cache = {}

	def fitnessTransform(self, fitness, individual):
		return fitness

	def evaluate(self, indivList):
		if indivList == []:
			return indivList

		# caching version (draft)
#		evalNeeded = []
#		for indiv in indivList:
#			if not hasattr(indiv, 'score'):
#				evalNeeded.append(indiv)
#		self.write(evalNeeded)
#		evaluations = self.read()
#		if len(evalNeeded) != len(evaluations):
#			raise IOError('No of evaluations is different from no of individuals')
#		for i in xrange(len(evalNeeded)):
#			evalNeeded[i].setEvaluation(evaluations[i])
#		return evalNeeded

		# non-caching version
		self.write(indivList)
		evaluations = self.read()
		while '' in evaluations:
			evaluations.remove('')
		if len(indivList) != len(evaluations):
			print str(indivList)  + ' '  + str(evaluations)
			print str(len(indivList))  + ' != '  + str(len(evaluations))
			raise IOError('No of evaluations is different from no of individuals')
		for i in xrange(len(indivList)):
			indivList[i].setEvaluation(self.fitnessTransform(evaluations[i], indivList[i]))
		return indivList
