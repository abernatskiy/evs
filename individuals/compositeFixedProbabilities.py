import re
import importlib

from baseIndividual import BaseIndividual

                                                                                
class Individual(BaseIndividual):
	'''Class for evolutionary individuals glued together from individuals of other
	   classes. Mutation of such composite individual mutates only one of its
	   parts; each class in the composite is chosen randomly with some fixed
	   probability assigned to it.

	   Constructor takes a dictionary with the following parameter fields:

	     compositeClass0, probabilityOfMutatingClass0
	     compositeClass1, probabilityOfMutatingClass1
	     ...
	     compositeClassN, probabilityOfMutatingClassN
	     - names and probabilities of part classes

	     <partClassParameterName>Class?
	     - params passed through the constructor of the composite to the
	     constructors of part classes, after stripping the trailing "Class?"

	   For string representations, the class assumes that each of the part has a
	   representation of form "ID GEN". The representations are then combined as
	   follows:
	     "ID0 GEN0" "ID1 GEN1" ... "IDN GENN" ->
	     -> "CommonID GEN0 GEN1 ... GENN"
	'''
	def __init__(self, params):
		self._extractPartClasses(params) # must be called before the parameters translator dictionaries are generated
		self._makeSampleParts()
#		super(Individual, self).__init__(params) # this calls the translator generators and translates the params

	def _extractPartClasses(self, params):
		# Extracting names and numbers
		partClassesNames = {}
		classPattern = re.compile('^compositeClass[0-9]+$')
		numPattern = re.compile('[0-9]+$')
		for pn, pv in params.iteritems():
			if classPattern.match(pn):
				classNum = int(numPattern.search(pn).group())
				partClassesNames[classNum] = pv
		# Checking if numbers are sequential
		if partClassesNames.keys() != list(range(len(partClassesNames))):
			raise ValueError('Classes must be numbered sequentially starting from zero in the config, and tey are not. Exiting.')
		# Loading the sources for all classes
		self.partClasses = []
		for i in range(len(partClassesNames)):
			self.partClasses.append(importlib.import_module('individuals.' + partClassesNames[i]).Individual) # CAREFUL, might not be in path

	def _makeSampleParts(self):
		self._sampleParts = []
		for pcl in self.partClasses:
			self._sampleParts.append(pcl.initEmpty())

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		return t

	def __str__(self):
		# Debugging version
		return 'Individuals within the compound:\n'

	def mutate(self):
		pass
