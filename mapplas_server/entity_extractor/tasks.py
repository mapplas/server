# -*- encoding: utf-8 -*-

from celery import task

from entity_extractor.models import Entities
from rest_api.models import Storefront

import chain_extractor


#	from entity_extractor.tasks import *
#	find_chains_in_apps.apply_async(['USA'])

'''
Finds chain name in application titles and assigns that polygon to app
'''
@task
def find_chains_in_apps(storefront_country_code):

	if storefront_country_code == 'USA':
		parent_id = 13443
	else:
		parent_id = 1
	
	storefront_id = Storefront.objects.get(country_code=storefront_country_code).storefront_id
	chains = Entities.objects.filter(region_type_id='CH', storefront_id=storefront_id, parent=parent_id)	
	
	step = 100
	start = 0
	
	first = True
	
	chains_size = chains.count()
	print(chains_size)			

	while start < chains_size:
		print('LOOP %d, %d' % (start, start+step))

		chain_step = chains[start:start+step]
		start = start + step
		
		chain_extractor.find_chains_in_apps_for_storefront(chain_step, storefront_country_code)