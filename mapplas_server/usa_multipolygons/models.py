from django.contrib.gis.db import models

class UsaCounties(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    county = models.CharField(max_length=80)
    name = models.CharField(max_length=80, null=True)

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
    mpoly = models.MultiPolygonField()
    
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __unicode__(self):
        return self.name + ' ' + self.county
