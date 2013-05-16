import os

import warnings
warnings.filterwarnings('ignore', r"django.contrib.localflavor is deprecated")

from django.contrib.gis.utils import LayerMapping
from spain_multipolygons.models import SpainRegions

region_mapping = {
    'name' : 'Name',
    'mpoly' : 'MULTIPOLYGON',
}

region_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), '/home/ubuntu/ENV/spain/52 [Melilla].shp'))
	
def run(verbose=True):
    lm = LayerMapping(SpainRegions, region_shp, region_mapping,
                      transform=False, encoding='utf8')

    lm.save(strict=True, verbose=verbose)