# -*- encoding: utf-8 -*-
import re
import spain_multipolygons

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities
from entity_extractor import regex

from spain_multipolygons.models import SpainRegions

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon

'''
--> Manual <-- method of main method.
'''
def find_geonames_in_apps_for_spain_regions_giving_region(region):
	print(region)
	
	regex = r'^.*(%s).*$' % region
	apps_region = Application.objects.filter(app_description__iregex = regex)
	
	check_apps(apps_region, region)

'''
Main method to create geometry objects for apps in regions.
--> Automatic <--

Entity types: R --> region, P --> Province, CC --> City/Capital of Province, PL --> Place

When entity type is PL, only search in ES language

'''
def find_geonames_in_apps_for_entities(entity_type):
	
	spain_region = Entities.objects.filter(region_type_id=entity_type)
	spain_region = spain_region[26:52]
			
	for region in spain_region:

		#name = region.name1.replace('_', ' ')

		print(region.name1)
		print('************')
	
		#Finds exact match of string
		regex = r'^.*(%s).*$' % region.name1
		
		app_details_with_regex_description = AppDetails.objects.filter(language_code=region.lang_code, description__iregex=regex)
		app_details_with_regex_title = AppDetails.objects.filter(language_code=region.lang_code, title__iregex=regex)
		
		check_apps(app_details_with_regex_description, region, entity_type)
		check_apps(app_details_with_regex_title, region, entity_type)
		
		
		if region.name2:
		
			#name2 = region.name2.replace('_', ' ')
			
			print(region.name2)
			print('************')
			
			regex = r'^.*(%s).*$' % region.name2
			app_details_with_regex_translated_description = AppDetails.objects.filter(language_code=region.lang_code2,description__iregex=regex)
			app_details_with_regex_translated_title = AppDetails.objects.filter(language_code=region.lang_code2, title__iregex=regex)
			
			check_apps(app_details_with_regex_translated_description, region, entity_type)
			check_apps(app_details_with_regex_translated_title, region, entity_type)
		
		
def check_app_detail_description(app_detail_description):
	
	if 'spanish' == regex.get_language(app_detail_description[:300]):
		return True		
	else:
		return False
	
	
'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(app_details_for_region, region, entity_type):

	storefront_id = get_storefront_id(region, entity_type)

	for app in app_details_for_region:
	
		if check_app_detail_description(app.description):
		
			try:
				app_price = AppPrice.objects.get(app_id=app.app_id, storefront_id=storefront_id)
				
				geometry = Geometry()
				
				try:
					if Application.objects.get(pk=app.app_id):
					
						geometry.app_id = app.app_id
						geometry.storefront_id = storefront_id
						geometry.origin = entity_type
						
				except Application.DoesNotExist:
					print('Does not exist application for description')
					continue
					
				polygon = Polygon.objects.get(entity_id=region.id)
	
				if polygon:
				
					geometry.polygon_id = polygon.id	
					geometry.save()
					
					print('App ' + app.title)
					#file_to_write.write('App ' + app.title.encode('utf-8'))
				else:
					print('null polygon for region ' + region.name1)
					#file_to_write.write('null polygon for region ' + region.encode('utf-8'))
			
			except AppPrice.DoesNotExist:
				# App does not exist for that storefront. Do nothing.
				print('App ' + app.title + ' does not exist in that storefront')
				#file_to_write.write('App ' + app.title.encode('utf-8') + ' does not exist in that storefront')
	
	
'''
Giving a region, returns the storefront id for it.
Only Spanish regions saved.
'''	
def get_storefront_id(region, entity_type):
	
	try:
		if(Entities.objects.get(name1=region.name1, region_type=entity_type) or Entities.objects.get(name2=region.name2, region_type=entity_type)):
			return 143454		#Storefront ESP - Spain
	except Entities.DoesNotExist:
		return 143441			#Storefront USA - United States of America
		
		
'''
Returns geonames for given country and province.
'''
def geonames_in_country_and_province(country, province):
	country = 'Europe/Madrid'
	province = 'Gipuzkoa'

	geonames = geonames_all_countries.objects.filter(country=country)
	province_cities = SpainRegions.objects.filter(province=province)
	searched_geonames = []
	
	for place in geonames:
	
		lat = place.latitude
		lon = place.longitude
		
		point_place = views.get_point(lat, lon)
		
		for city in province_cities:
			if (city.mpoly.contains(point_place)):
				searched_geonames(place)
				
	print(searched_geonames)
	
		
'''
Inserts into geonames_GeoNames_all_countries table given province value to given country name

set_province_column_to('Gipuzkoa', 'Europe/Madrid')
'''
def set_province_column_to(province_to_set, country_to_search):

	country_geonames = geonames_all_countries.objects.filter(country=country_to_search)
	province_cities = SpainRegions.objects.filter(province=province_to_set)
	
	for place in country_geonames:

		lat = place.latitude
		lon = place.longitude
		
		point_place = views.get_point(lat, lon)
		
		for city in province_cities:
			if (city.mpoly.contains(point_place)):
				place.province = province_to_set
				place.save()
				

def generate_polygons(entity_type):

	entities = Entities.objects.filter(region_type_id=entity_type)
	
	for entity in entities:
	
		poly = Polygon()
		
		poly.polygon = entity.mpoly
		poly.entity = entity
		poly.origin = entity_type
		poly.name = entity.name1
		
		poly.save()