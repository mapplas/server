# -*- encoding: utf-8 -*-

from rest_api.models import Application, Geometry, UserBlockedApps, UserPinnedApps

from django.contrib.gis.geos import Point

'''
SEARCHES APPS FOR THAT LATITUDE AND LONGITUDE
'''
def search(lat, lon, accuracy):
	
	point = Point(float(lon), float(lat))
	
	geom_intersecting_point = Geometry.objects.filter(polygon__intersects=point)
	apps = []
	
	for geom in geom_intersecting_point:
		
		app = Application.objects.get(app_id_appstore=geom.app.app_id_appstore)
		apps.append(app)
		
	# Remove duplicated apps
	apps_without_duplicates = list(set(apps))

	return apps_without_duplicates


'''
REMOVES USER BLOCKED APPS FROM GIVEN APPLICATION LIST
'''
def remove_user_blocked_apps(apps, user_id):

	not_blocked_apps = []

	for app in apps:
		try:
			blocked = UserBlockedApps.objects.get(user_id=user_id, app_id=app.app_id_appstore)
			
		except UserBlockedApps.DoesNotExist:
			not_blocked_apps.append(app)

	
	return not_blocked_apps
	
	
'''
SETS USER PINNED APPS AT THE BEGINNING OF THE LIST
'''
def pinned_apps_first(apps_ok_to_user, user_id, user_pinned_apps):
	pinned_apps = []

	'''
	Remove pinned apps from apps list
	Add that app to pinned apps to sent to user
	Not sent other apps pinned by user that they are not going to be sent
	'''
	for pinned_app in user_pinned_apps:
	
		for app in apps_ok_to_user:
		
			if pinned_app.app_id == app.app_id_appstore:
				
				apps_ok_to_user.remove(app)
				pinned_apps.append(Application.objects.get(pk=pinned_app.app_id))
				
	'''
	Add two lists, pinned apps before; and return
	'''
	return pinned_apps + apps_ok_to_user