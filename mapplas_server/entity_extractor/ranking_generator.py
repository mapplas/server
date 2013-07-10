# -*- encoding: utf-8 -*-

from rest_api.models import Application, UserPinnedApps, UserBlockedApps, UserSharedApps, Geometry, Polygon, Ranking, GenreApp
from entity_extractor.models import Entities

'''
Generates a ranking value for each geometry

If overwrite = Yes, all geometries ranking are recalculed
'''
def generate_ranking_for_geometries(overwrite):
	
	#
	# Constants
	#
	alpha_c = 1
	beta_c = 1
	delta_c = 1
	
	#
	ranking_max_value = 1002
	
	#
	pinned_apps_total_count = UserPinnedApps.objects.all().count()
	blocked_apps_total_count = UserBlockedApps.objects.all().count()
	shared_apps_total_count = UserSharedApps.objects.all().count()
	pin_block_share_total_relation = pinned_apps_total_count - blocked_apps_total_count + (2 * shared_apps_total_count)
	
	#
	food_and_drink_genre_id = 6023
	travel_genre_id = 6003
	navigation_genre_id = 6010
	reference_genre_id = 6006
	education_genre_id = 6017
	
	appstore_main_genre_ids = [food_and_drink_genre_id, travel_genre_id, navigation_genre_id, reference_genre_id, education_genre_id]
	
	
	# Overwrite previous generated geometries or not
	if overwrite:
		geometries = Geometry.objects.all()
	else:
		geometries = Geometry.objects.filter(ranking!=NoneType)
		
		
	# Loop all geometries
	for geometry in geometries:
	
		# Appstore ranking param
		ranking = get_ranking_parameter_for_geometry(geometry)
		ranking_parameter = float(1 / ranking)


		# Area ranking param
		app_polygons_area = get_area_parameter_for_geometry(geometry)
		area_parameter =  float(1 / app_polygons_area)
		
		
		# Popularity ranking param
		popularity_parameter = get_popularity_parameter_for_geometry(geometry, pin_block_share_total_relation)
		
		
		# Food & Drink | Travel | Navigation | Reference | Education genres ranks better
		if is_geometry_app_genre_in_main_appstore_genres(geometry, appstore_main_genre_ids):
			# Add more ranking
			
		
		# Oficial string match in app title ranks better
		if geometry_contains_official_string_in_app_title(geometry):
			# Add more ranking
			
		#
		# Ranking calculation
		#
		ranking =  float(alpha_c * ranking_parameter) + float(beta_c * area_parameter) + float(delta_c * popularity_parameter)

		geometry.ranking = float(ranking)
		geometry.save()
		
		print('******** %f - %f - %f' % (float(alpha_c * ranking_parameter), float(beta_c * area_parameter), float(delta_c * pin_block_share_relation_parameter)))
		app = Application.objects.get(pk=geometry.app_id)
		print('%f for app %s' % (ranking, app.app_name.encode('utf-8')))
		
		
'''
CALCULATES RANKING FIRST VALUE FROM APP STORE RANKING FOR APPLICATION
'''		
def get_ranking_parameter_for_geometry(geometry):

	# Ranking calculator
	rankings_for_app = Ranking.objects.filter(app_id=geometry.app_id).values_list('app_rank', flat=True)
	
	rankings_for_app_length = rankings_for_app.count()
	#print('rankings_for_app_length: %d' % rankings_for_app_length)
	if rankings_for_app_length > 0:
			
		rankings_sum = 0
		for ranking in rankings_for_app:
			rankings_sum = rankings_sum + ranking
	
		#print('rankings_sum %d' % rankings_sum)
		ranking = float(rankings_sum / rankings_for_app_length)
		
	else:
		ranking = ranking_max_value

	#print('ranking %f' % ranking)
	return ranking
	
	
'''
CALCULATES RANKING SECOND VALUE FROM AREA OF GEOMETRY POLYGONS
'''	
def get_area_parameter_for_geometry(geometry):
	# Area calculator
	polygons_for_app = Polygon.objects.filter(pk=geometry.polygon_id).values_list('polygon', flat=True)
	#print('polygons_for_app count %d' % len(polygons_for_app))
	
	app_polygons_area = 0.0
	for polygon in polygons_for_app:
	
		app_polygons_area = float(app_polygons_area + polygon.area)
	
	#print('app_polygons_area %f' % app_polygons_area)
	return app_polygons_area
	
	
'''
CALCULATES RANKING THIRD VALUE FROM PINNED, BLOCKED AND APPS SHARED INFO
'''	
def get_popularity_parameter_for_geometry(geometry, pin_block_share_total_relation):

	# Pin / block / share relation calculator
	app_pinned_count = UserPinnedApps.objects.filter(app_id=geometry.app_id).count()
	app_blocked_count = UserBlockedApps.objects.filter(app_id=geometry.app_id).count()
	app_shared_count = UserSharedApps.objects.filter(app_id=geometry.app_id).count()
	
	divisor = (app_pinned_count - app_blocked_count + (2 * app_shared_count))

	pin_block_share_relation_parameter = 0
	if divisor != 0:
		pin_block_share_relation_parameter = pin_block_share_total_relation / divisor
		
	return pin_block_share_relation_parameter
	
	
'''
CALCULATES BETTER RANK FOR APPS THAT MATCH Food & Drink | Travel | Navigation | Reference | Education GENRES
'''
def is_geometry_app_genre_in_main_appstore_genres(geometry, appstore_main_genre_ids):
	
	# Get app genre in appstore
	genre_app = GenreApp.objects.get(app_id=geometry.app_id, is_primary=True)
	
	# If geometry related app genre is in previous array, increment ranking	
	if genre_app.genre_id in appstore_main_genre_ids:
		return True
	else:
		return False
	

'''
CALCULATES BETTER RANK FOR APPS THAT MATCH OFFICIAL OR OFICIAL STRING IN APPLICATION TITLE

When extracting app with extractor algorithms, if 'official' or 'oficial' string was found, 716141 points were added to ranking.

'''
def geometry_contains_official_string_in_app_title(geometry):
	
	if geometry.ranking == 716141:
		return True
	else:
		return False