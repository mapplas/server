import re

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import spain_regions

from spain_multipolygons import views
from spain_multipolygons.models import SpainRegions

from rest_api.models import Application

from celery import task


def find_geonames_in_apps_for_spain_regions():

	#file_to_write = open('/home/ubuntu/server/apps.txt', 'w')

	spain_region = spain_regions.objects.all()
	
	for region in spain_region:
		print(region.name1)
		print('************')
	
		regex = r'^.*(%s).*$' % region.name1
		apps = Application.objects.filter(app_description__iregex = regex)
		print(apps)
		
		if region.name2:
			print(region.name2)
			print('************')
			
			regex = r'^.*(%s).*$' % region.name2
			apps_idiom = Application.objects.filter(app_description__iregex = regex)
			print(apps_idiom)
			
	#file_to_write.close()

		
'''
Returns geonames for given country and province
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