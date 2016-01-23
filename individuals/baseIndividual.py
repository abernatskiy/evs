import numpy as np
currentID = 0

class BaseIndividual(object):
	'''Base class for evolutionary individuals. Provides the following 
     functionality:
       - constructor which automatically assigns unique IDs (note: if 
         multiple Individual classes derived from this class are used 
         in some program, the IDs will all be drawn from the same pool);
       - representations of the individuals, given that __str__() is 
         defined for the derived class;
       - strict comparison of the individuals, given that 
         __lt__() is defined for the derived class;
       - ID check and renewal;
       - check for score existence.
   '''
	def __init__(self, params):
		self.renewID()
		self.params = params
		if self.ancestryTrackingEnabled():
			# ancestry is stored in form of a chain of records, e.g.
			# [(-1, 3),
			#  (564, 10),
			#  (600, 11)]
			# The first tuple is used to describe a lineage origination (LO) event, the rest describe mutations
			# The first field holds parent's ID. For LO events, a special value of -1 is used.
			# The second field hold the generation number at which the event took place.
			# The number of the first generation in which the child appears is used.
			# Thus, a tuple (564, 10) means that at generation 9 there was an individual named 564. It produced an
			# offspring which got to carry its genes on to generation 10. This offspring is either an ancestor of
			# the current individual (if there are subsequent records in the ancestry), or the individual itself.
			#
			# The only way to retrieve the history is to enable backups and retrieve these lists from the pickles. Deal with it.
			self.ancestry = []
			import __builtin__
			self.ancestry.append((-1, __builtin__.globalGenerationCounter)) # teleported here from evolvers.baseEvolver

	def __str__(self):
		representation = str(self.id)
		for value in self.values:
			representation += ' '
			representation += str(value)
		return representation

	def __repr__(self):
		return self.__str__()

	def __lt__(self, other):
		if self.checkIfScored() and other.checkIfScored():
			return self.score < other.score
		else:
			raise ValueError('Unscored individuals cannot be compared')

	def __eq__(self, other):
		return self.id == other.id

	def renewID(self):
		if self.ancestryTrackingEnabled():
			import __builtin__
			self.ancestry.append((self.id, __builtin__.globalGenerationCounter)) # teleported here from evolvers.baseEvolver
		global currentID
		self.id = currentID
		currentID = currentID + 1

	def recoverID(self):
		global currentID
		currentID = self.id+1 if self.id+1 > currentID else currentID

	def checkID(self, ID):
		if self.id != ID:
			raise ValueError('ID check failed')
		else:
			return True

	def checkIfScored(self):
		if not hasattr(self, 'score'):
			raise ValueError('Score presence checked for an unscored individual')
		else:
			return True

	def setEvaluation(self, scoreStr):
		valueStrings = scoreStr.split()
		if len(valueStrings) != 2:
			raise ValueError('Incorrectly formatted evaluation line')
		if self.checkID(int(valueStrings[0])):
			self.score = float(valueStrings[1])

	def noisifyScore(self, amplitude):
		self.score += (np.random.random()*2-1)*amplitude

	def ancestryTrackingEnabled(self):
		return hasattr(self, 'params') and self.params.has_key('trackAncestry') and self.params['trackAncestry'] == 'yes'

	def setParamDefault(self, paramName, paramVal):
		if not self.params.has_key(paramName):
			self.params[paramName] = paramVal
