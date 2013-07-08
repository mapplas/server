# -*- encoding: utf-8 -*-
from django.contrib.gis.geos import Point

from rest_api.models import Geometry, Polygon

from django.db.models import Q


def rank_apps(lat, lon, accuracy):

	point = Point(float(lon), float(lat))
	
	# 1º = 111.045km
	# Area = 1 km, we dont use accuracy now
	radius = 1 / 111.045
	my_area = point.buffer(radius)	
	
	# Get intersection polygon ids
	region_polygon_ids = Polygon.objects.filter(Q(origin='CC', polygon__intersects=my_area) | Q(origin='P', polygon__intersects=my_area) | Q(origin='R', polygon__intersects=my_area) | Q(origin='CH', polygon__intersects=my_area)).values_list('id', flat=True)
	
	# Get geometries for polygons	
	geometries_ids = Geometry.objects.filter(Q(polygon_id__in=region_polygon_ids)).order_by('-ranking')

	return geometries_ids