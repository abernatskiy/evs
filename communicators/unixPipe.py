import os
from baseCommunicator import BaseCommunicator

class Communicator(BaseCommunicator):
	def __init__(self, fninput='/tmp/evaluations.pipe', fnoutput='/tmp/individuals.pipe'):
		self.fninput = fninput
		self.fnoutput = fnoutput
		try:
			os.mkfifo(fninput)
			os.mkfifo(fnoutput)
		except OSError, e:
			pass

	def write(self, indivList):
		foutput = open(self.fnoutput, 'w')
		for indiv in indivList:
			foutput.write(str(indiv) + '\n')
		foutput.close()

	def read(self):
		evaluations = []
		finput = open(self.fninput, 'r')
		for line in finput:
			evaluations.append(line)
		finput.close()
		return evaluations
