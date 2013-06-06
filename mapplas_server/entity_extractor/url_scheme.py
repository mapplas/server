from rest_api.models import Application

import urllib2
from xml.dom import minidom


def get_url_scheme():

	#Application.url_schema
	
	i = 1
	while i < 2:
		url = ("http://handleopenurl.com/api/v1.2/list.xml?apikey=e4f76a3591abb85f2369d91027f3e939&page=%d" % i)
		response = urllib2.urlopen(url)
		xmldoc = minidom.parse(response)
				
		schemes = xmldoc.getElementsByTagName('URLScheme')
		names = xmldoc.getElementsByTagName('DisplayName')
				
		'''
		Get url scheme list
		'''
		scheme_name_list = {}
		position = 0

		for element in schemes:
			
			if element.firstChild and names[position].firstChild:
				scheme_name_list[names[position].firstChild.nodeValue.encode('utf-8')] = element.firstChild.nodeValue.encode('utf-8')
				
			position = position + 1
			
	return scheme_name_list
		
			