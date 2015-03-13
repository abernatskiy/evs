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
         isDominatedBy() is defined for the derived class;
       - ID check and renewal;
       - check for score existence.
   '''
	def __init__(self, params, generation=0):
		self.renewID()
		if params.has_key('trackAncestry') and params['trackAncestry'] == 'yes':
			self.ancestry = []
			self.ancestry.append((-1, generation))
		self.params = params

	def __repr__(self):
		return self.__str__()

	def __lt__(self, other):
		return self.isDominatedBy(other)

	def __eq__(self, other):
		return self.id == other.id

	def renewID(self, generation=0):
		if hasattr(self, 'params') and self.params.has_key('trackAncestry') and self.params['trackAncestry'] == 'yes':
			self.ancestry.append((self.id, generation))
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
		if self.checkID(int(valueStrings[0])):
			self.score = float(valueStrings[1])

	def noisifyScore(self, amplitude):
		self.score += (np.random.random()*2-1)*amplitude
