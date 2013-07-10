# -*- encoding: utf-8 -*-
import collections

from rest_api.models import Application, Geometry, UserBlockedApps, UserPinnedApps, Polygon, AppDeviceType
from rest_api import ranker

'''
SEARCHES APPS FOR THAT LATITUDE AND LONGITUDE
'''
def search(lat, lon, accuracy, uid):
	
	geometries_apps_list = ranker.rank_apps(lat, lon, accuracy)
		
	# Create ranking dictionary
	related_geom = geometries_apps_list.select_related('app_id')
	
	ranking_dict = collections.OrderedDict()
	
	for geometry in related_geom:
		ranking_dict[geometry.app.app_id_appstore] = geometry.origin
	

	# Get app ids from ranker
	apps_ids = geometries_apps_list.values_list('app_id', flat=True)
	
	# Get only apps compatible with iPhone and iPod
	iphone_ipod_device_ids = [1, 2, 3, 4, 5, 6, 9, 10, 11, 15, 18, 19]
	iphone_ipod_apps = AppDeviceType.objects.filter(device_type_id__in=iphone_ipod_device_ids, app_id__in=apps_ids).values_list('app_id', flat=True)
	
	iphone_ipod_apps = Application.objects.filter(pk__in=iphone_ipod_apps)
	
	# Remove user blocked apps
	apps_without_blocked = remove_user_blocked_apps(iphone_ipod_apps, uid)
	
	# Set user pinned apps before
	apps_with_pinned_before = pinned_apps_first(apps_without_blocked, uid, ranking_dict)
	
	return apps_with_pinned_before


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
def pinned_apps_first(apps_ok_to_user, user_id, ranking_dict):	
	
	user_pinned_apps_ids = UserPinnedApps.objects.filter(user_id=user_id).values_list('app_id', flat=True)
	user_pinned_apps = Application.objects.filter(pk__in=user_pinned_apps_ids)
	
	# Apps that are not pinned
	apps_without_pinned = apps_ok_to_user.exclude(pk__in=user_pinned_apps_ids)

	# Order apps ok to user
	apps = []
	apps_ok_to_user_ids = apps_without_pinned.values_list('app_id_appstore', flat=True)

	for app_id, origin in ranking_dict.items():
		if app_id in apps_ok_to_user_ids:
			apps.append(Application.objects.get(pk=app_id))
	
	# Apps pinned in apps ok to user
	pinned_apps_to_send = list(set(user_pinned_apps) & set(apps_ok_to_user))
			
	return pinned_apps_to_send + apps