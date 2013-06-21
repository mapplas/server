# -*- encoding: latin-1 -*-
import re, os, sys, csv
import spain_multipolygons
import codecs

from django.contrib.gis.geos import Point, GEOSGeometry, MultiPolygon

from entity_extractor.models import geonames_all_countries
from entity_extractor.models import Entities, EntityTypes
from entity_extractor import regex

from spain_multipolygons.models import SpainRegions

from rest_api.models import Application, Storefront, AppPrice, Geometry, AppDetails, Polygon, ChainCathegory


#	from entity_extractor import chain_generator
#	chain_generator.extract_entities_from_csv_files()

'''
Get all files from /home/ubuntu/temp/chains and generates a CH ENTITY with file points.
'''
def extract_entities_from_csv_files():
	
	p = re.compile(r'^.*.csv$')
	
	for path, subdirs, files in os.walk('/home/ubuntu/temp/chains/'):
	
		for filename in files:
			
			filename = str(filename)
			
			if p.match(filename):
					
				filename_clean = filename.replace('_', ' ')
				filename_clean = filename_clean.replace('.csv', '')
				
				try:
					entity = Entities.objects.get(name1=filename_clean, region_type='CH')
					print('Exists ' + filename_clean + ' entity')
					
					entity.mpoly = generate_mpoly_from_file(filename)
					entity.save()
					
				except Entities.DoesNotExist:
					print('Create ' + filename_clean + ' entity')
					entity = Entities()
					entity.name1 = get_name_from_file(filename)
					entity.name2 = filename
					entity.lang_code = 'ES'
					entity.lang_code2 = 'ES'
					entity.region_type = EntityTypes.objects.get(identifier='CH')
					entity.mpoly = generate_mpoly_from_file(filename)
					entity.save()
		
		

def get_name_from_file(filename):

	csv_file = open('/home/ubuntu/temp/chains/%s' % filename)
	csv_reader = csv.reader(csv_file , delimiter=',', quotechar='|')
	
	first = True
	
	for row in csv_reader:
		if first:
			return unicode(row[0], 'latin-1')
		else:
			break
		
	
				
def generate_mpoly_from_file(filename):

	csv_file = open('/home/ubuntu/temp/chains/%s' % filename)
	poligons = []

	csv_reader = csv.reader(csv_file , delimiter=',', quotechar='|')
	
	first = True
	
	for row in csv_reader:
	
		if not first:

		    latlon = ",".join(row)
		    latlon_splitted = latlon.split(',')
		    
		    lat = latlon_splitted[0]
		    lon = latlon_splitted[1]
		    
		    point = GEOSGeometry('POINT(%s %s)' % (lon, lat))
		    
		    # 1º = 111.045km
		    radius = 1.5 / 111.045
		    
		    area = point.buffer(radius)
		    poligons.append(area)
		    
		else:
			
			first = False

	return MultiPolygon(poligons)
	
'''

'''
#	from entity_extractor import chain_generator
#	chain_generator.populate_chain_category_table_from_txt()
def populate_chain_category_table_from_txt():

	csv_file = codecs.open('/home/ubuntu/temp/category_places.txt', encoding='latin-1')
	
	i = 0
	
	for row in csv_file:
		data_splitted = row.split(',')

		entity_name = data_splitted[0]
		#print(repr(entity_name))	u'Uterq\xc3\xbce'		
		mapplas_cathegory = data_splitted[1]
		
		try:
			entity = Entities.objects.get(name1=entity_name, region_type='CH')
			
			chain_cathegory = ChainCathegory()
			chain_cathegory.entity_id = entity.id
			chain_cathegory.mapplas_cathegories_id=mapplas_cathegory
			chain_cathegory.save()
			
			print('SAVED ' + entity_name)
			i = i + 1
			
		except Entities.DoesNotExist:
			print(entity_name + ' does NOT exist in entities')
		
			
	print(i)