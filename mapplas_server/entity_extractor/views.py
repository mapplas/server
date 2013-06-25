# -*- encoding: utf-8 -*-
import re
import spain_multipolygons

from entity_extractor.models import Entities

from spain_multipolygons.models import SpainRegions

from rest_api.models import AppDetails, Polygon

from entity_extractor import extractor_helper

# Main method to create geometry objects for apps in REGIONS, PROVINCE, CITY AND STATES.

'''
CC --> City/Capital of Province -- Search in name and description -- City max match
'''
def find_geonames_in_apps_for_capital_cities():
	
	entity_type = 'CC'
	
	cities = Entities.objects.filter(region_type_id=entity_type)
	cities = cities[0:26]
	
	for city in cities:

		print(city.name1)
		print('************')
	
		#Finds exact match of string
		regex = r'^.*(\m%s\M).*$' % city.name1
		
		app_details_with_regex_title = AppDetails.objects.filter(title__iregex=regex)
		app_details_with_regex_description = AppDetails.objects.filter(description__iregex=regex)
		extractor_helper.check_apps_for_city_match(app_details_with_regex_title, app_details_with_regex_description, city, entity_type)		
		
		if city.name2:
					
			print(city.name2)
			print('************')
			
			regex = r'^.*(\m%s\M).*$' % city.name2
			
			app_details_with_regex_translated_title = AppDetails.objects.filter(title__iregex=regex)
			app_details_with_regex_translated_description = AppDetails.objects.filter(description__iregex=regex)			
			extractor_helper.check_apps_for_city_match(app_details_with_regex_translated_title, app_details_with_regex_translated_description, city, entity_type)


'''
P --> Province -- Search in name and description
'''
def find_geonames_in_apps_for_province():
	
	entity_type = 'P'
	provinces = Entities.objects.filter(region_type_id=entity_type)
	
	for province in provinces:

		print(province.name1)
		print('************')
	
		#Finds exact match of string
		regex = r'^.*(\m%s\M).*$' % province.name1
		
		app_details_with_regex_title = AppDetails.objects.filter(title__iregex=regex)
		app_details_with_regex_description = AppDetails.objects.filter(description__iregex=regex)
		
		extractor_helper.check_apps(app_details_with_regex_title, province, entity_type)
		extractor_helper.check_apps(app_details_with_regex_description, province, entity_type)
		
		
		if province.name2:
					
			print(province.name2)
			print('************')
			
			regex = r'^.*(\m%s\M).*$' % province.name2
			
			app_details_with_regex_translated_title = AppDetails.objects.filter(title__iregex=regex)
			app_details_with_regex_translated_description = AppDetails.objects.filter(description__iregex=regex)
			
			extractor_helper.check_apps(app_details_with_regex_translated_title, province, entity_type)
			extractor_helper.check_apps(app_details_with_regex_translated_description, province, entity_type)


'''
R --> Region -- Search in name and description
'''
def find_geonames_in_apps_for_region():
	entity_type = 'R'
	regions = Entities.objects.filter(region_type_id=entity_type)
	
	for region in regions:

		print(region.name1)
		print('************')
	
		#Finds exact match of string
		regex = r'^.*(\m%s\M).*$' % region.name1
		
		app_details_with_regex_title = AppDetails.objects.filter(title__iregex=regex)
		app_details_with_regex_description = AppDetails.objects.filter(description__iregex=regex)
		
		extractor_helper.check_apps(app_details_with_regex_title, region, entity_type)
		extractor_helper.check_apps(app_details_with_regex_description, region, entity_type)
		
		
		if region.name2:
					
			print(region.name2)
			print('************')
			
			regex = r'^.*(\m%s\M).*$' % region.name2
			
			app_details_with_regex_translated_title = AppDetails.objects.filter(title__iregex=regex)
			app_details_with_regex_translated_description = AppDetails.objects.filter(description__iregex=regex)
			
			extractor_helper.check_apps(app_details_with_regex_translated_title, region, entity_type)
			extractor_helper.check_apps(app_details_with_regex_translated_description, region, entity_type)
			
			
'''
S --> State -- Only searched in name -- Do not search
'''
def find_geonames_in_apps_for_state():
	
	entity_type = 'S'
	states = Entities.objects.filter(region_type_id=entity_type)
	
	for state in states:

		print(state.name1)
		print('************')
	
		#Finds exact match of string
		regex = r'^.*(\m%s\M).*$' % state.name1
		
		app_details_with_regex_title = AppDetails.objects.filter(title__iregex=regex)		
		extractor_helper.check_apps(app_details_with_regex_title, state, entity_type)
		
		if state.name2:
					
			print(state.name2)
			print('************')
			
			regex = r'^.*(\m%s\M).*$' % state.name2
			
			app_details_with_regex_translated_title = AppDetails.objects.filter(title__iregex=regex)
			extractor_helper.check_apps(app_details_with_regex_translated_title, state, entity_type)
		
		
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