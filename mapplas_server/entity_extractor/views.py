# -*- encoding: utf-8 -*-
import re
import spain_multipolygons

from entity_extractor.models import Entities

from spain_multipolygons.models import SpainRegions

from rest_api.models import AppDetails, Polygon, Storefront

from entity_extractor import extractor_helper

# Main method to create geometry objects for apps in REGIONS, PROVINCE, CITY AND STATES.

'''
CC --> City/Capital of Province
P -->> Province / Sub-county
R --> Region / County

Storefront lang code:
	ESP - Spain
	USA - United States of America
'''
def find_geonames_for_all_region_entities_for_storefront(storefront_country_code):

	storefront_id = Storefront.objects.get(country_code=storefront_country_code).storefront_id

	regions = Entities.objects.filter(region_type_id='R', storefront_id=storefront_id)
	provinces = Entities.objects.filter(region_type_id='P', storefront_id=storefront_id)
	cities = Entities.objects.filter(region_type_id='CC', storefront_id=storefront_id)
	
	# Get cities gazetteer
	cities_file = open('/home/ubuntu/temp/cities/cities_regions_provinces.txt', 'r')
	lines = [line.strip().lower() for line in cities_file]
	cities_file.close()
	
	subs = re.compile("|".join(lines))
	
	find_for(regions, lines, subs)
	find_for(provinces, lines, subs)
	find_for(cities, lines, subs)


def find_for(entities, lines, subs):
	
	for entity in entities:
	
		if not entity_parent_names_equal(entity.parent, entity.name1):

		print(entity.name1)
		print('************')
	
		#Finds exact match of string
		regex = r'^.*(\m%s\M).*$' % entity.name1
		
		app_details_with_regex_title = AppDetails.objects.filter(title__iregex=regex)
		app_details_with_regex_description = AppDetails.objects.filter(description__iregex=regex)
		
		extractor_helper.check_apps_for_city_match(app_details_with_regex_title, app_details_with_regex_description, entity, entity.name1, subs)		
		
		if entity.name2 and not entity_parent_names_equal(entity.parent, entity.name2):
					
			print(entity.name2)
			print('************')
			
			regex = r'^.*(\m%s\M).*$' % entity.name2
			
			app_details_with_regex_translated_title = AppDetails.objects.filter(title__iregex=regex)
			app_details_with_regex_translated_description = AppDetails.objects.filter(description__iregex=regex)			
			
			extractor_helper.check_apps_for_city_match(app_details_with_regex_translated_title, app_details_with_regex_translated_description, entity, entity.name2, subs)


'''
Checks if entity's parent has same name
'''
def entity_parent_names_equal(parent_id, name):

	parent = Entities.objects.get(pk=parent_id)
	
	if parent.name1 == name or parent.name2 == name:
		print('%s entitys parent has SAME names: %s and %s' % (name, parent.name1, parent.name2))
		return True
	else:
		print('%s entitys parent has DIFFERENT names: %s and %s' % (name, parent.name1, parent.name2))
		return False


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
		extractor_helper.check_apps(app_details_with_regex_title, state, entity_type, True)
		
		if state.name2:
					
			print(state.name2)
			print('************')
			
			regex = r'^.*(\m%s\M).*$' % state.name2
			
			app_details_with_regex_translated_title = AppDetails.objects.filter(title__iregex=regex)
			extractor_helper.check_apps(app_details_with_regex_translated_title, state, entity_type, True)
		
		
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
		
		
'''
Generates polygon objects for all usa entities
'''
def generate_polygons_for_usa_entities():

	entities = Entities.objects.filter(storefront_id=143441)
	
	for entity in entities:
		
		try:
			# If exists do nothing
			polygon = Polygon.objects.get(entity_id=entity.id)
			print('Exists polygon for entity %s' % polygon.name)
			continue
			
		except Polygon.DoesNotExist:
		
			polygon = Polygon()
			
			polygon.polygon = entity.mpoly
			polygon.entity = entity
			polygon.origin = entity.region_type_id
			polygon.name = entity.name1
			
			polygon.save()
			
			print('Created polygon for entity %s' % polygon.name)