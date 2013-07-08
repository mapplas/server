import os

import warnings
warnings.filterwarnings('ignore', r"django.contrib.localflavor is deprecated")

from django.contrib.gis.utils import LayerMapping
from usa_multipolygons.models import UsaCounties

region_mapping = {
    'county' : 'Name',
    'mpoly' : 'MULTIPOLYGON',
}

county_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'shp/ny_counties.shp'))
	
def run(verbose=True):

	lm = LayerMapping(UsaCounties, county_shp, region_mapping, transform=False, encoding='utf8')
	
	lm.save(strict=True, verbose=verbose)