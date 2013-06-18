# -*- encoding: utf-8 -*-

from celery import task
import re
from django.core.files import File

from entity_extractor.models import Entities, EntityTypes
from entity_extractor import regex

from rest_api.models import Application, Storefront, Geometry, AppDetails, Polygon


'''
For each PL name and second name, finds apps that are in title comined with CC names.

>>> from entity_extractor.tasks import *
>>> find_geonames_combinating_entities.apply_async()


'''
@task
def find_geonames_combinating_entities():
	i = 1000
	
	pl_entity_names = Entities.objects.filter(region_type_id='PL').values_list('name1', flat=True)
	cc_entities = Entities.objects.filter(region_type_id='CC')
	
	#change iiiiii!!!	
	pl_entity_names = pl_entity_names[0:25]
		
	for pl in pl_entity_names:
	
		write_file = open('/home/ubuntu/temp/mx/mx_%s.txt' % pl, 'w')
		myFile = File(write_file)
	
		for cc in cc_entities:
	
			pl_name = pl
			pl_name_clean = pl_name.replace('_', ' ')
			cc_name = cc.name1
			
			regex1 = r'^.*(%s).*(%s).*$' % (pl_name_clean, cc_name)
			regex2 = r'^.*(%s).*(%s).*$' % (cc_name, pl_name_clean)
			
			apps_match_1 = AppDetails.objects.filter(language_code='ES', title__iregex=regex1)
			apps_match_2 = AppDetails.objects.filter(language_code='ES', title__iregex=regex2)
			apps_match = list(apps_match_1) + list(apps_match_2)
			
			if apps_match:
					myFile.write('\n')
					myFile.write(pl_name_clean.encode('utf-8'))
					myFile.write(' - ')
					myFile.write(cc_name.encode('utf-8'))
					myFile.write('\n')			
					myFile.write(' ************\n')
				
					insert_apps_into_db(apps_match, pl_name_clean, cc_name, True, myFile, i)
					i = i + 1
			
			
			if cc.name2 and cc.name2 != 'null' and cc.name2 != 'Null' and cc.name2 != 'NULL':
				cc_name = cc.name2
				
				regex1 = r'^.*(%s).*(%s).*$' % (pl_name_clean, cc_name)
				regex2 = r'^.*(%s).*(%s).*$' % (cc_name, pl_name_clean)
				
				apps_match_1 = AppDetails.objects.filter(language_code='ES', title__iregex=regex1)
				apps_match_2 = AppDetails.objects.filter(language_code='ES', title__iregex=regex2)
				apps_match = list(apps_match_1) + list(apps_match_2)
				
				if apps_match:
					myFile.write('\n')
					myFile.write(pl_name_clean.encode('utf-8'))
					myFile.write(' - ')
					myFile.write(cc_name.encode('utf-8'))
					myFile.write('\n')
					myFile.write('************\n')
					
					insert_apps_into_db(apps_match, pl_name_clean, cc_name, False, myFile, i)
					i = i + 1

		myFile.close()

'''
Inserts found combinations into db
'''
def insert_apps_into_db(apps_matched, pl_name, cc_entity, first, myFile, i):
	entity_type_str = 'MX'
	entity_type = EntityTypes.objects.get(pk=entity_type_str)
	lang_code = 'ES'
	storefront = Storefront.objects.get(pk=143454)
	
	# Create entity for match apps
	entity = Entities()
	entity.id = i
	entity.name1 = pl_name
	entity.name2 = cc_entity
	entity.region_type = entity_type
	entity.lang_code = lang_code
	entity.lang_code2 = lang_code
	if first:
		entity.mpoly = Entities.objects.get(region_type='CC', name1=cc_entity).mpoly
	else:
		entity.mpoly = Entities.objects.get(region_type='CC', name2=cc_entity).mpoly
	entity.save()
		
	# Create polygon for match apps
	polygon = Polygon()
	polygon.polygon = entity.mpoly
	polygon.entity = entity
	polygon.origin = entity_type_str
	polygon.name = pl_name + '-' + cc_entity
	polygon.save()

	for app in apps_matched:
		geometry = Geometry()
		try:
			geometry.app = Application.objects.get(pk=app.app_id)
			geometry.storefront = storefront
			geometry.polygon = polygon
			geometry.origin = entity_type_str
			geometry.save()
			myFile.write(app.title.encode('utf-8') + '\n')
		except Application.DoesNotExist:
			continue
		


