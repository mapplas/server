# -*- encoding: utf-8 -*-
import re
import spain_multipolygons

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities

from spain_multipolygons.models import SpainRegions

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails

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

Entity types: R --> region, P --> Province, CC --> City/Capital of Province
'''
def find_geonames_in_apps_for_entities(entity_type):

	spain_region = Entities.objects.filter(region_type_id=entity_type)
	
	for region in spain_region:
	
		print(region.name1)
		print('************')
	
		regex = r'^.*(%s).*$' % region.name1
		app_details_with_regex = AppDetails.objects.filter(language_code=region.lang_code, description__iregex=regex)
		
		check_apps(app_details_with_regex, region, entity_type)
		
		if region.name2:
			print(region.name2)
			print('************')
			
			regex = r'^.*(%s).*$' % region.name2
			app_details_with_regex_translated = AppDetails.objects.filter(language_code=region.lang_code, description__iregex=regex)
			
			check_apps(app_details_with_regex_translated, region, entity_type)
			

'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(app_details_for_region, region, entity_type):

	storefront_id = get_storefront_id(region, entity_type)

	for app in app_details_for_region:
		
		try:
			app_price = AppPrice.objects.get(app_id=app.app_id, storefront_id=storefront_id)
			
			try:
				geometry = Geometry.objects.get(app_id=app_id, storefront_id = storefront_id)
			
			except:
				geometry = Geometry()
				
				try:
					if Application.objects.get(pk=app.app_id):
					
						geometry.app_id = app.app_id
						geometry.storefront_id = storefront_id
						
				except Application.DoesNotExist:
					print('Does not exist application for description')
					continue
				
				
			mpoly = get_multipolygon_for_spain(region, entity_type)
			
			if mpoly:
				if geometry.polygon:
					geometry.polygon = geometry.polygon.union(mpoly)		# Union!!!
				else:
					geometry.polygon = mpoly
				geometry.save()
				print('App ' + app.title)
				#file_to_write.write('App ' + app.title.encode('utf-8'))
			else:
				print('null polygon for region ' + region)
				#file_to_write.write('null polygon for region ' + region.encode('utf-8'))
		
		except AppPrice.DoesNotExist:
			# App does not exist for that storefront. Do nothing.
			print('App ' + app.title + ' does not exist in that storefront')
			#file_to_write.write('App ' + app.title.encode('utf-8') + ' does not exist in that storefront')
			
			
'''
Returns multipolygon for given region
'''
def get_multipolygon_for_spain(region, entity_type):
	
	try:
		region = Entities.objects.get(name1=region, region_type=entity_type)
	
	except Entities.DoesNotExist:
		try:
			region = Entities.objects.get(name2=region, region_type=entity_type)
		
		except Entities.DoesNotExist:
			return null
		
	return region.mpoly
		
'''
Giving a region, returns the storefront id for it.
Only Spanish regions saved.
'''	
def get_storefront_id(region, entity_type):
	
	try:
		if(Entities.objects.get(name1=region, region_type=entity_type) or Entities.objects.get(name2=region, region_type=entity_type)):
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