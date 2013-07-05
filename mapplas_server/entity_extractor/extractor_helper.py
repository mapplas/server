# -*- encoding: utf-8 -*-

import re
from django.core.files import File

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities

from entity_extractor import lang_detector
from entity_extractor import regex

from spain_multipolygons.models import SpainRegions

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon

'''
Checks given string language is spanish
'''
def check_app_detail_description_is_spanish(app_detail_description):
	
	if 'spanish' == lang_detector.get_language(app_detail_description[:200]):
		return True		
	else:
		return False
	
	
'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(app_details_for_entity, entity, entity_type, app_geometry_save_dict, checking_title):

	storefront_id = get_storefront_id(entity, entity_type)

	for app in app_details_for_entity:
	
		if check_app_detail_description_is_spanish(app.description):
		
			if checking_title:
			
				if regex.is_valid_title_checking_years(app.title):
		
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
							
						polygon = Polygon.objects.get(entity_id=entity.id)
			
						if polygon:
						
							geometry.polygon_id = polygon.id	
							geometry.save()
							
							app_geometry_save_dict[app.app_id] = True 
							
							print('App ' + app.title)
							#file_to_write.write('App ' + app.title.encode('utf-8'))
						else:
							print('null polygon for region ' + entity.name1)
							#file_to_write.write('null polygon for region ' + region.encode('utf-8'))
					
					except AppPrice.DoesNotExist:
						# App does not exist for that storefront. Do nothing.
						print('App ' + app.title + ' does not exist in that storefront')
						#file_to_write.write('App ' + app.title.encode('utf-8') + ' does not exist in that storefront')
						
				else:
					print('Current year data error: %s' % app.title)
	
	return app_geometry_save_dict
	
	
'''
Giving a region, returns the storefront id for it.
Only Spanish regions saved.
'''	
def get_storefront_id(entity, entity_type):
	
	try:
		if(Entities.objects.get(name1=entity.name1, region_type=entity_type) or Entities.objects.get(name2=entity.name2, region_type=entity_type)):
			return 143454		#Storefront ESP - Spain
	except Entities.DoesNotExist:
		return 143441			#Storefront USA - United States of America


'''
Check if apps exist for given region in storefront.
If yes, check if from city gazetteers don't appear more than 3 different cities.
If no, save it.
'''
def check_apps_for_city_match(app_titles_for_entity, app_details_for_entity, entity, entity_type, name_to_search, subs):
		
	app_geometry_save_dict = {}
	
	# Check app titles
	app_geometry_save_dict = check_apps(app_titles_for_entity, entity, entity_type, app_geometry_save_dict, True)
	
	# Check app descriptions
	check_city_apps(app_details_for_entity, entity, entity_type, app_geometry_save_dict, name_to_search, subs)


'''
Checks apps text.
'''
def check_city_apps(apps, entity, entity_type, app_geometry_save_dict, name_to_search, subs):

	storefront_id = get_storefront_id(entity, entity_type)
	
	for app in apps:
	
		# Checks in dictionary if for that app is any geometry saved before (when checking title)
		if not app_geometry_save_dict.has_key(app.app_id):
	
			if check_app_detail_description_is_spanish(app.description):
			
				# Checks if they are not more than x cities in description
				if not check_more_than_x_cities(app.description, name_to_search, subs):
			
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
							
						polygon = Polygon.objects.get(entity_id=entity.id)
			
						if polygon:
						
							geometry.polygon_id = polygon.id	
							geometry.save()
														
							print('App ' + app.title)
							#file_to_write.write('App ' + app.title.encode('utf-8'))
						else:
							print('null polygon for region ' + entity.name1)
							#file_to_write.write('null polygon for region ' + region.encode('utf-8'))
					
					except AppPrice.DoesNotExist:
						# App does not exist for that storefront. Do nothing.
						print('App ' + app.title + ' does not exist in that storefront')
						#file_to_write.write('App ' + app.title.encode('utf-8') + ' does not exist in that storefront')
				
				else:
					polygon = Polygon.objects.get(entity_id=entity.id)
					print('App %s has more than 3 city names in description. App id:%d. Polygon id:%d' % (app.title, app.app_id_appstore, polygon.polygon_id))
		else:
			print('Geometry saved in title for app ' + app.title)
				

'''
Checks if in description are more than max_cities_number cities.
'''
def check_more_than_x_cities(text, name_to_search, subs):
	max_cities_number_in_description = 3
	
	matches = 0
	
	# iterative result
	for match in re.finditer(subs, text.lower()):

		if match.group(0) != name_to_search.lower():
			matches = matches + 1
		
		if matches > max_cities_number_in_description:
			break
			
		
	return matches > max_cities_number_in_description
