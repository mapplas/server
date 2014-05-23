# -*- encoding: utf-8 -*-
from rest_api.models import Geometry, Storefront, AppPrice
from entity_extractor.models import Entities

from django.db.models import Q


'''
Returns R and P origin geometries that intersect with user position ordered by ranking
'''
def get_rp_geoms(user_area):
	
	region_polygon_ids = Entities.objects.filter(Q(region_type_id='R', mpoly__intersects=user_area)).values_list('id', flat=True)
	province_polygon_ids = Entities.objects.filter(Q(region_type_id='P', mpoly__intersects=user_area)).values_list('id', flat=True)
	
	return Geometry.objects.filter(Q(entity_id__in=(region_polygon_ids | province_polygon_ids))).order_by('-ranking')
		
	
'''
Returns CC and WC origin geometries that intersect with user position ordered by ranking
'''
def get_cc_wc_geoms(user_area):
	
	city_capital_polygon_ids = Entities.objects.filter(Q(region_type_id='CC', mpoly__intersects=user_area)).values_list('id', flat=True)
	world_city_polygon_ids = Entities.objects.filter(Q(region_type_id='WC', mpoly__intersects=user_area)).values_list('id', flat=True)

	return Geometry.objects.filter(Q(entity_id__in=(city_capital_polygon_ids | world_city_polygon_ids))).order_by('-ranking')


'''
Returns WC origi
'''
def get_wc_geoms(user_area):
	region_polygon_ids = Entities.objects.filter(Q(region_type_id='WC', mpoly__intersects=user_area)).values_list('id', flat=True)
	
	return Geometry.objects.filter(Q(entity_id__in=region_polygon_ids)).order_by('-ranking', 'id')
	
	

'''
Returns R and P origin geometries for given entity
'''	
def get_rp_geoms_for_poly(entity):

	return Geometry.objects.filter(Q(entity_id=entity.id, origin='P') | Q(entity_id=entity.id, origin='R')).order_by('-ranking')


'''
Returns CC and WC origin geometries for given entity
'''	
def get_cc_wc_geoms_for_poly(entity):
	
	return Geometry.objects.filter(Q(entity_id=entity.id, origin='CC') | Q(entity_id=entity.id, origin='WC')).order_by('-ranking')