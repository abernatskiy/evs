class BaseCommunicator(object):
	def __init__(self):
		self.cache = {}

	def evaluate(self, indivList):
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

		self.write(indivList)
		evaluations = self.read()
		while '' in evaluations:
			evaluations.remove('')
		if len(indivList) != len(evaluations):
			print str(indivList)  + ' '  + str(evaluations)
			print str(len(indivList))  + ' != '  + str(len(evaluations))
			raise IOError('No of evaluations is different from no of individuals')
		for i in xrange(len(indivList)):
			indivList[i].setEvaluation(evaluations[i])
		return indivList
