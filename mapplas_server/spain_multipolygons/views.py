from django.contrib.gis.geos import Point, GEOSGeometry

from spain_multipolygons.models import SpainRegions


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