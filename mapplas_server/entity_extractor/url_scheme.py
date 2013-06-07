from rest_api.models import Application
from xml.dom import minidom

import urllib2
import urllib

def insert_schemes_to_db():
	
	scheme_list = get_url_scheme()
	print(scheme_list)
	keys = scheme_list.keys()
	
	for key in keys:
		try:
			apps = Application.objects.all().filter(app_name=key)
			
			for app in apps:
				app.url_schema = scheme_list.get(key)
				app.save()
				
				print('Url scheme added to app ' + app.app_name)
			
		except Application.DoesNotExist:
			print('Url scheme NOT added to app' + app.app_name) 


def get_url_scheme():
	
	scheme_name_list = {}
	i = 1
	
	while i <= 11:
		print(i)
		url = ("http://handleopenurl.com/api/v1.2/list.xml?apikey=e4f76a3591abb85f2369d91027f3e939&page=%d" % i)
		response = urllib2.urlopen(url)
		xmldoc = minidom.parse(response)
				
		schemes = xmldoc.getElementsByTagName('URLScheme')
		names = xmldoc.getElementsByTagName('DisplayName')
				
		'''
		Get url scheme list
		'''
		position = 0

		for element in schemes:
			
			if element.firstChild and names[position].firstChild:
				name = names[position].firstChild.nodeValue.decode('utf-8')
				scheme = element.firstChild.nodeValue.decode('utf-8')
				scheme_name_list[urllib.unquote_plus(name)] = urllib.unquote_plus(scheme)
				
			position = position + 1
		
		i = i + 1
			
	return scheme_name_list
		
			