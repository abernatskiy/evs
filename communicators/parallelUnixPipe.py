import os
import math
from baseCommunicator import BaseCommunicator

def chunks(l, n):
	"""Yield successive n-sized chunks from l."""
	for i in range(0, len(l), n):
		yield l[i:i + n]

class Communicator(BaseCommunicator):
	'''Communicator which uses unix pipes for
     data exchange between a server and multiple clients
  '''
	def __init__(self, fninput='/tmp/evaluations.pipe', fnoutput='/tmp/individuals.pipe'):
		super(BaseCommunicator, self).__init__()
		self.fninput = [ fninput + str(i) for i in range(4) ]
		self.fnoutput = [ fnoutput + str(i) for i in range(4) ]
		try:
			map(os.mkfifo, self.fninput)
			map(os.mkfifo, self.fnoutput)
		except OSError, e:
			pass

	def write(self, indivList):
		chunkSize = int(math.ceil(float(len(indivList))/4))
		indivChunks = chunks(indivList, chunkSize)
		foutput = []
		for fn, ch in zip(self.fnoutput, indivChunks):
			foutput.append(open(fn, 'w'))
			for indiv in ch:
				foutput[-1].write(str(indiv) + '\n')
		print 'wrote to all pipes'
		for fo in foutput:
			fo.close()

	def read(self):
		finput = []
		evaluations = []
		for fn in self.fninput:
			finput.append(open(fn, 'r'))
			for line in finput[-1]:
				evaluations.append(line)
		for fi in finput:
			fi.close()
		return evaluations
