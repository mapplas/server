# -*- encoding: utf-8 -*-
import re, os, csv

from entity_extractor.views import get_storefront_id

from django.contrib.gis.geos import Point, GEOSGeometry, MultiPolygon

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities, EntityTypes
from entity_extractor import lang_detector

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon, ChainCathegory, GenreApp, CathegoryRelationMatrix


#	from entity_extractor import chain_extractor
#	chain_extractor.find_chains_in_apps()

'''
Finds chain name in application titles and assigns that polygon to app
'''
def find_chains_in_apps():
	
	chains = Entities.objects.filter(region_type_id='CH')
	
	chains = chains[400:450]
			
	for chain in chains:
	
		name_to_search = chain.name1
	
		# Exceptions
		chains_with_description_only_in_english = ["H&M", "Domino's Pizza", "Calzedonia", "Promod"]
		
		if(name_to_search=="TOYS'R'US"):
			name_to_search = 'TOYS"R"US'

		# Print info
		print(name_to_search)
		print('************')
	
		# Finds exact match of string
		regex = r'^.*(\m%s\M).*$' % name_to_search
		
		# Gets app details that match with previous reg. expression	
		app_with_regex_title = AppDetails.objects.filter(title__iregex=regex)
		
		# Filter description in spanish
		if(chain.name1 not in chains_with_description_only_in_english):
			apps_with_regex_title_and_spanish = detect_spanish(app_with_regex_title)
		
		# Get chain matching cathegories
		chain_cathegories = ChainCathegory.objects.filter(entity_id=chain.id).values_list('mapplas_cathegories', flat=True)
		
		# Filter apps
		check_apps(apps_with_regex_title_and_spanish, chain, chain_cathegories)
		

'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(apps, chain, chain_cathegories):

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
				
				
			# Get app genre/genres
			appstore_genre = GenreApp.objects.filter(app_id=app.app_id, is_primary=True).values_list('genre_id', flat=True)
			
			mapplas_cathegories_for_app = CathegoryRelationMatrix.objects.filter(genre_id=appstore_genre).values_list('mapplas_cathegories', flat=True)
			common_cathegories = list(set(mapplas_cathegories_for_app) & set(chain_cathegories))

			print(common_cathegories)
			
			if len(common_cathegories) > 0:
				
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
			
			
'''
For each app with regex in its name, filter apps that their description is in Spanish language
'''
def detect_spanish(apps):

	spanish_app_details = []
	
	for app in apps:
		# With only 100 chars, apps like Caprabo are detected like french. Be careful!
		if lang_detector.get_language(app.description[:150]) == 'spanish':
			spanish_app_details.append(app)
			print('App in Spanish')
			
	return spanish_app_details