from evolvableFitnessFunction import Evolver as EFFEvolver

class Evolver(EFFEvolver):
	def _findFitnessVariantsElite(self, curIndivs, fitnessVariant, bestError):
		numIndivs = len(curIndivs)
		fitnessVariantElite = self.findParetoFrontManyObjectives([self.getErrorFunc(), self.getConnectionCostFunc()], population=curIndivs)
		print('{}: elite size is {}, subpopulation size {}, densities: {}'.format(fitnessVariant, len(fitnessVariantElite), numIndivs, sorted([ (self.getConnectionCostFunc()(indiv), self.getErrorFunc()(indiv)) for indiv in fitnessVariantElite ])))
		ultimateFitnessElite = [ indiv for indiv in curIndivs if indiv.isAChampion() ]
		# We want to keep the best individual according to the current fitness and the veteran that got the fitness variant through the ultimate update.
		# Problem is, they might be the same individual! Or the veteran might not exist yet
		newIndivs = fitnessVariantElite
		if len(ultimateFitnessElite)>0 and all([ ultimateFitnessElite[0].id!=fv.id for fv in fitnessVariantElite ]):
			newIndivs.append(ultimateFitnessElite[0])
		return newIndivs
