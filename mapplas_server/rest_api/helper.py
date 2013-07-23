import time
import re

from rest_api.models import Application

'''
METHOD THAT CONVERTS TIMEZONE TO SECONDS SINCE 1970
'''
def epoch(now_time):
	return time.mktime(now_time.timetuple())


'''
RETURNS STOREFRONT COUNTRY CODE FOR GIVEN LANGUAGE
'''
def getStorefrontCountryCodeForLanguage(lang):
	url = urllib2.unquote(lang)	
	
	if lang == urllib2.quote('español'):
		return getSpainStorefrontCode()
	else:
		return getUsaStorefrontId()


'''
RETURNS USA STOREFRONT IDENTIFIER
'''
def getUsaStorefrontId():
	return 143441


'''
RETURNS USA STOREFRONT COUNTRY CODE
'''
def getUsaStorefrontCode():
	return 'USA'


'''
RETURNS SPAIN STOREFRONT IDENTIFIER
'''
def getSpainStorefrontId():
	return 143454


'''
RETURNS SPAIN STOREFRONT COUNTRY CODE
'''
def getSpainStorefrontCode():
	return 'ESP'