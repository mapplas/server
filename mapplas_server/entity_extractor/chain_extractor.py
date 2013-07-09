# -*- encoding: utf-8 -*-
import re, os, csv

from django.contrib.gis.geos import Point, GEOSGeometry, MultiPolygon
from django.core.files import File

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities, EntityTypes
from entity_extractor import lang_detector

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon, ChainCathegory, GenreApp, CathegoryRelationMatrix

#	from entity_extractor import chain_extractor
#	chain_extractor.find_chains_in_apps()

'''
Finds chain name in application titles and assigns that polygon to app

Storefront country code:
	ESP - Spain
	USA - United States of America
'''
def find_chains_in_apps_for_storefront(storefront_country_code):

	storefront_id = Storefront.objects.get(country_code=storefront_country_code).storefront_id
	chains = Entities.objects.filter(region_type_id='CH', storefront_id=storefront_id)
	
	#chains = chains[400:450]
	
	# Exceptions
	chains_with_description_only_in_english = ["H&M", "Domino's Pizza", "Calzedonia", "Promod"]
			
	for chain in chains:
	
		name_to_search = chain.name1
		name_to_search_list = name_to_search.split('|')
		
		# Search only by first splitted name
		name = name_to_search_list[0]
				
		if(name == "Toys'R'Us"):
			name = 'TOYS"R"US'

		# Print info
		print(name)
		print('************')
	
		# Finds exact match of string
		regex = r'^.*(\m%s\M).*$' % name
		
		# Gets app details that match with previous reg. expression	
		app_with_regex_title = AppDetails.objects.filter(title__iregex=regex)
		
		# Filter description language
		if storefront_country_code == 'ESP':
			if(chain.name1 not in chains_with_description_only_in_english):
				apps_with_regex_title_and_language = detect_language_and_return_apps(app_with_regex_title, storefront_id)
		
		else:
			apps_with_regex_title_and_language = detect_language_and_return_apps(app_with_regex_title, storefront_id)
		
		# Get chain matching cathegories
		chain_cathegories = ChainCathegory.objects.filter(entity_id=chain.id).values_list('mapplas_cathegories', flat=True)
		
		# Filter apps
		check_apps(apps_with_regex_title_and_language, chain, chain_cathegories, storefront_id)
		

'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(apps, chain, chain_cathegories, storefront_id):

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
			
				# Filter title does not contain any other state name or ISO
				# Open countries name and iso file
				countries_file = open('/home/ubuntu/temp/countries/countries_name_iso.txt', 'r+')
			
				# Create log file for searches
				log_file = open('/home/ubuntu/temp/logs/countries_name_in_ch_titles.txt', 'w')
				myFile = File(log_file)
				
				detect_other_countries_name_in_title(app, countries_file, myFile)
				myFile.close()
				
				
				# Get current polygon
				try:
					polygon = Polygon.objects.get(entity_id=chain.id)
					
					# Avoid duplicating geometries. If geometry exists for same app, storefront and polygon, continue
					try:
						geometry = Geometry.objects.get(app_id=app.app_id, storefront_id=storefront_id, polygon_id=polygon.id)
						print('Duplicated app!!! ' + app.title)
						continue
						
					except Geometry.DoesNotExist:	
						
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
def detect_language_and_return_apps(apps, storefront_id):

	app_details_for_lang = []
	
	for app in apps:
	
		if check_app_detail_description_is_given_country(app.app_detail, storefront_id):
			app_details_for_lang.append(app)
			
	return app_details_for_lang
	
	
'''
For each app, check if in its title appears any other country name or ISO
'''
def detect_other_countries_name_in_title(app, countries_file, myFile):
		
	# Loop country names
	for line in countries_file:
		
		if line != 'Spain' and line != 'SP' and line != 'ESP' and line in app.app_name:
	
			myFile.write('%s in %s app. ID:%d' % (line, app.app_name, app.app_id_appstore))
			continue
				

'''
Checks given string language is spanish
'''
def check_app_detail_description_is_given_country(app_detail_description, storefront_id):

	language_to_check = 'english'

	if storefront_id == 143454:
		language_to_check = 'spanish'
	
	if language_to_check == lang_detector.get_language(app_detail_description[:200]):
		return True		
	else:
		return False