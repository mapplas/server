# -*- encoding: utf-8 -*-
import re, os, csv

from entity_extractor.views import get_storefront_id

from django.contrib.gis.geos import Point, GEOSGeometry, MultiPolygon

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities, EntityTypes
from entity_extractor import regex

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon

#	from entity_extractor import chain_extractor
#	chain_extractor.find_chains_in_apps()

'''
Finds chain name in application titles and assigns that polygon to app
'''
def find_chains_in_apps():
	
	chains = Entities.objects.filter(region_type_id='CH')
			
	for chain in chains:

		print(chain.name1)
		print('************')
	
		#Finds exact match of string
		regex = r'^.*(\m%s\M).*$' % chain.name1
				
		app_with_regex_title = AppDetails.objects.filter(language_code=chain.lang_code, title__iregex=regex)
		
		check_apps(app_with_regex_title, chain)
		

'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(apps, chain):

	storefront_id = get_storefront_id(chain, 'CH')

	for app in apps:
	
		try:
			app_price = AppPrice.objects.get(app_id=app.app_id, storefront_id=storefront_id)
			
			geometry = Geometry()
			
			try:
				Application.objects.get(pk=app.app_id)
				
				geometry.app_id = app.app_id
				geometry.storefront_id = storefront_id
				geometry.origin = 'CH'
					
			except Application.DoesNotExist:
				print('Does not exist application for description')
				continue
				
			
			# Get current polygon
			try:
				polygon = Polygon.objects.get(entity_id=chain.id)
			
				geometry.polygon_id = polygon.id	
				geometry.save()
				
				print('App ' + app.title)
				#file_to_write.write('App ' + app.title.encode('utf-8'))
				
			except Polygon.DoesNotExist:
				
				polygon = Polygon()
				polygon.polygon = chain.mpoly
				polygon.entity_id = chain.id
				polygon.origin = 'CH'
				polygon.name = chain.name1
				
				polygon.save()
				
				geometry.polygon_id = polygon.id	
				geometry.save()
			
				print('Created polygon for chain ' + chain.name1)
				print('App ' + app.title)
				#file_to_write.write('null polygon for region ' + region.encode('utf-8'))
		
		except AppPrice.DoesNotExist:
			# App does not exist for that storefront. Do nothing.
			print('App ' + app.title + ' does not exist in that storefront')
			#file_to_write.write('App ' + app.title.encode('utf-8') + ' does not exist in that storefront')