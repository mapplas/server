# -*- encoding: utf-8 -*-
from django.contrib.gis.geos import Point

from rest_api.models import Geometry, Polygon

from django.db.models import Q


def rank_apps(lat, lon, accuracy):

	point = Point(float(lon), float(lat))
	
	# 1º = 111.045km
	# radius = (float(accuracy) / 1000) / 111.045
	# my_area = point.buffer(radius)
		
	# Get polygons insersecting given area	
	query = ("select id from rest_api_polygon where origin='CH' and ST_Intersects(polygon, ST_GeomFromText('SRID=4326;POINT(%s %s)')) order by polygon <#> 'SRID=4326;POINT(%s %s)'" % (lon, lat, lon, lat))
	#chain_polygon_ids = Polygon.objects.raw(query)
	
	region_polygon_ids = Polygon.objects.filter(Q(origin='CC', polygon__intersects=point) | Q(origin='P', polygon__intersects=point) | Q(origin='R', polygon__intersects=point) | Q(origin='S', polygon__intersects=point)).values_list('id', flat=True)
	
	total = region_polygon_ids
	
	regions_geometries_ids = Geometry.objects.filter(polygon_id__in=total)
	
	return regions_geometries_ids