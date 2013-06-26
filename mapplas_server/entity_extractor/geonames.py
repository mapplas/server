# -*- encoding: utf-8 -*-
import re

from django.contrib.gis.geos import Point

from rest_api.models import AppDetails, Polygon, Geometry, Storefront, Application

from entity_extractor.models import Entities, EntityTypes


'''
IMPROVEMENT: find name in app title, and find cathegory in description.
'''
def extract_geonames_and_save():
	# Open geonames file
	cities_file = open('/home/ubuntu/temp/geonames/estadios.txt', 'r')
	
	# Spain multipolygon
	spain_mpoly = Entities.objects.get(name1='España').mpoly
	
	spanish_storefront = Storefront.objects.get(country_code='ESP')
	
	# 2km radius for polygon
	radius = 2000 / 111.045
	
	geoname_entity = Entities.objects.get(region_type='GN')

	# Loop file lines
	for line in cities_file:
	
		data_splitted = line.split(',')
		#cathegory = data_splitted[0]
		name = data_splitted[1]
		lat = data_splitted[2]
		lon = data_splitted[3]
		
		print(name + '---------\n')
		
		point = Point(float(lon), float(lat))
		
		# Check if geoname is in Spain
		if spain_mpoly.intersects(point):
		
			regex = r'^.*(\m%s\M).*$' % name
			
			first = True
			
			for app_id in AppDetails.objects.filter(description__iregex=regex).distinct('app_id').values_list('app_id', flat=True):
				print(Application.objects.get(pk=app_id).app_name)
				
				if first:
				
					# Create polygon with given point
					polygon = Polygon()
					polygon.mpoly = point.buffer(radius)
					polygon.entity_id = geoname_entity.id
					polygon.origin = 'GN'
					polygon.name = name
					polygon.save()
					first = False
					print('Created polygon for ' + name)
				
				# Create geometry that matches polygon & app
				
				geometry = Geometry()
				geometry.app_id = app_id
				geometry.storefront_id = spanish_storefront.storefront_id
				geometry.polygon_id = polygon.id
				geometry.origin = 'GN'
				geometry.save()
				print('Created geometry for ' + name)
				
		print('\n')
	
	cities_file.close()