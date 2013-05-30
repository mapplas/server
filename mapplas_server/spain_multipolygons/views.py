from django.contrib.gis.geos import Point, GEOSGeometry
from django.core.files import File
from django.contrib.gis.db.models import Union

from spain_multipolygons.models import SpainRegions

'''
Prints regions for province given
'''
def regions_for_province(prov):
	
	combined_area = SpainRegions.objects.filter(province=prov).aggregate(area=Union('mpoly'))['area']
	
	gipuzkoa_mpoly_file = open('/home/ubuntu/server/mapplas_server/spain_multipolygons/gipuzkoa_mpoly.txt', 'w')
	myFile = File(gipuzkoa_mpoly_file)
	
	gipuzkoa_mpoly_file.write(str(combined_area))
	
	gipuzkoa_mpoly_file.close()


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