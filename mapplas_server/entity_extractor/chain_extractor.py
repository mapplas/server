# -*- encoding: utf-8 -*-
import re, os, csv

from django.db.utils import DatabaseError

from django.contrib.gis.geos import Point, GEOSGeometry, MultiPolygon
from django.core.files import File

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities, EntityTypes
from entity_extractor import lang_detector

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon, ChainCathegory, GenreApp, CathegoryRelationMatrix

# 	Task done in tasks file
#	from entity_extractor import chain_extractor
#	chain_extractor.find_chains_in_apps()

'''
Finds chain name in application titles and assigns that polygon to app

Storefront country code:
	ESP - Spain
	USA - United States of America
'''
def find_chains_in_apps_for_storefront(chains, storefront_country_code):

# 	Task done in tasks file
# 	chains = Entities.objects.filter(region_type_id='CH', storefront_id=storefront_id)
		
	storefront_id = Storefront.objects.get(country_code=storefront_country_code).storefront_id	
		
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
# 		print(name)
# 		print('************')
		
		write_file = open('/home/ubuntu/temp/chains_log_%s/%s.txt' % (storefront_country_code.lower(), name), 'w')
		myFile = File(write_file)
		
		myFile.write(name.encode('utf-8') + '\n')
		myFile.write('*********************\n')
	
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
		check_apps(apps_with_regex_title_and_language, chain, chain_cathegories, storefront_id, myFile)
		
		myFile.close()

	
'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(apps, chain, chain_cathegories, storefront_id, myFile):

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
# 				print('Does not exist application for description')
				myFile.write('Does not exist application for description \n')
				continue
				
				
			# Get app genre/genres
			try:
				appstore_genre = GenreApp.objects.filter(app_id=app.app_id, is_primary=True).values_list('genre_id', flat=True)
				
				mapplas_cathegories_for_app = CathegoryRelationMatrix.objects.filter(genre_id=appstore_genre).values_list('mapplas_cathegories', flat=True)
				common_cathegories = list(set(mapplas_cathegories_for_app) & set(chain_cathegories))
			except DatabaseError:
				print('Database error with app %s' % app.title)
				continue
# 			print(common_cathegories)
			
			if len(common_cathegories) > 0:
			
				# Detect other countries name in title				
				if not detect_other_countries_name_in_title(app, storefront_id):
				
					# Get current polygon
					try:
						polygon = Polygon.objects.get(entity_id=chain.id)
						
						# Avoid duplicating geometries. If geometry exists for same app, storefront and polygon, continue
						try:
							geometry = Geometry.objects.get(app_id=app.app_id, storefront_id=storefront_id, polygon_id=polygon.id)
	# 						print('Duplicated app!!! ' + app.title)
							myFile.write('Duplicated app!!! %s \n' % app.title.encode('utf-8'))
							continue
							
						except Geometry.DoesNotExist:	
							
							geometry.polygon_id = polygon.id	
							
							# Check if words like official or oficial appears in title
							if check_if_is_official_app(app.title, storefront_id):
								geometry.ranking = 716141
								myFile.write('Searched official or oficial string in title \n')	
							
							geometry.save()
							
	# 						print('App ' + app.title)
							myFile.write('App %s \n' % app.title.encode('utf-8'))
						
					except Polygon.DoesNotExist:
						
						polygon = Polygon()
						polygon.polygon = chain.mpoly
						polygon.entity_id = chain.id
						polygon.origin = 'CH'
						polygon.name = chain.name1
						
						polygon.save()
						
						geometry.polygon_id = polygon.id
						
						# Check if words like official or oficial appears in title
						if check_if_is_official_app(app.title, storefront_id):
							geometry.ranking = 716141	
							myFile.write('Searched official or oficial string in title \n')	
							
						geometry.save()
					
	# 					print('Created polygon for chain ' + chain.name1)
	# 					print('App ' + app.title)
						myFile.write('Create polygon for chain %s \n' % chain.name1.encode('utf-8'))
	 					myFile.write('App %s \n' % app.title.encode('utf-8'))
				
		
		except AppPrice.DoesNotExist:
			# App does not exist for that storefront. Do nothing.
# 			print('App ' + app.title + ' does not exist in that storefront')
			myFile.write('App %s does not exist in that storefront \n' % app.title.encode('utf-8'))
			continue


'''
For each app with regex in its name, filter apps that their description is in Spanish language
'''
def detect_language_and_return_apps(apps, storefront_id):

	app_details_for_lang = []
	
	for app in apps:
	
		if check_app_detail_description_is_given_country(app.description, storefront_id):
			app_details_for_lang.append(app)
			
	return app_details_for_lang
	
	
'''
For each app, check if in its title appears any other country name or ISO
'''
def detect_other_countries_name_in_title(app, storefront_id):

	# Filter title does not contain any other state name or ISO
	# Open countries name and iso file
	countries_file = open('/home/ubuntu/temp/countries/countries_name_iso.txt', 'r+')

	# Spanish storefront
	if storefront_id == 143454:
		country_name = 'Spain'
		country_iso2 = 'SP'
		country_iso3 = 'ESP'
	else :
		country_name = 'United States'
		country_iso2 = 'US'
		country_iso3 = 'USA'
		
	found = False
	
		
	# Loop country names
	for line in countries_file:
	
		regex = r'\b%s\b' % line
				
		if (line != country_name and line != country_iso2 and line != country_iso3) and (re.search(regex, app.title) or re.search(regex, app.description)):
			
			log_file = open('/home/ubuntu/temp/logs/countries_name_in_ch_titles_%d.txt' % app.app_id, 'w')

			countries_name_in_ch_titles_file = File(log_file)
			countries_name_in_ch_titles_file.write('%s in %s app. ID:%d' % (line, app.title, app.app_id))
			
			found = True
			break
			
	# If any other country name found in title, check if in description or title current country name appears.
	if found:
		
		regex_name = r'\b%s\b' % country_name
		regex_iso2 = r'\b%s\b' % country_iso2
		regex_iso3 = r'\b%s\b' % country_iso3
	
		if (re.search(regex_name, app.description) or re.search(regex_iso2, app.description) or re.search(regex_iso3, app.description) or re.search(regex_name, app.title) or re.search(regex_iso2, app.title) or re.search(regex_iso3, app.title)):
			countries_name_in_ch_titles_file.write('Found %s in title or description. OK' % country_name)
			countries_name_in_ch_titles_file.close()
			return False
		else:
			countries_name_in_ch_titles_file.write('Not found %s in title or description. NOT SAVED' % country_name)
			countries_name_in_ch_titles_file.close()
			return True
			
	else:
		return False
		

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
		
		
'''
Check if in title strings 'official' and 'oficial' appears
'''
def check_if_is_official_app(title, storefront_id):

	str_official = 'official'
	if storefront_id == 143454:
		str_official = 'oficial'
	
	regex = r'\b%s\b' % str_official
	
	if re.search(regex, title):
		return True
	else:
		return False