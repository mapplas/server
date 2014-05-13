# -*- encoding: utf-8 -*-
import collections

from rest_api.models import Application, AppDeviceType
from rest_api import ranker

from django.contrib.gis.geos import Point


'''
SEARCHES APPS FOR THAT LATITUDE AND LONGITUDE
'''
def search(lat, lon, storefront_id):
	
	point = Point(float(lon), float(lat))
		
	# 1º = 111.045km
	# Area = 250m, we dont use accuracy now
	radius = 0.250 / 111.045
	user_area = point.buffer(radius)
		
	# Get geometries
	rp_geometries = ranker.get_rp_geoms(user_area, storefront_id)
	cc_geometries = ranker.get_cc_geoms(user_area, storefront_id)

	apps_ids = list(cc_geometries) + list(rp_geometries)
	
	# Get only apps compatible with iPhone and iPod
	iphone_ipod_device_ids = [1, 2, 3, 4, 5, 6, 9, 10, 11, 15, 18, 19]
	iphone_ipod_apps = AppDeviceType.objects.filter(device_type_id__in=iphone_ipod_device_ids, app_id__in=apps_ids).values_list('app_id', flat=True)
	
	return Application.objects.filter(pk__in=iphone_ipod_apps)