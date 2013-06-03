import re

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import SpainRegions

import spain_multipolygons
from spain_multipolygons import views

from rest_api.models import Application, Storefront, AppPrice, Geometry

from celery import task


def find_geonames_in_apps_for_spain_regions(region):

	#file_to_write = open('/home/ubuntu/server/apps.txt', 'w')

	spain_region = SpainRegions.objects.all()
	
	for region in spain_region:
		print(region.name1)
		print('************')
		#file_to_write.write(region.name1.encode('utf-8'))
		#file_to_write.write('**************')
	
		regex = r'^.*(%s).*$' % region.name1
		apps_region = Application.objects.filter(app_description__iregex = regex)
		
		check_apps(apps_region, region)
	
		
		if region.name2:
			print(region.name2)
			print('************')
			#file_to_write.write(region.name2.encode('utf-8'))
			#file_to_write.write('**************')
			
			regex = r'^.*(%s).*$' % region.name2
			apps_region_translated = Application.objects.filter(app_description__iregex = regex)
			
			check_apps(apps_region_translated, region)
		
	#file_to_write.close()

'''
Check if apps exist for given region in storefront.
If yes, created a geometry for that app in given region.
'''
def check_apps(apps_for_region, region):

	storefront_id = get_storefront_id(region)

	for app in apps_for_region:
		
		try:
			app_price = AppPrice.objects.get(app_id=app.app_id_appstore, storefront_id=storefront_id)
			
			try:
				geometry = Geometry.objects.get(app_id=app_id_storefront, storefront_id = storefront_id)
			
			except:
				geometry = Geometry()
				geometry.app_id = app.app_id_appstore
				geometry.storefront_id = storefront_id
				
				
			mpoly = get_multipolygon_for_spain(region)
			
			if mpoly:
				geometry.polygon = mpoly
				geometry.save()
				print('App ' + app.app_name)
				#file_to_write.write('App ' + app.app_name.encode('utf-8'))
			else:
				print('null polygon for region ' + region)
				#file_to_write.write('null polygon for region ' + region.encode('utf-8'))
		
		except AppPrice.DoesNotExist:
			# App does not exist for that storefront. Do nothing.
			print('App ' + app.app_name + ' does not exist in that storefront')
			#file_to_write.write('App ' + app.app_name.encode('utf-8') + ' does not exist in that storefront')
			
			
'''
Returns multipolygon for given region
'''
def get_multipolygon_for_spain(region):
	
	try:
		region = SpainRegions.objects.get(name1=region)
	
	except SpainRegions.DoesNotExist:
		try:
			region = SpainRegions.objects.get(name2=region)
		
		except SpainRegions.DoesNotExist:
			return null
		
	return region.mpoly
		
'''
Giving a region, returns the storefront id for it.
Only Spanish regions saved.
'''	
def get_storefront_id(region):
	
	try:
		if(SpainRegions.objects.get(name1=region) or SpainRegions.objects.get(name2=region)):
			return 143454		#Storefront ESP - Spain
	except SpainRegions.DoesNotExist:
		return 143441			#Storefront USA - United States of America
		
		
'''
Returns geonames for given country and province.
'''
def geonames_in_country_and_province(country, province):
	country = 'Europe/Madrid'
	province = 'Gipuzkoa'

	geonames = geonames_all_countries.objects.filter(country=country)
	province_cities = spain_multipolygons.models.SpainRegions.objects.filter(province=province)
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
	province_cities = spain_multipolygons.models.SpainRegions.objects.filter(province=province_to_set)
	
	for place in country_geonames:

		lat = place.latitude
		lon = place.longitude
		
		point_place = views.get_point(lat, lon)
		
		for city in province_cities:
			if (city.mpoly.contains(point_place)):
				place.province = province_to_set
				place.save()