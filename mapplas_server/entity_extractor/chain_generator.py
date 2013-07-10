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
STEP 1
Get all files from /home/ubuntu/temp/chains_XXX and generates a CH ENTITY with file points.

Storefront country code:
	ESP - Spain
	USA - United States of America
'''
def extract_entities_from_csv_files(storefront_country_code):
	
	p = re.compile(r'^.*.csv$')
	
	# CONSTANTS
	spain_state_entity_id = Entities.objects.get(name1='España').id
	spain_storefront_id = Storefront.objects.get(country_code='ESP').storefront_id
	
	usa_state_entity_id = Entities.objects.get(name1='United States of America').id
	usa_storefront_id = Storefront.objects.get(country_code='USA').storefront_id
	
	for path, subdirs, files in os.walk('/home/ubuntu/temp/chains_%s/' % storefront_country_code.lower()):
		
		for filename in files:
			
			filename = str(filename)
			
			if p.match(filename):
					
				filename_clean = filename.replace('_', ' ')
				filename_clean = filename_clean.replace('.csv', '')
				
				try:
					entity = Entities.objects.get(name1=filename_clean, region_type='CH')
					print('Exists ' + filename_clean + ' entity')
					
					entity.mpoly = generate_mpoly_from_file(filename, storefront_country_code)
					entity.save()
					
				except Entities.DoesNotExist:
					print('Create ' + filename_clean + ' entity')
					entity = Entities()
					entity.name1 = get_name_from_file(filename, storefront_country_code)
					entity.name2 = filename
					
					if storefront_country_code == 'ESP':
						entity.lang_code = 'ES'
						entity.lang_code2 = 'ES'
						entity.parent = spain_state_entity_id
						entity.storefront_id = spain_storefront_id
					else:
						entity.lang_code = 'EN'
						entity.lang_code2 = 'EN'
						entity.parent = usa_state_entity_id
						entity.storefront_id = usa_storefront_id
												
					entity.region_type = EntityTypes.objects.get(identifier='CH')
					entity.mpoly = generate_mpoly_from_file(filename, storefront_country_code)
					entity.save()
		
		

def get_name_from_file(filename, storefront_country_code):

	csv_file = open("/home/ubuntu/temp/chains_%s/%s" % (storefront_country_code.lower(), filename), "rU")
	csv_reader = csv.reader(csv_file , delimiter=',', quotechar='|')
	
	first = True
	
	for row in csv_reader:
		if first:
			return unicode(row[0], 'latin-1')
		else:
			break
		
	
				
def generate_mpoly_from_file(filename, storefront_country_code):

	csv_file = open("/home/ubuntu/temp/chains_%s/%s" % (storefront_country_code.lower(), filename), "rU")
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
		    # 5 meters of radius
		    radius = 0.005 / 111.045
		    
		    area = point.buffer(radius)
		    poligons.append(area)
		    
		else:
			
			first = False

	return MultiPolygon(poligons)
	
	
'''
STEP 2
Creates chain cathegories tables

Storefront country code:
	ESP - Spain
	USA - United States of America
'''
#	from entity_extractor import chain_generator
#	chain_generator.populate_chain_category_table_from_txt('USA')
def populate_chain_category_table_from_txt(storefront_country_code):

	csv_file = codecs.open('/home/ubuntu/temp/category_places_%s.txt' % storefront_country_code.lower(), encoding='latin-1')
	
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