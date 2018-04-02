import os
import math
import glob
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
		self.fninput = sorted(glob.glob(fninput + '*'))
		self.fnoutput = sorted(glob.glob(fnoutput + '*'))
		if len(self.fninput) != len(self.fnoutput):
			raise ValueError('Mismatch in the number of input and output pipes')
		self.numStreams = len(self.fninput)
		try:
			map(os.mkfifo, self.fninput)
			map(os.mkfifo, self.fnoutput)
		except OSError, e:
			pass

	def write(self, indivList):
		chunkSize = int(math.ceil(float(len(indivList))/self.numStreams))
		indivChunks = chunks(indivList, chunkSize)
		self.numChunks = 0
		foutput = []
		for fn, ch in zip(self.fnoutput, indivChunks):
#			print 'Writing chunk ' + str([ i.id for i in ch ]) + ' to ' + fn
			foutput.append(open(fn, 'w'))
			for indiv in ch:
				foutput[-1].write(str(indiv) + '\n')
			self.numChunks += 1 # this is very important
		for fo in foutput:
			fo.close()

	def read(self):
		finput = []
		evaluations = []
		for i in range(self.numChunks):
			fn = self.fninput[i]
#			print 'Opening ' + fn
			evalshere = []
			finput.append(open(fn, 'r'))
			for line in finput[-1]:
				evalshere.append(line)
			evaluations += evalshere
#			print 'Read ' + str(evalshere) + ' from ' + fn
		for fi in finput:
			fi.close()
		return evaluations
