# -*- encoding: utf-8 -*-
import collections

from rest_api.models import Application, AppDeviceType
from rest_api import ranker

from django.contrib.gis.geos import Point

from itertools import chain


'''
SEARCHES APPS FOR THAT LATITUDE AND LONGITUDE
'''
def search(lat, lon, accuracy):
	
	point = Point(float(lon), float(lat))
	
		
	# 1º = 111.045km
	# Area = 250m, we dont use accuracy now
	radius = float(float(accuracy) / 1000) / 111.045
	user_area = point.buffer(radius)
		
	# Get geometries
	rp_geometries = ranker.get_rp_geoms(user_area)
	cc_wc_geometries = ranker.get_cc_wc_geoms(user_area)

	geometry_mix = chain(cc_wc_geometries, rp_geometries)
	
	ranking_dict = collections.OrderedDict()
	apps_ids = []
	for geom in geometry_mix:
		geom_app = geom.app.app_id_appstore
		ranking_dict[geom_app] = geom.origin
		apps_ids.append(geom_app)
		
	# Get only apps compatible with iPhone and iPod
	iphone_ipod_device_ids = [2, 3, 4, 5, 6, 9, 10, 11, 15, 18, 19]
	iphone_ipod_apps = AppDeviceType.objects.filter(device_type_id__in=iphone_ipod_device_ids, app_id__in=apps_ids).values_list('app_id', flat=True)
		
	return Application.objects.filter(pk__in=iphone_ipod_apps)
	
	
'''
SEARCHES APPS FOR THAT ENTITY
'''
def search_for_polygon(entity, parent_entity):
	
	cc_wc_geometries = ranker.get_cc_wc_geoms_for_poly(entity)
	
	# Polygons like Madrid has not CC geometries, because its parent, (Madrid, P) has same name
	if len(cc_wc_geometries) == 0:
		rp_geometries = ranker.get_rp_geoms_for_poly(parent_entity)
		
	else:
		rp_geometries = ranker.get_rp_geoms_for_poly(entity)

	geometry_mix = chain(cc_wc_geometries, rp_geometries)
	
	ranking_dict = collections.OrderedDict()
	apps_ids = []
	for geom in geometry_mix:
		geom_app = geom.app.app_id_appstore
		ranking_dict[geom_app] = geom.origin
		apps_ids.append(geom_app)
		
	# Get only apps compatible with iPhone and iPod
	iphone_ipod_device_ids = [2, 3, 4, 5, 6, 9, 10, 11, 15, 18, 19]
	iphone_ipod_apps = AppDeviceType.objects.filter(device_type_id__in=iphone_ipod_device_ids, app_id__in=apps_ids).values_list('app_id', flat=True)
		
	return Application.objects.filter(pk__in=iphone_ipod_apps)
	
	
#          2 | iPhoneFirstGen
#          3 | iPodTouchFirstGen
#          4 | iPodTouchSecondGen
#          5 | iPhone3G
#          6 | iPhone3GS
#          7 | iPadWifi
#          8 | iPad3G
#          9 | iPhone4
#         10 | iPodTouchThirdGen
#         11 | iPodTouchFourthGen
#         12 | iPad2Wifi
#         13 | iPad23G
#         14 | MacDesktop
#         15 | iPhone4S
#         16 | iPadThirdGen
#         17 | iPadThirdGen4G
#         18 | iPhone5
#         19 | iPodTouchFifthGen
#         20 | iPadFourthGen
#         21 | iPadFourthGen4G
#         22 | iPadMini
#         23 | iPadMini4G