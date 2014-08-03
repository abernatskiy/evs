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
	def __init__(self, params):
		self.renewID()
		self.params = params

	def __repr__(self):
		return self.__str__()

	def __lt__(self, other):
		return self.isDominatedBy(other)

	def __eq__(self, other):
		return self.id == other.id

	def renewID(self):
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
