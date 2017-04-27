import __builtin__

from cluneSimplified import Evolver as CluneSimplifiedEvolver

class Evolver(CluneSimplifiedEvolver):
	'''Three-dimensional dragon, first of its kind'''
#	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
#		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)

	def getMorphologicalAge(self):
		return lambda x: __builtin__.globalGenerationCounter - x.timeOfLastMorphologicalMutation

	def getCluneParetoFront(self):
		funcs = [ self.getErrorFunc(), self.getConnectionCostFunc(), self.getMorphologicalAge() ]
		return self.findParetoFrontManyObjectives(funcs)
