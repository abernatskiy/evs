from copy import deepcopy

from ageFunction import Evolver as AFEvolver
from ageFunction import chooseTupleRandomly

class Evolver(AFEvolver):
	def getConnectionCostFunc(self):
		return lambda x: x.connectionCost()

	def _addLineageEliteToNewPopulation(self, lineage):
		objectives = [self.getCurrentErrorFunc(), self.getConnectionCostFunc()]
		pccFront = self.findParetoFrontManyObjectives(objectives, breakTiesByIDs=True, population=lineage)
		print('Current performance-connection cost Pareto front found and added to the elite')
		print('Front size {}, structure {}'.format(len(pccFront), [ (objective[0](x), objective[1](x)) for x in pccFront ]))
		for indiv in pccFront:
			self._addEliteIndiv(indiv)

	def _addLineageOffspringToNewPopulation(self, lineage):
		objectives = [self.getCurrentErrorFunc(), self.getConnectionCostFunc()]
		pccFront = self.findParetoFrontManyObjectives(objectives, breakTiesByIDs=True, population=lineage)
		print('Current performance-connection cost Pareto front of size {} is found. Selecting a parent for reproduction...')
		parent = chooseTupleRandomly(pccFront))
		newIndiv = deepcopy(parent)
		if newIndiv.mutate():
			self._newPopulation.append(newIndiv)
			print('Added new offspring {} of {} of lineage {}'.format(newIndiv.id, parent.id, self.getAgeFunc()(lineage[0])) )
