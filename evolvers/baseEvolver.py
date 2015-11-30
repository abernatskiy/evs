from copy import deepcopy
import numpy as np
import os

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
		if self._paramIsEnabled('trackAncestry'):
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
		if self._paramIsEnabled('trackAncestry'):
			import __builtin__
			__builtin__.globalGenerationCounter += 1
		if self.params.has_key('genStopAfter') and self.generation > self.params['genStopAfter']:
			print 'Done.\n'
			import sys
			sys.exit(0)

	def pickleSelf(self, postfix=''):
		if not self._shouldIRunAPeriodicFunctionNow('backup'):
			return
		self.randomGeneratorState = np.random.get_state()
		if not hasattr(self, '__pickleSelfCalled__'):
			self.__pickleSelfCalled__ = True
			import os
			import time
			import shutil
			if os.path.isdir('./backups'):
				print 'Old phenotypes found. Moving to a backups.save folder'
				if os.path.exists('./backups.save'):
					print 'WARNING! Phenotype save folder found at backups.save. Overwriting in 10 seconds, press Ctrl+C to abort...'
					time.sleep(10)
					shutil.rmtree('./backups.save')
					print 'Folder backups.save erased'
				shutil.move('./backups', './backups.save')
				os.mkdir('./backups')
			elif os.path.exists('./backups'):
				raise IOError('Backups path exists, but is not a directory')
			else:
				os.mkdir('./backups')
		if not hasattr(self, '__pickleLoaded__') or not self.__pickleLoaded__:
			global pickle
			import pickle
			self.__pickleLoaded__ = True
		file = open('./backups/' + str(self.generation).zfill(10) + postfix + '.p', 'w')
		self.__pickleLoaded__ = False
		pickle.dump(self, file)
		self.__pickleLoaded = True
		file.close()

	def recover(self):
		map(lambda x: x.recoverID(), self.population)   # make sure that we start from the next free ID
		np.random.set_state(self.randomGeneratorState)
		if self._paramIsEnabled('trackAncestry'): # if we're dealing with ancestry tracking (disabled by default)...
			import __builtin__
			if not hasattr(__builtin__, 'globalGenerationCounter'):
				# ...we should restore the content of our 'global' generation counter
				__builtin__.globalGenerationCounter = self.generation
			else:
				# it may happen that we're trying to continue evolution using a new version of python in which our little hack no longer works
				raise AttributeError('__builtin__ already has a globalGenerationCounter attribute, cannot initialize ancestry tracking')
		if self._paramIsEnabled('logBestIndividual'):
			self._truncateLogFile(self._bestIndividualLogFileName)

	def _truncateLogFile(self, filename):
		oldFilename = filename + '.old'
		os.rename(filename, oldFilename)
		with open(oldFilename, 'r') as oldFile:
			with open(filename, 'w') as file:
				for s in oldFile:
					if s.startswith(str(self.generation)):
						break
					file.write(s)
		os.remove(oldFilename)

	def printGeneration(self):
		if not self._shouldIRunAPeriodicFunctionNow('printGeneration'):
			return
		print 'Generation ' + str(self.generation)

	def printBestIndividual(self):
		if not self._shouldIRunAPeriodicFunctionNow('printBestIndividual'):
			return
		bestIndiv = self.population[-1]
		print 'Best individual: ' + str(bestIndiv) + ' score: ' + str(bestIndiv.score)

	def printPopulation(self):
		if not self._shouldIRunAPeriodicFunctionNow('printPopulation'):
			return
		print '-----------'
		for indiv in self.population:
			print str(indiv) + ' score: ' + str(indiv.score)
		print ''

	def printParetoFront(self, paretoFront, objname, objfunc):
		if not self._shouldIRunAPeriodicFunctionNow('printParetoFront'):
			return
		print 'Pareto front:'
		for indiv in paretoFront:
			print str(indiv) + ' score: ' + str(indiv.score) + ' ' + objname + ': ' + str(objfunc(indiv))
		print ''

	def paretoWarning(self, paretoFront):
		# Warn user when the Pareto front gets too large
		r = float(len(paretoFront))/float(self.params['populationSize'])
		if r == 0.0:
			raise RuntimeError('No nondominated individuals!')
		if r > 0.75:
			print 'WARNING! Proportion of nondominated individuals too high (' + str(r) + ')'

	def logBestIndividual(self, filename=None):
		if not self._shouldIRunAPeriodicFunctionNow('logBestIndividual'):
			return
		if filename is None:
			filename = 'bestIndividual' + str(self.params['randomSeed']) + '.log'
		self._bestIndividualLogFileName = filename
		bestIndiv = self.population[-1]
		if self.logHeaderWritten:
			with open(filename, 'a') as logFile:
				logFile.write(str(self.generation) + ' ' + str(bestIndiv.score) + ' ' + str(bestIndiv) + '\n')
		else:
			with open(filename, 'w') as logFile:
				self._writeParamsToLog(logFile)
				logFile.write('# Columns: generation score ID indivDesc0 indivDesc1 ...\n')
			self.logHeaderWritten = True
			self.logBestIndividual(filename=filename)

	def logPopulation(self, prefix='population'):
		if not self._shouldIRunAPeriodicFunctionNow('logPopulation'):
			return
		filename = prefix + '_gen' + str(self.generation) + '.log'
		with open(filename, 'w') as logFile:
			self._writeParamsToLog(logFile)
			logFile.write('# Columns: score ID indivDesc0 indivDesc1 ...\n')
			for indiv in self.population:
				logFile.write(str(indiv.score) + ' ' + str(indiv) + '\n')

	def _writeParamsToLog(self, file):
		file.write('# Evolver parameters: ' + self._deterministicDict2Str(self.params) + '\n')
		file.write('# Individual parameters: ' + self._deterministicDict2Str(self.indivParams) + '\n')

	def _deterministicDict2Str(self, dict):
		pairStrs = [ '\'' + key + '\': ' + str(dict[key]) for key in sorted(dict.keys()) ]
		return '{' + ','.join(pairStrs) + '}'

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

	def generateLogsAndStdout(self):
		# Generation number is printed after every update
		self.printGeneration()

		# Config-dependent output functions: won't do anything unless the config contains explicit permission
		self.logBestIndividual(filename = 'bestIndividual' + str(self.params['randomSeed']) + '.log')
		self.logPopulation(prefix = 'population' + str(self.params['randomSeed']))
		self.printBestIndividual()
		self.printPopulation()

	def _paramIsEnabled(self, paramName):
		return hasattr(self, 'params') and self.params.has_key(paramName) and self.params[paramName] == 'yes'

	def _shouldIRunAPeriodicFunctionNow(self, paramName):
		if not self._paramIsEnabled(paramName):
			return False
		period = 1 if not self.params.has_key(paramName + 'Period') else self.params[paramName + 'Period']
		if not self.generation % period == 0:
			return False
		return True
