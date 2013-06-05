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
	
	for app in apps:
		'''
		Check if app is blocked by user
		'''
		try:
			if (UserBlockedApps.objects.get(user_id=user_id, app_id=app.app_id_appstore)):
				apps.remove(app)
			
		except UserBlockedApps.DoesNotExist:
			'''
			Do nothing
			'''
			
	return apps
	
	
'''
SETS USER PINNED APPS AT THE BEGINNING OF THE LIST
'''
def pinned_apps_first(apps_ok_to_user, user_id):

	user_pinned_apps = UserPinnedApps.objects.filter(user_id=user_id)

	'''
	Remove pinned apps from apps list
	'''
	for pinned_app in user_pinned_apps:
	
		for app in apps_ok_to_user:
		
			if pinned_app.app_id == app.app_id_appstore:
				
				apps_ok_to_user.remove(app)
				
	'''
	Convert UserPinnedApps object list to app list
	'''
	pinned_apps = []
	
	for pinned_app in user_pinned_apps:
	
		pinned_apps.append(Application.objects.get(pk=pinned_app.app_id))
		
	'''
	Add two lists, pinned apps before; and return
	'''
	return pinned_apps + apps_ok_to_user