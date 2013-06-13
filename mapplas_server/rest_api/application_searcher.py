# -*- encoding: utf-8 -*-

from rest_api.models import Application, Geometry, UserBlockedApps, UserPinnedApps, Polygon, AppDeviceType

from django.contrib.gis.geos import Point


'''
SEARCHES APPS FOR THAT LATITUDE AND LONGITUDE
'''
def search(lat, lon, accuracy):
	point = Point(float(lon), float(lat))
	#area = point.buffer(accuracy)
	
	# Get polygons insersecting given area
	polygon_intersecting_points_ids = Polygon.objects.filter(polygon__intersects=point).values_list('id', flat=True)
	
	# Get geometries for polygons
	geometries_apps = Geometry.objects.filter(polygon_id__in=polygon_intersecting_points_ids).values_list('app_id', flat=True)

	# Get apps for that geometries	
	apps_ids = Application.objects.filter(pk__in=geometries_apps).values_list('app_id_appstore', flat=True) 
	
	# Get only apps compatible with iPhone and iPod
	iphone_ipod_device_ids = [1, 2, 3, 4, 5, 6, 9, 10, 11, 15, 18, 19]
	iphone_ipod_apps = AppDeviceType.objects.filter(device_type_id__in=iphone_ipod_device_ids, app_id__in=apps_ids).values_list('app_id', flat=True)
	
	return Application.objects.filter(pk__in=iphone_ipod_apps)


'''
REMOVES USER BLOCKED APPS FROM GIVEN APPLICATION LIST
'''
def remove_user_blocked_apps(apps, user_id):
	# Get given users blocked apps ids
	user_blocked_apps_ids = UserBlockedApps.objects.filter(user_id=user_id).values_list('app_id', flat=True)

	# Removes user blocked app ids from app list
	return apps.exclude(pk__in=user_blocked_apps_ids)


'''
SETS USER PINNED APPS AT THE BEGINNING OF THE LIST
'''
def pinned_apps_first(apps_ok_to_user, user_id):
	
	user_pinned_apps_ids = UserPinnedApps.objects.filter(user_id=user_id).values_list('app_id', flat=True)
	user_pinned_apps = Application.objects.filter(pk__in=user_pinned_apps_ids)
	
	apps_without_pinned = apps_ok_to_user.exclude(pk__in=user_pinned_apps_ids)
	
	# Remove duplicated apps
	return list(user_pinned_apps) + list(set(apps_without_pinned))