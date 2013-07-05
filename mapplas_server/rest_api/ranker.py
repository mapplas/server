# -*- encoding: utf-8 -*-
from django.contrib.gis.geos import Point

from rest_api.models import Geometry, Polygon

from django.db.models import Q


def rank_apps(lat, lon, accuracy):

	point = Point(float(lon), float(lat))
	
	# 1º = 111.045km
	radius = (float(accuracy) / 1000) / 111.045
	my_area = point.buffer(radius)
		
	# Get polygons insersecting given area	
	query = ("select id from rest_api_polygon where origin='CH' and ST_Intersects(polygon, ST_GeomFromText('SRID=4326;POINT(%s %s)')) order by polygon <#> 'SRID=4326;POINT(%s %s)'" % (lon, lat, lon, lat))
	#query = ("select id from rest_api_polygon where origin='CH' and ST_Intersects(polygon, ST_GeomFromText('SRID=4326;%s')) order by polygon <#> 'SRID=4326;%s'" % (my_area, my_area))
	chain_polygon_ids = Polygon.objects.raw(query)
	
	chain_ids = []
	for chain_id in chain_polygon_ids:
		chain_ids.append(chain_id)
		
	
	# Get regions polygon ids
	region_polygon_ids = Polygon.objects.filter(Q(origin='CC', polygon__intersects=my_area) | Q(origin='P', polygon__intersects=my_area) | Q(origin='R', polygon__intersects=my_area)).values_list('id', flat=True)
	
	# Get geometries for polygons	
	geometries_ids = Geometry.objects.filter(Q(polygon_id__in=region_polygon_ids) | Q(polygon_id__in=chain_ids)).order_by('-ranking')
# 	chain_geometries_ids = Geometry.objects.filter(polygon_id__in=chain_ids)
	
	#return region_geometries_ids | chain_geometries_ids
	return geometries_ids