from copy import deepcopy
import numpy as np

class BaseEvolver(object):
	'''Base class for evolutionary algorithms. Provides 
     methods for creating server output.'''
	def __init__(self, communicator, indivParams, evolParams):
		self.communicator = communicator
		self.params = evolParams
		self.population = []
		self.logHeaderWritten = False
		self.generation = 0
		if self.params.has_key('randomSeed'):
			np.random.seed(self.params['randomSeed'])

	def updatePopulation(self):
		self.generation += 1

	def pickleSelf(self):
		self.randomGeneratorState = np.random.get_state()
		if not hasattr(self, '__pickleSelfCalled__'):
			self.__pickleSelfCalled__ = True
			import os
			import glob
			import time
			if not os.path.exists('./backups'):
				os.makedirs('./backups')
			oldpickles = glob.glob('./backups/*.p')
			if oldpickles != []:
				print 'Old backups found! Press Ctrl+C in 10 seconds to abort their erasing...\n'
			time.sleep(10)
			for file in oldpickles:
				os.remove(file)
		if not hasattr(self, '__pickleLoaded__') or not self.__pickleLoaded__:
			global pickle
			import pickle
			self.__pickleLoaded__ = True
		file = open('./backups/' + str(self.generation).zfill(10) + '.p', 'w')
		self.__pickleLoaded__ = False
		pickle.dump(self, file)
		self.__pickleLoaded = True
		file.close()

	def recover(self):
		map(lambda x: x.recoverID(), self.population)   # make sure that we start from the next free ID
		np.random.set_state(self.randomGeneratorState)

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
				logFile.write(str(self.generation) + ' ' + str(bestIndiv.score) + ' ' + str(bestIndiv) + '\n')
		else:
			with open('bestIndividual.log', 'w') as logFile:
				logFile.write('# Columns: generation score ID indivDesc0 indivDesc1 ...\n')
			self.logHeaderWritten = True
			self.logBestIndividual()
