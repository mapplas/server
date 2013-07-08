# -*- encoding: utf-8 -*-

import os

import warnings
warnings.filterwarnings('ignore', r"django.contrib.localflavor is deprecated")

from django.contrib.gis.utils import LayerMapping
from usa_multipolygons.models import UsaCounties

# us_states.shp
# region_mapping = {
#     'county' : 'name',
#     'mpoly' : 'MULTIPOLYGON',
# }

# us_counties
# region_mapping = {
#     'name' : 'NAME',
#     'county' : 'STATE_NAME',
#     'mpoly' : 'MULTIPOLYGON',
# }

county_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'shp/UScounties.shp'))
	
def run(verbose=True):

	# us_states.shp
# 	lm = LayerMapping(UsaCounties, county_shp, region_mapping, transform=False, encoding='utf-8')
	
	# us_counties.shp
# 	lm = LayerMapping(UsaCounties, county_shp, region_mapping, transform=False, encoding='iso-8859-1')
	
	lm.save(strict=True, verbose=verbose)