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
		pass
	def _processParams(self, params):
		

	def __str__(self):
		# super() has to be redefined
		pass
	def mutate(self):
		pass
