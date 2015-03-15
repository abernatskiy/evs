from copy import deepcopy
import numpy as np

def firstDominatedBySecond(indiv0, indiv1, func0, func1):
	'''Assumes that both functions are minimized, as in the classical Pareto front picture'''
	# truth table:
	#                  f0(i0)<f0(i1)    f0(i0)=f0(i1)    f0(i0)>f0(i1)
	# f1(i0)<f1(i1)    F                F                F
	# f1(i0)=f1(i1)    F                ID0<ID1          T
	# f1(i0)>f1(i1)    F                T                T
	if indiv0.id == indiv1.id:
		raise RuntimeError('Pareto optimization error: Two individuals with the same ID compared')
	if func0(indiv0) == func0(indiv1):
		if func1(indiv0) == func1(indiv1):
#			return False # leads to an exponential explosion of the Pareto front, according to Josh
			return indiv0.id < indiv1.id # lower ID indicates that indiv0 was generated before indiv1 and is older
		else:
			return func1(indiv0) > func1(indiv1)
	else:
		return func0(indiv0) > func0(indiv1) and func1(indiv0) >= func1(indiv1)

def firstStochasticallyDominatedBySecond(indiv0, indiv1, func0, func1, secondObjProb):
	if np.random.random() > secondObjProb:
		return func0(indiv0) > func0(indiv1)
	else:
		return firstDominatedBySecond(indiv0, indiv1, func0, func1)

class BaseEvolver(object):
	'''Base class for evolutionary algorithms. Provides 
     methods for creating server output.'''
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		self.communicator = communicator
		self.params = evolParams
		self.indivParams = indivParams
		self.logHeaderWritten = False
		self.generation = 0
		# little dirty hack which exploit the fact that there's always just one Evolver to communicate generation number to Individuals
		if self.ancestryTrackingEnabled():
			indivParams['trackAncestry'] = 'yes'
			import __builtin__
			if not hasattr(__builtin__, 'globalGenerationCounter'):
				__builtin__.globalGenerationCounter = 0
			else:
				raise AttributeError('__builtin__ already has a globalGenerationCounter attribute, cannot initialize ancestry tracking')
		if self.params.has_key('randomSeed'):
			np.random.seed(self.params['randomSeed'])
		self.population = []
		if not initialPopulationFileName is None:
			self.appendPopulationFromFile(initialPopulationFileName)

	def updatePopulation(self):
		self.generation += 1
		if self.ancestryTrackingEnabled():
			import __builtin__
			__builtin__.globalGenerationCounter += 1
		if self.params.has_key('genStopAfter') and self.generation > self.params['genStopAfter']:
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
				print 'Old backups found! Press Ctrl+C in 10 seconds to abort erasing them...\n'
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
		if self.ancestryTrackingEnabled(): # if we're dealing with ancestry tracking (disabled by default)...
			import __builtin__
			if not hasattr(__builtin__, 'globalGenerationCounter'):
				# ...we should restore the content of out 'global' variable
				__builtin__.globalGenerationCounter = self.generation
			else:
				# it may happen that we're trying to continue evolution using a new version of python in which our little hack no longer works
				raise AttributeError('__builtin__ already has a globalGenerationCounter attribute, cannot initialize ancestry tracking')

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
				logFile.write('# Evolver parameters: ' + str(self.params) + '\n')
				logFile.write('# Individual parameters: ' + str(self.indivParams) + '\n')
				logFile.write('# Columns: generation score ID indivDesc0 indivDesc1 ...\n')
			self.logHeaderWritten = True
			self.logBestIndividual(filename=filename)

	def logPopulation(self, prefix='population'):
		filename = prefix + '_gen' + str(self.generation) + '.log'
		with open(filename, 'a') as logFile:
			logFile.write('# Evolver parameters: ' + str(self.params) + '\n')
			logFile.write('# Individual parameters: ' + str(self.indivParams) + '\n')
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

	def findStochasticalParetoFront(self, func0, func1):
		for indiv in self.population:
			indiv.__dominated__ = False
		for ii in self.population:
			for ij in self.population:
				if not ii is ij and firstStochasticallyDominatedBySecond(ii, ij, func0, func1, self.params['secondObjectiveProbability']):
					ii.__dominated__ = True
		paretoFront = filter(lambda x: not x.__dominated__, self.population)
		return paretoFront

	def noisifyAllScores(self):
		for indiv in self.population:
			indiv.noisifyScore(self.params['noiseAmplitude'])

	def ancestryTrackingEnabled(self):
		return hasattr(self, 'params') and self.params.has_key('trackAncestry') and self.params['trackAncestry'] == 'yes'

	def populationIsValid(self):
		return len(self.population) <= self.params['populationSize'] and all([ type(indiv) == self.params['indivClass'] for indiv in self.population ])

	def appendPopulationFromFile(self, filename):
		file = open(filename, 'r')
		for line in file:
			indiv = self.params['indivClass'](self.indivParams)
			indiv.fromStr(line)
			self.population.append(indiv)
		if not self.populationIsValid():
			raise ValueError('Inital population is too large')
		map(lambda x: x.recoverID(), self.population)   # make sure that we start from the next free ID
