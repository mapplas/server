import csv

from django.contrib.gis.geos import Point, GEOSGeometry, MultiPolygon
from django.contrib.gis.db.models import Union

from entity_extractor.models import Entities

'''
From entity_extractor_entities table gets 'PL' rows
Gets english name of place
Searches .csv file for that name
'''
def insert_mpolys_from_entity_names():
	
	placeEntities = Entities.objects.all().filter(region_type='PL')
	
	for placeEntity in placeEntities:
	
		entity_name = placeEntity.name2
		print(entity_name)
		placeEntity.mpoly = get_mpoly_for_entity(entity_name)
		placeEntity.save()
		print('SAVED')



def get_mpoly_for_entity(entity_name):

	csv_file = open("/home/ubuntu/temp/places/%s.csv" % entity_name) #prepare a csv file for our example
	poligons = []
	
	csv_reader = csv.reader(csv_file , delimiter=',', quotechar='|')
	#now the testReader is an array,so we can iterate it
	for row in csv_reader:
	    latlon = ",".join(row)
	    latlon_splitted = latlon.split(',')
	    
	    lat = latlon_splitted[0]
	    lon = latlon_splitted[1]
	    
	    point = GEOSGeometry('POINT(%s %s)' % (lon, lat))
	    radius = 500
	    area = point.buffer(radius)
	    poligons.append(area)


	return MultiPolygon(poligons)