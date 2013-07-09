# -*- encoding: utf-8 -*-
from rest_api.models import Application, UserPinnedApps, UserBlockedApps, UserSharedApps, Geometry, Polygon, Ranking

'''
Generates a ranking value for each geometry

If overwrite = Yes, all geometries ranking are recalculed
'''
def generate_ranking_for_geometries(overwrite):

	# Constants
	alpha_c = 1
	beta_c = 1
	delta_c = 1
	
	ranking_max_value = 1002
	
	pinned_apps_total_count = UserPinnedApps.objects.all().count()
	blocked_apps_total_count = UserBlockedApps.objects.all().count()
	shared_apps_total_count = UserSharedApps.objects.all().count()
	pin_block_share_total_relation = pinned_apps_total_count - blocked_apps_total_count + (2 * shared_apps_total_count)
	
	# Overwrite previous generated geometries or not
	if overwrite:
		geometries = Geometry.objects.all()
	else:
		geometries = Geometry.objects.filter(ranking!=NoneType)
		
		
	# Loop all geometries
	for geometry in geometries:
	
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
		
		ranking_parameter = float(1 / ranking)
		#print('ranking_parameter %f' % ranking_parameter)

		# Area calculator
		polygons_for_app = Polygon.objects.filter(pk=geometry.polygon_id).values_list('polygon', flat=True)
		#print('polygons_for_app count %d' % len(polygons_for_app))
		
		app_polygons_area = 0.0
		for polygon in polygons_for_app:
		
			app_polygons_area = float(app_polygons_area + polygon.area)
		
		#print('app_polygons_area %f' % app_polygons_area)
		
		area_parameter =  float(1 / app_polygons_area)
		#print('area_parameter %f' % area_parameter)
		
		# Pin / block / share relation calculator
		app_pinned_count = UserPinnedApps.objects.filter(app_id=geometry.app_id).count()
		app_blocked_count = UserBlockedApps.objects.filter(app_id=geometry.app_id).count()
		app_shared_count = UserSharedApps.objects.filter(app_id=geometry.app_id).count()
		
		divisor = (app_pinned_count - app_blocked_count + (2 * app_shared_count))

		if divisor == 0:
			pin_block_share_relation_parameter = 0
		else:
			pin_block_share_relation_parameter = pin_block_share_total_relation / divisor
			
		
		# Ranking calculation
		ranking =  float(alpha_c * ranking_parameter) + float(beta_c * area_parameter) + float(delta_c * pin_block_share_relation_parameter)

		geometry.ranking = float(ranking)
		geometry.save()
		
		print('******** %f - %f - %f' % (float(alpha_c * ranking_parameter), float(beta_c * area_parameter), float(delta_c * pin_block_share_relation_parameter)))
		app = Application.objects.get(pk=geometry.app_id)
		print('%f for app %s' % (ranking, app.app_name.encode('utf-8')))