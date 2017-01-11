def afpr(number, precision=10):
	'''Alignable floating point representation'''
	if number < 0:
		return ('%0.' + str(precision) + 'f') % number
	else:
		return ('%0.' + str(precision+1) + 'f') % number

def translateParametersDictionary(dict, optionalParametersTranslator, requiredParametersTranslator=None):
	translatorFuncs = {'toFloat'  : float,
	                   'toInt'    : int,
	                   'toBool'   : lambda x: x if type(x) is bool else x == 'yes',
	                   'toString' : str} # all translator functions must be projections: f(f(x)) = f(x) for any x
	def translateParamDictInModes(dictionary, translator, allParamsRequired):
		for convStr, paramNames in translator.iteritems():
			for paramName in paramNames:
				if allParamsRequired or dictionary.has_key(paramName):
					dictionary[paramName] = translatorFuncs[convStr](dictionary[paramName])
		return dictionary
	if requiredParametersTranslator:
		try:
			dict = translateParamDictInModes(dict, requiredParametersTranslator, True)
		except KeyError:
			raise ValueError('Required parameter is missing from the parameter dictionary ' + str(dict) + '. Requirements: ' + str(requiredParametersTranslator))
	return translateParamDictInModes(dict, optionalParametersTranslator, False)

def emptyParametersTranslator():
	return { 'toFloat': set(), 'toInt': set(), 'toBool': set(), 'toString': set() }
