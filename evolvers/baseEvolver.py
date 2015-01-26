from copy import deepcopy
import numpy as np

def firstDominatedBySecond(indiv0, indiv1, func0, func1):
	'''Assumes that both functions are minimized, as in the classical Pareto front picture'''
	# truth table:
	#                  f0(i0)<f0(i1)    f0(i0)=f0(i1)    f0(i0)>f0(i1)
	# f1(i0)<f1(i1)    F                F                F
	# f1(i0)=f1(i1)    F                F                T
	# f1(i0)>f1(i1)    F                T                T
	if indiv0.id == indiv1.id:
		raise RuntimeError('Pareto optimization error: Two individuals with the same ID compared')
	if func0(indiv0) == func0(indiv1):
		if func1(indiv0) == func1(indiv1):
			return False
		else:
			return func1(indiv0) > func1(indiv1)
	else:
		return func0(indiv0) > func0(indiv1) and func1(indiv0) >= func1(indiv1)

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
		if self.params.has_key('genStopAfter'):
			if self.generation > self.params['genStopAfter']:
				print 'Done.\n'
				import sys
				sys.exit(0)

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

	def printGeneration(self):
		print self.generation

	def printBestIndividual(self):
		bestIndiv = self.population[-1]
		print 'Best individual: ' + str(bestIndiv) + ' score: ' + str(bestIndiv.score)

	def printPopulation(self):
		print '----------'
		for indiv in self.population:
			print str(indiv) + ' score: ' + str(indiv.score)
		print ''

	def logBestIndividual(self, filename='bestIndividual.log'):
		bestIndiv = self.population[-1]
		if self.logHeaderWritten:
			with open(filename, 'a') as logFile:
				logFile.write(str(self.generation) + ' ' + str(bestIndiv.score) + ' ' + str(bestIndiv) + '\n')
		else:
			with open(filename, 'w') as logFile:
				logFile.write('# Columns: generation score ID indivDesc0 indivDesc1 ...\n')
			self.logHeaderWritten = True
			self.logBestIndividual(filename=filename)

	def logPopulation(self, prefix='population'):
		filename = prefix + '_gen' + str(self.generation) + '.log'
		with open(filename, 'a') as logFile:
			logFile.write('# Columns: score ID indivDesc0 indivDesc1 ...\n')
			for indiv in self.population:
				logFile.write(str(indiv.score) + ' ' + str(indiv) + '\n')

	def findParetoFront(self, func0, func1):
		for indiv in self.population:
			indiv.__dominated__ = False
		for ii in self.population:
			for ij in self.population:
				if not ii is ij and firstDominatedBySecond(ii, ij, func0, func1):
					ii.__dominated__ = True
		paretoFront = filter(lambda x: not x.__dominated__, self.population)
		return paretoFront
