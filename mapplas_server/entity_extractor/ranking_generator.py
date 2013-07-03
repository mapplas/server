# -*- encoding: utf-8 -*-
from rest_api.models import Application, UserPinnedApps, UserBlockedApps, UserSharedApps, Geometry, Polygon, Ranking

'''
Generates a ranking value for each geometry
'''
def generate_ranking_for_geometries():

	# Constants
	ranking_max_value = 1002
	
	pinned_apps_total_count = UserPinnedApps.objects.all().count()
	blocked_apps_total_count = UserBlockedApps.objects.all().count()
	shared_apps_total_count = UserSharedApps.objects.all().count()
	pin_block_share_total_relation = pinned_apps_total_count - blocked_apps_total_count + (2 * shared_apps_total_count)
	
	# Loop all geometries
	for geometry in Geometry.objects.all():
	
		# Ranking calculator
		rankings_for_app = Ranking.objects.filter(app_id=geometry.app_id).values_list('app_rank', flat=True)
		
		rankings_for_app_length = rankings_for_app.count()
		
		if rankings_for_app_length > 0:
				
			rankings_sum = 0
			for ranking in rankings_for_app:
				rankings_sum = rankings_sum + ranking
		
			ranking = rankings_sum / rankings_for_app_length
			
		else:
			ranking = 1002
			
		
		ranking_parameter = 1 / ranking
		
		
		# Area calculator
		polygons_for_app = Polygon.objects.filter(pk=geometry.polygon_id).values_list('polygon', flat=True)
		
		app_polygons_area = 0
		for polygon in polygons_for_app:
		
			app_polygons_area = app_polygons_area.area
			
		area_parameter = 1 / app_polygons_area
		
		
		# Pin / block / share relation calculator
		app_pinned_count = UserPinnedApps.objects.filter(app_id=geometry.app_id).count()
		app_blocked_count = UserBlockedApps.objects.filter(app_id=geometry.app_id).count()
		app_shared_count = UserSharedApps.objects.filter(app_id=geometry.app_id).count()
		
		pin_block_share_relation_parameter = pin_block_share_total_relation / (app_pinned_count - app_blocked_count + (2 * app_shared_count))
		
		
		# Ranking calculation
		ranking = (alpha_c * ranking_parameter) + (beta_c * area_parameter) + (delta_c * pin_block_share_relation_parameter)

		geometry.ranking = ranking
		geometry.save()
		
		print('********')
		print(ranking)
		print(Application.objects.get(pk=geometry.app_id).app_name()