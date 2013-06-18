# -*- encoding: utf-8 -*-
import re, os, csv
import spain_multipolygons

from django.contrib.gis.geos import Point, GEOSGeometry, MultiPolygon

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities, EntityTypes
from entity_extractor import regex

from spain_multipolygons.models import SpainRegions

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon

from django.core.files import File

#	from entity_extractor import chain_generator
#	chain_generator.extract_entities_from_csv_files()

'''
Get all files from /home/ubuntu/temp/chains and generates a CH ENTITY with file points.
'''
def extract_entities_from_csv_files():

	chain_entity_type = EntityTypes.objects.get(identifier='CH')
	
	p = re.compile(r'^.*.csv$')
	
	for path, subdirs, files in os.walk(r'/home/ubuntu/temp/chains/'):
		for filename in files:
		
			if p.match(str(filename)):
			
				filename_str = str(filename)
			
				filename_clean = filename_str.replace('_', ' ')
				filename_clean = filename_clean.replace('.csv', '')
				
				try:
					entity = Entities.objects.get(name1=filename_clean, region_type='CH')
					print('Exists ' + filename_clean + ' entity')
					
					entity.mpoly = generate_mpoly_from_file(filename)
					entity.save()
					
				except Entities.DoesNotExist:
					print('Create ' + filename_clean + ' entity')
					entity = Entities()
					entity.name1 = filename_clean
					entity.name2 = filename
					entity.lang_code = 'ES'
					entity.lang_code2 = 'ES'
					entity.region_type = chain_entity_type
					entity.mpoly = generate_mpoly_from_file(filename)
					entity.save()


def generate_mpoly_from_file(filename):

	csv_file = open('/home/ubuntu/temp/chains/%s' % filename) #prepare a csv file for our example
	poligons = []
	print(filename)
	csv_reader = csv.reader(csv_file , delimiter=',', quotechar='|')
	
	for row in csv_reader:
	    latlon = ",".join(row)
	    latlon_splitted = latlon.split(',')
	    
	    lat = latlon_splitted[0]
	    lon = latlon_splitted[1]
	    
	    point = GEOSGeometry('POINT(%s %s)' % (lon, lat))
	    
	    # 1º = 111.045km
	    radius = 0.5 / 111.045
	    
	    area = point.buffer(radius)
	    poligons.append(area)

	return MultiPolygon(poligons)
