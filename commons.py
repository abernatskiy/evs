def afpr(number, precision=10):
	'''Alignable floating point representation'''
	if number < 0:
		return ('%0.' + str(precision) + 'f') % number
	else:
		return ('%0.' + str(precision+1) + 'f') % number

def translateParamDict(dict, optionalParamsTranslator, requiredParamsTranslator=None):
	translatorFuncs = {'toFloat'  : float,
	                   'toInt'    : int,
	                   'toBool'   : lambda x: x is 'yes',
	                   'toString' : str}
	def translateParamDictInModes(dictionary, translator, allParamsRequired):
		for convStr, paramNames in translator.iteritems():
			for paramName in paramNames:
				if allParamsRequired or dictionary.has_key(paramName):
					dictionary[paramName] = translatorFuncs[convStr](dictionary[paramName])
		return dictionary
	if requiredParamsTranslator:
		try:
			dict = translateParamDictInModes(dict, requiredParamsTranslator, True)
		except KeyError:
			raise ValueError('Required parameter is missing from the parameter dictionary ' + str(dict) + '. Requirements: ' + str(requiredParamsTranslator))
	return translateParamDictInModes(dict, optionalParamsTranslator, False)
