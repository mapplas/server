from django.contrib.gis.db import models

class UsaCounties(models.Model):
    county = models.CharField(max_length=80)
    name = models.CharField(max_length=80, null=True)
    parent = models.IntegerField(null=True)

    mpoly = models.MultiPolygonField()
    
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __unicode__(self):
        return self.county
