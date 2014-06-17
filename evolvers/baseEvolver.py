from copy import deepcopy

class BaseEvolver(object):
	'''Base class for evolutionary algorithms. Provides 
     methods for creating server output.'''
	def __init__(self, communicator, indivParams, evolParams):
		self.communicator = communicator
		self.params = evolParams
		self.population = []
		self.logHeaderWritten = False

	def printBestIndividual(self):
		bestIndiv = self.population[-1]
		print 'Best individual: ' + str(bestIndiv) + ' score: ' + str(bestIndiv.score)

	def printPopulation(self):
		print '----------'
		for indiv in self.population:
			print str(indiv) + ' score: ' + str(indiv.score)
		print ''

	def logBestIndividual(self):
		bestIndiv = self.population[-1]
		if self.logHeaderWritten:
			with open('bestIndividual.log', 'a') as logFile:
				logFile.write(str(bestIndiv) + ' ' + str(bestIndiv.score))
		else:
			with open('bestIndividual.log', 'w') as logFile:
				logFile.write('# Columns: score ID indivDesc0 indivDesc1 ...\n')
				logFile.write(str(bestIndiv.score) + ' ' + str(bestIndiv) + '\n')
