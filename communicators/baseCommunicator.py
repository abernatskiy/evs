class BaseCommunicator:
	def evaluate(self, indivList):
		self.write(indivList)
		evaluations = self.read()
		if len(indivList) != len(evaluations):
			raise IOError('No of evaluations is different from no of individuals')
		for i in xrange(len(indivList)):
			indivList[i].setEvaluation(evaluations[i])
		return indivList
