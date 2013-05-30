import re

from geonames.models import GeoNames_all_countries

from spain_multipolygons import views
from spain_multipolygons.models import SpainRegions

from rest_api.models import Application


INDEX = 21

def find_geonames_in_apps_for_province(province):
	
	province = 'Gipuzkoa'
	
	# Get applications
	index = 0
	apps = Application.objects.all()
	app_sublist = get_more_apps(apps, index)
	
	# Get geonames for given province
	spain_geonames = GeoNames_all_countries.objects.filter(province=province)
	
	look_for_province_apps(province, apps, app_sublist, index)
	look_for_province_geonames(spain_geonames, apps, app_sublist, index)
			
	
def look_for_province_geonames(spain_geonames, apps, app_sublist, index):
	for place in spain_geonames:
		print(place)
		print('**************')
	
		while (index <= INDEX):
		
			for app in app_sublist:
	
				regex = re.compile(r'\b%s\b' % place.name1)
				
				if (bool(regex.search(app.app_description))):
					print (place.name1 + ' and app related: ' + app.app_name)

			index = index + 1
			app_sublist = get_more_apps(apps, index)
			
		index = 0;
		app_sublist = get_more_apps(apps, index)


def look_for_province_apps(province, apps, app_sublist, index):
	print(province)
	print('**************')
	while (index <= INDEX):
		
		for app in app_sublist:

			regex = re.compile(r'\b%s\b' % province)
			
			if (bool(regex.search(app.app_description))):
				print (province + ' and app related: ' + app.app_name)

		index = index + 1
		app_sublist = get_more_apps(apps, index)
		
	index = 0;
	app_sublist = get_more_apps(apps, index)
								
	
def get_more_apps(apps, index):
	if(index == 0):
		return apps[0:30000]
	elif (index == 1):
		return apps[30000:60000]
	elif (index == 2):
		return apps[60000:90000]
	elif (index == 3):
		return apps[90000:120000]
	elif (index == 4):
		return apps[120000:150000]
	elif (index == 5):
		return apps[150000:180000]	
	elif (index == 6):
		return apps[180000:210000]
	elif (index == 7):
		return apps[210000:240000]
	elif (index == 8):
		return apps[240000:270000]
	elif (index == 9):
		return apps[270000:300000]
	elif (index == 10):
		return apps[300000:330000]
	elif (index == 11):
		return apps[330000:360000]
	elif (index == 12):
		return apps[360000:390000]
	elif (index == 13):
		return apps[390000:420000]
	elif (index == 14):
		return apps[420000:450000]
	elif (index == 15):
		return apps[450000:480000]
	elif (index == 16):
		return apps[480000:510000]
	elif (index == 17):
		return apps[510000:540000]
	elif (index == 18):
		return apps[540000:570000]
	elif (index == 19):
		return apps[570000:600000]
	elif (index == 20):
		return apps[600000:630000]
	elif (index == 21):
		return apps[630000:660000]
	else:
		return []
		
'''
Returns geonames for given country and province
'''
def geonames_in_country_and_province(country, province):
	country = 'Europe/Madrid'
	province = 'Gipuzkoa'

	geonames = GeoNames_all_countries.objects.filter(country=country)
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

	country_geonames = GeoNames_all_countries.objects.filter(country=country_to_search)
	province_cities = SpainRegions.objects.filter(province=province_to_set)
	
	for place in country_geonames:

		lat = place.latitude
		lon = place.longitude
		
		point_place = views.get_point(lat, lon)
		
		for city in province_cities:
			if (city.mpoly.contains(point_place)):
				place.province = province_to_set
				place.save()