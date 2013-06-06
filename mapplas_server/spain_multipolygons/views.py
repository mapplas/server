# -*- encoding: utf-8 -*-

from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db import models

from django.core.files import File
from django.contrib.gis.db.models import Union

from spain_multipolygons.models import SpainRegions

from entity_extractor.models import Entities
from django.contrib.gis import geos

'''
Prints regions for province given
'''
def regions_for_province(prov):
	
	combined_area = SpainRegions.objects.filter(province=prov).aggregate(area=Union('mpoly'))['area']
	
	gipuzkoa_mpoly_file = open('/home/ubuntu/server/mapplas_server/spain_multipolygons/gipuzkoa_mpoly.txt', 'w')
	myFile = File(gipuzkoa_mpoly_file)
	
	gipuzkoa_mpoly_file.write(str(combined_area))
	
	gipuzkoa_mpoly_file.close()


'''
Returns name of region for given latitude and longitude
'''
def name_of_region_for(latitude, longitude):
	point = get_point(latitude, longitude)
	
	region = SpainRegions.objects.filter(mpoly__contains=point)
	
	if not region:
		return 'No region found'
	else:
		return region[0].name
		
		
'''
Returns true if exists a region for given latitude and longitude
'''		
def exists_region_for(latitude, longitude):
	point = get_point(latitude, longitude)
	
	region = SpainRegions.objects.filter(mpoly__contains=point)
	
	if not region:
		return False
	else:
		return True


'''
Returns a GEOSGeometry object from latitude and longitude given
'''
def get_point(latitude, longitude):
	return GEOSGeometry('POINT(%f %f)' % (longitude, latitude))
	
'''
Generates a polygon/multipolygon for provinces in Spain.
Saves that multipolygon in entity_extractor tables
'''
def generate_multipolygons_for_regions():
	
	regions = SpainRegions.objects.order_by('province').distinct('province')
	
	for region in regions:
		print(region.province)
		
		if region.province != 'mpoly_error':
			
			province_poly = SpainRegions.objects.filter(province=region.province).aggregate(area=Union('mpoly'))['area']
			
			try:
				region_in_main_table = Entities.objects.get(name1=region.province, region_type_id='P')
	
				if province_poly:
					if isinstance(province_poly, geos.Polygon):
					
						province_mpoly = geos.MultiPolygon(province_poly)
						region_in_main_table.mpoly = province_mpoly
						
					else:
					
						region_in_main_table.mpoly = province_poly
		
					region_in_main_table.save()
					print('mpoly saved')
					
			except Entities.DoesNotExist:
				print('Does not exist Entity for province ' + region.province)
			
				
'''
Generates a Multipolygon for spain authonomic comunities, from province multipolygons.
'''
def generate_multipolygons_for_comunities():
	
	comunities = Entities.objects.order_by('name1').filter(parent=0)
	
	for comunity in comunities:
	
		if not comunity.mpoly:
			print(comunity.name1 + ' YES')
			parent_id = comunity.id
			subs_mpoly = Entities.objects.filter(parent=parent_id).aggregate(area=Union('mpoly'))['area']
			
			if subs_mpoly:
				if isinstance(subs_mpoly, geos.Polygon):
					province_mpoly = geos.MultiPolygon(subs_mpoly)
					comunity.mpoly = province_mpoly
				else:
					comunity.mpoly = subs_mpoly
					
			comunity.save()
			
		else:
			print('NO ' + comunity.name1)
					