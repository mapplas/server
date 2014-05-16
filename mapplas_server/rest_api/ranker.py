# -*- encoding: utf-8 -*-
from rest_api.models import Geometry, Storefront, AppPrice
from entity_extractor.models import Entities

from django.db.models import Q


'''
Returns R and P origin geometries that intersect with user position ordered by ranking
'''
def get_rp_geoms(user_area, storefront_id):
	
	region_polygon_ids = Entities.objects.filter(Q(region_type_id='R', mpoly__intersects=user_area)).values_list('id', flat=True)
	province_polygon_ids = Entities.objects.filter(Q(region_type_id='P', mpoly__intersects=user_area)).values_list('id', flat=True)
	
	app_ids = Geometry.objects.filter(Q(entity_id__in=(region_polygon_ids | province_polygon_ids))).order_by('-ranking').values_list('app_id', flat=True)
	
	return AppPrice.objects.filter(app_id__in=app_ids, storefront_id=storefront_id).values_list('app_id', flat=True)
	
	
'''
Returns CC origin geometries that intersect with user position ordered by ranking
'''
def get_cc_geoms(user_area, storefront_id):
	
	region_polygon_ids = Entities.objects.filter(Q(region_type_id='CC', mpoly__intersects=user_area)).values_list('id', flat=True)
	app_ids = Geometry.objects.filter(Q(entity_id__in=region_polygon_ids)).order_by('-ranking').values_list('app_id', flat=True)
	
	return AppPrice.objects.filter(app_id__in=app_ids, storefront_id=storefront_id).values_list('app_id', flat=True)


'''
Returns WC origi
'''
def get_wc_geoms(user_area, storefront_id):
	region_polygon_ids = Entities.objects.filter(Q(region_type_id='WC', mpoly__intersects=user_area)).values_list('id', flat=True)
	
	app_ids = Geometry.objects.filter(Q(entity_id__in=region_polygon_ids)).order_by('-ranking', 'id').values_list('app_id', flat=True)
	
	return AppPrice.objects.filter(app_id__in=app_ids, storefront_id=storefront_id).values_list('app_id', flat=True)