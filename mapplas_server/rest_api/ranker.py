# -*- encoding: utf-8 -*-
from django.contrib.gis.geos import Point

from rest_api.models import Geometry, Polygon, Storefront
from entity_extractor.models import Entities

from django.db.models import Q


def rank_apps(lat, lon, accuracy):

	point = Point(float(lon), float(lat))
		
	# 1º = 111.045km
	# Area = 1 km, we dont use accuracy now
	radius = 1 / 111.045
	my_area = point.buffer(radius)	
	
	# Get intersection polygon ids
	region_polygon_ids = Polygon.objects.filter(Q(origin='CC', polygon__intersects=my_area) | Q(origin='P', polygon__intersects=my_area) | Q(origin='R', polygon__intersects=my_area) | Q(origin='CH', polygon__intersects=my_area)).values_list('id', flat=True)
	
# 	storefront_id = get_storefront_id_for_point(point)
	
	# Get geometries for polygons	
	geometries_ids = Geometry.objects.filter(Q(polygon_id__in=region_polygon_ids)).order_by('-ranking')

	return geometries_ids
	
	
'''
From given point, returns storefront that corresponds with it.
'''
def get_storefront_id_for_point(point):
	
	try: 
		Entities.objects.get(name1='España', mpoly__intersects=point)
		return Storefront.objects.get(country_code='ESP')
		
	except Entities.DoesNotExist:
		return Storefront.objects.get(country_code='USA')