# -*- encoding: utf-8 -*-
from rest_api.models import Application, Geometry, Polygon, DeveloperApp


# from entity_extractor import diff_geometries_developer_for_polygon_apps
# diff_geometries_developer_for_polygon_apps.delete_same_developer_geometries_for_polygon_depending_on_ranking()


'''
Gets all polygons saved for chains.
'''
def delete_same_developer_geometries_for_polygon_depending_on_ranking():

	polygons = Polygon.objects.filter(origin='CH')

  	for poly in polygons:
	
		geometries_for_polygon = Geometry.objects.filter(polygon_id=poly.id)
		geometries_for_polygon_count = geometries_for_polygon.count()
	
		geometries_for_polygon_app_ids = geometries_for_polygon.values_list('app_id', flat=True)
		
		# If exists more than two geometry for polygon do:
		if geometries_for_polygon_count >= 2:
			
			app_developer_for_geometries = DeveloperApp.objects.filter(app_id__in=geometries_for_polygon_app_ids).distinct('developer_id')
	
			# There is same number of developers and geometries. OK
			if app_developer_for_geometries.count() == geometries_for_polygon_count:
				print('There are same number of developers and geometries')
			
			# There are less developers than geometries. Rank negatively (-2).
			else:
				
				geometries_for_same_developer_and_polygon = geometries_for_polygon.order_by('-ranking')
				geometries_ids_for_same_developer_and_polygon = geometries_for_same_developer_and_polygon.values_list('id', flat=True)
				
				print('*************')
				geom = geometries_for_same_developer_and_polygon[:1].values_list('app_id', flat=True)
				
				geometry = Geometry.objects.get(pk=geometries_ids_for_same_developer_and_polygon[0])
				app = Application.objects.get(pk=geom[0])
				
				print('WINNER: %s app for polygon %s. RANKING: %f' % (app.app_name, poly.name, geometry.ranking))
				
				print('LOOSERS: ')
				first = True
				i = 1		
				for geom in geometries_for_same_developer_and_polygon:
					if not first:
						geometry = Geometry.objects.get(pk=geometries_ids_for_same_developer_and_polygon[i])
						print('%s WITH RANKING: %f' % (Application.objects.get(pk=geom.app_id).app_name), geometry.ranking)
						i = i+1
						geometry.ranking = -2
						geometry.save()
					else:
						first = False
											
		else:
			print('Only there is %d geometry for %s polygon' % (geometries_for_polygon_count, poly.name))