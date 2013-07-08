# -*- encoding: utf-8 -*-

from celery import task
from django.core.files import File

'''
CHAINS TASKS
'''
import re, os, csv

from entity_extractor.extractor_helper import get_storefront_id

from django.contrib.gis.geos import Point, GEOSGeometry, MultiPolygon

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities, EntityTypes
from entity_extractor import lang_detector

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon, ChainCathegory, GenreApp, CathegoryRelationMatrix


#	from entity_extractor.tasks import *
#	find_chains_in_apps.apply_async()

'''
Finds chain name in application titles and assigns that polygon to app
'''
@task
def find_chains_in_apps():
	
	chains = Entities.objects.filter(region_type_id='CH')
	
	chains = chains[700:800]
				
	for chain in chains:
	
		name_to_search = chain.name1
		
		name_split = name_to_search.split('|')
	
		# Exceptions
		chains_with_description_only_in_english = ["H&M", "Domino's Pizza", "Calzedonia", "Promod"]
		
		for name in name_split:
		
			if(name == "Toys'R'Us"):
				name = 'TOYS"R"US'
	
			# Print info
			#print(name_to_search)
			#print('************')
			
			write_file = open('/home/ubuntu/temp/chains_log/%s.txt' % name, 'w')
			myFile = File(write_file)
			
			myFile.write(name.encode('utf-8') + '\n')
			myFile.write('*********************\n')
		
			# Finds exact match of string
			regex = r'^.*(\m%s\M).*$' % name
			
			# Gets app details that match with previous reg. expression	
			app_with_regex_title = AppDetails.objects.filter(title__iregex=regex)
			
			# Filter description in spanish
			if(chain.name1 not in chains_with_description_only_in_english):
				app_with_regex_title = detect_spanish(app_with_regex_title)
			
			# Get chain matching cathegories
			chain_cathegories = ChainCathegory.objects.filter(entity_id=chain.id).values_list('mapplas_cathegories', flat=True)
			
			# Filter apps
			check_apps(app_with_regex_title, chain, chain_cathegories, myFile)
		
		myFile.close()
		

'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(apps, chain, chain_cathegories, myFile):

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
				#print('Does not exist application for description')
				myFile.write('Does not exist application for description \n')
				continue
				
				
			# Get app genre/genres
			appstore_genre = GenreApp.objects.filter(app_id=app.app_id, is_primary=True).values_list('genre_id', flat=True)
			
			mapplas_cathegories_for_app = CathegoryRelationMatrix.objects.filter(genre_id=appstore_genre).values_list('mapplas_cathegories', flat=True)
			common_cathegories = list(set(mapplas_cathegories_for_app) & set(chain_cathegories))

			# print(common_cathegories)
			
			if len(common_cathegories) > 0:
				
				# Get current polygon
				try:
					polygon = Polygon.objects.get(entity_id=chain.id)
				
					geometry.polygon_id = polygon.id	
					geometry.save()
					
					#print('App ' + app.title)
					myFile.write('App ' + app.title.encode('utf-8') + '\n')
					
				except Polygon.DoesNotExist:
					
					polygon = Polygon()
					polygon.polygon = chain.mpoly
					polygon.entity_id = chain.id
					polygon.origin = 'CH'
					polygon.name = chain.name1
					
					polygon.save()
					
					geometry.polygon_id = polygon.id	
					geometry.save()
				
					#print('Created polygon for chain ' + chain.name1)
					#print('App ' + app.title)
					myFile.write('Created polygon for chain ' + chain.name1.encode('utf-8') + '\n')
					myFile.write('App ' + app.title.encode('utf-8') + '\n')
		
		except AppPrice.DoesNotExist:
			# App does not exist for that storefront. Do nothing.
			#print('App ' + app.title + ' does not exist in that storefront')
			myFile.write('App ' + app.title.encode('utf-8') + ' does not exist in that storefront')
			
			
'''
For each app with regex in its name, filter apps that their description is in Spanish language
'''
def detect_spanish(apps):

	spanish_app_details = []
	
	for app in apps:
		# With only 100 chars, apps like Caprabo are detected like french. Be careful!
		if lang_detector.get_language(app.description[:150]) == 'spanish':
			spanish_app_details.append(app)
			
	return spanish_app_details

'''
# -*- encoding: utf-8 -*-

import re

from entity_extractor.models import Entities, EntityTypes
from entity_extractor import regex

from rest_api.models import Application, Storefront, Geometry, AppDetails, Polygon
'''

'''
For each PL name and second name, finds apps that are in title comined with CC names.

>>> from entity_extractor.tasks import *
>>> find_geonames_combinating_entities.apply_async()



@task
def find_geonames_combinating_entities():
	i = 1000
	
	pl_entity_names = Entities.objects.filter(region_type_id='PL').values_list('name1', flat=True)
	cc_entities = Entities.objects.filter(region_type_id='CC')
	
	#change iiiiii!!!	
	pl_entity_names = pl_entity_names[0:25]
		
	for pl in pl_entity_names:
	
		write_file = open('/home/ubuntu/temp/mx/mx_%s.txt' % pl, 'w')
		myFile = File(write_file)
	
		for cc in cc_entities:
	
			pl_name = pl
			pl_name_clean = pl_name.replace('_', ' ')
			cc_name = cc.name1
			
			regex1 = r'^.*(%s).*(%s).*$' % (pl_name_clean, cc_name)
			regex2 = r'^.*(%s).*(%s).*$' % (cc_name, pl_name_clean)
			
			apps_match_1 = AppDetails.objects.filter(language_code='ES', title__iregex=regex1)
			apps_match_2 = AppDetails.objects.filter(language_code='ES', title__iregex=regex2)
			apps_match = list(apps_match_1) + list(apps_match_2)
			
			if apps_match:
					myFile.write('\n')
					myFile.write(pl_name_clean.encode('utf-8'))
					myFile.write(' - ')
					myFile.write(cc_name.encode('utf-8'))
					myFile.write('\n')			
					myFile.write(' ************\n')
				
					insert_apps_into_db(apps_match, pl_name_clean, cc_name, True, myFile, i)
					i = i + 1
			
			
			if cc.name2 and cc.name2 != 'null' and cc.name2 != 'Null' and cc.name2 != 'NULL':
				cc_name = cc.name2
				
				regex1 = r'^.*(%s).*(%s).*$' % (pl_name_clean, cc_name)
				regex2 = r'^.*(%s).*(%s).*$' % (cc_name, pl_name_clean)
				
				apps_match_1 = AppDetails.objects.filter(language_code='ES', title__iregex=regex1)
				apps_match_2 = AppDetails.objects.filter(language_code='ES', title__iregex=regex2)
				apps_match = list(apps_match_1) + list(apps_match_2)
				
				if apps_match:
					myFile.write('\n')
					myFile.write(pl_name_clean.encode('utf-8'))
					myFile.write(' - ')
					myFile.write(cc_name.encode('utf-8'))
					myFile.write('\n')
					myFile.write('************\n')
					
					insert_apps_into_db(apps_match, pl_name_clean, cc_name, False, myFile, i)
					i = i + 1

		myFile.close()


Inserts found combinations into db

def insert_apps_into_db(apps_matched, pl_name, cc_entity, first, myFile, i):
	entity_type_str = 'MX'
	entity_type = EntityTypes.objects.get(pk=entity_type_str)
	lang_code = 'ES'
	storefront = Storefront.objects.get(pk=143454)
	
	# Create entity for match apps
	entity = Entities()
	entity.id = i
	entity.name1 = pl_name
	entity.name2 = cc_entity
	entity.region_type = entity_type
	entity.lang_code = lang_code
	entity.lang_code2 = lang_code
	if first:
		entity.mpoly = Entities.objects.get(region_type='CC', name1=cc_entity).mpoly
	else:
		entity.mpoly = Entities.objects.get(region_type='CC', name2=cc_entity).mpoly
	entity.save()
		
	# Create polygon for match apps
	polygon = Polygon()
	polygon.polygon = entity.mpoly
	polygon.entity = entity
	polygon.origin = entity_type_str
	polygon.name = pl_name + '-' + cc_entity
	polygon.save()

	for app in apps_matched:
		geometry = Geometry()
		try:
			geometry.app = Application.objects.get(pk=app.app_id)
			geometry.storefront = storefront
			geometry.polygon = polygon
			geometry.origin = entity_type_str
			geometry.save()
			myFile.write(app.title.encode('utf-8') + '\n')
		except Application.DoesNotExist:
			continue
'''