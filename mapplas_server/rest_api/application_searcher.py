from rest_api.models import Application, Geometry

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