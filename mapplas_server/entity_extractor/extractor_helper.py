import re

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities
from entity_extractor import lang_detector

from spain_multipolygons.models import SpainRegions

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon

'''
Checks given string language is spanish
'''
def check_app_detail_description(app_detail_description):
	
	if 'spanish' == lang_detector.get_language(app_detail_description[:200]):
		return True		
	else:
		return False
	
	
'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(app_details_for_entity, entity, entity_type):

	storefront_id = get_storefront_id(entity, entity_type)

	for app in app_details_for_entity:
	
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
